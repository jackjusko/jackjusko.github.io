# Tools Section & BBL to Case Converter – Implementation

## Overview

Added a standalone **Tools** section to the console app, separate from the blog (The Ledger) and the main landing. First tool: **BBL to Case Equivalent Converter**, which translates barrels into 12 oz cases, 16 oz 4-packs, or 1/2 BBL kegs.

## Implementation Summary

### 1. File Structure

- `platforms/console/src/views/tools/ToolsIndex.vue` – Tools landing with card grid
- `platforms/console/src/views/tools/BblToCase.vue` – BBL to case converter
- `platforms/console/src/views/tools/CsvSearch.vue` – Moved from `views/CsvSearch.vue`

### 2. Router

- `/tools` → ToolsIndex
- `/tools/bbl-to-case` → BblToCase
- `/tools/csv-search` → CsvSearch (migrated from blog layout)

All routes use `meta: { requiresAuth: false, isTools: true }`. Auth guard updated so authenticated users can access tools without redirect.

### 3. Layout (App.vue)

New `isTools` branch: header (logo + Tools, nav: All tools, BBL to Case, CSV Search), main, footer. Uses `ledger-beer` theme.

### 4. Navigation

- Landing nav: added Tools link
- Blog header: added Tools link (desktop + mobile)
- Tools header: links to The Ledger and BrewLedger

### 5. BBL Converter Logic

- 1 US BBL = 31 gal = 3,968 fl oz
- 12 oz case (24-pack) = 288 fl oz → ~13.78 cases/BBL
- 16 oz 4-pack = 64 fl oz → 62 four-packs/BBL
- 1/2 BBL keg = 15.5 gal → 2 kegs/BBL

### 6. Sitemap

Added `/tools`, `/tools/bbl-to-case`, `/tools/csv-search`.

### 7. BlogPost CsvSearch Import

Updated BlogPost.vue to import CsvSearch from `./tools/CsvSearch.vue` (same component, new path).

## Edge Cases & Considerations

1. **Authenticated users**: Tools remain accessible when logged in; no redirect to dashboard.
2. **Blog embedding**: CsvSearch still embeds in blog posts via `sandboxCsvUrl`; import path updated.
3. **Decimal BBLs**: Converter accepts decimals (e.g. 7.5 BBL).
4. **Negative/empty input**: Non-numeric or negative values show 0 results.

## Additions (file upload, prerender)

- **CSV Search file upload**: Users can upload a CSV file via `<input type="file">` in addition to loading from URL. File is read with FileReader (UTF-8), parsed with same parseCsv logic. Upload only shown when `!embedded`.
- **Prerender**: Added `/tools`, `/tools/bbl-to-case`, `/tools/csv-search` to `vite.config.js` prerender routes.

## Testing Recommendations

- Visit `/tools` and confirm tool cards and links
- Visit `/tools/bbl-to-case`, enter 7 BBL, verify ~96 cases, ~434 4-packs, 14 kegs
- Visit `/tools/csv-search`, confirm behavior unchanged
- From blog header, click Tools and verify layout
- From landing, click Tools and verify navigation
- With auth token, visit `/tools` and confirm no redirect to dashboard
