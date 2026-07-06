## Mobile Batch Detail parity (Iteration 1)

Context: The mobile `BatchDetail.vue` has diverged from the console flow for production-complete/serving/storage and vessel milestones. I compared the mobile view to `platforms/console/src/views/BatchDetail.vue` and the requirements in `analysis.md`.

Findings
- Serving tanks: `Adjust Volume` and `Set Volume` simply update `batch_location` volume and volume snapshots. Console reconciles serving tanks through ledger on-hand (`getCurrentBeerAtLocation`/`getBeerItemForServingLocation`) with RECEIVE/CONSUME entries, conflicts blocking, and deltas based on current on-hand. Mobile misses this, so tank adjustments and setpoints won’t correct ledger, can go negative, and ignore tank conflicts.
- Transfers to storage: Mobile allows choosing a storage location without requiring a matching Finished Beer RECEIVE entry; console requires `log_to_ledger` + beer item when a destination location is chosen.
- Milestone production complete: Console treats the production-complete milestone as a trigger to open the Production Complete modal (button + label are clickable). Mobile toggles it like a normal milestone, bypassing the required flow and ledger RECEIVE.
- Minor UX gaps: Mobile production-complete destination list lacks grouping/empty-state hints; serving location occupancy uses `getCurrentBeerAtLocation` but not `getBeerItemForServingLocation` on set-volume/adjust flows.

Plan
- Add tank-aware adjust/set volume paths mirroring console: resolve occupancy, enforce no-conflict, derive beer item, write ledger entries (RECEIVE/CONSUME) with notes, allow positive/negative deltas, and only use volume snapshots for non-tanks. Include on-hand read via `getBeerItemForServingLocation` for set-volume delta.
- Enforce transfer validation for destination locations: require `log_to_ledger` + beer item when destination location is provided (storage moves).
- Treat production-complete milestone as an entry point to the Production Complete modal; do not allow simple toggle.
- Keep UI changes minimal but add any needed helper/computed state to support the above behaviors.

## Iteration 2 (post-implementation review)

What changed
- Adjust/Set Volume now branch for serving tanks: resolve occupancy conflicts, fetch on-hand via `getBeerItemForServingLocation`, and reconcile with ledger RECEIVE/CONSUME entries; non-tanks still use snapshots/adjustments.
- Transfer modal blocks storage moves without a ledger RECEIVE; destination selection auto-enables ledger logging and defaults the beer item.
- Production-complete milestone chip opens the Production Complete modal instead of toggling directly; milestone remains clickable for other steps.

Remaining risks / follow-ups
- Tank set/adjust flows rely on current ledger on-hand; offline drift between on-hand and batch_location volume is now corrected via ledger but still depends on sync freshness.
- Set Volume for tanks uses current time for ledger entries; backdating isn’t supported for tanks (matches console behavior). If backdating is needed later, add explicit timestamp handling.
