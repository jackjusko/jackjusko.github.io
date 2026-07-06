# Milestone Templates System - Feature Analysis

## Overview

The Milestone Templates System replaces preset milestones with hide/show by org-level milestone templates. Organizations manage named milestone checklists; batches receive a snapshot of a template at creation. Users can add, remove, reorder, and edit milestone labels/descriptions. Status equals the last completed milestone's label. Hiding has been removed.

## Implemented Changes

### 1. Schema & Repositories

- **Server `init_db.js`**: Added `createEntityTable('milestone_templates')`.
- **Client `db.js`** (Dexie v13): Added `milestone_templates` store; updated `batch_milestones` index from `milestone_type` to `milestone_definition_id`.
- **MilestoneTemplateRepository**: CRUD, `ensureDefaultTemplate()`, `DEFAULT_MILESTONES` (11 items), `LEGACY_TYPE_TO_INDEX` for migration.
- **BatchMilestoneRepository**: Removed DEFINITIONS/hide logic; `getDefinitionsForBatch()`, `ensure(batchId, milestoneDefinitionId)`, `initForBatch(batchId, definitions, initialStatus)`; migration helpers.
- **BatchRepository**: Removed hideMilestone/showMilestone/getHiddenMilestones; template snapshot on create; `getDefaultTemplateId()`.

### 2. Sync & Server

- **SyncService**: Added `milestone_templates` to gather, send, apply, markAsSynced (mobile and console).
- **Server validateEntity**: `milestone_template` (name, milestones array), `batch_milestone` (batch_id + milestone_definition_id OR milestone_type), `batch` (milestone_definitions optional array).
- **Server sync**: processChange and fetchUpdates for `milestone_templates`.

### 3. Migration

- **migrateMilestoneTemplates.js** (mobile and console): `runMilestoneTemplatesMigration()` on app load when session exists; `migrateBatchIfNeeded(batch)` in BatchDetail loadData.
- Migration: ensure Default template per org; backfill `batch.milestone_definitions`; convert `batch_milestones.milestone_type` → `milestone_definition_id`.

### 4. UI

- **MilestoneTemplates.vue** & **MilestoneTemplateForm.vue**: List, create, edit templates (add/remove/reorder milestones).
- **BatchForm**: Milestone template selector.
- **BatchDetail**: Uses `batch.milestone_definitions`; removed hide UI; toggle by `milestone_definition_id`; status = last completed milestone label.
- **MilestonePieChart** (console): Uses milestone definitions; removed hide/unhide; simplified props.
- **Dashboard** (console): Active batches = last milestone not completed; removed hide handlers.
- **Settings**: Link to Milestone Templates (mobile and console).

### 5. Status Logic

- Status = label of last completed milestone (by sort_order).
- If none completed: "PLANNED".
- Active batch = not all milestones completed.

---

## First-Iteration Review: Potential Weak Points

### 1. Console Batch Route Missing

- **Issue**: Dashboard `handleSectorClick` navigates to `/batches/${batchId}` but console router may not have this route.
- **Risk**: 404 or blank page when clicking pie chart sector.
- **Recommendation**: Add `/batches/:id` route to console router with BatchDetail view, or change sector click to do nothing / show a toast until route exists.

### 2. Legacy Backfill in BatchDetail

- **Issue**: Legacy backfill in BatchDetail uses hardcoded indices (defs[0], defs[2], defs[8]) for KNOCKOUT, FERMENTATION_START, PACKAGING_COMPLETE. Custom templates may have different order.
- **Mitigation**: Legacy backfill runs only when batch has no milestone_definitions and status is non-PLANNED. After migration, most batches will have milestone_definitions. Custom templates created after migration will have defs from the start.
- **Edge case**: If user creates a batch with a custom template that has fewer than 9 milestones, defs[8] would be undefined; the `&& defs[8]` check prevents errors.

### 3. Default Template Seeding

- **Issue**: Default template is created per-org on first sync or migration. If multiple devices create default templates concurrently, we could get duplicates.
- **Mitigation**: `ensureDefaultTemplate` checks for existing templates before creating. First device to run wins. Sync will propagate the default; other devices may create a duplicate locally before sync, but last-write-wins on sync could resolve. Duplicate defaults are low-risk (same content).

### 4. Batch Create Without Template

- **Issue**: If no templates exist and `getDefaultTemplateId()` fails, BatchRepository.create uses `DEFAULT_MILESTONES` from repository. Those use `uuidv4()` at module load for ids – same ids on every call could cause collisions if two batches created before any template exists.
- **Mitigation**: `ensureDefaultTemplate` runs before `getDefaultTemplateId()`, so a Default template should exist. If org has no templates, we create one. The `DEFAULT_MILESTONES.map(m => ({ ...m, id: uuidv4() }))` fallback generates new ids per batch.

