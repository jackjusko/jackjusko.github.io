# Feature Analysis: Serving Tank & Finished Beer Cleanup

## Summary of changes

1. **Default Finished Beer item (new orgs only)**  
   New organizations no longer get a default "Finished Beer" item at registration. The Finished Beer **category** is still created (system, undeletable). Beer items are created per-recipe/per-batch when needed (e.g. Mark Production Complete). Existing orgs keep any default item created by migration or prior registration. Server delete guard for the default item (name and category both "Finished Beer") remains for backward compatibility.

2. **New batches cannot be assigned to serving tanks**  
   - **Console & mobile BatchForm**: Vessel dropdown excludes serving tanks (vessels with `location_id`). Helper text: "Serving tanks cannot be assigned here; use Mark Production Complete to send beer to a serving tank."  
   - **BatchDetail Split/Transfer**: Split destinations and Combine destination vessel dropdowns use the same filtered list (non-serving vessels only).  
   - **Server**: Already rejected `batch_location` when vessel had `location_id`; no change.

3. **Overall batch reading removed**  
   - **Log Reading** (console and mobile BatchDetail): "Overall batch" option removed. User must select a specific vessel. Default when opening the modal is the first batch location. Save validates that a vessel is selected.  
   - Readings are always stored with a non-null `batch_location_id` for new entries; existing null readings remain in history.

4. **Serving tank view reflects inventory after production complete**  
   - **Console Vessels.vue**: For vessels with a linked location (serving tanks), display is driven by `getCurrentBeerAtLocation(location_id)`: beer item name (or "Empty" / "Multiple beers – resolve on Serving page") and on-hand volume in bbl. Batch-based display is overridden for these vessels so that after production complete (batch_location removed), the tank shows ledger inventory, not "Empty".  
   - **Console Serving.vue**: Already used `getCurrentBeerAtLocation`; added `onActivated(loadTanks)` so returning to the page refreshes data.  
   - **Console Vessels.vue**: Added `onActivated(refresh)` for the same reason.  
   - **Mobile VesselsList.vue**: For vessels with `location_id`, card content (batch name, volume) comes from `getCurrentBeerAtLocation`; removed reliance on a single default beer item and LedgerRepository.getOnhand for empty tanks. Added `onActivated(loadVessels)`.

## First-pass analysis (risks / edge cases)

- **Orgs with no Finished Beer item**: Production complete and other flows already resolve or create beer items (recipe-linked or batch-name). No change required there; only registration no longer pre-creates the default item.  
- **BatchForm with only serving tanks**: If every vessel is a serving tank, `vesselsForBatch` is empty and the user cannot assign a vessel. This is correct; we show the helper text.  
- **Reading modal with no batch locations**: If the batch has no vessels assigned, the reading modal opens with no vessel selected and the dropdown has no valid option. Save correctly shows "Select a vessel for this reading." Consider disabling or hiding "Log Reading" when `batchLocations.length === 0` in a follow-up if desired.  
- **Serving tank with batch_location**: Console Vessels still has a row from `batch_locations` for that vessel, but we override `batchName` and `currentVolume` from occupancy. So we show beer name + on-hand; "Open batch" / "Set volume" still use `row.batchId` so links remain correct.  
- **Mobile VesselsList**: Removed `ItemRepository.getBeerItems()` and `LedgerRepository` from the load path for this view; all serving-tank data comes from `ServingOccupancyService.getCurrentBeerAtLocation`.

## Second-pass analysis (follow-up considerations)

- **Tutorial / docs**: Tutorial step that mentions "Finished beer items can be tied to batches when you mark production complete" remains accurate; no change to tutorial text.  
- **Seed / test scripts**: `seed_test_account.js`, `seed_test_ledger.js`, and `migrate_ttb_beer_category.js` / `migrate_restore_finished_beer_item.js` still create or restore the default Finished Beer item for existing/test orgs. Not changed; only register-org was updated.  
- **Vessels "Open batch" / "Set volume" for serving tanks**: When a serving tank shows inventory (beer name + bbl) but still has a `batch_location` (batch not yet production-complete), the row keeps `hasBatch: true` and `batchId` so the actions still work. When production complete removes the batch_location, the same vessel appears from emptyRows and we still enrich from occupancy, so we show "Empty" or the current beer and volume; no batch actions in that case.  
- **Lint**: Removed unused `ItemRepository` and `LedgerRepository` imports from mobile VesselsList; no other lint issues identified.

## Files touched

- **Server**: `server/server.js` (remove default beer item creation on register-org).  
- **Console**: `BatchForm.vue` (vesselsForBatch, helper text), `BatchDetail.vue` (reading modal vessel required, Split/Combine vessel lists, saveReading validation), `Vessels.vue` (ServingOccupancyService for serving tanks, onActivated), `Serving.vue` (onActivated; **all serving locations**: includes standalone serving locations with no linked vessel, key `vesselId || 'loc-' + locationId`, subtitle "(no vessel)" for location-only rows).
- **Mobile**: `BatchForm.vue` (vesselsForBatch, helper text), `BatchDetail.vue` (reading modal vessel required, Split/Combine vessel lists, saveReading validation), `VesselsList.vue` (getCurrentBeerAtLocation for serving tanks, onActivated, remove ItemRepository/LedgerRepository from load), `Serving.vue` (same as console: include standalone serving locations, key and "(no vessel)" label).
