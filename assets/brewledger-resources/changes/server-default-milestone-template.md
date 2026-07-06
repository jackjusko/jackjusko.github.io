# Server-Created Default Milestone Template

## Summary

The default milestone template for an organization is now created by the server at org registration (new orgs only). Clients no longer create it when none exist locally; they rely on sync to receive it.

## Changes

### Server ([server/server.js](server/server.js))

- **`buildDefaultMilestoneTemplateMilestones()`**: New helper that returns the default milestones array (11 user milestones—Knocked Out through Batch Closed—plus the forced "Production Complete" milestone with `is_system: true`). Each milestone gets a new UUID via `uuidv4()`.
- **register-org**: After inserting default categories (and before creating the session), the server inserts one row into `milestone_templates` with entity `{ id, org_id, name: 'Default', milestones, is_default: true, updated_at, version: 1 }`. Same table/column pattern as categories (`id`, `org_id`, `updated_at`, `server_updated_at`, `version`, `data`).

### Clients (mobile and console)

- **MilestoneTemplateRepository.ensureDefaultTemplate(orgId)** ([platforms/brewledger-app/src/repositories/MilestoneTemplateRepository.js](platforms/brewledger-app/src/repositories/MilestoneTemplateRepository.js), [platforms/console/src/repositories/MilestoneTemplateRepository.js](platforms/console/src/repositories/MilestoneTemplateRepository.js)):
  - When **zero** templates exist for the org: do not create a template; return `null`. Sync will eventually deliver the server-created default for new orgs.
  - When **at least one** template exists: unchanged—ensure one is marked `is_default` (prefer "Default" by name or first template), then return that template.

### Mobile SyncService

- No change. The existing post-apply deduplication (remove local templates that share a name with a server-applied template but have a different id) remains as a guard.

## Caller behavior

- **Migration** (`runMilestoneTemplatesMigration`, `migrateBatchIfNeeded`): After `ensureDefaultTemplate`, they call `getAll()` and use the first or "Default" template. If none exist (e.g. before first sync), they return early or leave the batch unchanged; after sync, templates are present and migration can run again if needed.
- **BatchRepository.create** / **getDefaultTemplateId**: If no template exists yet, they already fall back to in-memory default definitions or null; no change required.
- **BatchForm**: Loads `milestoneTemplates` via `getAll()`; empty list until sync populates.

## Documentation

- **analysis.md**: Milestone Templates → Sync section updated to state that the server creates the default at registration (new orgs only) and that clients no longer create the initial default.
