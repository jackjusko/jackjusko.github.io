# Reports Page Cleanup and Data-Backed Reports – Feature Analysis

**Note (2026-02-19):** The two data-backed reports described below (Removals by purpose & tax status, Production volume by batch & location) were later removed from the Reports page and their API routes and frontend services deleted. See `reports-removals-production-removal.md`.

## Summary

The Reports view was simplified by removing placeholder report cards and non-functional UI, and two new data-backed reports were implemented: **Removals by purpose & tax status** and **Production volume by batch & location**, with CSV export.

## What Was Removed

- **Inventory Report**, **Production Report**, and **Financial Report** cards (no backend; "Generate Report" did nothing).
- **Recent Reports** table (mock data; no API).
- **Custom Report Configuration** block (static form; no backend).
- **Advanced Reporting System** promo (marketing copy; no live feature).

## What Was Kept

- TTB Form 5130.9 card (links to `/reports/ttb-form`).
- Beer Removals, Racking Operations, Losses & Theft cards (links to `/removals`, `/racking`, `/losses`).
- **Serving & Inventory Rollup** card (unchanged): date range, Refresh, server-backed with local fallback; brewed by location, inventory change by batch/brand, bulk by vessel, packaged by location.

## New Backend Endpoints

- **`GET /api/reports/removals`** (auth): Query params `periodStart`, `periodEnd` (ISO). Returns ledger entries of type `CONSUME` or `TRANSFER_OUT` in the period. Response: `{ removals: [{ purpose, tax_status, form, item_name, location_name, quantity, created_at }] }`. Uses `removal_purpose`, `tax_status`, and `consumption_form` (or `data.consumption_form`). Quantity is normalized to a positive value (handles both positive and negative ledger quantities). Safe JSON parse and error handling mirror `/api/reports/serving`.
- **`GET /api/reports/production`** (auth): Query params `periodStart`, `periodEnd`. Returns RECEIVE entries with `batch_id` aggregated by batch and by location. Response: `{ byBatch: [{ batch_id, batch_name, quantity }], byLocation: [{ location_id, location_name, quantity }] }`.

## New Frontend

- **RemovalsReportService.js**: `getRemovalsReport({ periodStart, periodEnd })` → GET `/reports/removals` with auth; returns `{ removals: [] }`.
- **ProductionReportService.js**: `getProductionReport({ periodStart, periodEnd })` → GET `/reports/production`; returns `{ byBatch, byLocation }`.
- **utils/csvExport.js**: `toCsv(rows, columns?)`, `downloadCsv(csvContent, filename)`; escapes commas/quotes/newlines for RFC-style CSV.
- **Reports.vue**:
  - **Removals report** card: date inputs, Refresh, table (Purpose, Tax status, TTB column, Item, Location, Quantity), Download CSV, loading/error/empty states.
  - **Production report** card: date inputs, Refresh, two panels (By batch, By location), "CSV by batch" and "CSV by location" buttons, loading/error/empty states.
  - Removals and production each use their own period refs; all three report sections load on mount.

## Edge Cases and Design Notes

- **Removals quantity**: Server accepts both positive and negative ledger quantities and outputs `quantity` as a positive value for display/CSV.
- **Missing metadata**: `purpose`, `tax_status`, or `form` missing on ledger entries show as "Unspecified"; deleted item/location show as "Unknown" / "Unspecified".
- **Date range**: No range limit enforced; very large ranges may be slow (acceptable for current scale).
- **CSV**: Client-side generation only; no server CSV endpoint. Filenames include date range (e.g. `removals-2026-01-01-2026-01-31.csv`).
- **Concurrent loads**: Each section has its own loading flag; Refresh only disables that section’s buttons.
- **No financial reports**: Inventory/Production/Financial cards were removed; no revenue/cost/margin reports until cost data and reporting are implemented.

## Verification (no manual test run)

- Endpoints: auth middleware applied; date parsing and inRange logic; safeParse for JSON; 500 on throw; response keys match frontend.
- Services: auth header; default empty arrays; errors surfaced to UI.
- UI: loading states; error banners; empty states; CSV buttons disabled when no data or loading.
- CSV: column order explicit; commas/quotes escaped; filename includes report type and dates.

## Post-implementation passes (3x)

- **Pass 1 (functional/edge-case)**: Confirmed empty and error states; date-range handling. Added server-side validation for report endpoints: invalid `periodStart`/`periodEnd` (e.g. non-parseable or NaN) are treated as null so the range is unbounded instead of incorrect filtering.
- **Pass 2 (data integrity)**: Verified backend response keys match frontend (removals: purpose, tax_status, form, item_name, location_name, quantity, created_at; production: byBatch/byLocation with batch_id, batch_name, quantity and location_id, location_name, quantity). Quantity coercions and fallback labels (Unspecified, Unknown) confirmed.
- **Pass 3 (UX/resilience)**: Loading flags disable Refresh and CSV buttons; CSV column order and escaping (csvExport.js) verified; copy clarifies live vs. removed features.

## Follow-ups / Limitations

- Packaged inventory by location is already in Serving rollup; could add a dedicated CSV export for it later.
- Removals report is row-level (one row per ledger entry); no server-side grouping by purpose/tax_status/form if a summary view is needed later.
- Production report reuses the same RECEIVE-with-batch_id logic as serving; no new data model.
- Date-only inputs send midnight UTC; entries on the end date after midnight may be excluded depending on server timezone; consider end-of-day for periodEnd if “through end date” semantics are required.
