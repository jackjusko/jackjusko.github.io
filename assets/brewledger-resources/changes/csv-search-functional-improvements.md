# CSV Search – Functional Improvements

## Overview

Implemented the functional improvement plan for the CSV Search tool: column sorting, pagination, export to CSV, delimiter detection, Inventory "Below reorder" summary, and preset-aware inline charts (replacing the standalone Visualize mode).

## Changes

### 1. Column Sorting

- Click any column header to sort by that column; click again to toggle ascending/descending.
- Sort indicator (▲/▼) shown in the active column header.
- Numeric columns are sorted numerically; others lexicographically.
- `sortedRows` computed from `filteredRows`; `displayLimit` applies to sorted result.

### 2. Pagination / Show More

- Default display: first 50 rows (was 40).
- "Load 50 more" button when there are more rows than shown; increases visible count by 50.
- `displayLimit` resets to 50 when loading a new file or clearing.

### 3. Export Filtered to CSV

- "Download CSV" button in toolbar.
- Exports **all** filtered and sorted rows (not just the visible page) with headers.
- RFC-style escaping (quotes and commas); delimiter matches current parse delimiter (effective delimiter).
- Filename: `{source-name}-{YYYY-MM-DD}.csv` when from upload, else `brewledger-csv-export-{date}.csv`.

### 4. Inventory Preset: Below Reorder Summary

- When view mode is Inventory Audit, a "Below reorder" summary table appears above the data table.
- Columns: Product, Current stock, Reorder point, Shortage (reorder − stock).
- Sorted by shortage descending; one-glance reorder list.
- Product column inferred from headers (product, item, sku, name, etc.).

### 5. Delimiter Auto-Detection and Override

- Before parsing, first 1–2 lines are scanned (outside quotes) for comma, semicolon, and tab counts.
- If tabs dominate → tab; else if semicolons > commas → semicolon; else comma.
- Parsing uses `parseCsv(text, delim)` with the detected or overridden delimiter.
- Toolbar shows a "Delimiter" dropdown when data is loaded: **Auto (comma|semicolon|tab)** or manual **Comma**, **Semicolon**, **Tab**.
- Changing the override re-parses from stored raw text (`csvRawText`). Export uses the same delimiter.

### 6. Preset-Aware Inline Charts (Visualizer Rework)

- **Removed**: Standalone "Visualize" mode (Category/Value dropdowns, full-page bar/line chart).
- **Added**: Per-preset "Chart" toggle in each summary box:
  - **Distributor Sales**: Inline bar chart of Top Sellers (product vs quantity).
  - **Hop Contract**: Inline bar chart of poundage by variety.
  - **Inventory Audit**: Inline bar chart of Below reorder items (product vs shortage).
- Charts use the same summary data as the tables; compact SVG, no extra column picking.
- Toggle label: "Chart" / "Hide chart"; charts hidden in print (`no-print`).

## Technical Notes

- Sort and display limit reset on new load/clear; delimiter override is not cleared (user choice persists until new file).
- `isColNumeric(colIdx)` used for sort type; sample-based like previous numeric detection.
- All logic remains in `CsvSearch.vue`; no new dependencies or routes.
