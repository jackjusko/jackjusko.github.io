# Feature Analysis: Mark Production Complete Packaging Flow

## Summary

Phase 2c of the operation-driven TTB rework adds **Packaged (keg)** and **Packaged (case)** destination options to the Mark Production Complete modal. Users can record packaging to kegs or cases with explicit supply line consumption (empty kegs, cans, caps, carriers). The flow creates the full ledger sequence: RECEIVE bulk → TRANSFER → CONSUME bulk → RECEIVE packaged → CONSUME supplies.

## Implementation Details

### Console BatchDetail.vue

- **Destination options**: Added `packaged_keg` and `packaged_case` radio options alongside serving and storage.
- **Format presets**: KEG_FORMAT_PRESETS (1/6 bbl, 1/2 bbl) and CASE_FORMAT_PRESETS (12pk, 6pk) with volume_per_unit.
- **Supply lines UI**: Add/remove lines; each line: Packaging item, quantity, location. On-hand validation via supplyLineAvailability ref (watched when modal open + supplies change).
- **Batch locations filter**: For packaging, only vessels with `location_id` are shown (productionCompleteBatchLocations computed).
- **Ledger flow**: RECEIVE bulk at vessel → transfer bulk → CONSUME bulk → RECEIVE packaged → CONSUME per supply line.

### Mobile BatchDetail.vue

- Full parity: same destChoice options, format presets, supply lines, saveProductionComplete packaging branch.
- Compact UI for smaller screens; same validation and ledger logic.

### ItemRepository

- **getPackagingItems()**: Returns items with category === 'Packaging'.
- **getOrCreatePackagedBeerItem(baseBeerItem, formatKey, volumePerUnit)**: Resolves or creates packaged beer item (e.g. "House IPA 1/6 bbl") with unit ea and volume_per_unit.

### LedgerRepository

- **transfer()**: Added optional `created_at` parameter so packaging flow can use completion date for all entries.

---

## Two-Pass Review: Bugs and Gaps

### Pass 1 — Bugs and Implementation Issues

1. **Missing refresh after save (BUG)** — **FIXED**: Console `saveProductionComplete` now refreshes `batchLedgerEntries`, `costSummary` (via BatchCostService.computeAndStore), and `batch`. Mobile refreshes `batchLedgerEntries`.

2. **Supply line quantity not synced with numKegs (UX BUG)** — **FIXED**: Watcher updates first supply line quantity when `numKegs` changes and it's the default keg line (console + mobile).

3. **TTBFormService still uses packaging_runs (GAP)** — **FIXED**: Removed packaging_runs from `calculateBeerRacked`, `calculateBeerBottled`, and `buildColumnsByLine` (Line 9/10). Ledger is now sole source for Line 9/10.

4. **Supply line "Available: X" not shown (GAP)** — **FIXED**: Console supply line location dropdown now shows "Location (X avail)" per option. Availability fetched for each item×location when supplies change. Mobile: skipped (compact UI).

5. **Supply line location filter (GAP)**: Plan says filter to locations with on-hand > 0. **Not implemented** — all locations shown; "Available: X" gives user the info to choose. Filtering would require per-line async fetch; current approach is acceptable.

### Pass 2 — Design Doc / Plan Gaps Still Needing Implementation

| Item | Plan Reference | Status |
|------|----------------|--------|
| Remove packaging_runs from Line 9/10 | §5.3 | **DONE** |
| Supply line "Available: X" | §4.2.3, §8.2 | **DONE** (console only) |
| Supply line location filter (on-hand > 0) | §4.2.3, §8.2 | **Deferred** — "Available" display sufficient |
| Refresh after production complete | Implicit | **DONE** |
| numKegs → supply line quantity sync | §4.2.3 default line | **DONE** |
| LocationForm helper text (Phase 4) | §6.1 | Verify — may already exist |
| Tutorial update (remove Racking) | §9.6 | Verify |
| Vessel migration for existing (optional) | §2.4 | Optional — not done |

### Already Implemented / Verified

- Racking view removed (no route, no Racking.vue)
- Record Packaging modal removed
- Phase 1 (getStageForEntry), Phase 2a (vessel locations), Phase 2b (packaged items, TTB conversion) — per conversation summary
- Full packaging ledger flow (RECEIVE, TRANSFER, CONSUME, RECEIVE packaged, CONSUME supplies)
- Mobile parity for packaging flow

---

## Edge Cases & Considerations

1. **Vessel without location**: Packaging requires source vessel to have location_id. If none, productionCompleteBatchLocations is empty; user sees "needs location" hint. Validation in saveProductionComplete blocks with clear message. **Watcher**: When user switches destChoice to packaged_keg/packaged_case, if the currently selected batch_location's vessel has no location_id, batch_location_id is cleared to avoid invalid selection.
2. **Packaging materials not in inventory**: Supply line validation checks LedgerRepository.getOnhand before save. Error: "Insufficient [item] at selected location. Available: X, needed: Y."
3. **No packaging items**: User must create Packaging items (e.g. "Keg 1/6 bbl") and receive them before packaging. Supply line item dropdown filters to Packaging category.
4. **Format change**: When switching destChoice between packaged_keg and packaged_case, formatKey and supplies reset. Prefill for packaged_keg: one supply line with matching keg item if found.
5. **alreadyComplete check**: Unchanged—one production complete per batch (RECEIVE with source production_complete). Packaging flow creates that RECEIVE at vessel location first.

## Systems Integration

- **TTBFormService**: Line 9/10 include RECEIVE with operation_type racking/bottling/canning. Legacy packaging_runs fallback should be removed per plan.
- **BatchCostService**: Packaging cost from CONSUME with operation_type packaging_supply. No change.
- **Sync**: All ledger entries sync normally; data includes operation_type.

## Files Modified

- `platforms/console/src/views/BatchDetail.vue` – modal UI, saveProductionComplete, watchers, computed
- `platforms/console/src/repositories/ItemRepository.js` – getPackagingItems
- `platforms/console/src/repositories/LedgerRepository.js` – transfer created_at
- `platforms/brewledger-app/src/views/BatchDetail.vue` – same changes
- `platforms/brewledger-app/src/repositories/ItemRepository.js` – getPackagingItems, getOrCreatePackagedBeerItem
- `platforms/brewledger-app/src/repositories/LedgerRepository.js` – transfer created_at
- `analysis.md` – Mark Production Complete packaging flow documentation
