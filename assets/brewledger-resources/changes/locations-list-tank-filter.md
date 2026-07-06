# Feature Analysis: Locations List — Hide Non-Serving Tank Locations

## Summary

The Locations page now hides locations that are bound to non-serving tanks (fermenters, brites, unitanks). Serving locations (bound to SERVING vessels) and standalone locations remain visible. This avoids clutter from auto-created cellar locations (e.g. "FV-1", "BT-1") while keeping serving locations (e.g. "Serving Tank 3") and generic storage locations.

## Implementation

### Console and Mobile LocationsList.vue

- Load both locations and vessels
- Build `nonServingTankLocationIds`: location IDs from vessels where `type !== 'SERVING'`
- Filter displayed locations: exclude those in `nonServingTankLocationIds`
- Result: standalone locations + serving locations (one row per location; no duplicates)

## Edge Cases

| Case | Handling |
|------|----------|
| Fermenter location (e.g. FV-1) | Hidden |
| Brite location (e.g. BT-1) | Hidden |
| Serving tank location (e.g. Serving Tank 3) | Shown |
| Standalone location (Keg Storage, Cold Room) | Shown |
| Vessel with no type | Treated as non-serving (hidden if bound) |

## Files Touched

- `platforms/console/src/views/LocationsList.vue`
- `platforms/brewledger-app/src/views/LocationsList.vue`
