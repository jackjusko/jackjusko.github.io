# User Management on Desktop – Feature Analysis

## Summary
Add-new-user functionality has been migrated to the desktop console. The console Settings **User Management** tab now shows a real user list (Name, Email) and an “Add new user” form for organization admins. Roles, last active, and edit/delete actions are out of scope. The mobile app continues to offer the same invite flow in Settings for admins.

## First-Pass Analysis

### Implemented Changes
- **Server** (`server/server.js`)
  - New **GET /api/users** (authMiddleware): returns `{ users: [{ id, name, email, role, created_at }] }` for the current org. Caller must be admin (403 otherwise).
  - Existing **POST /api/auth/invite** unchanged: admin-only, creates user in same org with name/email/password; 400 for missing fields or duplicate email, 403 for non-admin.
- **Console**
  - **UserService** (`platforms/console/src/services/UserService.js`): `getUsers()` (GET /api/users) and `inviteUser({ name, email, password })` (POST /api/auth/invite); uses AuthService.getSession() for token; throws with clear messages on API/network errors.
  - **Settings.vue** User Management tab:
    - Non-admin: single message “Only organization admins can view and manage users.”
    - Admin: loading state, error state with Retry, table (Name, Email only), empty state (“No users yet. Add one below.”), then “Add new user” form (Full name, Email, Temporary password, Confirm password). Create user button disabled when loading, password mismatch, or missing name/email/password. Inline invite error; success via global modal. On success, form cleared and user list refreshed.
  - Users loaded when tab is `users` (onMounted and watch(activeTab)); `loadUsers` no-op when not admin.

### Risks and Edge Cases (First Pass)
1. **Tab switch before loadUsers resolves**: If user switches away from Users tab quickly, loadUsers still runs; state (usersList, usersError) is safe. No cancel needed for this scope.
2. **Duplicate email**: Server returns 400 “Email already registered”; UserService throws; Settings shows inviteError. Good.
3. **403 on list**: Non-admin opening Users tab sees “Only organization admins…” and never calls GET /api/users. Admin who is demoted (role changed elsewhere) would get 403 on next list or invite; we show usersError or inviteError from server message. Acceptable.
4. **Token expiry during invite**: Request fails with 401; axios may not set response.data.error. UserService throws “Failed to create user” or network message. Generic but acceptable.
5. **Mobile invite unchanged**: Mobile Settings still has invite (admin-only). Both platforms use same backend; no conflict.

### Follow-ups From First Pass
- None required. Optional: ensure server 401 responses include a JSON body with `error` so UserService can surface “Session expired” (currently server may return generic 401).

## Second-Pass Analysis

### Additional Review
- **isAdmin from useSession**: useSession exposes `isAdmin` computed (session.role === 'admin'). Settings uses it for guard and for calling loadUsers; when tab is users and user is admin, loadUsers runs. Correct.
- **loadUsers when tab becomes users**: watch(activeTab) calls loadUsers() when tab === 'users'. If user is admin and switches to Users tab, list loads. If user is not admin, loadUsers() returns early without setting usersError, and UI shows read-only message. Correct.
- **Invite form validation**: Button disabled when invitePasswordMismatch || !inviteName?.trim() || !inviteEmail?.trim() || !invitePassword. inviteUser() also checks and sets inviteError for password mismatch. Double-check prevents submit. Good.
- **Modal usage**: showAlert('Success', 'User created.', 'primary') uses console’s useModal; App.vue provides global ModalDialog. Alert closes on confirm; no further action needed. Good.
- **API base URL**: UserService uses API_BASE_URL from config; GET /api/users and POST /api/auth/invite are relative to that base. Console config uses same API_BASE_URL as other features. Correct.

### Second-Pass Follow-ups
- None. Implementation is consistent; documentation and analysis.md update complete the feature.

## Third pass (check your work)
- **inviteError on success**: Cleared `inviteError` after successful invite so a previous failure message does not remain visible.
- **Session and role**: Login stores `role` via setSession; AuthService persists as `userRole`; useSession’s `isAdmin` uses `session.role === 'admin'`. Confirmed.
- **Routes**: GET /api/users and POST /api/auth/invite use authMiddleware; req.user.userId and req.user.orgId set correctly. Confirmed.
- **Settings route**: /settings has requiresAuth: true, so only authenticated users see the Users tab. Non-admin sees message; admin sees list and form. Confirmed.

## Integration with analysis.md

- **Settings Tabs** (Console): Replace “User Management: User accounts (placeholder)” with: **User Management**: List org users (Name, Email) and add new users (admin only). GET /api/users for list; POST /api/auth/invite for create. Non-admins see read-only message. No roles/last-active/edit/delete in UI.
- **Backend**: Document GET /api/users (admin-only, org-scoped) and that invite remains the only create path.
