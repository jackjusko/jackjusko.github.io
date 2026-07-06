# Serving: One Beer Item per Location (Feature Analysis)

## Summary
Console serving and production-complete flows now enforce **one beer item per serving location** at a time. Occupancy is derived from ledger on-hand (which Finished Beer items have quantity at that location), not from batch_location. Production complete shows current beer per location and, when the user selects an already-occupied serving location, a confirmation dialog: Same beer – add on top; Remove first; Cancel.

## First-Pass Analysis

### Implemented
- **ServingOccupancyService** (`platforms/console/src/services/ServingOccupancyService.js`): `getCurrentBeerAtLocation(locationId)` returns `{ item, onHand }`, `{ conflict: true, items }`, or `{ empty: true }`. `getBeerItemForServingLocation(locationId)` returns the single item to use or null.
- **BatchDetail production complete**: Serving locations list is built with `getCurrentBeerAtLocation` per location; each option shows current beer name or "Empty" or "Multiple beers – resolve on Serving page" (disabled when conflict). No longer excludes locations by batch_location occupancy. On "Mark Complete", if the selected serving location has one beer item, a 3-button dialog appears: "Same beer – add on top" (proceed with that item), "Remove first" (alert to zero/remove on Serving page), "Cancel". If conflict, selection is blocked with message. RECEIVE uses existing item when adding on top, else `getOrCreateBeerItemForBatch(batch)`. Source batch_location is still deleted after production complete (vessel cleared).
- **Serving.vue**: Tanks list uses `getCurrentBeerAtLocation` per vessel location; each tank has `beerItem`, `beerItemName`, `onHand`, `conflict`. Set volume / Record removal / Set empty use `tank.beerItem` for ledger entries; buttons disabled when `tank.conflict || !tank.beerItem`. Set empty only zeros the current beer item at that location (CONSUME); no batch_location delete. Removed BatchRepository and BatchLocationRepository imports; removed batch name/link from UI.

### Edge Cases and Potential Gaps
1. **Mobile app**: Parity implemented (2026-02-16). Mobile now has the same flows: `ServingOccupancyService` in `platforms/brewledger-app/src/services/ServingOccupancyService.js`; BatchDetail production complete uses occupancy per location, option labels show current beer/Empty/conflict, 3-button confirm when location has beer; Serving.vue uses per-location beer item, Set volume/Record removal/Set empty with guards and Set empty button/modal.
2. **Vessels view**: Still shows batch per vessel via batch_locations. No change; vessel–batch association remains for non-serving workflows (fermenters, brites). Serving tanks may show "no batch" after this change when beer is present only via ledger; acceptable.
3. **Server validation**: Server does not enforce "one beer per serving location"; it only validates entity shape and batch_location vessel exclusivity. Mixed beer at one location is possible if data is edited elsewhere. Conflict is detected client-side from on-hand; resolving requires user action on Serving page.
4. **Ledger batch_id**: Serving.vue no longer sends `batch_id` on CONSUME/RECEIVE for set volume, record removal, set empty. TTB and history still have item_id and location_id; batch-level traceability for those entries is reduced. Optional for TTB; acceptable.
5. **Production complete – Storage**: Unchanged; storage locations have no "current beer" occupancy check. Only serving destination triggers the confirmation flow.
6. **Deduplication**: Serving locations list dedupes by location id when adding vessel-linked locations so the same location does not appear twice.

### Second-Pass Considerations
- Confirm that when a serving location has exactly one beer item and user chooses "Same beer – add on top", the RECEIVE uses that item and volume is additive (no overwrite).
- Confirm conflict state: multiple beer items with on-hand > 0 at same location can occur from manual receives or multi-tab use; messaging directs user to Serving page to resolve.
- Documentation: Update analysis.md to describe the new model (one beer per serving location, occupancy from ledger, no batch link for serving occupancy).

## Second-Pass Analysis (Post First-Pass Review)

### Verification
- **Add on top**: `saveProductionComplete` uses `productionCompleteExistingItem` when set (from "Same beer" click); RECEIVE posts `quantity: volumeBarrels` to that item at the selected location. Ledger is append-only; on-hand is summed. Additive behavior confirmed.
- **Conflict**: Handled in openProductionCompleteModal (option disabled, label "Multiple beers – resolve on Serving page") and in onProductionCompleteConfirm (alert and no dialog). Serving.vue disables actions and shows "Multiple beers – resolve inventory". No automatic resolution; user must adjust on Serving page.
- **Empty tank**: Set volume with 0 is allowed (reconcile to 0); record removal and set empty require beerItem and on-hand. "No beer" tanks show "Add beer first" when user tries an action (buttons disabled for no beer).

### Additional Notes
- **ServingReportsService / server reports**: May still aggregate by batch or vessel; no change in this feature. Reports that group by location and item remain correct.
- **analysis.md**: Add a bullet under the Serving / production complete section describing the one-beer-per-location model, occupancy from ledger, and the production-complete confirmation dialog when the selected serving location already has beer.

### Post-review fix (serving-finished-beer-review.md)
- **Console Batch Detail tank flows**: Adjust volume (tank) and Set volume (tank) were still using `getDefaultFinishedBeerItem()`. Updated to use `getCurrentBeerAtLocation` / `getBeerItemForServingLocation` so ledger and on-hand align with the one-beer-per-location model; conflict blocks with message; empty + negative change blocked; empty + positive change uses `getOrCreateBeerItemForBatch(batch)`.
