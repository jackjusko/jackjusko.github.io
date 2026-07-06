## Remove Unintegrated UI (Iteration 1)

### Goal
Remove console UI that advertises or surfaces integrations that are not actually available, so users are not shown dead ends.

### Scope Observed
- `platforms/console/src/views/Settings.vue` has an “Accounting (QBO)” tab with full QuickBooks connection, mapping, and push flows plus the supporting tab metadata and watchers.
- Marketing variants `Landing_A.vue`, `Landing_B.vue`, and `Landing_C.vue` heavily promote “QuickBooks sync” despite there being no production-ready QuickBooks integration available.
- `platforms/console/src/services/QBOService.js` is solely for these UI surfaces.

### Risks / Edge Cases
- Route query `?tab=accounting` could become invalid once the tab is removed; need to ensure the tab list/validator no longer references it.
- Any lingering imports of `ItemRepository`/`QBOService` in Settings would break the build after removal.
- Removing marketing claims must not leave broken anchors or layout gaps in landing variants.
- Ensure removal does not affect other settings tabs (locations, milestones, API) or the general layout styling.

### Plan
1) Strip the Accounting/QBO tab UI and supporting state/actions from `Settings.vue`, removing the tab entry and accounting-specific watchers. Make the tab routing guard resilient without the accounting id.  
2) Delete `QBOService.js` since no callers should remain.  
3) Remove “QuickBooks sync” marketing blocks/links from `Landing_A/B/C.vue`, smoothing any spacing or CTA replacements to keep layouts intact.  
4) Re-run a second iteration after implementation to confirm no residual references or regressions.

## Iteration 2 Review

### Findings
- Accounting/QBO tab and helpers are fully removed from `Settings.vue`; the tab list now ignores `accounting`, and the route guard defaults cleanly to `general` when unknown tabs are requested.
- `QBOService.js` is deleted and no remaining imports reference it. No `QBO`/`qbo` strings appear in the console UI code.
- Landing variants A/B/C no longer claim QuickBooks sync; CTA anchors were retitled to “Finance” where needed, and finance messaging now speaks to exports/reporting without promising an integration.

### Follow-up Actions
- None required beyond keeping backend QBO endpoints hidden; current UI no longer exposes or markets the integration.
