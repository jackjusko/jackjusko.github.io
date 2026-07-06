# BrewLedger Orphaned Code Audit

**Date:** March 3, 2025  
**Scope:** `platforms/console`, `platforms/brewledger-app`, `server`

---

## 1. Unused Imports

| File | Unused Import | Notes |
|------|---------------|-------|
| `platforms/console/src/views/Serving.vue` | `getBeerItemForServingLocation` | Only `getCurrentBeerAtLocation` is used from ServingOccupancyService |

---

## 2. Unused / Orphaned Components

### Console (`platforms/console/src/components/`)

| Component | Status | Notes |
|----------|--------|-------|
| **MilestonePieChart.vue** | **ORPHANED** | Removed from Dashboard (2026-03); not imported anywhere |
| BlogSidebar.vue | Used | Imported in App.vue |
| LedgerFeaturedBadge.vue | Used | App.vue, LedgerAbout.vue, BlogPost.vue, BlogSidebar.vue |
| LedgerCtaSidebar.vue | Used | App.vue |
| ModalDialog.vue | Used | App.vue, BatchDetail.vue |
| TTBFormPreview.vue | Used | TTBForm.vue |
| BreweryInfoForm.vue | Used | Settings.vue |
| MarkdownRenderer.vue | Used | AIAssistant.vue, BlogPost.vue |
| TutorialShell.vue | Used | App.vue |
| TutorialProgressBar.vue | Used | TutorialShell.vue |
| TutorialStepCard.vue | Used | TutorialShell.vue |

### BrewLedger App (`platforms/brewledger-app/src/components/`)

| Component | Status | Notes |
|----------|--------|-------|
| **HelloWorld.vue** | **ORPHANED** | Not imported anywhere; App.vue uses BottomNav and ModalDialog only |
| MilestonePieChart.vue | **ORPHANED** | Not imported anywhere |
| BottomNav.vue | Used | App.vue |
| ModalDialog.vue | Used | App.vue |

---

## 3. Unused Routes / Stale Route References

### Commented-Out Blog Routes (Console)

Router (`platforms/console/src/router/index.js`) has these routes commented out:

- `/blog` → BlogList
- `/blog/about` → LedgerAbout
- `/blog/subscribe` → LedgerSubscribe
- `/blog/section/:sectionKey` → LedgerSection
- `/blog/:slug` → BlogPost

**Impact:** App.vue still has a blog layout (`$route.meta.isBlog`) and imports BlogSidebar, LedgerCtaSidebar, LedgerFeaturedBadge. Because these routes are disabled, that layout is never used. Blog views (BlogList, LedgerAbout, LedgerSubscribe, LedgerSection, BlogPost) exist but are unreachable.

### Alternate Landing Pages (Console)

| View | Status | Notes |
|------|--------|-------|
| **Landing_A.vue** | **ORPHANED** | Not in router; router uses Landing.vue |
| **Landing_B.vue** | **ORPHANED** | Not in router |
| **Landing_C.vue** | **ORPHANED** | Not in router |

### Deleted View Reference

| View | Status | Notes |
|------|--------|-------|
| **Racking.vue** | **DELETED** | Removed per git status; no remaining imports in router or App.vue |

---

## 4. Dead Code / Unused Functions

### LedgerRepository

| Method | Status | Notes |
|--------|--------|-------|
| **getOnhandByLocation** | **UNUSED** | Defined in both console and brewledger-app LedgerRepository; never called externally |

### ParLevelRepository

| Export | Status | Notes |
|--------|--------|-------|
| **isGlobalParLevel** | **UNUSED** | Exported but never imported or called |

---

## 5. Orphaned Repositories

| Repository | Platform | Notes |
|------------|----------|-------|
| **ItemTemplateRepository** | Console | Not imported anywhere. Server exposes `/api/item-templates`, `/api/item-templates/:id`, `/api/item-templates/import` but no client code calls them. |

---

## 6. API Endpoints (Server) Never Called from Client

| Endpoint | Method | Notes |
|----------|--------|-------|
| `/api/item-templates` | GET | No client usage |
| `/api/item-templates/:id` | GET | No client usage |
| `/api/item-templates/import` | POST | No client usage |

---

## 7. Repository Methods Never Invoked

| Repository | Method | Notes |
|------------|--------|-------|
| ItemTemplateRepository | search, getAll, getById, importToOrg | Entire repository is orphaned |
| LedgerRepository | getOnhandByLocation | Defined but never called |
| ParLevelRepository | isGlobalParLevel | Exported but never used |

---

## 8. Unused Exports

| File | Export | Notes |
|------|--------|-------|
| `ParLevelRepository.js` | isGlobalParLevel | No consumers |
| `LedgerRepository.js` | getOnhandByLocation | Internal-only; not used by callers |

---

## 9. Stale References

| Reference | Location | Issue |
|-----------|----------|-------|
| **Racking.vue** | N/A | File deleted; no remaining references |
| **Blog routes** | `platforms/console/src/App.vue` | Blog layout and components (BlogSidebar, LedgerCtaSidebar, LedgerFeaturedBadge) are wired for `$route.meta.isBlog`, but blog routes are commented out, so this layout is unreachable |
| **Landing page href** | `platforms/console/src/views/Landing.vue` | `<a href="/blog">` points to a route that does not exist (blog routes commented out) |

---

## Summary Table

| Category | Count | Items |
|----------|-------|-------|
| Orphaned components | 4 | MilestonePieChart (console + app), HelloWorld, alternate Landings (A/B/C) |
| Unreachable views | 5 | BlogList, LedgerAbout, LedgerSubscribe, LedgerSection, BlogPost |
| Orphaned repository | 1 | ItemTemplateRepository |
| Unused repository methods | 2 | getOnhandByLocation, isGlobalParLevel |
| Unused API endpoints | 3 | item-templates (GET, GET/:id, POST import) |
| Stale/dead layout | 1 | Blog layout in App.vue (routes commented out) |

---

## Recommendations

1. **Remove orphaned components:** HelloWorld.vue, MilestonePieChart.vue (both platforms), Landing_A.vue, Landing_B.vue, Landing_C.vue.
2. **Resolve blog routes:** Either re-enable blog routes or remove the blog layout and related components (BlogSidebar, LedgerCtaSidebar, blog views).
3. **Remove ItemTemplateRepository:** Delete the file and consider deprecating or removing the item-templates API if no future use is planned.
4. **Clean up exports:** Remove or use `isGlobalParLevel` and `getOnhandByLocation` as appropriate.
5. **Fix Landing.vue:** Change `/blog` link to a valid target or remove it if the blog is deprecated.
