# Implementation Plan: Packaging, Keg Supply, and TTB Operation-Driven Rework

This plan implements the design in `ttb_stage_operation-driven_rework_bc3b8bad.plan.md`. It is organized by section with precise file paths, function names, and change descriptions. Ripple effects and edge cases are called out. Two passes over the plan have been performed to identify shortcomings and edge cases.

## Scope Summary

| Area | Key files | Summary of changes |
|------|-----------|--------------------|
| TTB columns | TTBFormService.js | operation_type drives column; fallback to location stage |
| Vessels | Vessels.vue, server.js | All vessel types get location_id; batch validation updated |
| Packaged beer | ItemRepository, ItemForm | volume_per_unit, getOrCreatePackagedBeerItem |
| **Packaging materials** | BatchDetail.vue | Explicit supply lines UI; CONSUME per material with operation_type packaging_supply |
| Production complete | BatchDetail.vue | Add packaged_keg, packaged_case; beer entries + supply CONSUMEs |
| Removal | Racking.vue (delete), router, App.vue | Remove Racking page |
| Packaging modal | BatchDetail.vue | Remove; packaging in production complete |
| Mobile | brewledger-app equivalents | Parity for vessels, BatchDetail, ItemRepository |

---

## 0. Prerequisites and Dependency Order

**Critical dependency:** Phase 2a (vessel locations) must precede Phase 2c (packaging flow), because packaging to keg requires the source vessel to have a bound location. Phase 1 is independent. Phase 2b (packaged items, TTB conversion) must precede Phase 2c.

**Recommended implementation order:**
1. Phase 1: TTB operation-driven stage (low risk, validates approach)
2. Phase 2a: Vessel = location for fermenters/brites
3. Phase 2b: Packaged beer items + volume_per_unit + TTB conversion
4. Phase 2c: Mark Production Complete packaging flow (keg/case)
5. Phase 3: Remove Racking view, deprecate packaging_runs
6. Phase 4: Location stage clarification (optional)

**Pre-requisite for packaging flow:** Users must have (1) empty keg items (e.g. "Keg 1/6 bbl") in Packaging category, (2) received empty kegs at a location (via Receive), (3) vessels with bound locations. Seed data or migration can create default keg items.

---

## 1. Phase 1: Operation-Driven Stage for TTB Column Assignment

### 1.1 TTBFormService — Derive column from operation_type

**File:** `platforms/console/src/services/TTBFormService.js`

**Current behavior:** For movement lines (4, 9, 10, 22, 23, 24, etc.), column (b/d/e/f) is derived from `getStage(entry.location_id)` which uses `location.stage`.

**Change:** Add a helper `getStageForEntry(entry, stageMap)` that:
- If `entry.data?.ttb_stage` is set and valid, return it.
- If `entry.operation_type === 'production_complete'`, return `'cellar'`.
- If `entry.operation_type === 'racking'`, for TRANSFER_IN/destination use `'racking_keg'`; for TRANSFER_OUT/source use `'cellar'` (or source location stage).
- If `entry.operation_type === 'bottling'` or `'canning'`, for destination use `'case'`.
- Else fallback to `stageMap.get(entry.location_id) || 'cellar'`.

**Precise changes:**
1. Add `function getStageForEntry(entry, stageMap, isDestination)` — `isDestination` distinguishes TRANSFER_IN (destination) vs TRANSFER_OUT (source). For TRANSFER pairs, OUT uses source stage (cellar), IN uses operation-driven destination stage (racking_keg, case).
2. Replace all `getStage(e.location_id)` and `e => getStage(e.location_id)` in `buildColumnsByLine` with `e => getStageForEntry(e, stageMap, ...)` where the third arg is inferred from entry type (TRANSFER_IN = destination, TRANSFER_OUT = source, RECEIVE = destination, CONSUME = source).
3. For Line 21 (consumption_form): keep existing logic — `consumption_form` overrides; no change.
4. For Line 1 and Line 33 (inventory at rest): keep `getStage(locId)` from location — no change. Inventory at rest uses location stage.

**Ripple:** None. This is read-only logic. Existing ledger entries without `operation_type` will fallback to location stage.

**Edge case:** Entries with `operation_type: 'transfer'` (generic) — fallback to location stage. Ensure Transfer.vue and other flows that create generic transfers don't break.

---

### 1.2 LedgerRepository — Ensure operation_type is persisted

**File:** `platforms/console/src/repositories/LedgerRepository.js` (and `platforms/brewledger-app/src/repositories/LedgerRepository.js`)

**Current behavior:** `addEntry` accepts `operation_type` and stores it in `data`. `transfer` passes `operationType` to both TRANSFER_OUT and TRANSFER_IN.

**Change:** Verify that `operation_type` is included in the `data` JSON sent to server and stored. Audit all call sites:
- BatchDetail `saveProductionComplete`: already sets `data: { source: 'production_complete' }`. Add `operation_type: 'production_complete'` to data for consistency (or rely on `source` for Line 2; operation_type for column is separate).
- Racking.vue: uses `operationType: 'racking'` in transfer — already correct.
- Transfer.vue: user selects operation type — already correct.
- Removals: sets `consumption_form` in data — no operation_type needed for removals.

