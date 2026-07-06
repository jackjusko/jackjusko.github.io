# Vessel Split / Batch Locations - Feature Analysis

## Overview

Batch volume can now be split across multiple vessels (one batch → many vessel splits). One tank’s volume can be split to multiple destination tanks with validation that sum(destinations) ≤ source volume. Work completed: mobile app, server, and DB (init_db). Console app and per-split milestones were explicitly deferred.

## Implemented Changes

### 1. Database (Server & Client)

- **Server `init_db.js`**: Added `createEntityTable('batch_locations')`. Entity tables use generic `(id, org_id, updated_at, server_updated_at, version, data)`; batch_locations stored as JSON in `data`.
- **Client `db.js`**: Dexie v11 adds store `batch_locations: 'id, parent_batch_id, vessel_id, org_id, sync_status'` and updates `batches` (no vessel_id index), `batch_readings` (adds `batch_location_id`), `batch_milestones` (adds `batch_location_id`). v10 schema left as-is for upgrade path.

### 2. Batch Entity

- **Batch**: No longer has single `current_vessel_id` / `current_volume` in create flow. Added `total_theoretical_volume` (sum of all splits). `planned_volume_unit` kept for display. Batch JSON may still contain legacy `vessel_id`/`planned_volume` for backfill and list display.
- **BatchRepository.create**: Accepts either `splits: [{ vessel_id, current_volume }, ...]` or legacy `vessel_id` + `planned_volume`/`current_volume`. Creates batch then creates batch_locations (single or multiple). Sets `total_theoretical_volume`. Removed vessel_id → TRANSFERRED milestone logic from `update()`.

### 3. Batch Locations (Vessel Splits)

- **BatchLocationRepository**: `getById`, `getByBatchId`, `create`, `update`, `delete`, `setSplitsForBatch` (upsert by vessel_id), `transferSplit({ sourceBatchLocationId, destinations })`, `applyRemoteUpsert`. Status and metrics: `current_gravity`, `current_ph`, `current_temp`, `status` (Fermenting, Crash, Conditioning, Carbonating).
- **Server**: `validateEntity('batch_location', …)` requires `parent_batch_id`, `vessel_id`; optional `current_volume` (number); `status` must be one of the four if present. Sync: processChange and fetchUpdates for `batch_locations`.

### 4. Batch Readings

- **batch_readings**: Optional `batch_location_id`. Readings can be batch-level (no vessel) or per vessel. `BatchReadingRepository.add` accepts `batch_location_id`; `getByBatchLocationId` added.
- **BatchDetail**: When saving a reading with `batch_location_id`, the corresponding batch_location’s `current_gravity` / `current_ph` / `current_temp` is updated from the reading value. Readings tab shows vessel name when `batch_location_id` is set (via `getVesselNameForReading`).

### 5. Sync

- **SyncService**: Gathers, marks, and applies `batch_locations`; `BatchLocationRepository.applyRemoteUpsert` in applyServerUpdates.
- **Server**: Response includes `batch_locations` in updates; clients receive new/updated splits after sync.

### 6. Mobile UI

- **BatchForm**: Single “Volume” field replaced with vessel splits: default one row (vessel + volume), “+ Add another vessel”, total = sum of volumes. Save builds `splits` and `total_theoretical_volume`; at least one vessel with volume required.
- **BatchDetail**: Header shows total volume (`displayTotalVolume` = `total_theoretical_volume` or sum of batch_locations). “Current Vessel” replaced with vessel cards: each card = one batch_location (vessel name, volume, status, gravity/temp/pH). “Log Reading” per card opens reading modal with `batch_location_id` set. “Split / Transfer” modal: source = one batch_location, destinations = multiple rows (vessel + volume), validation sum ≤ source volume; calls `BatchLocationRepository.transferSplit`. Legacy backfill: if batch has `vessel_id` and no batch_locations, create one batch_location and set `total_theoretical_volume`.
- **BatchesList**: Volume = `total_theoretical_volume ?? planned_volume`; vessel name still from `vessel_id` (legacy).
- **BatchRecipeConsume**: Scale factor uses `total_theoretical_volume ?? planned_volume`.

### 7. Ledger

- **LedgerRepository.transferSplit** (one-to-many inventory transfer) was removed per request; batch volume split is handled only via batch_locations, not ledger.

---

## First-Iteration Review: Potential Weak Points

### 1. Backfill and legacy data

- **Backfill only on load**: Legacy batch (vessel_id, no batch_locations) is backfilled when BatchDetail loads. BatchesList and other views don’t load batch_locations, so they still show `vessel_id` and `planned_volume`. Consistent, but if a user never opens BatchDetail, that batch never gets backfilled locally.
- **Server**: No migration script for existing batches. Old clients may still send batch with `vessel_id`; server accepts it (no validation that batch must not have vessel_id). New clients don’t send vessel_id when using splits. No server-side backfill of batch_locations from existing batch rows.
- **Risk**: Existing batches in production will have vessel_id in JSON; they will only get a batch_location row when a client that has the new code opens that batch (mobile). Acceptable if rollout is “all clients updated,” but worth documenting.

