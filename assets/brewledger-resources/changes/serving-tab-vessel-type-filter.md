# Feature Analysis: Serving Tab Vessel Type Filter & Display Logic

## Summary

1. **Vessel type filter**: Only **Serving Tank** vessels (type `SERVING`) with a linked location are considered. Fermenters and brites with `location_id` are excluded.
2. **Location-first display**: Refactored to iterate over **serving-stage locations** as the primary source. Each location produces exactly one card. Vessels are looked up by `location_id`; if a vessel exists for that location, the card shows the vessel name and supports Set volume; otherwise it shows as a standalone location (no vessel). This eliminates duplication when both a tank and its auto-created location would have appeared.

## Implementation

### Console and Mobile Serving.vue

- `isServingType(v)` helper: `v.type === 'SERVING' || v.type === 'Serving'`
- **Location-first logic**: `servingLocations` = all locations with `stage === 'serving'`. For each, `vesselByLocationId.get(loc.id)` yields the linked vessel (if any). One card per location; vessel name used when vessel exists.
- Removed the previous two-loop approach (vessels first, then standalone locations) that could show both a vessel card and a location card for the same tank.

## Edge Cases

| Case | Handling |
|------|----------|
| Fermenter/brite with location_id | Excluded; only SERVING vessels in vesselByLocationId |
| Serving tank without location_id | Excluded; unlinkedServingCount message prompts user to link on Vessels page |
| Tank + auto-created location | One card; location is primary, vessel enriches (name, Set volume) |
| Standalone serving location | One card; no vessel, shows location name with "(no vessel)" |

## Files Touched

- `platforms/console/src/views/Serving.vue`
- `platforms/brewledger-app/src/views/Serving.vue`
