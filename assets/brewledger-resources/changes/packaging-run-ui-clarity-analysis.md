## Packaging Run UI Clarity — Iteration 1

### Context
- Recording a packaging run currently logs metadata and packaging supply consumption but does **not** move beer or adjust batch/vessel volumes.
- UI shows source/destination locations, implying a transfer that does not occur.
- Users expect a packaging action to move beer into finished/serving locations.

### Pain Points / Risks
- Misleading affordance: source/destination pickers suggest inventory movement.
- Hidden behavior: supply consumption is the only material effect; beer inventory remains unchanged.
- Reporting mismatch risk: users may assume on-hand updates after packaging and miss doing a transfer/volume adjust.
- Terminology gap: “Record Packaging Run” lacks a reminder that it’s a log-only action.

### Plan for Iteration 1
- Add concise helper copy in the modal to state that this action logs packaging + supplies only and does **not** move beer/volume.
- Label source/destination as “reference only” so intent is explicit.
- Add a short tip reminding users to use transfers/volume adjustments for moving beer.

### Open Questions (deferred)
- Should packaging automatically create beer transfers/volume adjustments?
- Should destination be required when packaging finished goods?

## Iteration 2 Review & Follow-ups

### What changed in iteration 1
- Added a “logging only” info block to the modal.
- Relabeled source/destination as “reference only” and clarified helper text.

### Remaining risks
- Users may still miss the call to action for moving beer, even with the banner.
- Destination hint doesn’t direct where to perform the move (transfer vs. volume set).

### Plan for iteration 2
- Add a succinct tip near the location selectors pointing to the Transfer/Set Volume actions for actual beer movement.
- Keep wording lightweight so the modal stays scannable.

