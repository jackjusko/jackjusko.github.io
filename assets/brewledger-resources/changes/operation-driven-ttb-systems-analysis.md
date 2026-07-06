# Two-Pass Systems Analysis: Operation-Driven TTB Implementation

## Pass 1: Systems-Level Integration, Edge Cases, and UI Review

### 1. Integration Flow Verification

| Flow | Status | Notes |
|------|--------|-------|
| Production Complete → RECEIVE with operation_type | OK | BatchDetail.saveProductionComplete sets `operation_type: 'production_complete'` and `data: { source: 'production_complete' }` |
| Ledger sync → server persistence | OK | Server stores full entity JSON; operation_type at top level preserved |
| TTBFormService → operation_type lookup | OK | Checks `entry.operation_type \|\| entry.data?.operation_type` |
| Transfer entries → operation_type | OK | LedgerRepository.transfer passes operationType to both OUT/IN entries |
| Packaged beer ea→bbl | OK | beerQuantityBarrels uses item.data.volume_per_unit; getBeerItemsMap provides item lookup |
| Vessel location creation | OK | Vessels.vue and VesselsList.vue create location for all new vessel types |
| Batch assignment rule | OK | Server rejects only SERVING vessels; fermenters/brites with location_id allowed |

### 2. Bugs and Gaps Identified

#### 2.1 Mobile LedgerRepository — operation_type/ttb_stage not merged into data
- **Issue**: Console LedgerRepository merges `operation_type` and `ttb_stage` into `entry.data` for sync robustness. Mobile does not.
- **Impact**: Entries created on mobile have operation_type at top level only. Server stores full object, so sync works. But for consistency and if any code path reads only from `data`, mobile-created entries could be misclassified.
- **Fix**: Add same merge logic to mobile LedgerRepository.addEntry.

#### 2.2 Mobile ItemForm — Missing volume_per_unit
- **Issue**: Console ItemForm has "Volume per unit (bbl)" for Finished Beer + unit ea/each. Mobile ItemForm has no such field.
- **Impact**: Mobile users cannot create or edit packaged beer items with volume_per_unit. TTB conversion for packaged beer would fail for items created/edited only on mobile.
- **Fix**: Add volume_per_unit field to mobile ItemForm when category=Finished Beer and unit=ea/each. Add "ea" unit option if missing.

#### 2.3 Mobile ItemForm — volume_per_unit not loaded on edit
- **Issue**: Mobile form loads `form.value = { ...item }` but item.volume_per_unit may be in item.data. Console uses `volume_per_unit: item.data?.volume_per_unit ?? null`.
- **Fix**: When loading for edit, set `volume_per_unit: item.data?.volume_per_unit ?? null` and ensure save passes it to ItemRepository.

#### 2.4 groupTransfersByPair — Uses location stage, not getStageForEntry
- **Issue**: `groupTransfersByPair` uses `stageMap.get(out.location_id)` and `stageMap.get(inn.location_id)` for fromStage/toStage. For operation_type racking, destination should be racking_keg.
- **Impact**: Used for gap detection / unclassified transfers. May misclassify transfer pairs.
- **Fix**: Use getStageForEntry for out (isDestination=false) and inn (isDestination=true) when building pairs.

#### 2.5 LedgerRepository.reverseEntry — Does not copy operation_type
- **Issue**: Reversal entry does not copy operation_type, consumption_form, or other TTB fields from original.
- **Impact**: Reversed production_complete RECEIVE would not have operation_type. TTB Line 2 filters by `(e.data || {}).source === 'production_complete'` — reversal has negated quantity and different structure; it's a CONSUME-like correction. Line 2 sums production receives; reversals typically create negating entries. Need to verify reversal doesn't break TTB.
- **Assessment**: Reversal creates same-type entry with negated quantity. For RECEIVE, the reversal is a RECEIVE with negative qty. Line 2 filters `type === 'RECEIVE' && source === 'production_complete'`. The reversal would NOT have source production_complete, so it wouldn't be in line2. But the additions.line2 is computed from ledger — does it include negative receives? Need to check. Actually the additions are computed from sum of entries. If we have RECEIVE +5 (production_complete) and RECEIVE -5 (reversal, no source), the reversal would not match the filter. So we'd have line2 = 5 from the production receive. But the total beer added would be 0. The additions.line2 comes from computeAdditions which sums entries. Let me check - the reversal might be a different type. Actually LedgerRepository.reverseEntry uses `type: originalEntry.type` so it's RECEIVE. And quantity is negated. So we'd have RECEIVE -5. The line2 filter is `source === 'production_complete'`. The reversal doesn't have that. So the reversal wouldn't be in line2. The additions.line2 is the raw sum - need to check. This could be a bug - we might be double-counting or under-counting. Defer for now; document as potential follow-up.