**Precise change:** In LedgerRepository.addEntry, ensure `operation_type` from entry is merged into `data` before persist. Check server sync payload — `data` is a JSON blob; ensure `operation_type` is inside it if we want it queryable. Current: `data` often contains `source`, `consumption_form`, etc. Add `operation_type` to the merge.

**Ripple:** Server must accept and store `operation_type` in ledger data. Check `server/server.js` ledger validation — it likely passes through `data` as JSON; no schema change.

---

### 1.3 Server — Ledger data validation

**File:** `server/server.js`

**Change:** No validation change required. `data` is stored as JSON. Ensure no validation strips `operation_type` or `ttb_stage`. Audit `processChange` for ledger — it typically stores `data` as-is.

---

## 2. Phase 2a: Vessel = Location for Fermenters and Brites

### 2.1 Vessels.vue — Extend location creation to all vessel types

**File:** `platforms/console/src/views/Vessels.vue`

**Current behavior:** Only `SERVING` vessels get `location_id`. Create path: if SERVING, create location with `stage: 'serving'` and set `location_id`. Else `location_id: null`.

**Change:** For **all** vessel types (FERMENTER, BRITE, SERVING, OTHER), create a location when creating a new vessel. Use stage based on type:
- SERVING → `stage: 'serving'`
- FERMENTER, BRITE → `stage: 'cellar'` (bulk)
- OTHER → `stage: 'cellar'` (default)

**Precise changes:**
1. In `saveVessel` create branch: remove `if (form.value.type === 'SERVING')`. Always create location for new vessels.
2. `stage` = `form.value.type === 'SERVING' ? 'serving' : 'cellar'`.
3. Set `location_id: newLocation.id` for all new vessels.
4. In update branch: allow `location_id` for non-SERVING vessels. Currently `location_id: form.value.type === 'SERVING' ? form.value.location_id : null`. Change to `location_id: form.value.location_id ?? null` for all types. But existing FERMENTER/BRITE vessels have no location_id; editing them would need a way to create/bind a location. **Option A:** On edit, if vessel has no location_id, show "Create location" button that creates and binds. **Option B:** Only new vessels get auto-location; existing vessels stay as-is until user explicitly adds location. Recommend Option B for minimal change; Option A in a follow-up.
5. Form: for non-SERVING vessels, show location_id selector or read-only bound location. Currently SERVING shows `formServingLocationName`. Extend to show bound location for any vessel with location_id. For create, we auto-create so no selector. For edit, show read-only location name (like SERVING).

**Ripple:**
- **Batch assignment:** Server rejects `batch_location` for vessels with `location_id` (serving tanks). We must **remove** that restriction for FERMENTER/BRITE — only SERVING tanks should reject batch assignment. Check `server/server.js` validateEntity for batch_location.
- **VesselRepository:** No change; already passes location_id.
- **BatchForm vessel dropdown:** Excludes vessels with location_id (serving tanks). Keep that for SERVING only. Need to distinguish: exclude only SERVING vessels with location_id, not FERMENTER/BRITE with location_id. **Critical:** Batch assignment to fermenter/brite is allowed; to serving tank is not. So the filter should be: exclude vessels where `type === 'SERVING'` (or where type is SERVING and has location_id). Current logic may be "exclude vessels with location_id" — that would incorrectly exclude new FERMENTER/BRITE with locations. Change to: exclude vessels where `type === 'SERVING'`.

---

### 2.2 Server — Batch assignment rule

**File:** `server/server.js`

**Current behavior:** `validateEntity('batch_location')` rejects assigning a vessel that has `location_id` (to prevent batches on serving tanks).

**Change:** Reject only when vessel `type === 'SERVING'`. Fermenters and brites with location_id are allowed to have batches.

**Precise change:** In batch_location validation, fetch vessel. If vessel has `location_id` AND vessel type is SERVING, reject. If vessel has location_id but type is FERMENTER or BRITE, allow.

---

### 2.3 Mobile VesselsList / VesselForm

**File:** `platforms/brewledger-app/src/views/VesselsList.vue` (or equivalent)

**Change:** Mirror console. When creating vessel, create location for all types. Same stage mapping. Ensure mobile VesselRepository and sync handle location_id for non-SERVING.

---

### 2.4 Migration for existing vessels

**New file:** `server/migrate_vessel_locations.js` (optional)

**Purpose:** For existing orgs, add locations to fermenters/brites that don't have them. Run once per org. Creates a location per vessel (name = vessel name, stage = cellar), sets vessel.location_id. Sync will propagate.

**Edge case:** Vessels with duplicate names could create duplicate location names. Use `Vessel ${vessel.name} (${vessel.id.slice(0,8)})` or similar to avoid collision. Or: `vessel.name` is often unique per org.

---

## 3. Phase 2b: Packaged Beer Items and volume_per_unit

### 3.1 Item schema — volume_per_unit

**Files:** `platforms/console/src/views/ItemForm.vue`, `platforms/brewledger-app/src/views/ItemForm.vue`, `server/server.js`

