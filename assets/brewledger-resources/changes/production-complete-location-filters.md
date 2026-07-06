# Feature Analysis: Mark Production Complete Location Filters

## Summary

Fixed two bugs in the Mark Production Complete modal destination dropdowns:

1. **Serving destination**: Now shows only serving locations (`stage === 'serving'`). Previously included cellar locations from fermenters/brites because `servingVessels` had no type filter.
2. **Packaged (keg/case) destination**: Now excludes serving locations (`stage !== 'serving'`). Previously could show standalone serving locations.

## Implementation

### Console BatchDetail.vue

- **Serving**: `servingVessels` restricted to vessels with `type === 'SERVING'`. First loop builds list from locations with `stage === 'serving'`; vessel name resolved via `servingVessels.find()` when a tank links to the location. Second loop (SERVING vessels only) adds any vessel-linked locations not already in the first loop.
- **Storage**: Added `l.stage !== 'serving'` to `productionCompleteStorageLocations` filter.

### Mobile BatchDetail.vue

- **Serving**: Added first loop over locations with `stage === 'serving'` (mobile previously only had vessel-linked locations). `servingVessels` restricted to `type === 'SERVING'`. Vessel name resolved when a tank links to the location.
- **Storage**: Added `l.stage !== 'serving'` to `productionCompleteStorageLocations` computed.

## Edge Cases

| Case | Handling |
|------|----------|
| Fermenter/brite with location_id | Excluded from serving list; cellar locations no longer appear |
| Standalone serving location | Shown in serving list; excluded from packaged list |
| Packaged to keg/case storage | Only non-serving locations (cellar, racking_keg, case, etc.) |

## Files Touched

- `platforms/console/src/views/BatchDetail.vue`
- `platforms/brewledger-app/src/views/BatchDetail.vue`