### 2. Delete / remove vessel

- **BatchLocationRepository**: No sync of deletes. If we delete a batch_location locally (e.g. “remove vessel” from batch), server and other devices never see that delete; they still have the old row. Current UI doesn’t expose “remove vessel” (only Split/Transfer which moves volume). So no delete path in UI yet.
- **transferSplit**: When source volume goes to zero we delete the source batch_location locally; that delete is not synced. Other devices will still have the source split until they overwrite from another sync (we don’t send deletes). So: deleting a split is “local only” and could cause zombie state on other devices if we add remove-vessel later.

### 3. Milestones

- **Spec mentioned**: “milestone checks against specific vessel splits (e.g. Dry Hopped for FV-01 but not FV-02).” Not implemented: milestones remain batch-level only. `batch_milestones` has optional `batch_location_id` in Dexie v11 schema but no UI or repository logic uses it. Deferred as requested (“for the time being, only work on the mobile UI”).

### 4. Console app

- Console was explicitly out of scope. It still assumes single vessel (e.g. vessel_id on batch). When console loads a batch that has been migrated to batch_locations on mobile, console may show no vessel or stale vessel_id. Document as known limitation until console is updated.

### 5. Validation and edge cases

- **setSplitsForBatch**: Validates sum(splits) ≤ total_theoretical_volume when provided. Does not validate that vessel_id exists in vessels table (client-side); server validateEntity for batch_location doesn’t check vessel exists.
- **transferSplit**: Validates sum(destinations) ≤ source volume. If same vessel appears in two destination rows, we create/update that vessel’s split twice (volume summed). No duplicate-vessel check.
- **Empty splits**: BatchForm requires at least one vessel with volume. BatchDetail shows “No vessels assigned” if batch_locations.length === 0; Split/Transfer is the only way to add. Creating a batch with no splits (e.g. API) would leave batch with total_theoretical_volume 0 or null and no batch_locations; UI would show empty state. Acceptable.

### 6. Readings and metrics

- **Batch-level readings**: Readings without `batch_location_id` still supported; they don’t update any split’s current_gravity/current_ph/current_temp. So “batch-level” readings are display-only in the Readings tab and don’t populate vessel cards.
- **Per-split metrics**: Only the latest reading per type per split is stored on the batch_location (current_gravity, etc.). History is in batch_readings. If we ever need “latest per type” from DB we’d query batch_readings; for now UI uses batch_location fields for the cards.

### 7. Sync ordering and conflicts

- **Order**: Client pushes changes then fetches updates. If two devices both add batch_locations for the same batch, both get new IDs; server accepts both. No last-write-wins on “same logical split” (we don’t key by batch_id + vessel_id on the server for conflict resolution). Acceptable for current use.
- **Optimistic locking**: batch_locations use version; server rejects stale updates. Same as other entities.

### 8. Tests

- BatchRepository.spec.js: Vessel-change → TRANSFERRED test removed. New test: create with vessel_id + planned_volume creates one batch_location with correct volume. Test run was skipped per user request; test may need BatchLocationRepository and Dexie v11 in test env (e.g. schema upgrade on db.open()).

---

## Recommendations After First Iteration

1. **Document**: In analysis.md, add a “Vessel split / batch_locations” section: schema, repositories, UI behavior, backfill, and limitation “Console not updated; milestones remain batch-level.”
2. **Optional server validation**: In `validateEntity('batch_location')`, optionally ensure `parent_batch_id` exists in batches and `vessel_id` exists in vessels (referential checks). Low priority.
3. **No delete sync for now**: Leave as-is; document that removing a vessel (if we add it) would be local-only until we add delete sync or soft-delete for batch_locations.
4. **Console**: When in scope, update console to load batch_locations, show vessel cards, and use total_theoretical_volume / planned_volume_unit for display.

---

## Second-Iteration Additions (Review of First Analysis)

### 9. BatchRepository.create and planned_volume_unit

- **create**: We delete `splits`, `vessel_id`, `current_volume` from newBatch before db.batches.add. We do not delete `planned_volume_unit`; it’s passed in and stored on the batch. BatchesList and BatchDetail use `batch.planned_volume_unit` for display. Good.

### 10. BatchLocationRepository.transferSplit and existing splits