**Change:** Add optional `volume_per_unit` (number, bbl per ea) for items. Only relevant when `unit === 'ea'` and `category === 'Finished Beer'`. Store in `items.data` (JSON). No DB schema change — data is in JSON blob.

**Precise changes:**
1. ItemForm: when category is Finished Beer and unit is ea, show optional "Volume per unit (bbl)" input. Help text: "For TTB conversion. E.g. 0.16 for 1/6 bbl keg, 0.5 for 1/2 bbl."
2. ItemRepository.create/update: merge `volume_per_unit` into entity.
3. Server: no validation change; data is passthrough. Optionally validate: if unit is ea and category Finished Beer, allow volume_per_unit; if set, must be positive number.

---

### 3.2 ItemRepository — getOrCreatePackagedBeerItem

**File:** `platforms/console/src/repositories/ItemRepository.js` (and mobile)

**New function:** `getOrCreatePackagedBeerItem(baseBeerItem, formatKey, volumePerUnit)`.

- `baseBeerItem`: the bulk beer item (e.g. House IPA).
- `formatKey`: e.g. `'1/6 bbl'`, `'1/2 bbl'`, `'12pk'`.
- `volumePerUnit`: number, bbl per ea.

Logic: Look for existing item with `category === 'Finished Beer'`, `unit === 'ea'`, `data.base_beer_item_id === baseBeerItem.id` (if we store it), and name or format matching. Normalize: `House IPA 1/6 bbl` or similar. If found, return. Else create with `name: ${baseBeerItem.name} ${formatKey}`, `category: 'Finished Beer'`, `unit: 'ea'`, `data: { volume_per_unit: volumePerUnit, base_beer_item_id: baseBeerItem.id }`.

**Precise implementation:** Similar to getOrCreateBeerItemForBatch. Match by base_beer_item_id + formatKey (or name pattern). Create if not found.

---

### 3.3 TTBFormService — Convert ea to bbl for packaged beer

**File:** `platforms/console/src/services/TTBFormService.js`

**Change:** All beer quantity calculations must handle packaged items (unit ea). Add helper `beerQuantityBarrels(entry, item)`:
- If item has `volume_per_unit`, return `Math.abs(entry.quantity || 0) * item.volume_per_unit`.
- Else return `Math.abs(entry.quantity || 0)` (bulk, already in bbl).

**Ripple:** Every place that calls `beerQuantityBarrels(entry)` must now pass the item when the entry is for a packaged beer item. `getBeerItemIds()` returns item ids; we need item details for volume_per_unit. Options: (A) Load items in each calc and pass item map. (B) Extend getBeerItemIds to return a Map of id→item. (C) Create getBeerItems() and use it in TTBFormService to build item map; pass to beerQuantityBarrels.

**Precise changes:**
1. Add `async getBeerItemsMap()` — returns Map<id, item> for beer items.
2. In each calculation that sums beer quantities, load item map and use `beerQuantityBarrels(entry, itemMap.get(entry.item_id))`.
3. Update `beerQuantityBarrels(qty)` to `beerQuantityBarrels(entry, item)` — if item?.volume_per_unit, use quantity * volume_per_unit; else use Math.abs(entry.quantity).
4. **All affected functions:** calculateBeginningInventory, calculateBeerProduced, calculateBeerReceivedFromRackingBottling, calculateBeerReturnedAfterRemoval, calculateBeerRacked (when switching to ledger), calculateBeerBottled, classifyRemovalEntry and removal loops, getBeerOnhandByStage, buildColumnsByLine, etc. This is a significant change — audit every function that touches beer quantities.

**Edge case:** Item not found in map (deleted, sync lag) — fallback to quantity as-is (assume bbl).

---

### 3.4 LedgerRepository — getTotalOnhand, getAllOnhand for display

**File:** `platforms/console/src/repositories/LedgerRepository.js`

**Change:** No change. On-hand returns quantity in item's unit. UI displays "15 ea" or "15 kegs" for packaged items. TTB conversion is only in TTBFormService.

---

### 3.5 Inventory, Items, Beers views — Display unit correctly

**Files:** `platforms/console/src/views/Inventory.vue`, `ItemsList.vue`, `Beers.vue`

**Change:** Ensure unit "ea" displays as "ea" or "kegs" / "cases" based on context. No code change if we already show `item.unit`. Optionally: for packaged beer with unit ea, show "kegs" or "cases" in UI. Low priority.

---

## 4. Phase 2c: Mark Production Complete — Packaging Flow

### 4.1 BatchDetail — Extend production complete modal

**File:** `platforms/console/src/views/BatchDetail.vue`

**Current flow:** User picks Serving or Storage, then location. Creates single RECEIVE. For Storage, picks generic location (Cellar, Keg Storage, etc.).

