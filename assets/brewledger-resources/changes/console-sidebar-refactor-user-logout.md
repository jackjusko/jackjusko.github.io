# Console Sidebar Refactor: User Display & Logout Location

## Summary

Refactored the desktop console sidebar to simplify the UI:

1. **Removed sidebar footer** – The sticky bottom section (brewery name, user name, dark mode toggle, logout button) has been removed.
2. **Dashboard-only user display** – Logged-in user name and brewery name are now shown only on the Dashboard, near the top, in a compact `text-sm` line (e.g. "Jane Doe · Acme Brewing").
3. **Logout in Settings** – Logout is now in Settings → General, alongside Display Preferences and Password. Uses the same logic (stop sync, clear token cache, AuthService.logout, clearSession, navigate to `/`).

## Changes

### App.vue
- Removed `console-sidebar-footer` block (user avatar, org/user names, theme toggle, logout button).
- Removed unused `handleLogout`, `AuthService`, `clearTokenCache`, and default `router` imports.

### Dashboard.vue
- Added a compact line at the top showing `session.userName · session.orgName` when session is available. Uses `text-sm text-neutral-500 dark:text-stone-400` for subtle appearance.

### Settings.vue
- Added "Logout" card in General tab, before the Password card.
- Implemented `handleLogout()` using SyncService.stopSyncLoop, clearTokenCache, AuthService.logout, clearSession, router.push('/').
- Added imports: AuthService, SyncService, clearTokenCache, clearSession from useSession.

### style.css
- No changes. The `.console-sidebar-footer`, `.console-sidebar-user`, `.console-sidebar-avatar`, `.console-sidebar-actions`, `.console-sidebar-btn` classes remain but are unused; can be pruned in a future cleanup if desired.

## Edge Cases & Considerations

1. **Theme toggle**: Users now toggle dark mode only from Settings → General → Display Preferences. Blog and Tools layouts retain their own header theme toggles. Theme is persisted via localStorage and document.documentElement.classList.
2. **Session on Dashboard**: Dashboard already loads session via AuthService.getSession() in onMounted; the user/brewery display uses `session?.userName` and `session?.orgName`, so it appears once session is loaded.
3. **Logout flow**: Matches previous App.vue behavior – stop sync loop, clear token cache, logout, clear session, redirect to `/`.
