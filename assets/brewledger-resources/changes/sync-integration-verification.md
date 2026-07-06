# Sync integration verification (recent changes)

Verification that recent batch/vessel changes are correctly integrated through SyncService → server → DB.

## Entities involved

| Entity | Client (Dexie) | SyncService | Server processChange | Server DB | Server fetchUpdates | Client apply |
|--------|----------------|-------------|---------------------|-----------|---------------------|--------------|
| **batch_locations** | db.batch_locations (v11) | gather, mark, apply | processChange('batch_locations', bl, 'batch_location') | createEntityTable('batch_locations') – full entity in `data` JSON | fetchUpdates('batch_locations') – returns full entity from `data` | BatchLocationRepository.applyRemoteUpsert |
| **batch_additions** | db.batch_additions | gather, mark, apply | processChange('batch_additions', a, 'batch_addition') | createEntityTable('batch_additions') – full entity in `data` JSON (includes optional batch_location_id) | fetchUpdates('batch_additions') | BatchAdditionRepository.applyRemoteUpsert |
| **batch_volume_adjustments** | db.batch_volume_adjustments (v12) | gather, mark, apply | processChange('batch_volume_adjustments', bva, 'batch_volume_adjustment') | createEntityTable('batch_volume_adjustments') – full entity in `data` | fetchUpdates('batch_volume_adjustments') | BatchVolumeAdjustmentRepository.applyRemoteUpsert |

## Verification results

### 1. SyncService (platforms/brewledger-app/src/services/SyncService.js)
- **Gather**: `batch_additions`, `batch_locations`, `batch_volume_adjustments` included in `changes` (lines 55, 65–66). ✓
- **Mark**: `markAsSynced` marks all three tables (lines 125, 134–135). ✓
- **Apply**: `applyServerUpdates` calls `BatchAdditionRepository`, `BatchLocationRepository`, `BatchVolumeAdjustmentRepository` for `updates.batch_additions`, `updates.batch_locations`, `updates.batch_volume_adjustments` (lines 159, 169–170). ✓

### 2. SyncRepository (getPendingOps)
- Tables list includes `batch_additions`, `batch_locations`, `batch_volume_adjustments` (lines 8–10). ✓

### 3. Server (server/server.js)
- **validateEntity**: `batch_addition` (batch_id, item_id, event_type; batch_location_id optional), `batch_location` (parent_batch_id, vessel_id, current_volume, status), `batch_volume_adjustment` (batch_location_id, volume_change). ✓
- **processChange**: All three entity types processed; full entity JSON stringified and stored in `data` column (lines 1013–1048). ✓
- **fetchUpdates**: All three tables fetched; `data` parsed and pushed to response (lines 1176–1186). ✓

### 4. Server DB (server/init_db.js)
- `createEntityTable('batch_additions')`, `createEntityTable('batch_locations')`, `createEntityTable('batch_volume_adjustments')` – each table has `id, org_id, updated_at, server_updated_at, version, data`. Full entity (including batch_location_id on additions) lives in `data`. ✓

### 5. Client repositories
- **BatchAdditionRepository.add**: Builds `newAddition` with `...addition`, so `batch_location_id` is included when present; stored in Dexie with `sync_status: 'pending'`. ✓
- **BatchAdditionRepository.applyRemoteUpsert**: `db.batch_additions.put(addition)` – full server entity (including batch_location_id) stored. ✓
- **BatchLocationRepository.applyRemoteUpsert**: `db.batch_locations.put(split)`. ✓
- **BatchVolumeAdjustmentRepository.applyRemoteUpsert**: `db.batch_volume_adjustments.put(adjustment)`. ✓

### 6. Client DB (platforms/brewledger-app/src/db.js)
- Dexie stores full objects; store schemas only define indexes. `batch_additions` objects can include `batch_location_id`; no schema change required. ✓

## Pull path (server → client)

SyncService correctly pulls down all changes from the server:

1. **Response**: Server sends `res.json({ updates: responseUpdates, inventory_snapshot, serverTimestamp, orgStatus })`. `responseUpdates` is populated by `fetchUpdates(table, responseUpdates.<table>)` for every entity type, including `batch_additions`, `batch_locations`, `batch_volume_adjustments` (server.js ~1134–1186, 1204–1205).

2. **Client**: `const { updates, serverTimestamp, inventory_snapshot, orgStatus } = response.data`; then `await this.applyServerUpdates(updates, inventory_snapshot)` (SyncService.js 79, 94).

3. **applyServerUpdates**: For each entity type, calls `apply(Repo, updates.<key>)`. Every key is explicitly applied (SyncService.js 155–171):
   - `apply(BatchAdditionRepository, updates.batch_additions)`
   - `apply(BatchLocationRepository, updates.batch_locations)`
   - `apply(BatchVolumeAdjustmentRepository, updates.batch_volume_adjustments)`
   - (and all other entity types)

4. **apply helper**: `for (const item of items) { await repo.applyRemoteUpsert({ ...item, sync_status: 'synced' }); }`. So every item in each array is written to Dexie with full entity data (including batch_location_id on additions).

So SyncService is correctly pulling down all of these changes; no entity types are missing on the pull path.

## Summary
All recent changes (batch list vessels/volumes, additions per vessel with batch_location_id, batch_locations, batch_volume_adjustments) are correctly integrated: client writes set sync_status pending, SyncService sends full entities, server validates and stores full JSON in `data`, fetchUpdates returns full entities, and client applyServerUpdates applies every returned entity via the corresponding repository’s applyRemoteUpsert.