**New flow:** Add third option: **Packaged (keg)** or **Packaged (case)**. When Packaged (keg):
1. User selects source vessel (batch_location) — must have location_id (vessel = location).
2. User selects destination location (keg storage).
3. User selects keg format (1/2 bbl, 1/6 bbl, etc.) and quantity (number of kegs).
4. System computes volume: kegs × volume_per_unit.
5. System creates:
   - RECEIVE bulk at vessel location (Line 2)
   - TRANSFER_OUT bulk from vessel location (Line 22) — wait, TRANSFER needs a destination. The transfer is bulk from vessel to... where? The bulk doesn't go to keg storage as bulk — it becomes packaged. So we need:
     - RECEIVE bulk at vessel
     - CONSUME bulk from vessel (or TRANSFER_OUT to a "packaging" location?)
   - Actually: TRANSFER_OUT from vessel, TRANSFER_IN to destination. But the item would be bulk for both. The destination would receive bulk. Then we'd need to CONSUME bulk and RECEIVE packaged at same destination. So:
     - RECEIVE bulk at vessel (Line 2)
     - TRANSFER bulk from vessel to destination: TRANSFER_OUT + TRANSFER_IN. Both use bulk beer item. Destination now has bulk. Then CONSUME bulk from destination, RECEIVE packaged at destination. That's 5 entries. Or:
     - RECEIVE bulk at vessel
     - CONSUME bulk from vessel (beer left vessel)
     - RECEIVE packaged at destination
   - Line 22 expects TRANSFER_OUT. So we need TRANSFER_OUT. The pair: TRANSFER_OUT from vessel, TRANSFER_IN to destination. Item = bulk. So destination receives bulk. Then we CONSUME bulk from destination, RECEIVE packaged at destination. Net at destination: bulk in, bulk out, packaged in. So we need:
     1. RECEIVE bulk at vessel (Line 2)
     2. TRANSFER bulk: OUT from vessel, IN to destination. Line 22 gets OUT. Line 4 gets IN (beer received from racking). But Line 9 is "beer racked" — we need RECEIVE packaged for that. So:
     3. CONSUME bulk from destination
     4. RECEIVE packaged at destination (Line 9)
   - That's 4 entries for beer + CONSUME for empty kegs. The CONSUME bulk and RECEIVE packaged happen at same location. So we have bulk at destination momentarily. That works.

**Full flow (5 beer entries + 1 keg entry):**
1. RECEIVE bulk at vessel location (Line 2)
2. TRANSFER bulk: OUT from vessel, IN to destination — both use bulk beer item. Line 22 gets OUT, Line 4 gets IN.
3. CONSUME bulk from destination (converts bulk to packaged)
4. RECEIVE packaged at destination (Line 9)
5. CONSUME empty kegs from keg storage location

The destination receives bulk (TRANSFER_IN), then we convert in place: CONSUME bulk, RECEIVE packaged. Same location.

**Precise implementation:**
1. Add `destChoice: 'packaged_keg' | 'packaged_case'` to production complete form.
2. When packaged_keg: require source batch_location whose vessel has location_id. Require destination location (keg storage). Require keg format (dropdown: 1/2 bbl, 1/6 bbl, etc. with volume_per_unit). Require number of kegs.
3. Resolve packaged beer item via getOrCreatePackagedBeerItem(baseBeer, formatKey, volumePerUnit).
4. **Packaging materials (supply lines):** Show supply lines UI (see §4.2). For keg, prefill one line: item = format's packagingItemName (e.g. "Keg 1/6 bbl"), quantity = numKegs, location = user selects. Require at least one supply line for keg (empty kegs). Validate: each line has on-hand >= quantity.
5. Create ledger entries in order:
   - RECEIVE bulk at vessel.location_id (Line 2)
   - LedgerRepository.transfer({ itemId: bulkBeer.id, fromLocationId: vessel.location_id, toLocationId: destination.id, quantity: volumeBbl, operationType: 'racking', batchId }) — Line 22 + Line 4
   - LedgerRepository.addEntry({ type: 'CONSUME', item_id: bulkBeer.id, location_id: destination.id, quantity: -volumeBbl, batch_id, operation_type: 'racking' })
   - LedgerRepository.addEntry({ type: 'RECEIVE', item_id: packagedBeer.id, location_id: destination.id, quantity: numKegs, batch_id, operation_type: 'racking' }) — Line 9
   - For each supply line: LedgerRepository.addEntry({ type: 'CONSUME', item_id, location_id, quantity: -Math.abs(qty), batch_id, operation_type: 'packaging_supply' })
6. Complete milestone, delete batch_location.

---

### 4.2 Explicit Packaging Materials Consumption Setup

Packaging materials (empty kegs, cans, caps, carriers, etc.) are consumed when packaging. Each packaging operation must explicitly record which materials were used, from which locations, and in what quantities.

#### 4.2.1 Packaging materials as items

- **Category:** Packaging (existing). Items like "Keg 1/6 bbl", "Keg 1/2 bbl", "Cans", "Crown Caps", "6-pack carrier", "12-pack case" live in Packaging.
- **Units:** ea for kegs; ea, case, or lb for cans/caps/carriers depending on how the brewery tracks them.
- **Pre-requisite:** User must create these items and RECEIVE them at locations before packaging. No auto-creation of packaging materials.

#### 4.2.2 Format-to-materials mapping (explicit rules)

