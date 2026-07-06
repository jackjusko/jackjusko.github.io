# Hide Non-Serving Tank Locations in Forms — Feature Analysis (Iteration 1)

## Summary

Locations bound to non-serving vessels (fermenters, brites, unitanks) are auto-created for record-keeping (e.g., packaging flow). They should **not** be user-selectable in forms for receiving, transferring, consuming, or moving inventory. Only standalone locations and serving locations (bound to SERVING vessels) should appear in user-selectable dropdowns.

## Filter Logic

```javascript
const nonServingTankLocationIds = new Set(
  (vessels || [])
    .filter((v) => v.location_id && (v.type || '').toUpperCase() !== 'SERVING')
    .map((v) => v.location_id)
);
// Display: locations.filter((l) => !nonServingTankLocationIds.has(l.id))
```

## Implementation Summary

### Views Updated

| View | Platform | Change |
|------|----------|--------|
| Transfer | console + mobile | Load vessels, filter locations for From/To dropdowns |
| Consume | console + mobile | Load vessels, filter locations for "From location" |
| BatchDetail | console + mobile | Add `selectableLocationsForAddIngredientAndSupply` for Add Ingredient "From Location" and Supply lines; transfer destination unchanged |
| BatchRecipeConsume | console + mobile | Filter `getAvailableLocations()` to exclude non-serving tank locations |
| Losses | console | Load vessels, filter locations |
| Removals | console | Load vessels, filter locations (removal + in-bond receipt forms) |
| RemoveBeer | mobile | Load vessels, filter locations |
| SalesOrder | console | Load vessels, filter locations for fulfillment location |
| ItemForm | console + mobile | Filter default location dropdown |
| Count | mobile | Filter locations for start-count session |

### Views Unchanged (per plan)

- **Receive**: Excludes all tank locations — no change
- **Par Levels / ReorderList**: Excludes all tank locations — no change
- **BatchDetail transfer destination**: Excludes all tank locations — no change

## Potential Issues & Edge Cases

### 1. Vessel type casing
- Filter uses `(v.type || '').toUpperCase() !== 'SERVING'` — handles null, undefined, and mixed-case vessel types.

### 2. Deleted locations
- All filters include `!l.deleted_at` where applicable (e.g., `locations.filter(l => !l.deleted_at && !nonServingTankLocationIds.has(l.id))`).

### 3. BatchRecipeConsume — computed timing
- `getAvailableLocations` is called during `onMounted` forEach after `vessels.value` is set. `nonServingTankLocationIds` is a computed that depends on `vessels.value`, so it will be correct when the forEach runs.

### 4. Count view — fermenter physical counts
- Plan noted: "Do you ever run physical counts at fermenter/brite locations?" Implemented filter per plan; if users need to count at fermenters, this can be revisited.

### 5. LocationsList.vue reference
- `LocationsList.vue` already uses this pattern (excludes non-serving tank locations). Our per-view implementation is consistent.

### 6. Missing VesselRepository
- Both platforms have `VesselRepository.js`; all imports verified.

### 7. Supply line availability (BatchDetail)
- Console: supply line availability watch now iterates over `selectableLocationsForAddIngredientAndSupply` instead of full `locations` — only builds availability for locations shown in dropdown. Correct.

### 8. Form state when location becomes invalid
- If a user had a non-serving tank location selected before the filter was applied (e.g., from cached form state), the location would no longer appear in the dropdown. The form would still have the old `location_id`; validation may pass if the backend accepts it. **Mitigation**: Unlikely in practice since these locations were never intended for user selection; existing data with such locations would be legacy. No explicit clear-on-load added.

### 9. Receive / Par Levels / Transfer destination
- These intentionally exclude **all** tank locations (not just non-serving). No change per plan.

## Iteration 2 — Additional Findings

### Additional Views Updated

- **Removals.vue (console)**: Console equivalent of RemoveBeer (mobile); has location dropdowns for both removal form and in-bond receipt form. Added filter for consistency.
- **SalesOrder.vue (console)**: Location dropdown for "fulfill from" when creating a sales order (removal with purpose 'sale'). Added filter.

### Views Not Filtered (Intentional)

- **Vessels.vue / VesselsList.vue**: Location dropdown for linking a vessel to a location. When creating a fermenter/brite, the user may need to create or select a location to link. The vessel form is for vessel configuration, not for transfer/consume operations. Per plan, not in scope.
- **LocationsList.vue**: Already filters (reference implementation).
- **Receive, Par Levels, BatchDetail transfer destination**: Exclude all tank locations; no change.
- **Ledger, Inventory, Dashboard, Export, Reports, Settings**: Location used for filtering/display, not for selecting transfer/consume destination.
- **Serving.vue**: Uses locations for display of serving tanks; not a form for selecting where to move beer.

### Final Checklist

- [x] All plan-specified views updated
- [x] Removals and SalesOrder added (iteration 2)
- [x] analysis.md updated
- [x] No linter errors
