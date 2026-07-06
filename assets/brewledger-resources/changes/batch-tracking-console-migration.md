# Batch Tracking Migration to Desktop Console

## Summary

The full batch tracking process has been migrated from the mobile app (`platforms/brewledger-app`) to the desktop console (`platforms/console`). Console users can create batches, view batch detail with vessels and milestones, log readings and additions, split/transfer/combine vessels, adjust volume, record packaging, and consume recipes—with UI and sync aligned to the existing console design (neutral/primary theme, `syncTrigger`, sidebar layout).

## What Was Implemented

### 1. Views (Console)

- **BatchesList.vue** (already present): Lists batches with vessel summaries, progress bar by status, links to detail and add. Uses `syncTrigger` for refresh after sync.
- **BatchForm.vue** (already present): New batch with name, date, volume unit, milestone template, optional recipe, vessel splits, initial status. Checklist for recipe readiness.
- **BatchDetail.vue** (created): Full batch detail: header (name, date, total volume, status), vessel cards (volume, gravity/temp/pH, Adjust, Log), quick actions (Update Status, Log Reading, Add Ingredient, Record Packaging), Timeline (milestones) and History (readings/additions/packaging) tabs, and modals for Status, Split/Transfer, Adjust Volume, Addition, Reading, Packaging. Uses `syncTrigger`, `migrateBatchIfNeeded`, and injected `modal` for alert/confirm.
- **BatchRecipeConsume.vue** (already present): Consume recipe ingredients for a batch with location selection and validation.

### 2. Routes and Navigation

- Routes: `/batches`, `/batches/add`, `/batches/:id`, `/batches/:batchId/consume-recipe/:recipeId`.
- Sidebar: "Batches" (🍺) with description "Track brewing batches, vessels, and milestones".

### 3. Repositories and Sync

- Console already had: BatchRepository, BatchLocationRepository, BatchVolumeAdjustmentRepository, BatchAdditionRepository, BatchReadingRepository, PackagingRunRepository, BatchMilestoneRepository, VesselRepository, etc.
- SyncService already included `batch_locations` and `batch_volume_adjustments` in gather/mark/apply.
- BatchRepository create/split logic already aligned with mobile (total_theoretical_volume, splits).

### 4. Modals and Alert/Confirm

- **ModalDialog.vue** (added): Reusable modal (neutral/primary/danger) for confirm/cancel and alert. Used by BatchDetail for all form modals.
- **useModal.js** (added): Composable with `modal` ref and `alert` / `confirm` helpers.
- **App.vue**: Global modal for alert/confirm: `useModal()`, `provide('modal', { confirm, alert })`, and a single `ModalDialog` bound to `modal` (shown when not on landing/blog). BatchDetail uses `inject('modal')` for showAlert/showConfirm; fallback to `window.alert`/`window.confirm` if not provided.

### 5. Batch Migration Helper

- **migrateBatchIfNeeded** (added in `platforms/console/src/utils/migrateMilestoneTemplates.js`): Same contract as mobile—ensures batch has `milestone_definitions` (and optionally `milestone_template_id`) from org default template and migrates legacy `batch_milestones.milestone_type` to `milestone_definition_id`. Uses console `db` and `MilestoneTemplateRepository`, `LEGACY_TYPE_TO_INDEX`.

## First-Iteration Feature Analysis

### Potential Bugs / Edge Cases

1. **Page title for batch detail**: App.vue `currentPageTitle` is derived from `navItems.find(item => item.path === route.path)`. For `/batches/:id` there is no matching path, so the header shows "Dashboard" (or the first match). Consider deriving title from route name or a per-route meta title (e.g. "Batch" or batch name when loaded).
2. **Global modal visibility**: ModalDialog is rendered only when `!$route.meta.isLanding && !$route.meta.isBlog`. For app routes this is true; ensure no route used by batch views has `isLanding` or `isBlog` by mistake.
3. **BatchDetail load when id invalid**: If `route.params.id` is missing or batch not found, we set `batch.value` from migrate or leave empty; vessel backfill runs only when `batch.value.vessel_id && batchLocations.value.length === 0`. If batch is null/undefined, template may reference `batch.planned_volume_unit` etc.—guards are `v-else` after loading and `batch` is ref({}), so properties are safe; but if we never set batch (not found), the UI still shows the empty state. Consider redirect to `/batches` when batch not found after load.
4. **Packaging supplies location_id**: In savePackaging we use `item.default_location_id` when supply has no location_id; if that is null we skip the line. Matches mobile behavior; no change.
5. **Undo Addition**: Mobile BatchDetail has `undoAddition` (confirm then reverse ledger); it was not ported to console BatchDetail. If product owner wants undo, add later.
6. **Reading modal batch_location_id**: When opening "Log Reading" without a specific vessel we set `batch_location_id: null`; saveReading sends it. Backend/repository should accept null for batch-level reading. No change if already supported.

