# Removal of "Removals by purpose & tax status" and "Production volume by batch & location" Reports

## Summary

The Reports page no longer includes the **Removals by purpose & tax status** or **Production volume by batch & location** report cards. All associated frontend code and server API routes for these reports were removed.

## What Was Removed

### Frontend (console)

- **Reports.vue**: The two report card sections (Removals by purpose & tax status; Production volume by batch & location), including:
  - Date range inputs, Refresh, and CSV download buttons
  - Table/panels and loading/error/empty state UI
  - Refs: `removalsPeriodStart`/`removalsPeriodEnd`, `productionPeriodStart`/`productionPeriodEnd`, `removalsReport`, `removalsLoading`/`removalsError`, `productionReport`, `productionLoading`/`productionError`
  - Functions: `loadRemovalsReport`, `loadProductionReport`, `downloadRemovalsCsv`, `downloadProductionCsvBatch`, `downloadProductionCsvLocation`, and `REMOVALS_CSV_COLUMNS`
  - Imports: `getRemovalsReport`, `getProductionReport`, `toCsv`, `downloadCsv`
  - Calls to `loadRemovalsReport` and `loadProductionReport` from `onMounted`
  - Unused scoped `.data-table` styles (previously used by the removals table)
- **RemovalsReportService.js**: Deleted (was the only consumer of `GET /api/reports/removals`).
- **ProductionReportService.js**: Deleted (was the only consumer of `GET /api/reports/production`).

### Backend (server)

- **server.js**: Removed routes:
  - `GET /api/reports/removals` (CONSUME/TRANSFER_OUT by purpose, tax_status, consumption_form).
  - `GET /api/reports/production` (RECEIVE with batch_id aggregated by batch and by location).

## What Remains on Reports Page

- Report type links: TTB Form 5130.9, Beer Removals, Racking, Losses.
- **Serving & Inventory Rollup** card (date range, Refresh, server-backed with local fallback; brewed by location, inventory change by batch/brand, bulk by vessel, packaged by location).

## Notes

- **utils/csvExport.js** is unchanged and remains in the repo for potential future report CSV export.
- Historical context: these two reports were added in the reports cleanup (see `changes/reports-cleanup-implementation.md`); they have now been intentionally removed.

## Feature Analysis

### First pass

- **Orphaned references**: No remaining imports or references to `RemovalsReportService` or `ProductionReportService`; server no longer exposes the two report routes.
- **csvExport**: Only used by the removed reports; the utility file is kept for reuse. No other console code currently imports it.
- **Reports.vue**: No leftover refs or methods; watch only runs for `periodStart`/`periodEnd` (Serving rollup). Lint and runtime behavior of the Reports page should be unchanged aside from the removed sections.

### Second pass

- **Tests**: Grep shows no tests for `GET /api/reports/removals` or `GET /api/reports/production`, or for `RemovalsReportService`/`ProductionReportService`. TTBFormService tests use "removals" and "production" in the TTB form sense (form lines, beer produced), not the removed report features—no test changes required.
- **Historical doc**: `reports-cleanup-implementation.md` now includes a note at the top that these two reports were later removed, with a pointer to this document.
- **analysis.md**: Updated in two places (Reports View bullet and Reports cleanup bullet) to describe the removal and reference this change doc.
