# Vessel Exclusivity & Desktop Visualization - Analysis

## Goals
- Enforce one active batch per vessel (prevent double-booking).
- Surface a desktop visualization of vessels showing what’s in each tank.

## Current State (before changes)
- `batch_locations` allow multiple batches to reference the same `vessel_id`; only per-batch dedupe exists.
- Server validation for `batch_location` checks required fields and status but not vessel occupancy.
- Console Vessels view is read-only; shows only vessels that have splits, not empty tanks; no visual grid.
- Mobile has vessel CRUD and uses the same repository logic (no exclusivity guard).

## Risks / Edge Cases
- Double-booked vessels: nothing stops batch A and batch B from sharing a vessel.
- Local-only deletes: `batch_location` deletes don’t sync; must not rely on delete for freeing vessels.
- Destination moves (transfer/combine) can silently reassign a vessel already in use.
- Visualization may mislead if we omit empty vessels or stale data (deleted_at).

## Plan
- Add exclusivity guard in client repositories (console + mobile) that rejects assigning a vessel already bound to another batch (ignoring deleted rows), used in create/split/transfer/combine paths.
- Add server-side validation in `/api/sync` to enforce exclusivity authoritatively.
- Enhance console Vessels view with a card/grid “occupancy” visual and include empty vessels in the overview/table.
- Update `analysis.md` after implementation.

## Iteration 2 Review (after implementation)
- Added exclusivity guards:
  - Client: shared `assertVesselAvailable` in console + mobile `BatchLocationRepository` used in create, setSplits, transfer, and combine paths; errors early with a clear message.
  - Server: `validateEntity('batch_location')` now rejects assignments when another batch already uses the vessel (org + non-deleted row check).
- Visualization: console Vessels view now shows a card grid of all vessels (including empty) with batch, status, volume, last set, and location; table also includes empties. Added inline modal to create/edit vessels from the Vessels page.
- Delete propagation: `batch_locations` with `deleted_at` now sync across devices (server returns tombstones; client `applyRemoteUpsert` deletes locally), so freeing a vessel is reflected on other clients.
- Residual risks:
  - Error surfacing depends on callers showing thrown messages; batch forms using setSplits should present the rejection, but legacy flows without try/catch would show a generic alert/console error.
  - Optional future hardening: server referential validation that `vessel_id` exists.