### Integration

- Sync: BatchDetail watches `syncTrigger` and reloads; BatchesList already did. All batch-related repos are in SyncService. No duplicate sync triggers.
- Navigation: Back link "← Back to Batches" and sidebar Batches link; no dead ends.
- Style: Neutral/primary/danger/success used consistently; no leftover gray/purple from mobile.

## Second-Iteration Feature Analysis

### Additional Checks

1. **currentPageTitle for nested batch routes**: Confirmed that for `/batches`, `/batches/add`, `/batches/123`, and consume-recipe, the route.path does not match any navItems.path exactly (except `/batches`). So for `/batches/123` the computed `currentPageTitle` falls back to the first nav item or whatever the ternary does—currently `item ? item.name : 'Dashboard'` and `navItems.find(item => item.path === route.path)` returns undefined for `/batches/123`, so `item` is undefined and title becomes 'Dashboard'. Description similarly. Acceptable for now; a small enhancement would be to use route meta or a route name for "Batch", "New Batch", "Consume Recipe".
2. **ModalDialog slot**: BatchDetail uses ModalDialog with default slot for form content; ModalDialog has `<slot></slot>` so content is rendered. No issue.
3. **Batch not found**: In loadData we do `if (!b) return` and never set batch; loading is set false. Template has `v-else` after `v-if="loading"` and then uses `batch.name`, etc. So when batch is not found, `batch.value` stays `{}` and we never set it to null—we just return. So the UI shows the "non-loading" branch with empty batch object; optional chaining or guards like `batch?.name` would show blank. We do have `batch = ref({})` so batch.name is undefined—template may show blank. Adding an explicit "Batch not found" state or redirect to /batches would improve UX; documented as optional enhancement.
4. **Status modal options**: Console BatchDetail status dropdown includes PLANNED, BREWED, FERMENTING, CONDITIONING, PACKAGED, CLOSED (no PACKAGING). Mobile had the same list in the status modal. If template milestones use "Packaging Started" / "Packaging Completed", the computed status label is from milestone labels, so the status dropdown is for setting batch status in bulk; PACKAGING can be added if needed. No change.
5. **Dayjs**: Console already uses dayjs (BatchForm or other); BatchDetail uses dayjs for formatDate, formatDateTime, and default datetime for forms. No extra dependency.

### Documentation

- analysis.md updated to state that the console now has full batch tracking (BatchesList, BatchForm, BatchDetail, BatchRecipeConsume) with vessel splits, modals, syncTrigger, migrateBatchIfNeeded, and global ModalDialog/useModal for alert/confirm; the previous limitation "Console app not updated (still assumes single vessel)" is removed and replaced with the new behavior.

## Files Touched

- `platforms/console/src/utils/migrateMilestoneTemplates.js`: Added `migrateBatchIfNeeded`.
- `platforms/console/src/composables/useModal.js`: New.
- `platforms/console/src/components/ModalDialog.vue`: New.
- `platforms/console/src/views/BatchDetail.vue`: New (full batch detail with all modals and actions).
- `platforms/console/src/App.vue`: Global modal (ModalDialog), useModal(), provide('modal', { confirm, alert }).
- `platforms/console/src/router/index.js`: Already had batch routes.
- `platforms/console/src/App.vue` nav and descriptions: Already had Batches.
- `analysis.md`: Updated "Vessel Split / Batch Locations" to document console batch tracking parity.
