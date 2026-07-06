# Dashboard trial banner on desktop (Settings → Billing)

## Summary
Desktop console Dashboard already showed a trial-phase alert (days remaining) with an "Upgrade" button linking to `/settings?tab=billing`. The change makes the **entire banner** clickable so that any click on the alert navigates to Settings with the Billing tab active, matching user expectation ("redirect to the settings page, billing tab when clicked").

## Implementation
- **File**: `platforms/console/src/views/Dashboard.vue`
- **Change**: Replaced the outer `<div>` + inner `<router-link>` with a single `<router-link>` wrapping the full banner. Destination remains `/settings?tab=billing`. The "Upgrade" control is now a `<span>` styled as a button (no nested `<a>`). Added hover styles (`hover:bg-blue-100/80 dark:hover:bg-blue-900/30`) and `cursor-pointer` for affordance.

## Behavior
- When `trialDaysRemaining !== null && trialDaysRemaining >= 0 && isTrialing`, the banner is shown.
- Clicking anywhere on the banner (text, icon, or Upgrade pill) navigates to `/settings?tab=billing`.
- Settings view initializes `activeTab` from `route.query.tab` and keeps it in sync via a watcher; `tab=billing` is in `validTabIds`, so the Billing tab is shown.

## Edge cases considered
- **No nested links**: Single `<router-link>` only; inner CTA is `<span class="btn ...">` to avoid invalid HTML and duplicate focus targets.
- **Accessibility**: One focusable link for the whole card; screen readers announce one "Upgrade" or "link" to settings/billing; keyboard users can focus and activate once.
- **Router**: Vue Router handles `/settings?tab=billing`; Settings already supports `?tab=` for all tabs (see `getTabFromRoute()` and `watch(() => route.query.tab, ...)`).

## Second-pass review
- **Mobile parity**: Mobile Dashboard trial banner links to `/settings` (no tab); mobile Settings may not use tab query. Desktop-only change; no mobile file edits.
- **Session/trial state**: `trialDaysRemaining` and `isTrialing` are derived from `AuthService.getSession()` and `updateTrialFromSession()`; no change to that logic.
- **Lint**: No new lint issues; `router-link` and `span` are valid.
- **Focus/keyboard**: Single `router-link` gives one tab stop; Enter/Space activate and navigate. No focus trap or duplicate links.
- **Visual feedback**: `no-underline text-inherit` keeps text styling; hover background change confirms clickability of the whole card. `pointer-events-none` on the inner span is optional (click still reaches the link); kept for clarity that the pill is not a separate control.

## Documentation
- `analysis.md`: Added bullet under Desktop UI Design System: "Dashboard trial banner (console, 2026-02-19)" describing the alert and full-card link to Settings → Billing.
