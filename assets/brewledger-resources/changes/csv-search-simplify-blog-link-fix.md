# CSV Search Simplification and Blog Link-Only Fix

## Summary

After the blog migration to server-rendered HTML, the embedded CSV viewer on two posts (BSG catalog, cellar logging) no longer rendered—BlogPost.vue with CsvSearch was bypassed. The standalone CSV tool was also broken and overcomplicated. This change simplifies the CSV tool to a minimal viewer and replaces the broken "searchable below" with direct links.

## Changes Implemented

### 1. CSV Search Tool – Simplified

**File**: `platforms/console/src/views/tools/CsvSearch.vue`

- **Removed**: Smart parsers (Distributor Sales, Hop Contract, Inventory Audit), preset view tabs, charts, column sort, pagination, delimiter override, share link, print, download CSV.
- **Kept**: Load from URL or file upload, search filter, table display.
- **Result**: ~250 lines (down from ~740). Minimal: load CSV, search rows, view table.
- **Fix**: Corrected `hasCsv` logic so the load form vs viewer states render correctly. Added `router.replace` when clearing so URL query is removed and user returns to load form.

### 2. Blog Posts – Link-Only Fix

**BSG post** (`server/content/blog/brewers-supply-group-bsg-complete-inventory.md`):
- Replaced "searchable below" with link to `/tools/csv-search?url=/bsg-inventory.csv` and download link to `/bsg-inventory.csv`.
- Removed `sandboxCsvUrl` from frontmatter.

**Cellar post** (`server/content/blog/precision-data-cellar-manual-logging.md`):
- Replaced "Below you can search through a sample CSV..." with link to `/tools/csv-search?url=/sample-cellar-log.csv` and download link.
- Removed `sandboxCsvUrl` from frontmatter.

**Console copies** (`platforms/console/src/blog/posts/*.md`): Same updates for consistency.

### 3. Supporting Updates

- `ToolsIndex.vue`: Updated CSV Search card description.
- `App.vue`: Updated SEO meta description for `/tools/csv-search`.

## Verification

- Visit `/tools/csv-search` → load form appears.
- Visit `/tools/csv-search?url=/bsg-inventory.csv` → CSV loads and displays; search works.
- Visit `/blog/brewers-supply-group-bsg-complete-inventory` → links to CSV tool and download work.
- Visit `/blog/precision-data-cellar-manual-logging` → same.

## Notes

- BlogPost.vue still has the CsvSearch embed block; it is dead code since blog routes are server-handled. Left in place for potential future SPA blog use.
- blogLoader.js still parses `sandboxCsvUrl`; harmless if unused.

---

## First-Iteration Feature Analysis

### Edge Cases Considered

1. **Relative URLs**: Changed input type from `url` to `text` so `/bsg-inventory.csv` can be entered. `fetch()` with relative URL resolves against current origin.
2. **Route query on mount**: `onMounted` explicitly calls `fetchCsv(effectiveCsvUrl.value)`; watch has `immediate: false` to avoid double fetch.
3. **Clear + route**: When user clicks "Change file or URL", we call `router.replace` to remove `?url=` from query so `effectiveCsvUrl` becomes null and load form is shown.
4. **Large CSVs**: All filtered rows render in DOM; no pagination. Acceptable for minimal tool; could add virtualization later if needed.
5. **Delimiter**: Auto-detect only; no manual override. Unusual delimiters may fail; acceptable for minimal scope.

### Potential Weak Points

- **CORS**: External URLs (e.g. `https://example.com/data.csv`) may fail due to CORS. Error message already suggests trying file upload. No change.
- **Empty/header-only CSV**: `rows.length === 0` triggers "CSV appears empty." Good.
