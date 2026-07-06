## Vessel actions when no batch assigned

### Iteration 1 analysis
- Requirement: If a vessel has no batch, the desktop Vessels view should not let users click “Open batch” or “Set volume”; instead show that no batch is assigned. Vessel IDs should be hidden from display.
- Current changes: Buttons are only rendered when a batch id is present; empty vessels now show a muted “No batch assigned” message. Vessel ID labels were removed from cards and table rows.
- Risks / weak points:
  - The action guard uses a simple truthy check on `row.batchId`; if an id of `0` or an empty string ever appears, we would incorrectly hide valid actions. Better to rely on an explicit `hasBatch` flag derived during row assembly.
  - Rows that represent “empty” vessels can still surface snapshot/volume values if stale data exists in the split record. Aligning the action guard with an explicit `hasBatch` flag will let us also treat such rows as empty in a consistent way later if needed.
- Planned adjustments for this iteration:
  - Introduce a `hasBatch` boolean when building rows and use it to drive the actions rendering instead of a truthy `batchId` check.
  - Keep UI copy the same but make the conditional more explicit to avoid accidental regressions.

### Iteration 2 analysis
- Post-change review: Actions now use `hasBatch`, eliminating accidental suppression if a falsy but valid id ever appears. Empty vessels still avoid showing actions.
- New risk/observation:
  - Splits that have lost their batch (e.g., stale data) will now display “No batch assigned” for actions, but they still show any persisted volume and snapshot data, which could mislead operators into thinking a batch is assigned. We should blank volume/snapshot details when `hasBatch` is false to keep the row clearly empty.
- Planned adjustments for this iteration:
  - When building rows, if `hasBatch` is false, zero out `currentVolume` and `lastSnapshot` so empty vessels consistently show no setpoint or volume alongside the “No batch assigned” status.