| Format | Materials consumed | Quantity per unit | Notes |
|--------|--------------------|-------------------|-------|
| 1/6 bbl keg | Keg 1/6 bbl | 1 ea per keg | One empty keg per filled keg |
| 1/2 bbl keg | Keg 1/2 bbl | 1 ea per keg | One empty keg per filled keg |
| 12pk case (cans) | Cans, Crown caps, 12-pack carrier | 12, 12, 1 per case | User configures exact items |
| 6pk case (cans) | Cans, Crown caps, 6-pack carrier | 6, 6, 1 per case | User configures |
| 12pk case (bottles) | Bottles, Crown caps, 12-pack case | 12, 12, 1 per case | User configures |

**Implementation:** Do **not** hardcode format→materials. Instead, use a **supply lines** UI: user adds one line per material (item, quantity, location). For kegs: default 1× empty keg item per keg filled; user can add more (e.g. keg caps, labels). For cases: user adds cans, caps, carriers as needed. This keeps the system flexible for different brewery setups.

#### 4.2.3 Supply lines UI (packaged_keg and packaged_case)

When user selects packaged_keg or packaged_case, show a **Packaging materials** section:

1. **Default line for keg:** When format "1/6 bbl" and numKegs = 15, prefill one line: item = "Keg 1/6 bbl" (match by name or format preset), quantity = 15, location = dropdown of locations with on-hand >= 15. User can change. Add "Add material" to add more (e.g. keg caps).
2. **Default lines for case:** When format "12pk" and numCases = 10, no auto-prefill — user adds lines: Cans (120), Crown caps (120), 12-pack carrier (10), etc. Or we could offer presets: "12pk can" preset adds 3 lines with common item names; user picks actual items.
3. **Each line:** item (dropdown, filter: Packaging category), quantity (number), location (dropdown, filter: locations where item has on-hand > 0). Show "Available: X" next to location.
4. **Validation before save:** For each line, `LedgerRepository.getOnhand(item_id, location_id) >= quantity`. If any fail, show error: "Insufficient [item name] at [location]. Available: X, needed: Y."

#### 4.2.4 Ledger entries for packaging materials

For each supply line `{ item_id, quantity, location_id }`:

```
LedgerRepository.addEntry({
  type: 'CONSUME',
  item_id,
  location_id,
  quantity: -Math.abs(quantity),
  batch_id,
  operation_type: 'packaging_supply',
  created_at: completionDate
})
```

- `operation_type: 'packaging_supply'` — used by BatchCostService for packaging cost rollup.
- `batch_id` — links consumption to batch for cost and history.
- Quantity is negative (CONSUME removes inventory).

#### 4.2.5 Order of operations (full packaging flow with materials)

For packaged_keg:
1. Beer entries (RECEIVE bulk, TRANSFER, CONSUME bulk, RECEIVE packaged)
2. Packaging materials CONSUME entries (one per supply line)

For packaged_case:
1. Beer entries (same pattern as keg, operation_type bottling/canning)
2. Packaging materials CONSUME entries (one per supply line)

All entries use the same `created_at` (completion date). Execute in a single logical transaction; if any CONSUME fails validation, abort the whole operation.

#### 4.2.6 Packaging materials configuration (optional future)

A **Packaging format presets** config could store: "12pk can" → consume Item A (qty 12×), Item B (qty 12×), Item C (qty 1×) per case. User defines presets in Settings. For initial implementation, use manual supply lines only; presets can be added later.

---

### 4.3 Keg format presets

**New:** Define keg format presets: `{ key: '1/6 bbl', label: '1/6 bbl', volumePerUnit: 0.16, packagingItemName: 'Keg 1/6 bbl' }, { key: '1/2 bbl', label: '1/2 bbl', volumePerUnit: 0.5, packagingItemName: 'Keg 1/2 bbl' }`. Use in dropdown. `packagingItemName` is a hint for default supply line; resolve to actual item by name match in Packaging category. User can override.

---

### 4.5 TTBFormService — Line 9 from ledger

**File:** `platforms/console/src/services/TTBFormService.js`

**Current:** Line 9 from packaging_runs (KEG format).

**Change:** Line 9 = RECEIVE entries for packaged beer items (items with volume_per_unit) where operation_type or data indicates racking. Sum RECEIVE with operation_type racking, item is packaged beer. Sum quantity × volume_per_unit.

**Precise change:** calculateBeerRacked: instead of packaging_runs, query ledger for RECEIVE with operation_type racking and item_id in packaged beer item ids. Sum beerQuantityBarrels(entry, item) for each.

---

### 4.6 BatchDetail — Packaging to case (bottling/canning)

Similar to keg. User selects format (12pk, 6pk, etc.), quantity, destination. CONSUME bulk, TRANSFER bulk, CONSUME bulk, RECEIVE packaged, **plus supply lines** for cans, caps, carriers. Each supply line creates CONSUME with operation_type packaging_supply. Operation type bottling/canning for beer entries. Line 10 from ledger RECEIVE packaged with operation_type bottling/canning. **Supply lines are mandatory** — user must add at least cans/caps/carriers (or equivalent) for case packaging. Validation: all supply lines must have sufficient on-hand.

