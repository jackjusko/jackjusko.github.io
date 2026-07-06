## Feature analysis — Serving volume vs ledger alignment (Iteration 1)

### Context
- Production complete creates a single `RECEIVE` ledger entry (Finished Beer) with a chosen location; it does not move or set vessel volume.
- Serving state for reports is derived from ledger location/stage, while the serving card uses `batch_locations.current_volume`.
- Set/Adjust Volume updates `current_volume` (and snapshot/adjustment rows) but does not touch ledger.
- Transfers can optionally log a RECEIVE into a destination location, but default adjust/set flows do not remove on-hand.

### Observed risk
- After production complete, users lower vessel volume (poured beer) via Adjust/Set Volume without posting a ledger removal. On-hand at the serving location stays high while vessel volume drops—“double inventory” divergence between ledger and tank.

### Goals
- Keep serving on-hand and vessel volume in sync when volume is decreased in a serving context.
- Make the workflow clearer: production complete + serving location means the beer is now serving; volume remains editable.

### Options considered
- **Auto-log removal on negative adjust:** When volume decreases, automatically create a `CONSUME` ledger entry (Finished Beer) against a user-selected serving location. Needs UI to pick location and confirm.
- **Force use of Removals screen:** Too heavy; breaks inline serving workflow.
- **Just warn:** Low value; problem persists.

### Proposed direction
- Extend Adjust Volume modal with an optional “log serving pour” toggle (enabled when volume_change < 0) that requires a serving-stage location; create a matching `CONSUME` ledger entry with negative quantity and note referencing the vessel.
- Add helper copy in production-complete modal reminding that selecting a serving location marks it serving and volume stays editable; guide to use adjust/transfer with serving removal logging for pours.
- Keep current_volume update as-is to maintain serving card accuracy; ledger entry handles on-hand.

### Open questions / edge cases
- Which item to use for serving removals? Use Finished Beer item (same as production complete).
- What if no serving-stage location exists? Offer all locations but label stage; validation should allow any location but nudge to serving.
- How to avoid double-logging when transfer already logged RECEIVE? Our change only applies to negative Adjust Volume; transfers unchanged.

---

## Feature analysis — Iteration 2 (post-implementation review)

### Changes made after Iteration 1
- Added optional “log serving removal” toggle to Adjust Volume; when enabled (and volume change is negative) it creates a `CONSUME` ledger entry for Finished Beer at a chosen location with an operation_type of `serving_pour`.
- Prefilled serving locations and clarified the production-complete modal that choosing a serving-stage location marks it serving while volume stays editable.

### Remaining risks / observations
- Users can still leave the toggle off and continue to diverge ledger vs tank. A gentle default-on behavior when volume goes negative would reduce misses.
- Location choice is free-form (any stage); acceptable, but a serving-stage nudge is still just informational.
- Finished Beer item dependency surfaces an error if the catalog is missing; acceptable fallback.

### Follow-up adjustments planned
- Auto-enable the serving-removal toggle whenever volume_change is negative (user can still opt out) to steer users toward syncing ledger with tank changes.

### Follow-up applied
- Auto-enable toggle on negative volume change and prefill a serving location when available.
- **Set Volume**: Same “log serving removal” option added to the Set Volume (snapshot) modal when the resulting delta is negative; validates before saving snapshot and creates CONSUME with note “Set volume …” for the decrease.
