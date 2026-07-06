# Feature analysis: AWS SES auth emails (welcome, invite, password reset)

## Pass 1: Risks and edge cases

### Email failure handling
- **Risk**: SES down or misconfigured could break auth flows if we threw.
- **Mitigation**: Mailer catches all errors and logs; never throws. Welcome and invite send email after `res.json()`; invite/register responses are unchanged on email failure. Request-password-reset always returns 200 then sends email asynchronously.

### Token expiry and replay
- **Risk**: Stolen or replayed reset tokens.
- **Mitigation**: Tokens expire in 1 hour; `validateResetToken` checks `expires_at` and `used_at`. `markTokenUsed` is called after successful password update so each token is single-use.

### Rate limiting
- **Risk**: Abuse of request-password-reset (email enumeration, spam) or reset-password (brute force).
- **Mitigation**: Both endpoints use `authLimiter` (20 requests per 15 minutes per IP), same as login.

### HTML/text fallback
- **Risk**: Some clients only show plain text.
- **Mitigation**: Templates provide both `text` and `html`; mailer sends both when present.

### Missing SES configuration
- **Risk**: Server crash or noisy errors when env vars unset.
- **Mitigation**: Mailer builds SES client only when all of region, accessKeyId, secretAccessKey, and fromEmail are set; otherwise logs a single warning and no-ops on send.

### Request reset response timing
- **Risk**: Delaying response until email is sent could leak existence of account (timing) or cause timeouts.
- **Mitigation**: Response is sent immediately with a generic message; email is sent after (fire-and-forget). No timing leak; same 200 body whether or not user exists.

### Invite and reset URLs
- **Risk**: Wrong login/reset URL in emails when deployed.
- **Mitigation**: Invite login URL uses `RESET_BASE_URL` (strip trailing /reset path) + `/login`, or placeholder. Reset link uses `RESET_BASE_URL` or `https://app.example.com/reset`. Deploy must set `RESET_BASE_URL` (e.g. `https://getbrewledger.com/reset`) so links point at the console app.

### Pass 1 follow-up implemented
- Server-side minimum password length on reset: `reset-password` now rejects `newPassword` shorter than 6 characters (aligned with console `minlength="6"`) to avoid weak passwords if API is called directly.

---

## Pass 2: Re-review and follow-up

### Password reset table growth
- **Observation**: `password_resets` rows are never deleted; only validated by expiry and `used_at`.
- **Decision**: Acceptable. Expired/used rows are harmless; periodic cleanup can be added later if needed.

### Console reset page without token
- **Observation**: Visiting `/reset` without `?token=...` shows a message and link to login.
- **Decision**: Already handled in ResetPassword.vue; no change.

### Invite email and RESET_BASE_URL
- **Observation**: Invite login URL is derived by replacing `/reset.*` with empty and appending `/login`. If `RESET_BASE_URL` is `https://getbrewledger.com/reset`, login URL becomes `https://getbrewledger.com/login`. Console route is `/login`, so base path must be the app origin.
- **Decision**: Document in analysis.md that `RESET_BASE_URL` should be the full reset page URL (e.g. `https://getbrewledger.com/reset`) so both reset and login links use the same origin. Already documented.

### Error messages
- **Observation**: Reset endpoints return generic messages for invalid/expired token and for missing/invalid body to avoid leaking information.
- **Decision**: No change; current wording is appropriate.

### Pass 2 follow-up
- No further code changes. Analysis.md updated with full SES/auth-email subsection; this file records both passes.