---

## 5. Phase 3: Remove Racking View, Deprecate Packaging Runs

### 5.1 Remove Racking route and view

**Files:** `platforms/console/src/router/index.js`, `platforms/console/src/App.vue`, `platforms/console/src/views/Dashboard.vue`, `platforms/console/src/views/Reports.vue`

**Changes:**
1. Remove `/racking` route.
2. Remove Racking from sidebar nav (App.vue navItems).
3. Remove Racking from Dashboard quick actions.
4. Remove Racking link from Reports page.
5. Delete or deprecate `platforms/console/src/views/Racking.vue`. Recommend: delete after confirming no imports elsewhere.

**Ripple:** Mobile has no Racking route; Transfer has operation_type racking. Mobile Transfer.vue stays. Console Transfer.vue stays — users can still do manual transfers with operation_type racking. The removal is of the dedicated Racking *page*, not the ability to record racking. Racking is now done via Mark Production Complete. For edge case: what if user needs to record racking *after* production complete (e.g. batch was completed to cellar, then later racked)? That would be a Transfer from cellar to keg storage. So we keep Transfer with racking option for that flow. The design says packaging happens at Mark Production Complete. But some breweries might complete to cellar first, then rack later. So we should NOT remove the ability to do a racking transfer. We're removing the Racking *page* which was a batch-centric flow. The Transfer page with operation_type racking can handle "rack from cellar to keg storage." But that transfer would move bulk beer, not create packaged beer. The new model has packaged beer as separate items. So a "rack from cellar" transfer would be: bulk beer from cellar to... where? If we're tracking packaged beer, we'd need to CONSUME bulk and RECEIVE packaged. So a standalone "Record Racking" flow (post-production) would need: CONSUME bulk from cellar, RECEIVE packaged at destination, CONSUME empty kegs. That could live in Transfer or a simplified Racking flow. For Phase 3, we're removing the Racking page. The Transfer page can do bulk transfers. Creating packaged beer (CONSUME bulk + RECEIVE packaged) would need a separate flow. **Decision:** Phase 3 removes Racking page. Post-production racking (cellar → kegs) is a future enhancement — for now, packaging only at Mark Production Complete. Document as limitation.

---

### 5.2 Remove Packaging modal from BatchDetail

**File:** `platforms/console/src/views/BatchDetail.vue` (and mobile)

**Change:** Remove "Record Packaging" button and packaging modal. Packaging is now part of Mark Production Complete (packaged_keg, packaged_case). Remove openPackagingModal, savePackaging, forms.packaging, modals.packaging.

**Ripple:** PackagingRunRepository.create is no longer called from BatchDetail. Other callers? Grep for PackagingRunRepository.create — only BatchDetail and Racking. Racking is removed. So no more create calls. Packaging runs table will stop receiving new data.

---

### 5.3 TTBFormService — Line 9 and 10 from ledger only

**Change:** calculateBeerRacked and calculateBeerBottled use ledger only. Remove packaging_runs queries. (Done in 4.3 and 4.4.)

---

### 5.4 Deprecate packaging_runs

**Options:** (A) Keep table for historical data; no new writes. (B) Migration to derive packaging from ledger and backfill if needed. (C) Remove from sync/validation so new clients don't send. Recommend A: keep table, stop creating. Sync still works for existing data. No migration.

---

## 6. Phase 4: Location Stage Clarification

### 6.1 LocationForm and Settings copy

**Files:** `platforms/console/src/views/LocationForm.vue`, `platforms/console/src/views/Settings.vue`

**Change:** Add helper text: "Stage is used for inventory at rest (TTB Lines 1 and 33). For movements, the operation type determines the TTB column." No functional change.

---

## 7. Ripple Effects Summary

| Change | Affects |
|--------|---------|
| Vessel location_id for all types | Batch assignment filter, server validation |
| Packaged beer items (ea) | TTBFormService (all beer calcs), Removals, Sales Order, Inventory display |
| Mark Production Complete packaging | BatchDetail modal, ItemRepository (new fn), LedgerRepository (multiple entries) |
| Remove Racking page | Nav, Dashboard, Reports, router |
| Remove Packaging modal | BatchDetail, PackagingRunRepository |
| TTB operation-driven stage | TTBFormService buildColumnsByLine, PDF export |

---

## 8. First Pass — Shortcomings and Edge Cases

### 8.1 Vessel without location (existing vessels)

**Issue:** Existing fermenters/brites have no location_id. Packaging to keg requires vessel with location.

**Resolution:** Phase 2a Option B: only new vessels get auto-location. For packaging, require source vessel to have location_id. If batch's vessel has no location, show message: "This vessel has no location. Edit the vessel to add a location (same as serving tanks)." Provide link to Vessels. Alternatively, in production complete when user selects packaged_keg, filter batch_locations to only those whose vessel has location_id. If none, show "No vessels with locations. Add locations to your fermenters/brites in Vessels."

---

### 8.2 Packaging materials not in inventory

