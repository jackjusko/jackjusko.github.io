# Milestone Templates Duplicate on Login – Fix

## Problem

On the mobile app, when a user logged in (especially on a new device or after clearing data), milestone templates for the organization could appear duplicated—e.g. two "Default" templates in the list.

## Root Cause

1. **Server does not create default milestone templates.** At org registration (`/api/auth/register-org`), the server only creates the org, admin user, default categories (including Finished Beer), and session. It does **not** insert any rows into `milestone_templates`. So the server never seeds a "Default" template for new orgs.

2. **Client creates the default.** The first time a client needs templates (migration or opening Batch Form), `MilestoneTemplateRepository.ensureDefaultTemplate(orgId)` runs. If the local DB has **no** templates for that org, it creates a new "Default" template with a **client-generated UUID** and adds it to IndexedDB.

3. **Race on login.** After login, the mobile app runs `runMilestoneTemplatesMigration()` in an App.vue watch (immediate) when `session.orgId` is set. That calls `ensureDefaultTemplate(orgId)`. If the local DB is empty (new device, reinstall, etc.), a new "Default" template is created with UUID-A. Later, sync runs and the server returns the org’s existing templates (e.g. "Default" with UUID-B from a previous device). `applyRemoteUpsert` uses `db.put(template)`, which upserts by primary key: the server template (UUID-B) is stored, but the locally created template (UUID-A) is a different row. So the DB ends up with two rows—both named "Default"—and the UI shows duplicates.

## Fix

In the mobile app’s `SyncService.applyServerUpdates`, after applying `updates.milestone_templates`, we **deduplicate by name**: for the current org, any local template that has the same `name` as a template we just received from the server but a **different** `id` is removed. That removes the locally-created duplicate while keeping the server-authoritative copy.

- **File:** `platforms/brewledger-app/src/services/SyncService.js`
- **Logic:** If `updates.milestone_templates` is non-empty, get current session `orgId`, build sets of applied `id`s and `name`s, then for each local milestone template in that org, if its name is in the applied names set and its id is not in the applied ids set, delete it.

## Verification

- Existing org, login on device with empty local DB: migration creates one local "Default"; sync applies server "Default"; dedupe step deletes the local one → single "Default" in list.
- New org: server has 0 templates; client creates "Default" and syncs it up; no server templates in update → dedupe step does nothing.
- Console: same server behavior; console also runs migration but typically has already synced; if console ever had the same race, the same dedupe could be added to console SyncService for consistency (optional).

## Analysis.md

- Documented in analysis.md under Milestone Templates System (Sync): duplicate-on-login fix and that server does not create default milestone templates at registration.
