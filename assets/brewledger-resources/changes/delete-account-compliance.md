# Delete Account Compliance - Feature Analysis

## First Iteration

### Implementation Summary
- Added `users.deleted` column (INTEGER DEFAULT 0) via idempotent ALTER in init_db.js
- POST /api/auth/delete-account: sets deleted=1, deletes sessions
- Login rejects deleted users with generic "Invalid credentials"
- Auth middleware checks user not deleted
- GET /api/users and request-password-reset exclude deleted users
- Desktop and mobile Settings have delete account UI with confirmation

### Potential Issues & Edge Cases

1. **Console Settings - token source**: The console uses `session.value?.token`. The useSession composable gets session from AuthService.getSession(), which builds from localStorage. AuthService.getSession does NOT return a token in its object - it only returns orgId, userId, etc. from localStorage. The token is stored in localStorage under 'token' but getSession may not include it. Need to verify.
   
2. **Token in session object**: Checking AuthService.getSession() - it returns `{ token, orgId, userId, ... }` where token = localStorage.getItem('token'). So token IS in the returned object. Good.

3. **Invite flow for deleted-account email**: If an admin tries to invite someone whose email was previously used by a deleted user, the INSERT will fail on UNIQUE constraint. We did not add handling for this - the plan said "keep existing check; deleted users with same email would still hit UNIQUE". A better UX would be to check for deleted user and return a specific message like "This email was associated with a deleted account. Contact support." - but that's out of scope per plan.

4. **reset-password for deleted user**: The reset-password endpoint validates the token and updates the user's password. If someone has a valid reset token from before their account was deleted, they could theoretically use it. The reset token is linked to user_id. When we mark user deleted, we don't invalidate their password_resets. A deleted user with a valid reset token could reset password and then... login would still reject them (deleted check). So they'd end up with updated password but still can't log in. Low risk. We could add: when processing reset-password, reject if user.deleted. Worth doing for cleanliness.

5. **init_db CREATE TABLE vs ALTER**: For brand-new databases, CREATE TABLE users runs first (without deleted column), then the ALTER adds it. So new DBs get the column. For existing DBs, ALTER adds it. Good.

6. **SQLite INTEGER and boolean**: `deleted = 1` works; `user.deleted` could be 0, 1, or undefined (for old rows before ALTER - but ALTER adds DEFAULT 0 so existing rows get 0). Actually, when we ADD COLUMN with DEFAULT 0, existing rows get 0. New inserts would need to explicitly set deleted or rely on default. Our UPDATE sets deleted=1. Our checks use `user.deleted` (truthy when 1) and `(deleted IS NULL OR deleted = 0)` for SQL. Good.

7. **Desktop modal wiring**: We switched to inject('modal') - but Settings might be rendered in a context where modal is not provided (e.g. when would that happen?). The dashboard layout provides it. Settings is under the main app with sidebar, so it should have access. Fallback to window.confirm is fine.

8. **Mobile - session.token**: Mobile useSession returns session from AuthService.getSession() which includes token. Good.

9. **Race: delete succeeds but redirect fails**: If network/JS fails after API success but before clearSession/router.push, user might still have token in localStorage. Next API call would get 401 (sessions deleted). The client would need to handle 401 globally - router guard might redirect. But our deleteAccount catch for 401 does clear and redirect. The success path also clears and redirects. We're good.

10. **Check reset-password**: Should we reject reset when user is deleted? Yes - add check in reset-password handler. IMPLEMENTED.

---

## Second Iteration

### Additional Considerations

11. **request-password-reset**: We already filter with `AND (deleted IS NULL OR deleted = 0)` so deleted users never receive reset emails. Good.

12. **Admin request for deleted user**: If admin requests password reset for a deleted user's email - we simply don't send (user not found in filtered query). Generic response. Good.

13. **Console AuthService.getSession**: Confirmed - console AuthService.getSession returns `token` in the object (line 14). No change needed.

14. **Invite flow**: Per plan, out of scope. Deleted-user email would fail on INSERT (UNIQUE). No change.

15. **Final**: All identified weak points addressed. reset-password now rejects deleted users.