**Issue:** User adds supply line for "Keg 1/6 bbl" but doesn't have that item, or has 0 on-hand at selected location.

**Resolution:** (1) Supply line item dropdown filters to Packaging category. (2) Location dropdown shows only locations where item has on-hand > 0; display "Available: X" per location. (3) Before save, validate each line: `getOnhand(item_id, location_id) >= quantity`. If any fail, show error: "Insufficient [item name] at [location]. Available: X, needed: Y. Receive more at Receive, or reduce quantity."

---

### 8.3 Bulk beer at vessel — RECEIVE creates positive on-hand

**Issue:** RECEIVE bulk at vessel location. But vessel might already have beer from batch_location (operational). We're creating ledger RECEIVE. The vessel's ledger on-hand will increase. Then we TRANSFER_OUT. So we're not double-counting with batch_location — batch_location is deleted after production complete. The vessel goes empty (no batch). So we're good. But: what if the vessel had a location and we RECEIVE there — does that location already have beer from a previous operation? Unlikely for a vessel we're completing from. We're completing the batch, so the vessel is the source. We RECEIVE (putting beer on ledger at vessel), then TRANSFER_OUT. The vessel ends at 0. Good.

---

### 8.4 Transfer pair — same item for bulk

**Issue:** TRANSFER uses one item. We're transferring bulk beer. The TRANSFER_IN puts bulk at destination. Then we CONSUME bulk and RECEIVE packaged. The CONSUME and RECEIVE use different items (bulk vs packaged). So we need 4 beer-related entries: RECEIVE bulk, TRANSFER bulk (OUT+IN), CONSUME bulk, RECEIVE packaged. Plus CONSUME empty kegs. Total 5 ledger entries for one packaging action.

---

### 8.5 Line 4 (beer received from racking)

**Issue:** Line 4 = TRANSFER_IN with operation_type racking. Our flow creates TRANSFER_IN (bulk) at destination. So Line 4 would get that. But Line 4 is "beer received from racking and bottling" — that's the beer coming into a location from racking. Our TRANSFER_IN is bulk beer arriving at destination. Then we CONSUME it and RECEIVE packaged. So the TRANSFER_IN is bulk, not packaged. TTB Line 4 might expect "beer received from racking" = beer that was racked and is now in keg form. The design doc says Line 4 = TRANSFER_IN racking. So we're good — the bulk is "received from racking" (it came from the racking process). The racking process moved bulk from vessel to destination. So Line 4 gets the TRANSFER_IN. Good.

---

### 8.6 Mobile parity

**Issue:** Mobile has no Racking page. Mobile has BatchDetail with packaging modal. We're removing packaging modal. Mobile needs the same Mark Production Complete packaging flow.
**Resolution:** Implement packaging options in mobile BatchDetail production complete modal. Same logic as console.

---

### 8.7 Sync and offline

**Issue:** Multiple ledger entries in one "transaction." If sync fails mid-way, we could have partial state.
**Resolution:** Create all entries in a loop; trigger sync once at end. If one fails, we could wrap in a transaction — but ledger is append-only; no rollback. Best effort: create all, then sync. If sync fails, user can retry. Document that packaging creates multiple entries atomically from UI perspective.

---

### 8.8 Cleanup of zero-on-hand packaged beer items

**Issue:** LedgerRepository.cleanupBeerItemsAtZero soft-deletes beer items at zero. Packaged beer items are also Finished Beer. They would get cleaned up. Is that desired? Per-batch beer items get cleaned up. Packaged beer (House IPA 1/6 bbl) might go to zero when all kegs are sold. Cleaning up is consistent. But we might want to keep the item for future use. Design says same as per-batch: cleanup when zero. Optional: skip cleanup for packaged items (base_beer_item_id set) so we keep SKU definitions. Recommend: cleanup packaged items at zero too; they can be recreated when needed.

---

## 9. Second Pass — Additional Considerations

### 9.1 Sales Order and Removals — Packaged beer

**Issue:** Sales Order and Removals allow selecting beer items. Packaged beer items (ea) will appear. When user CONSUMEs packaged beer, quantity is in ea. TTBFormService must convert. Already covered in 3.3.

**Removals:** Ensure consumption_form can be set. For packaged beer removed from keg storage, consumption_form = 'keg' for Line 21. Location stage might be racking_keg. If we use operation-driven, the CONSUME from a racking_keg location with removal_purpose serving/on_premise — we might use consumption_form. Removals already has "Served from" dropdown. Good.

---

### 9.2 QuickBooks item mapping

**Issue:** Sales Order pushes to QBO. Beer items are mapped. Packaged beer items (House IPA 1/6 bbl) are new. User needs to map them in Integrations. No code change; they'll appear in beer items list for mapping.

---

### 9.3 Reports — Serving & Inventory Rollup

**Issue:** Reports may show "packaged on hand" by storage. If we have packaged beer (ea) at locations, the report should include it. Check ServingReportsService, server /api/reports/serving. May need to include packaged beer items and convert ea to bbl for display. Or show ea separately.

---

### 9.4 Recipe sync to beers