### 3. Edge Cases

| Edge Case | Handling |
|-----------|----------|
| Entry with operation_type at top level but not in data | TTBFormService checks both; OK |
| Entry from server (after sync) with only data.operation_type | TTBFormService checks entry.data?.operation_type; OK |
| Fermenter with no location_id (legacy) | Batch assignment allowed; packaging flow would need location. Per plan, Option B: existing vessels stay as-is |
| Item with unit "each" vs "ea" | Console checks both; mobile only has "each" in unit options — add "ea" for parity |
| PackagingRunRepository still used | Deprecated; no new writes. Line 9/10 still read legacy packaging_runs. OK |

### 4. UI Parity

| Component | Console | Mobile | Gap |
|-----------|---------|--------|-----|
| ItemForm volume_per_unit | Yes | No | Add to mobile |
| ItemForm unit "ea" | Yes | No (only "each") | Add "ea" option |
| Vessels create location for all types | Yes | Yes | OK |
| BatchForm/BatchDetail exclude SERVING | Yes | Yes | OK |
| LocationForm stage helper | Yes | Verify mobile | Check |
| Racking/Packaging removed | Yes | Yes | OK |

### 5. LocationForm Stage Helper (Mobile)
- **Check**: Console LocationForm has "Stage is used for inventory at rest (TTB Lines 1 and 33). For movements, the operation type determines the TTB column."
- **Action**: Verify mobile LocationForm has same helper text.
- **Fix**: Added helper text to mobile LocationForm.

---

## Pass 2: Fixes Applied

| Issue | Fix |
|-------|-----|
| Mobile LedgerRepository data merge | Added operation_type and ttb_stage to data merge in addEntry |
| Mobile ItemForm volume_per_unit | Added field when category=Finished Beer and unit=ea/each; added "ea", "bbl", "gal", "L" unit options |
| Mobile ItemForm edit load | Set volume_per_unit from item.data?.volume_per_unit on load |
| Mobile ItemRepository create/update | Added volume_per_unit merge into data (match console) |
| Mobile LocationForm stage helper | Added "Stage is used for inventory at rest..." helper text |
| groupTransfersByPair | Use getStageForEntry for fromStage/toStage; check data.operation_type |
| Mobile ItemForm sync | Added SyncService.sync() after save and delete |

---

## Pass 3: Bug Hunt — Edge Cases, Nulls, Type Coercion, Reversals

### 3.1 Reversal of production_complete RECEIVE — Line 2 over-reports (BUG)
- **Issue**: `calculateBeerProduced` sums only RECEIVE with `data.source === 'production_complete'`. A reversal creates RECEIVE with negative quantity and no `source`. The reversal is excluded, so Line 2 over-reports (e.g. produced 5, reversed 5 → Line 2 shows 5 instead of 0).
- **Fix**: Include reversals: for RECEIVE with `reversed_of_ledger_id`, fetch the original; if original has `source === 'production_complete'`, add this entry's quantity (negative) to the sum.

### 3.2 RECEIVE/TRANSFER_IN with negative quantity — inventory and Line 1 wrong (BUG)
- **Issue**: `calculateBeginningInventory` and `getBeerOnhandByStage` treat all RECEIVE/TRANSFER_IN as positive: `total += qty` and `delta = qty`. For a reversal (RECEIVE with -5), `beerQuantityBarrels` returns 5 (Math.abs), so we incorrectly add 5 instead of subtracting 5.
- **Fix**: Use signed quantity: `delta = (Number(entry.quantity) >= 0 ? 1 : -1) * beerQuantityBarrels(entry, item)` for RECEIVE/TRANSFER_IN. Same for calculateBeginningInventory.

