# CSV Search – Brewery Data Intelligence Upgrade

## Overview

Pivoted the CSV Search tool from a generic file viewer into a Brewery Data Intelligence utility with industry-specific presets, charting, shareable links, and print export.

## Features Implemented

### 1. Industry-Specific Presets (Smart Parser)

Column detection is case-insensitive and flexible (partial matches).

- **Distributor Sales**: Detects Product/Item/SKU, Quantity/Qty/Units, Unit Price columns. Shows "Top Sellers" summary—aggregate by product, sum quantity, optional revenue (qty × price). Top 15.
- **Hop Contract**: Detects Variety/Hop, Pounds/Lbs, Alpha Acid, Year columns. Shows by-variety summary with total lbs, avg alpha, year. Total poundage at bottom. Top 20 varieties.
- **Inventory Audit**: Detects Current Stock/On Hand/Quantity, Reorder Point/Par/Min columns. Rows where stock < reorder are highlighted in red (row background + cell emphasis).

View tabs appear only when the corresponding columns are detected. "Raw" is always available.

### 2. Dynamic Data Visualization

- **Visualize** button switches to chart view.
- **Category (X)** and **Value (Y)** selects—category from any header; value from auto-detected numeric columns.
- **Chart type**: Bar or Line.
- Numeric detection: columns with ≥3 parseable numbers in first 50 rows.
- Bar chart: grouped/aggregated by category, summed values. Line chart: same data as trend.
- SVG-based, no external chart library.

### 3. Shareable Results

- **Copy link** button (when CSV loaded from URL, not file upload).
- URL format: `/tools/csv-search?url=<encoded-csv-url>&q=<search-query>`.
- Recipient opens link → CSV loads from URL, search filter applied from `q` param.

### 4. Print-Friendly Export

- **Print** button triggers `window.print()`.
- Toolbar, view tabs, and action buttons hidden in print media.
- Table prints with current filters applied; clean layout for physical checklist.

## Not Implemented (Per Request)

- **Import to BrewLedger**: Explicitly excluded for now.

## Technical Notes

- All logic is self-contained in `CsvSearch.vue`; no backend or new routes.
- `colIndex(headers, ...patterns)` finds first column whose header includes any pattern (case-insensitive).
- Chart uses inline SVG with viewBox for responsiveness.