**Issue:** Beers page has "Sync from recipes" — creates bulk beer items. Packaged beer items are created on-demand during packaging. No sync from recipe for packaged. OK.

---

### 9.5 Batch cost

**Issue:** BatchCostService computes cost from CONSUME entries. Packaging creates CONSUME for empty kegs (packaging_supply) and CONSUME for bulk. The bulk CONSUME is "consuming" bulk beer — that might not have a cost (we're converting, not purchasing). The empty keg CONSUME has cost (kegs were purchased). Batch cost should include packaging supplies. Already: PackagingRunRepository creates CONSUME with operation_type packaging_supply. We're creating CONSUME for empty kegs. Use same operation_type? Or 'packaging_supply'. BatchCostService looks for packaging_supply. So we need to create CONSUME for empty kegs with operation_type 'packaging_supply'. Good.

---

### 9.6 Tutorial and onboarding

**Issue:** Tutorial mentions Racking. Update tutorial steps to remove Racking, add "Mark Production Complete with packaging" step.
**File:** `platforms/console/src/services/tutorial/tutorialSteps.js`

---

### 9.7 Seed data

**Issue:** seed_test_account creates items including "Keg 1/6 bbl". Ensure it has distribution (on-hand) so packaging flow works. Add "Keg 1/2 bbl" if needed. Create a packaged beer item for testing? Optional.

---

### 9.8 Column mapping verification

**Issue:** Plan mentions code uses racking_keg→d, bottling_bulk→e, case→f. Design doc says (c) Racking Keg, (d) Bottling Bulk, (e) Case. Verify against ttb.pdf. If wrong, fix STAGE_TO_COLUMN mapping.

---

### 9.9 Duplicate production complete guard

**Issue:** BatchDetail prevents duplicate RECEIVE with `data.source === 'production_complete'`. We create one such RECEIVE (bulk). The packaged RECEIVE has `operation_type: 'racking'`, not production_complete. So the guard still works. No change needed.

---

### 9.10 LedgerRepository.cleanupBeerItemsAtZero — packaged items

**Issue:** cleanupBeerItemsAtZero soft-deletes Finished Beer items at zero. Packaged beer items are Finished Beer. When all kegs are sold, item goes to zero. We could skip cleanup for items with `base_beer_item_id` or `volume_per_unit` to preserve SKU definitions. Recommend: cleanup packaged items at zero too (consistent with per-batch beer items). User can recreate when needed.

---

### 9.11 Batch history / timeline

**Issue:** BatchDetail History tab shows ledger entries for the batch. Packaging will create 6 entries (RECEIVE bulk, TRANSFER_OUT, TRANSFER_IN, CONSUME bulk, RECEIVE packaged, CONSUME kegs). All should have batch_id. History will show them. Consider grouping or summarizing for UX — "Packaged 15 kegs of House IPA 1/6 bbl" as one line. Optional enhancement.

---

### 9.12 Server ledger validation — quantity sign

**Issue:** CONSUME entries typically have negative quantity. Server may validate. Ensure CONSUME entries use negative quantity (or the convention the app uses). LedgerRepository.addEntry for CONSUME: check current convention.

---

## 10. Implementation Checklist (Condensed)

**Phase 1 — Operation-driven stage**
- [ ] 1.1: TTBFormService getStageForEntry, use for movement lines
- [ ] 1.2: LedgerRepository ensure operation_type in data

**Phase 2a — Vessel = location**
- [ ] 2.1: Vessels.vue create location for all vessel types
- [ ] 2.2: Server batch_location validation — allow FERMENTER/BRITE with location_id
- [ ] 2.3: Mobile vessel create — same as console
- [ ] 2.4: Optional migration for existing vessels

**Phase 2b — Packaged beer items**
- [ ] 2.5: ItemForm volume_per_unit for packaged beer
- [ ] 2.6: ItemRepository getOrCreatePackagedBeerItem
- [ ] 2.7: TTBFormService beerQuantityBarrels with item, all calcs
- [ ] 2.8: TTBFormService Line 9 from ledger
- [ ] 2.9: TTBFormService Line 10 from ledger (when switching to ledger)

**Phase 2c — Mark Production Complete packaging**
- [ ] 2.10: BatchDetail production complete — add packaged_keg, packaged_case
- [ ] 2.11: **Packaging materials supply lines UI** — item, quantity, location per line; on-hand validation
- [ ] 2.12: Keg format presets with packagingItemName for default supply line
- [ ] 2.13: BatchDetail packaging to case (with supply lines for cans, caps, carriers)
- [ ] 2.14: Mobile BatchDetail packaging flow parity

**Phase 3 — Remove Racking, deprecate packaging_runs**
- [ ] 3.1: Remove Racking route, nav, view
- [ ] 3.2: Remove Packaging modal from BatchDetail (console + mobile)
- [ ] 3.3: TTBFormService Line 9/10 from ledger only (no packaging_runs)

**Phase 4 — Location stage**
- [ ] 4.1: LocationForm copy update

**Cross-cutting**
- [ ] Tutorial: Update steps
- [ ] analysis.md: Document all changes
- [ ] Feature analysis: Two iterations per AGENTS.md
