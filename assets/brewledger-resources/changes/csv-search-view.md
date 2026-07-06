# CSV Search View – Feature Analysis

## Summary

A new view in `platforms/console/` allows searching through CSV data loaded from a direct URL. The view is available as a standalone page at `/tools/csv-search` (with optional `?url=...`) and can be embedded in a blog post via frontmatter `sandboxCsvUrl`. It is sandboxed in the post "Precision Data in the Cellar: Moving Beyond Manual Logging."

## Implementation Overview

- **View**: `views/CsvSearch.vue` – fetches CSV from URL (route query or prop), parses with a simple RFC-style parser (handles quoted fields, commas inside quotes), displays searchable table.
- **Route**: `/tools/csv-search` – `meta: { requiresAuth: false, isBlog: true, title: 'CSV Search | BrewLedger Blog' }` so it uses the blog layout.
- **Blog sandbox**: `BlogPost.vue` renders `CsvSearch` below the article when post has `sandboxCsvUrl`; `blogLoader.js` includes `sandboxCsvUrl` in post objects.
- **Sample CSV**: `public/sample-cellar-log.csv` – sample cellar log used by the precision-data-cellar post.
- **Post**: `precision-data-cellar-manual-logging.md` – frontmatter `sandboxCsvUrl: /sample-cellar-log.csv` and a short "Try it" section with link to `/tools/csv-search`.

## First Iteration – Potential Issues

### 1. **Relative URL in embedded mode**

- `sandboxCsvUrl` is `/sample-cellar-log.csv` (path). `fetch('/sample-cellar-log.csv')` is same-origin and works. If a post used `https://other.com/file.csv`, CORS would apply; error message already mentions CORS. No change needed for paths.

### 2. **CSV parser edge cases**

- Parser is hand-rolled: handles `"`, `,`, `\n`, `""` inside quotes. Does not handle `\r\n` line endings inside quoted fields (only strips `\r` when not in quotes). Many CSVs use `\r\n`; the current loop treats `\n` as row end, so `\r` before `\n` ends up in the field. We strip `\r` only when not in quotes—so `"a\r\nb"` would keep `\r`. Consider normalizing: replace `\r\n` with `\n` at start of parse. **Action: normalize line endings before parsing.**

### 3. **Empty or header-only CSV**

- If CSV has only headers (one row), `dataRows` = [], `filteredRows` = [], table body shows "No rows match your search." even with empty search. We should distinguish "no data rows" from "no match for search." **Action: show "No data rows" when `dataRows.length === 0` and no search; keep current message when search is non-empty and filtered is empty.**

### 4. **Rows with varying column count**

- Parser doesn’t pad rows; some rows may have fewer cells. Table uses `v-for="(cell, colIndex) in row"` so short rows show fewer cells; headers stay. Acceptable. Optional: pad row to headers.length for alignment. Defer unless needed.

### 5. **SEO / sitemap**

- `/tools/csv-search` is a tool page. Sitemap currently lists root, /blog, and post URLs. Adding `/tools/csv-search` is optional; not required for "sandboxed in a blog post." Defer.

### 6. **Link in markdown**

- "[CSV Search](/tools/csv-search)" renders as `<a href="/tools/csv-search">`. In an SPA this triggers a full navigation; Vue Router will handle it if the app is already loaded (depending on how the app is mounted). Same-origin link is correct. No change.

### 7. **Embedded mode: no URL input**

- When `embedded=true`, we don’t show the URL form and we don’t show "Change URL." So the only way to see another CSV from that post is to go to `/tools/csv-search`. Intentional. No change.

## Planned Follow-ups (First Iteration)

1. Normalize CSV text: replace `\r\n` and `\r` with `\n` before parsing. **Done.**
2. When `dataRows.length === 0` and `searchQuery` is empty, show "No data rows in this CSV." instead of "No rows match your search." **Done.**

---

## Second Iteration – Additional Considerations

### 1. **Standalone page without URL**

- On `/tools/csv-search` with no `?url=` and no `initialCsvUrl`, the user sees the URL form. Submitting loads that URL and sets `csvUrl`; `effectiveCsvUrl` becomes that URL so the table view shows. Correct. If the user then clicks "Change URL", we clear and show the form again. Good.

### 2. **Standalone with query url**

- Visiting `/tools/csv-search?url=https://example.com/data.csv`: `effectiveCsvUrl` is from `route.query.url` (not embedded, no initialCsvUrl). We fetch that URL on mount. We also set `urlInput.value = route.query.url` in onMounted so if they click "Change URL" and re-load, the input is pre-filled. Good.

### 3. **Security / XSS**

- CSV content is rendered as text in table cells via `{{ cell }}`, not `v-html`. No XSS from CSV data. URLs come from frontmatter (build-time) or user input; we don’t inject URL into innerHTML. Safe.

### 4. **Large CSVs**

- Entire CSV is held in memory and all rows rendered in the DOM. Very large files could slow the UI. Acceptable for a blog sandbox / demo; we could add virtualization or pagination later if needed. No change for this feature.

### 5. **Accessibility**

- Search input has `aria-label="Search CSV rows"`. Table has semantic `<table>`, `<thead>`, `<tbody>`. No live region for "X of Y rows"; screen readers get it from the DOM. Optional: add `aria-live` for filter result count. Defer.

### 6. **Document title on standalone page**

- Route has `meta: { title: 'CSV Search | BrewLedger Blog' }`. App.vue useHead was updated to prefer `route.meta.title`, so the tools page gets the correct title. Good.

### 7. **Sitemap**

- `/tools/csv-search` is still not in sitemap. Optional for discoverability; not required for sandbox. Document in analysis; no code change.

## Second Iteration – No Further Code Changes

All first-iteration fixes are implemented. Second pass did not identify additional required changes; remaining items are optional (large CSV handling, sitemap, aria-live).
