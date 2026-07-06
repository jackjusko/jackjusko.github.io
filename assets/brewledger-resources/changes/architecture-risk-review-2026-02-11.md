# Architecture & Risk Review (2026-02-11)

## Summary
Two-pass architecture and risk review focusing on security, data integrity, scalability, and operational resilience. No code changes were executed per request; findings and recommended follow-ups only.

---

## Iteration 1 — Findings

- **Secret exposure (client and server)**: Live Stripe secret/key and webhook secret are committed in `server/server.js`; the public landing page embeds a Discord webhook URL for demo requests. Both enable credential scraping and abuse (spam, egress of PII) if this repo or build output is exposed.
- **QBO token storage**: QuickBooks access/refresh tokens and realm IDs are stored in SQLite in plaintext without envelope encryption or KMS; refresh scheduling relies on ad-hoc checks (`isQboExpired` with 5m buffer) and shares the same token across all server workers.
- **Sync integrity gaps**: Known limitation in analysis: batch_location deletes (remove/merge/combine) do not sync, so devices diverge on vessel splits. Volume adjustments and ledger entries rely on referential checks but have no double-submit protection during offline retries.
- **Offline/online contact form**: Landing page contact form posts directly to Discord without bot-check, rate limit, or server mediation. Abuse can flood the webhook and log unvalidated user input; failures surface generic errors only.
- **SQLite single-node scalability**: Backend uses a single SQLite file for all orgs with no WAL/backup strategy documented, and no per-tenant throttling beyond auth rate limit. High write volume (ledger, sync) risks lock contention and data loss on host failure.
- **Logging/PII**: Stripe, QBO, and contact payloads can be logged in plaintext (server console, Discord) with no redaction/rotation strategy.

---

## Iteration 2 — Refined assessment & recommendations

- **Secret management**
  - Move Stripe keys/webhook secret and Discord webhook URL to environment variables; use separate test vs prod keys; rotate immediately after removal from code.
  - Add outbound rate limit + bot check for the contact form; proxy via backend to hide webhook URL.
- **Accounting integrations**
  - Encrypt QBO tokens at rest (KMS/wrapping key) and store per-org. Add per-request `org_id` scoping and ensure refresh is serialized per org to avoid token races. Add audit logging with redaction.
- **Sync integrity**
  - Prioritize delete-sync for `batch_locations` (including combine/remove) and add idempotency keys on volume adjustments and ledger posts to avoid duplicate writes on retry.
  - Add conflict detection on client apply when server rejects referential integrity (e.g., missing vessel/item) to prevent silent drops.
- **Scalability/ops**
  - Move to PostgreSQL or at least enable WAL + backups for SQLite; add health checks for DB locks. Establish per-org rate limits for sync endpoints to prevent noisy neighbors.
- **Compliance/observability**
  - Add structured logging with PII redaction and log rotation; trace IDs across sync, billing, and QBO calls. Document incident response for leaked webhooks/keys.

No implementation was performed; these are documented actions for follow-up.
