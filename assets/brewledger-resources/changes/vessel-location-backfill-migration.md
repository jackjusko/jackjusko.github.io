# Feature Analysis: Vessel Location Backfill Migration

## Summary

Migration script `server/migrate_backfill_vessel_locations.js` creates locations for vessels that do not have an associated `location_id` and links them. This addresses legacy vessels created before the operation-driven TTB implementation (Phase 2a), which now creates a location for every new vessel (fermenter, brite, serving tank).

## Implementation

### Script Behavior

- **Input**: All vessels in the database (server-side)
- **Filter**: Skips vessels that already have `location_id`; skips soft-deleted vessels (`deleted_at`)
- **Per vessel**:
  1. Create a new location with `name` = vessel name (or `"Vessel {id}"` if name empty), `stage` = `'serving'` for type SERVING, `'cellar'` for FERMENTER/BRITE/UNITANK/BARREL/OTHER
  2. Update vessel `data` to include `location_id` = new location id; bump `version`, `updated_at`, `server_updated_at`

### Idempotency

- Skips vessels with existing `location_id`; safe to run multiple times
- `DRY_RUN=1` prints what would be done without writing

### Usage

```bash
node server/migrate_backfill_vessel_locations.js
DB_PATH=/path/to/database.sqlite node server/migrate_backfill_vessel_locations.js
DRY_RUN=1 node server/migrate_backfill_vessel_locations.js
```

## Edge Cases

| Case | Handling |
|------|----------|
| Vessel with empty name | Location name = `"Vessel {vessel_id}"` |
| Duplicate vessel names in same org | Each gets its own location (same as serving-tank auto-location) |
| Location limit (max_locations) | Script does not check; may exceed limit for orgs with many legacy vessels. Consider running `migrate_max_locations_100.js` first if orgs had lower limits |
| Sync | New locations and updated vessels will sync to clients on next sync; clients will receive both entities |

## Rationale

Per `operation-driven-ttb-systems-analysis.md`, legacy vessels (no `location_id`) were left as-is (Option B). The packaging flow and TTB reporting benefit from vessels having linked locations. This migration allows existing deployments to backfill without manual edits.

## Second-Pass Analysis

### Transaction Atomicity
- **Risk**: If location INSERT succeeds but vessel UPDATE fails (e.g. mid-run crash), orphan locations would remain.
- **Mitigation**: Wrapped all writes in a single transaction (`BEGIN` … `COMMIT`); on any failure, `ROLLBACK` leaves DB unchanged.

### Sync and Client State
- New locations and updated vessels are written to server tables; clients receive them on next sync via `fetchUpdates`. No client-side migration needed.

## Files Touched

- **New**: `server/migrate_backfill_vessel_locations.js`
- **Updated**: `analysis.md` (Backfill Scripts section)
