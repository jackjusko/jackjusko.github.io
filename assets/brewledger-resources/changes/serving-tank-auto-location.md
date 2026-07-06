# Serving tank auto-location – feature analysis

## Summary

When **adding** a new serving tank (console and mobile), the location dropdown is removed. A new location is created automatically with `stage: 'serving'` and `name` equal to the tank name, and the new vessel is bound to that location. When **editing** an existing serving tank, the bound location is shown read-only; no new location is created.

## Implementation

### Console ([platforms/console/src/views/Vessels.vue](platforms/console/src/views/Vessels.vue))

- **New serving tank:** Form shows helper text: "A serving location will be created with this name and the tank will be linked to it." No location dropdown.
- **Edit serving tank:** Read-only display "Location: {{ locationName }} (serving)" via computed `formServingLocationName` from `form.location_id` and `locations`.
- **saveVessel:** On create + type SERVING: `LocationRepository.create({ name: form.value.name.trim(), stage: 'serving' })` then `VesselRepository.create({ name, type: 'SERVING', location_id: newLocation.id })`. On edit, payload includes existing `location_id` for SERVING; non-SERVING sends `location_id: null`.

### Mobile ([platforms/brewledger-app/src/views/VesselsList.vue](platforms/brewledger-app/src/views/VesselsList.vue))

- Same pattern: new + SERVING shows helper text; edit + SERVING shows read-only location name.
- **saveVessel:** Same create flow (location first, then vessel with `location_id`). Edit unchanged.
- **watch(form.type):** Still clears `location_id` when switching away from SERVING.

### No server or repository changes

- `LocationRepository.create()` and `POST /api/locations` unchanged; location limit enforced as before.
- Vessel create/update already accept `location_id`.

## Edge cases

- **Empty/whitespace name:** Location name uses `form.value.name.trim()`. Vessel name is required by the form, so a non-empty trimmed value is used for the location.
- **Location limit:** If the org has reached `max_locations`, `LocationRepository.create` fails (403); the error is shown and the vessel is not created.
- **Edit then change type away from SERVING:** Existing behavior sends `location_id: null` for non-SERVING; vessel is unlinked from the location.
- **Duplicate tank names:** Two new tanks with the same name (e.g. "Tap 1") create two locations with the same name. Allowed; server does not require unique location names.

## Rationale

Serving page tank cards display data keyed by **location** (ledger on-hand per location). When two serving tanks shared one location, both cards showed identical data ("mirroring"). By creating one location per new serving tank and binding the tank to it, each tank has independent inventory and the mirroring bug is avoided at the source.

## Second iteration (post-implementation)

### Review

- **Create flow:** Location is created first, then vessel with `location_id`. If vessel create fails after location create (e.g. network or validation), an orphan location remains. This is acceptable per plan; user can delete the location from Locations or reuse it. No code change.
- **Edit flow:** Read-only location name is resolved from `locations.value` (console) or `locations.value` (mobile). Both load locations on page load/refresh, so when the user opens Edit, the list is populated. No race condition.
- **Console BARREL type:** Console Vessels.vue option list does not include BARREL in the type dropdown (only FERMENTER, UNITANK, BRITE, SERVING, OTHER). Mobile includes BARREL. Inconsistency pre-dates this feature; no change in this task.
- **Sync:** After save we call `SyncService.sync()` (console) or `SyncService.sync()` (mobile). New location and new vessel will sync; order of application on server is independent. No change.

### Conclusion

No additional code changes required. Implementation is complete and matches the plan; edge cases are documented and acceptable.
