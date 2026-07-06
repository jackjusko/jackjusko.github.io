# Billing Desktop Migration – Feature Analysis

## Summary
Billing has been moved from the mobile app (`platforms/brewledger-app`) to the desktop console. The console exposes a **Billing** tab under Settings with Stripe checkout and Customer Portal. The mobile app no longer has a Billing view; it shows a message and link to manage billing on the desktop.

## First-Pass Analysis

### Implemented Changes
- **Console**
  - New **Billing** tab in `platforms/console/src/views/Settings.vue`: status card (plan, status pill, trial info), Subscribe (checkout) and Manage subscription / Billing history (portal) actions, error/success banners, loading states.
  - Routes `/billing/success` and `/billing/cancel` in console router; both use `BillingRedirect.vue` to redirect to `/settings?tab=billing` (success preserves `session_id`).
  - Router guard: expired/cancelled users are sent to `/settings?tab=billing`; `/billing/*` is allowed so return from Stripe works.
  - On load with `?tab=billing&session_id=...`, Settings calls `confirm-subscription`, updates session, syncs, then replaces query; `billingConfirmAttempted` prevents double confirmation.
- **Mobile**
  - Billing route and `Billing.vue` removed. Router guard sends expired/cancelled users to `/settings`.
  - Settings subscription section: single “Billing is managed on the desktop app” card with link to `https://getbrewledger.com`. Removed Manage Subscription, Subscribe/Upgrade, Billing History, Cancel Plan and all billing API/portal/deeplink logic.
  - Dashboard trial banner “Upgrade” link points to `/settings` instead of `/billing`.
- **Server**
  - No code changes. Checkout success/cancel URLs use client `returnUrl`; console sends `window.location.origin`, so success/cancel land on console `/billing/success` and `/billing/cancel`.

### Risks and Edge Cases (First Pass)
1. **Console URL on mobile**: Mobile Settings links to hardcoded `https://getbrewledger.com`. If the console is deployed elsewhere (e.g. subpath or different domain), the link is wrong. *Mitigation*: Document; consider a config value or build-time env for console URL.
2. **Session refresh after login**: Console session (plan/status) comes from localStorage populated at login. After confirm-subscription we call `setSession` and `refreshSession`; we do not re-fetch from server. If the auth/verify endpoint returns updated subscription, we could refresh after confirm. *Current behavior is sufficient*: we set plan/status from confirm response.
3. **Double confirm**: Guarded by `billingConfirmAttempted` in Settings; both onMounted and watch can trigger confirm, only the first runs.
4. **Portal return on console**: After Customer Portal, Stripe redirects to `returnUrl` (we pass origin). For console that is the same origin; the user lands on `/settings` (server default for portal return path when `inAppBrowser: false`). So no dedicated portal-return route needed on console; user may need to refresh or we could add a “Return URL” in Stripe Dashboard pointing to `/settings?tab=billing` for clarity.
5. **Mobile tests**: `platforms/brewledger-app/src/tests/backend/billing.spec.js` exercises server billing endpoints; no mobile UI tests found. No change to server contracts; mobile removal is UI-only.

### Follow-ups From First Pass
- None required for MVP. Console URL on mobile can be made configurable in a later change.

## Second-Pass Analysis

### Additional Review
- **getTabFromRoute() with session_id**: If user lands on `/settings?tab=billing&session_id=cs_xxx` (e.g. direct paste or refresh), `getTabFromRoute()` returns `billing`, so `activeTab` is billing and onMounted runs confirm. Correct.
- **BillingRedirect and guard**: Expired user completes checkout; Stripe redirects to `origin/billing/success?session_id=...`. Guard allows `to.path.startsWith('/billing/')`, so the request is not redirected. BillingRedirect then does `router.replace` to `/settings?tab=billing&session_id=...`. Guard runs again; path is `/settings`, so allowed. Good.
- **Login session data**: Console Login does not explicitly store `subscriptionPlan` / `subscriptionStatus` from the auth response; they may be set by the auth endpoint or by a separate session endpoint. Confirm-subscription flow updates localStorage via `setSession`, so after checkout the UI shows Active without a full page reload.
- **hasStripeCustomer**: Portal button is shown when status is active, past_due, or cancelled. New users (trialing, no Stripe customer) still see only the Subscribe button; if they had a customer id from a previous subscription, portal would work. Correct.
- **Cancel URL**: Server uses `cancel_url: ${baseUrl}/billing/cancel`. Console has that route and redirects to `/settings?tab=billing` (no session_id). User sees billing tab; no confirmation needed. Good.

### Second-Pass Follow-ups
- None. Implementation is consistent; documentation and analysis.md update complete the migration.

## Post–Second-Pass Fixes (Edge Cases & Integration)

### Issues Found and Fixed
1. **Double confirm from `watch(activeTab)`**: The `watch(activeTab)` callback called `confirmBillingSession(route.query.session_id)` when switching to the billing tab without checking `billingConfirmAttempted`, so confirm could run twice (e.g. with the query watch). **Fix**: Guard with `!billingConfirmAttempted.value` and set `billingConfirmAttempted.value = true` before calling.
2. **No retry after confirm failure**: After a failed confirm (network or 400), `billingConfirmAttempted` stayed true, so refresh or re-opening the tab did not retry. **Fix**: Set `billingConfirmAttempted.value = false` in the `else` and `catch` branches of `confirmBillingSession` so the user can retry.
3. **General tab subscription pill**: The General tab showed only Active / Trial / Inactive; `past_due` was not shown. **Fix**: Added "Past due" to the General tab subscription status pill (label and warning styling), consistent with the Billing tab.

### Edge Cases Documented (No Code Change)
- **Token expiry on return from Stripe**: If the user stays on Stripe Checkout long enough for the JWT to expire, Stripe redirects to `/billing/success?session_id=...` and the auth guard sends them to login; the `session_id` is then lost. Recovery would require preserving the return URL across login (future enhancement).
- **Portal return URL**: Console sends `returnUrl` (origin only); server builds portal `return_url` as `origin + '/settings'`. User returns to Settings on the General tab; they can open the Billing tab to see updated status. Optional: pass `returnUrl` with `?tab=billing` if the server or client is extended to support it.

## Pass 3 – Additional Edge Cases & Fixes

### Issues Found and Fixed
1. **Mobile: Old /billing URLs**: After removing the Billing view, navigating to `/billing`, `/billing/success`, or `/billing/cancel` (e.g. bookmarks, old deep links) would match no route and show a blank or broken view. **Fix**: Added redirect routes in the mobile router: `{ path: '/billing', redirect: '/settings' }`, and same for `/billing/success` and `/billing/cancel`, so legacy URLs land on Settings.
2. **Console: Billing buttons with no session**: If session were missing or token cleared (e.g. logout in another tab), Subscribe and Manage subscription could still be clicked and would send `Bearer undefined`. **Fix**: Disable both billing action buttons when `!session?.token` so the UI fails safe and avoids 401s.

### Pass 3 Notes
- Mobile redirects run before the guard; expired users hitting `/billing` are redirected to `/settings` and then the guard keeps them there. Active users with an old `/billing/success?session_id=...` bookmark land on `/settings` without confirming (mobile no longer performs checkout; acceptable).

## Pass 4 – Final Verification

### Verification
- Mobile redirect routes are in place; order of routes is correct (redirects before specific routes).
- Console billing buttons use `session?.token`; in the template `session` is the unwrapped ref from useSession, so the check is correct.
- No linter errors on modified files.
- No further code changes; edge cases from passes 1–3 are covered.
