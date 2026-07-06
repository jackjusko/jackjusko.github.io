# Billing Mobile Cleanup – Feature Analysis (Iteration 1)

## Summary of Changes

1. **Billing.vue**
   - Fixed "Return to Dashboard" link from `/dashboard` to `/` (dashboard route is `/`).
   - When a successful purchase has been made (`success === true`), the buy-plan card is hidden; only the success state is shown.
   - Success and buy-plan states are full-screen, modern, and themed (neutral/success/danger/amber, rounded-xl, body-sm/md, consistent with Dashboard/App).

2. **Settings.vue**
   - "Manage Subscription" on native (Capacitor) opens the Stripe Customer Portal in the in-app browser (`@capacitor/browser`) instead of `window.location.href`.
   - On return (app becomes active again), we run `SyncService.sync()` and `refreshSession()` so subscription status is up to date; listener is added when opening the browser and removed after first sync on resume.

## Potential Issues & Edge Cases (First Pass)

### Billing.vue
- **Loading + success**: When deep link confirms subscription, we set `success = true` and `loading = false`. The template shows success state when `success` is true and does not show the loading spinner in that case. OK.
- **Web success flow**: On web, after confirm-subscription we call `router.replace('/')` so the user never sees the Billing success screen on web. The "Return to Dashboard" link is only needed for the native deep-link flow where we stay on Billing with success. OK.
- **isPaidSubscriber**: When `success` is true we also set `subscriptionStatus.value = 'active'`, so if the template ever fell through to the "main content" branch we would show "You're subscribed" and the link to Settings rather than the plan card. Because we use `v-else-if="success"` for the success screen, the buy section is never shown when success is true. OK.
- **Min height**: We use `min-h-[calc(100vh-8rem)]` to approximate full-screen within the app chrome (header + bottom nav). This may vary with safe areas; acceptable for consistency with other views.

### Settings.vue
- **appStateChange timing**: When we open the in-app browser, the app goes to background (`isActive: false`). When the user closes the browser, the app comes to foreground (`isActive: true`). We only run sync when `state.isActive` is true, so we don’t sync on the "going to background" event. OK.
- **Multiple returns**: We remove the listener after the first sync on resume, so we don’t keep syncing on every subsequent app focus. OK.
- **returnUrl on native**: We pass `new URL(API_BASE_URL).origin` so the Stripe portal’s return_url is the API origin (e.g. `https://api.example.com`) plus `/settings`. The user may then see that URL in the in-app browser after finishing in the portal. If the app is served from a different origin, that’s expected; the user closes the browser to return to the app. No change needed.
- **Listener cleanup**: We don’t remove the listener on component unmount if the user navigates away before closing the browser. The listener holds a reference to `appStateHandle` in closure; when the app later becomes active we remove it. If the component is unmounted, we could leave a dangling listener until next app resume. Consider storing the handle and removing it in `onUnmounted` to avoid any leak.

### Integration
- **Router**: Dashboard is at `/`; no route named `/dashboard` exists. The fix to use `/` is correct.
- **Capacitor**: Billing.vue already uses `Capacitor`, `Browser`, and `App` for checkout and deep linking; Settings.vue now uses the same stack for the portal. Consistent.

## Follow-up (Addressed in Second Pass)

1. **Settings.vue**: Added `onUnmounted` to remove the `appStateChange` listener (`portalAppStateHandle`) when the user navigates away while the in-app browser is open, avoiding a dangling listener. The handle is stored in a module-level variable so both the listener callback and `onUnmounted` can clear it.
2. **Billing.vue**: Optional aria-label on "Return to Dashboard" deferred; current implementation is sufficient.
3. **Billing.vue**: Success state uses flex centering and `min-h-[calc(100vh-8rem)]`; no change for narrow viewports.

## Second-Pass Review

- **Billing.vue**: Success screen shows only "Return to Dashboard" to `/`; no plan card. Error/expired banners appear only in the non-success branch. Loading spinner shows only when `loading && !success`. All branches use themed tokens (success/danger/amber/neutral, rounded-xl, body-sm/md). Implemented.
- **Settings.vue**: On native, portal opens in Capacitor Browser; `returnUrl` uses API origin so Stripe redirects to that origin + `/settings`. Listener removed on first app resume (sync + refresh) or on component unmount. Implemented.
- **Router**: Dashboard at `/` is documented in analysis; no `/dashboard` route. Confirmed.
- **Documentation**: analysis.md updated below to reflect Billing mobile UI and Settings in-app browser behavior.