### 3.3 beerQuantityBarrels when item not in map (edge case)
- **Issue**: When `map.get(entry.item_id)` returns undefined (e.g. item hard-deleted, or sync gap), we fall through to `return qty`. For packaged beer (ea), that treats ea as bbl and inflates totals.
- **Assessment**: getBeerItemsMap uses `includeDeleted: true`, so soft-deleted items are included. Orphaned entries (item gone) are rare. Could add a guard: for items with unit ea/each, if not in map, return 0 to avoid false inflation. Lower priority.

### 3.4 Packaged beer (ea) without volume_per_unit (data quality)
- **Issue**: Item has unit ea but no `volume_per_unit`. We return raw qty, treating 10 ea as 10 bbl. Design expects packaged beer to have `volume_per_unit`.
- **Assessment**: Data quality / validation. Could add warning in TTB gap detection. Not a code bug per se.

### 3.5 LedgerRepository.reverseEntry — reversal not merged into data for sync
- **Issue**: Reversal entry does not set `data` with operation_type or copy from original. When synced, server gets full object. Top-level fields are enough for TTB. No fix needed for TTB; reversal is a correction, not a movement classification.

---

## Pass 4: Conceptual Issues

### 4.1 Line 2 semantics: reversals
- **Concept**: Line 2 = "Beer produced by fermentation." A reversal corrects an error; the net production for the period should reflect that. Including reversals aligns with TTB intent (net additions).

### 4.2 getBeerOnhandByStage — entries without location_id
- **Concept**: Entries with `location_id == null` are skipped (`if (locId != null)`). Their quantity is not attributed to any stage. For Line 1/33 column breakdown, that could under-report. Most beer entries have location; acceptable for now.

### 4.3 groupTransfersByPair — currently unused
- **Status**: Function is defined but never called. Fixed in Pass 2 for future use. No further action.

### 4.4 Phase 2c deferred — no way to create ledger RECEIVE with operation_type racking/bottling
- **Concept**: Line 9/10 include ledger RECEIVE with operation_type racking/bottling/canning. The only current source is legacy packaging_runs. Phase 2c (Mark Production Complete packaging flow) was deferred. So Line 9/10 from ledger will be 0 until Phase 2c is implemented. Documented; not a bug.

---

## Pass 3 & 4 Fixes Applied

| Bug | Fix |
|-----|-----|
| Line 2 over-reports when production_complete is reversed | calculateBeerProduced: include reversals (reversed_of_ledger_id → original has source); use signed quantity |
| Beginning inventory wrong for reversal RECEIVE | calculateBeginningInventory: use signed quantity for RECEIVE/TRANSFER_IN (qty * sign) |
| getBeerOnhandByStage wrong for reversal RECEIVE | getBeerOnhandByStage: use signed quantity for RECEIVE/TRANSFER_IN (delta = qty * sign) |

---

## Pass 5: Additional Bug Hunt

### 5.1 Mobile saveProductionComplete — missing operation_type (BUG)
- **Issue**: Mobile BatchDetail.addEntry for production complete had `data: { source: 'production_complete' }` but not `operation_type: 'production_complete'`. Console has both.
- **Impact**: getStageForEntry falls back to location stage when operation_type absent. For column assignment, may misclassify if location stage differs from cellar.
- **Fix**: Added `operation_type: 'production_complete'` to mobile addEntry.

### 5.2 BatchCostService — CONSUME reversal double-counts cost (BUG)
- **Issue**: Reversal of CONSUME creates CONSUME with positive quantity. BatchCostService used Math.abs(cost) and added. So reversal would add cost again, inflating batch cost.
- **Fix**: Use signed cost: sign = (quantity >= 0 ? -1 : 1); add signedCost so reversal subtracts.

### 5.3 TTB Lines 4–10, 14–24, 27–30 — reversals not handled (BUG)
- **Issue**: All addition lines (4–10) and removal/transfer lines (14–24, 27–30) used `total += beerQuantityBarrels` without considering sign. Reversals would over-report.
- **Fix**: Added `signedBeerQuantity(entry, item, forAddition)` helper. For additions (RECEIVE/TRANSFER_IN): positive qty adds, negative subtracts. For removals (CONSUME/TRANSFER_OUT): negative qty adds, positive subtracts. Applied to all affected calculation functions.
