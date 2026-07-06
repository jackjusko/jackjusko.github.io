# Sync Integrity & Idempotency (2026-02-11)

## Scope
- Propagate batch location deletions across devices.
- Add idempotency for ledger entries and batch volume adjustments to prevent duplicate writes on retry.

## Changes
- **Batch locations (console + mobile)**: Soft-delete (`deleted_at`, version++) instead of hard delete in combine/transfer/remove flows; getters ignore deleted rows; remote upserts purge locally when `deleted_at` is present.
- **Sync apply**: Remote batch_location deletes now remove local rows via repository apply.
- **Server validation**: Allows batch_location deletes without vessel/volume checks.
- **Idempotency keys**: `client_request_id` added on creation for ledger entries and batch volume adjustments (mobile + console).
- **Server dedupe**: New `client_request_id` columns and unique indexes on `ledger_entries` and `batch_volume_adjustments`; sync handler skips duplicates before upsert.
- **Migration**: `server/migrate_client_request_id.js` adds the new columns and indexes for existing databases.

## Risks / Follow-ups
- Ensure migration runs in all environments before deploying clients that send `client_request_id`.
- Consider adding Dexie indexes for client_request_id if client-side duplicate detection is needed.
- Monitor for legacy rows without `client_request_id`; server dedupe remains best-effort on id collisions. 
