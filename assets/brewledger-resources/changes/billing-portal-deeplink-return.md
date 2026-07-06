# Billing Portal Return Deeplink – Feature Analysis (Iteration 1)

## Summary of Changes

When the user clicks "Manage Subscription" (or "Billing History") in the brewledger app on native (Capacitor), the Stripe Customer Portal opens in the in-app browser. Previously, the portal’s "Return to BrewLedger" button sent the user to the API origin + `/settings` (e.g. `https://getbrewledger.com/settings`), which loaded the web app inside the in-app browser instead of opening the native app. The user had to manually close the browser to get back to the app.

### Implemented Fix

1. **Server (`server/server.js`)**
   - Added `GET /api/billing/portal-return`: returns an HTML page that immediately redirects to `brewledger://settings`, mirroring the existing `success-redirect` pattern used for checkout.
   - Updated `POST /api/billing/create-portal-session`: accepts optional `inAppBrowser` in the body. When `inAppBrowser` is true, the Stripe portal `return_url` is set to `${baseUrl}/api/billing/portal-return` instead of `${baseUrl}/settings`. Thus, when the user clicks "Return to BrewLedger" in the portal, the in-app browser loads the redirect page, which sends it to the app via the deep link.

2. **Settings.vue**
   - When calling `create-portal-session`, the app now sends `inAppBrowser: isNative` (where `isNative = Capacitor.isNativePlatform()`), so the server uses the portal-return URL on native.

3. **App.vue**
   - On native, on mount: if the app was launched with `brewledger://settings` (e.g. cold start from portal return), we call `Browser.close()`, navigate to `/settings` if not already there, and `refreshSession()`.
   - On native, we register an `App.addListener('appUrlOpen', ...)` for the lifetime of the app. When the URL is `brewledger://settings`, we do the same: close browser, push `/settings` if needed, refresh session. This handles the case where the app was in background and the user clicked "Return to BrewLedger" in the portal.
   - Listener is removed in `onUnmounted` to avoid leaks.

## Potential Issues & Edge Cases (First Pass)

### Server
- **Portal return path**: `/api/billing/portal-return` is a GET endpoint with no auth. It only returns a redirect to `brewledger://settings`. No sensitive data; acceptable to leave unauthenticated (same as `success-redirect`).
- **baseUrl for native**: When `inAppBrowser` is true, the client sends `returnUrl` as the API origin (e.g. `https://getbrewledger.com`). So `portalReturnUrl` becomes `https://getbrewledger.com/api/billing/portal-return`. Stripe redirects the user’s browser to that URL. Correct.

### Settings.vue
- **Backward compatibility**: If an old client does not send `inAppBrowser`, the server uses `return_url: ${baseUrl}/settings` (web behavior). No change for web or old native clients beyond the improved native flow when the new flag is sent.

### App.vue
- **getLaunchUrl()**: Only fires when the app is launched via the URL (cold start). If the user had the app in background and returns via the portal, the OS brings the app to foreground and `appUrlOpen` fires; we don’t rely on getLaunchUrl for that. OK.
- **Browser.close()**: If the in-app browser was not open (e.g. user closed it manually before clicking Return, or opened the app via another path), calling `Browser.close()` is a no-op or safe. Capacitor docs indicate it’s safe to call when no browser is open.
- **Router push**: If the user is already on `/settings`, `router.push('/settings')` is redundant but harmless.
- **Listener lifetime**: We add one listener in App.vue onMounted and remove it in onUnmounted. App.vue is the root; it is only unmounted when the app is destroyed. So the listener stays for the full app session. We do not remove it after handling a single `brewledger://settings` so that repeated "Manage Subscription" → "Return to BrewLedger" flows continue to work.
- **Auth pages**: If the user is on login/register when the app is opened via `brewledger://settings` (e.g. session expired), we still close the browser and push `/settings`. The router guard will redirect unauthenticated users to login. So the user may land on login after "Return to BrewLedger". Acceptable; they can log in and then go to settings.

### Integration
- **Stripe portal**: Stripe’s Customer Portal allows any valid URL for `return_url`. Our redirect page is served over HTTPS (same origin as API). No issue.
- **appStateChange in Settings.vue**: Settings.vue still has the `appStateChange` listener when the portal is opened. When the user returns via the deep link, the app comes to foreground and we handle it in App.vue (close browser, push /settings, refresh). The appStateChange listener may also fire when the app becomes active. So we might run refreshSession() twice (once in App.vue, once in Settings.vue). Redundant but safe; no need to remove the appStateChange behavior.

## Follow-up (Addressed in Second Pass)

1. **Browser.close()**: Wrapped in try/catch in `handlePortalReturnDeepLink`; if the browser was not open, the call is safe and any error is swallowed. No change needed.
2. **router.push('/settings')**: Code already only pushes when `route.path !== '/settings'`, avoiding redundant navigation.
3. **analysis.md**: Updated to document the portal return deep link, `/api/billing/portal-return`, and `inAppBrowser` for create-portal-session.

## Second-Pass Review

- **URL scheme**: The app already uses `brewledger://` for checkout success (`brewledger://billing/success`). The same scheme with path `settings` (`brewledger://settings`) is used for portal return; no additional native configuration required beyond the existing scheme.
- **Double refresh**: When returning via deep link, App.vue runs refreshSession(). If the user lands on Settings, that component’s appStateChange listener may also run when the app becomes active; both can trigger refresh. Redundant sync/refresh is acceptable and ensures subscription state is current.
- **Web**: Web clients do not send `inAppBrowser`; they get `return_url: ${baseUrl}/settings` and continue to use normal browser navigation. No change to web behavior.
- **Console app**: The console (desktop) app does not use Capacitor; it uses `window.location.origin` and does not send `inAppBrowser`. Server treats it as web. Correct.

## Follow-up: In-App Browser Does Not Hand Off Custom Schemes (Iteration 3)

- **Issue**: On real devices, the portal return page ("Returning to BrewLedger...") loaded in the in-app browser (SFSafariViewController / Chrome Custom Tabs), but the redirect to `brewledger://settings` did **not** open the app—the in-app browser does not hand off custom URL schemes to the OS. The user was stuck on the page.
- **Fix**:
  1. **Server** (`/api/billing/portal-return`): Page copy changed to "You're all set. Close this window to return to BrewLedger." with an optional "Open BrewLedger" link (for devices where the scheme might work). No automatic meta-refresh that implies the app will open; the primary CTA is closing the window.
  2. **Settings.vue**: When opening the portal on native, we now also add `Browser.addListener('browserFinished', ...)`. When the user closes the in-app browser (after seeing the message), this fires. We run a single cleanup (guard with `portalReturnHandled`): remove both `appStateChange` and `browserFinished` listeners, run `SyncService.sync()`, `refreshSession()`, `refresh()`, and push `/settings` if needed. So "return to app" is achieved by the user closing the window and the app reacting to `browserFinished`.
- **App.vue** deeplink handling for `brewledger://settings` remains for edge cases (e.g. user opened portal in system browser or a future platform that hands off).