- **transferSplit**: For each destination we either update an existing batch_location (same batch + vessel_id) or create a new one. We then reduce source by destSum; if new source volume ≤ 0 we delete the source. So we can end up with more splits (e.g. source FV-01 20 → FV-02 10, FV-03 10 creates/updates two splits and deletes source). Correct.
- **Edge case**: If user enters same vessel twice in destinations with volumes 5 and 5, we process twice and add 5+5 to that vessel’s split. Intentional; no duplicate-vessel coalescing.

### 11. Server fetchUpdates for batch_locations

- **Table name**: Server uses table name `batch_locations` (with underscore). init_db creates it. fetchUpdates('batch_locations', responseUpdates.batch_locations) uses the same name. SQLite table names are case-insensitive. No issue.

### 12. Dexie version 11 upgrade

- **New installs**: db.open() applies v10 then v11; batch_locations store and updated indexes appear.
- **Existing installs**: Upgrade from v10 to v11 runs; batches index changes (vessel_id removed), batch_readings and batch_milestones get batch_location_id index, batch_locations added. Existing batch records keep their fields (including vessel_id) in the object; only indexes change. Safe.

### 13. BatchesList vessel label

- **vesselName**: Still from `batch.vessel_id`. After backfill we don’t clear batch.vessel_id on the batch record (we only set total_theoretical_volume). So legacy batches keep showing one vessel name. Batches that were created with splits never have vessel_id; vesselName will be null and we don’t show “Multiple” yet. Could add “Multiple vessels” when batch has total_theoretical_volume but no vessel_id; deferred as minor.

### 14. SyncRepository.getPendingOps

- **SyncRepository**: getPendingOps iterates a fixed list of tables; batch_locations is not in that list. So “pending ops” count for the sync status indicator might not include pending batch_locations. If the UI uses getPendingOps to show “N pending changes,” batch_locations would be missing. Checking: SyncService.sync() gathers from db.batch_locations.where('sync_status').equals('pending') directly; it doesn’t use SyncRepository.getPendingOps for the payload. So sync payload is correct. Only the optional “pending count” display could be wrong. Recommendation: add 'batch_locations' to SyncRepository.getPendingOps table list so any sync-status UI is accurate.

---

## Implementation: SyncRepository.getPendingOps

- Add `batch_locations` to the tables array in SyncRepository.getPendingOps so pending batch_location changes are included in the pending ops count (if used by sync status UI).

---

## Additional Features: Volume Adjustments & Many-to-One Combine

### Batch Volume Adjustments

- **Purpose**: Log volume changes per vessel (serving, loss, trub) without affecting inventory ledger (which is for items, not liquid).
- **Schema**: New `batch_volume_adjustments` table/store (Dexie v12): id, batch_location_id, volume_change (number, can be negative), reason, created_at, org_id, sync_status.
- **BatchVolumeAdjustmentRepository**: create, getById, getByBatchLocationId, applyRemoteUpsert.
- **Server**: validateEntity('batch_volume_adjustment') requires batch_location_id and volume_change (number); processChange, fetchUpdates, responseUpdates for batch_volume_adjustments.
- **SyncService**: Includes batch_volume_adjustments in gather/mark/apply.
- **UI**: "Adjust" button on each vessel card; modal: volume_change (negative for loss), reason; saves adjustment and updates batch_location.current_volume; validates new volume ≥ 0.

### Many-to-One Combine

- **BatchLocationRepository.combineSplits({ sourceBatchLocationIds, destinationVesselId })**: Combines multiple source splits into one destination vessel. Sums source volumes; creates or updates destination split; deletes source splits. All sources must be from same batch.
- **UI**: Split/Transfer modal has two modes: "Split (1 → Many)" and "Combine (Many → 1)". Combine: checkboxes for source vessels, dropdown for destination vessel, displays total volume to combine.

### UI Redesign for Simplicity

- **Quick Actions**: Prominent "Log Reading" and "Add Ingredient" buttons at top (no tab navigation required for most common actions).
- **Tabs Simplified**: "Timeline" (milestones) and "History" (all events: readings, additions, packaging in one chronological list with icons).
- **Vessel Cards**: Cleaner layout with metrics grid, "Adjust" link (small, top-right), "Log Reading" button at bottom of each card.
- **History Tab**: Unified event feed with icons (🌡️ 💧 🧪 🌾 📦) and vessel labels for readings; no separate Additions/Readings/Packaging tabs.

### Edge Cases & Limitations

- **Combine deletes sources**: Source splits are deleted locally; no delete sync yet (same limitation as transferSplit when source volume → 0). Other devices will get new destination split but old sources remain until we add delete sync.
- **Negative volume**: Adjust volume validates new volume ≥ 0; prevents going negative.
- **Combine validation**: All sources must be from same batch (checked); destination vessel can be new or existing (creates or updates split).
- **History tab**: Shows all events; no filtering by type yet (could add filter buttons if needed).
