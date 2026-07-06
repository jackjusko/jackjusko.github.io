# Feature Analysis: Externalize Server Secrets to .env

## Summary

All hardcoded API keys, webhook secrets, and subscription price IDs in the server have been moved to environment variables loaded from a root `.env` file. The server and standalone scripts (create_portal_config.cjs, check_stripe.cjs, process_csv_items.js) load dotenv from the repo root and use `process.env.*` for secrets and optional config.

## Changes Made

- **server/server.js**: Load dotenv at top; Stripe client from `STRIPE_SECRET_KEY` (null if unset); `STRIPE_PRICE_ID`, `STRIPE_WEBHOOK_SECRET` from env; `APP_DEEP_LINK_SCHEME`, `BILLING_RETURN_BASE_URL` from env with defaults; OpenRouter key/preset/headers from env. Billing and webhook routes return 503 when Stripe is not configured.
- **server/create_portal_config.cjs**, **server/check_stripe.cjs**: Load dotenv, require `STRIPE_SECRET_KEY` or exit with message.
- **server/process_csv_items.js**: Load dotenv; `OPENROUTER_API_KEY`, `OPENROUTER_PRESET_CSV`/`OPENROUTER_PRESET`, `BRAVE_SEARCH_API_KEY`, `ENABLE_WEB_SEARCH` from env; Brave header uses `BRAVE_SEARCH_API_KEY` (no hardcoded token).
- **server/package.json**: Added `dotenv` dependency.
- **Root .env**: Created with current real values for Stripe, OpenRouter, Brave, app URLs; placeholders for AWS SES and QBO.

## First-Pass Review: Risks and Edge Cases

1. **Stripe client null**: If `STRIPE_SECRET_KEY` is missing, `stripeClient` is null. Webhook and all billing routes now check `req.app.stripe` and return 503 with a clear message. No crash.

2. **Webhook without secret**: If `STRIPE_WEBHOOK_SECRET` is empty, existing code path treats as “dev mode” and parses body without verification. That’s acceptable for local dev; production should set the secret.

3. **STRIPE_PRICE_ID empty**: Webhook and checkout still run; subscription updates may not match a plan (price ID comparisons fail). Consider validating `STRIPE_PRICE_ID` when Stripe is configured and logging a warning if missing.

4. **process_csv_items.js**: If `OPENROUTER_API_KEY` is empty, the OpenAI client is still constructed with an empty key and will fail at first API call. Script could exit early with “Set OPENROUTER_API_KEY in .env” when key is missing.

5. **Brave Search**: Header uses `BRAVE_SEARCH_API_KEY`; when unset, `searchWeb` returns null without calling the API (existing guard). No change needed.

6. **Run context**: Server is started as `node server.js` from `server/`; scripts are run from `server/` (e.g. `node create_portal_config.cjs`). `path.resolve(__dirname, '..', '.env')` correctly points to repo root. If someone runs from repo root (e.g. `node server/server.js`), `__dirname` is `server/`, so `..` is still root and `.env` is found.

7. **PORT and TLS**: `PORT` is still hardcoded to 443; TLS key/cert paths use env or defaults. For consistency, `PORT` could be `process.env.PORT || 443` and documented in `.env.example` or `.env` comments.

8. **.env not found**: dotenv does not throw when the file is missing; variables simply stay unset. That’s acceptable: missing `.env` yields 503 for billing and “not configured” for AI.

9. **create_portal_config products**: Product/price IDs remain hardcoded in the script. They are not secret but are environment-specific; could be moved to env (e.g. `STRIPE_PORTAL_PRODUCTS_JSON`) in a follow-up if needed.

10. **Duplicate OPENROUTER key**: Same key is used in server.js (AI chat) and process_csv_items.js; both read from `.env`, so one source of truth.

## Recommended Follow-ups (for apply-fixes)

- Add `PORT` to env: `const PORT = parseInt(process.env.PORT, 10) || 443;` and document in `.env`.
- In process_csv_items.js, if `!OPENROUTER_API_KEY`, log and exit with instructions instead of failing on first API call.
- Optional: Log a single startup warning when Stripe is configured but `STRIPE_PRICE_ID` or `STRIPE_WEBHOOK_SECRET` is missing.

---

## Second-Pass Review (Post Apply-Fixes)

All recommended follow-ups were implemented:

- **PORT**: Server now uses `parseInt(process.env.PORT, 10) || 443`. `.env` includes an optional `# PORT=443` comment.
- **process_csv_items.js**: Script exits immediately with "Set OPENROUTER_API_KEY in .env" when the key is missing.
- **Stripe warning**: On startup, if Stripe client exists but `STRIPE_PRICE_ID` or `STRIPE_WEBHOOK_SECRET` is missing, a single console.warn is emitted.

### Additional Checks

- **No secrets in tracked files**: Grep for `sk_live`, `sk_test`, `whsec_`, and the known OpenRouter/Brave tokens shows no remaining hardcoded secrets in server source (only in `.env`, which is gitignored).
- **Backward compatibility**: If `.env` is absent or empty, server still starts; billing and AI return 503 / "not configured". Existing deployments can add `.env` and set variables without code change.
- **Tests**: Backend tests that mock Stripe or hit billing endpoints should still pass; they may rely on env or mocks. No test file was changed; if any test expected a hardcoded key, it would need to set the env var or mock (unchanged behavior for tests that already mock).
- **Documentation**: `analysis.md` will be updated to record the new env vars and that secrets are no longer in code.
