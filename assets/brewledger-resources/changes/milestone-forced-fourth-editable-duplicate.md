# Feature analysis: Milestone template forced “Production Complete” bug fix

## Task
Fix the bug where the 4th (forced) milestone “Production Complete” was editable and adding a milestone after it caused duplicate forced milestones (finished → added → second finished).

## First iteration – implementation summary

### Repository (mobile + console)
- **`isForcedMilestone(m)`**: Returns true when `m.label === PRODUCTION_COMPLETE_LABEL` or `m.is_system === true`.
- **`ensureForcedLastMilestone(milestones)`**: Filters incoming list to **user milestones only** (`milestones.filter(m => !isForcedMilestone(m))`), then appends exactly one forced milestone. No longer checks “if last is Production Complete return as-is” — we always strip and re-append so payloads like `[A, B, C, Production Complete, D]` become `[A, B, C, D, Production Complete]`.
- **create/update**: Map incoming milestones to include `is_system: m.is_system || false` so stored data carries the flag. Same logic used for create and update.
- **Export**: `PRODUCTION_COMPLETE_LABEL` exported from both repos so forms can identify the forced milestone consistently.

### Form (mobile + console)
- **Load**: When mapping `t.milestones` into `form.milestones`, preserve `is_system: m.is_system || false`.
- **`isSystemMilestone(m)`**: Helper used in template and script: `m && (m.is_system === true || m.label === PRODUCTION_COMPLETE_LABEL)`.
- **Template**:
  - If `isSystemMilestone(m)`: render label and description as read-only text, plus “Required for TTB” badge; **no** inputs, **no** move/remove buttons.
  - Else: existing editable row (inputs, move up/down, remove).
- **addMilestone**: If the last milestone is the system one, **insert** at `form.milestones.length - 1`; otherwise push at end. Ensures the forced milestone always stays last.
- **removeMilestone / moveUp / moveDown**: Guard with `isSystemMilestone(form.milestones[idx])` and return early (no-op) for the forced milestone; UI already hides buttons for it.
- **save**: Include `is_system: m.is_system || false` in each milestone sent to the repository so the repo can filter correctly.

## Edge cases and integration (first pass)

1. **Existing templates with multiple “Production Complete” entries**: On next update, the repo strips all forced milestones and appends one. Result: single Production Complete at the end. No migration script required.
2. **New template (no milestones)**: Form starts with one empty user milestone; repo’s `ensureForcedLastMilestone` still receives it (create path). If we sent empty list, repo would return `[Production Complete]`; current form sends at least one row. Behavior unchanged.
3. **Template with only forced milestone**: If somehow the list were only `[Production Complete]`, after strip we’d have `[]`, then we’d append one → `[Production Complete]`. Form always has at least one user row for new template; for edit, load would show one system row read-only. “Add” would insert before it. OK.
4. **Sync**: Stored template always has `[...user, Production Complete]`. Other devices receive the same structure. No sync schema change; `is_system` is part of milestone object in existing JSON.
5. **Batch snapshot**: Batches snapshot `milestone_definitions` from the template at creation. Snapshot already includes whatever is in the template (including the forced milestone). No change to batch logic.
6. **Console vs mobile**: Both platforms use the same repository pattern and same form logic; only styling differs (e.g. “Required for TTB” badge class: blue on mobile, primary on console).

## Weak points / follow-ups (first iteration)

1. **Validation**: We do not enforce “at least one user milestone” in the repo. Form validation requires at least one milestone with a label; if the user deletes all user milestones and leaves only the read-only one, save still sends `[Production Complete]`. Repo would store `[Production Complete]`. That’s a single-milestone template (only the forced one). Allowing it is acceptable; if product wants to require at least one user milestone, add that in form validation or repo.
2. **Label match**: We identify forced by `label === PRODUCTION_COMPLETE_LABEL` or `is_system === true`. If an old record had a user milestone with label “Production Complete” and `is_system !== true`, we’d treat it as forced and strip it. Rare; acceptable for consistency.
3. **Second iteration**: After implementing any fixes for the above, re-read this document, expand the analysis with any new edge cases or integration points, then apply a second round of changes and document in analysis.md.

---

## Second iteration – validation and documentation

### Additional change (first-iteration follow-up)
- **Form validation (mobile + console)**: Require at least one **user** milestone with a label before save. Use `form.milestones.filter(m => m.label?.trim() && !isSystemMilestone(m)).length > 0`. Message: “Add at least one milestone with a label (besides the required ‘Production Complete’).” Prevents saving a template that has only the forced milestone (no user-defined milestones).

### Edge cases re-checked
- **New template**: Form starts with one empty user row; user must give it a label (or add more). Validation requires at least one user milestone with a label. OK.
- **Edit template**: If user deletes all user milestones and leaves only the read-only Production Complete, save is blocked by validation. OK.
- **Sync / batch snapshot**: No change; already covered in first iteration.
- **analysis.md**: Document forced-milestone behavior (strip-before-append, read-only in form, add-before-forced) in the Milestone Templates section so future changes stay consistent.
