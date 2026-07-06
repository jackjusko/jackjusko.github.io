## Iteration 1 – Analysis
- User bug: new milestones append after the forced `Production Complete` item, and move-down lets users place items after it. UI must always keep the forced milestone last so batches snapshot the intended order without confusion.
- Current guardrails: repository strips/append forced milestone on save, but the form still shows the wrong order, inviting mistakes before save.
- Risks:
  - Existing templates loaded into the form might have the forced milestone missing or not last if data was edited elsewhere; UI should normalize before showing.
  - Move controls can still swap into the forced slot.
  - Add flow needs to insert before the forced entry rather than after it.
- Planned fixes:
  - Insert new milestones directly before the forced one.
  - Block moving a milestone down if the next entry is the forced milestone.
  - Normalize loaded templates in the form so the forced milestone is present and last, even for older data.
- Test passes to run manually: create/edit template, add milestone near the end, attempt move-down past `Production Complete`, and verify save keeps order.

## Iteration 2 – Analysis
- Re-reviewed the form flow with the new guards. Confirmed add/move logic now respects the forced milestone slot, but normalized loading needed to be resilient to older templates missing or misplacing the forced row.
- Tightened normalization to always rebuild a forced milestone and keep it last, caching the located forced row to avoid repeated scans and ensure description/id consistency.
- No additional UI controls needed; save path already reassigns sort order by rendered index, keeping the forced milestone last in persisted data.
- Manual checks to perform: open an existing template with missing/misordered forced milestone (should auto-fix), add milestones and ensure they land before `Production Complete`, attempt move-down past forced (blocked), and save to confirm ordering persists.