### 5. Status Modal Mapping

- **Issue**: Status modal maps PLANNED/BREWED/FERMENTING/etc. to milestone count (e.g. BREWED=1, FERMENTING=3). Custom templates with different milestone counts may not align.
- **Mitigation**: The mapping is a best-effort for the default workflow. Users with custom templates may prefer toggling milestones directly. For PLANNED, we uncheck all milestones.

### 6. Empty Milestone Definitions

- **Issue**: If `batch.milestone_definitions` is empty (e.g. corrupted or edge case), BatchDetail fallback uses `MilestoneTemplateRepository.DEFAULT_MILESTONES` with `m.id || `def-${i}``. Those ids won't match any `batch_milestones` records.
- **Mitigation**: Migration backfills milestone_definitions. `migrateBatchIfNeeded` runs on BatchDetail load. Fallback is for extreme edge cases; toggle would create milestones with those ids.

### 7. Server-Side Migration

- **Issue**: Server has no migration script. Existing batches in SQLite may lack `milestone_definitions`. Clients migrating locally will push updated batches to server; server accepts them. Batches that never get opened by a client with new code won't be migrated on server.
- **Mitigation**: Acceptable – client is source of truth for migration. When client opens a batch, migration runs and sync pushes the updated batch.

### 8. Tests

- **Issue**: BatchMilestoneRepository and BatchRepository tests likely still expect `milestone_type`, `hideMilestone`, `getHiddenMilestones`, DEFINITIONS.
- **Recommendation**: Update tests to use `milestone_definition_id`, remove hide-related tests, add MilestoneTemplateRepository tests.

### 9. BatchesList / Other Views

- **Issue**: BatchesList and other views that display batch status may expect enum values (PLANNED, BREWED, etc.). Status is now freeform (milestone labels).
- **Mitigation**: `getStatusClass` in BatchDetail maps known labels to CSS classes. Other views (BatchesList, Dashboard) display status as-is. "Batch Closed" and other labels will render; custom labels get default styling.

### 10. Sync Order

- **Issue**: Migration creates/updates batches and batch_milestones. If sync runs before migration completes, we might push stale data.
- **Mitigation**: Migration runs when session exists; sync typically runs after. No strict ordering guarantee, but migration is synchronous per batch, so by the time user interacts, migration should be done.

---

## Second-Iteration Review: Additional Considerations

### 11. Console DB Version History

- **Issue**: Console db.js added v11, v12, v13. If console had different version history (e.g. only v10), upgrade path should work. If console already had v11/v12 with different store definitions, Dexie upgrade could fail.
- **Mitigation**: Console db as inspected only had v10. v11–v13 added sequentially. If production console has different history, may need manual migration.

### 12. Delete Template When In Use

- **Issue**: Deleting a template doesn't affect batches (they store snapshots). Block delete only when it's the org default and the only template.
- **Current**: Block delete when `templates.length <= 1`. Allow delete when multiple templates exist.
- **Edge case**: If user deletes "Default" and it was used by many batches, those batches keep their snapshots. No data loss.

### 13. Template Name Uniqueness

- **Issue**: No uniqueness constraint on template name per org. User could create multiple "Default" templates.
- **Mitigation**: `getDefaultTemplateId` uses `find(t => t.name === 'Default') || templates[0]`. Multiple Defaults would pick first. Low priority.

### 14. Milestone Definition ID Stability

- **Issue**: When editing a template, milestone ids are preserved. When snapshotting to batch, we copy ids. If user edits template and changes a milestone's label, existing batches keep old label (snapshot).
- **Correct behavior**: Snapshots are immutable per batch. Template edits don't affect existing batches.

### 15. Status Display in BatchesList

- **Issue**: BatchesList shows batch status. With dynamic labels ("Knocked Out", "Fermentation Started"), the status badge may need `getStatusClass` mapping. If BatchesList doesn't have this mapping, custom labels get default/gray style.
- **Recommendation**: Add status-to-class mapping in BatchesList if it displays status badges, or use a shared utility.

---

## Documentation Updates

- **analysis.md**: Replaced "Milestone Pie Chart & Hiding Feature" with "Milestone Templates System" section. Updated Inventory Management limitations line to reference new system.
- **Feature analysis**: This document in `changes/milestone-templates-system-analysis.md`.
