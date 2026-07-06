## Items List Card Refresh – Feature Analysis (Iteration 1)

### Goals
- Move the Items list away from wide tables to approachable cards inspired by the provided reference.
- Keep the UI uncluttered while surfacing key facts: name, category, on-hand quantity, and optional value.
- Retain search and the split between Ingredients and Finished Beer without forcing excessive scrolling.

### Findings / Pain Points
- Current view is two full-width tables; rows feel sparse and visually dated.
- There is no quick read on on-hand quantity or value for each item, requiring navigation elsewhere.
- Action affordance is a single “Edit” link per row; not obvious as a primary action.
- Density is inconsistent between Ingredients and Finished Beer (badge only on beer rows).

### Proposed Approach
- Replace tables with responsive card grids per section (Ingredients / Finished Beer).
- For each card: name + category pill, on-hand quantity, optional estimated value, unit, and a primary action link.
- Compute on-hand totals via `LedgerRepository.getAllOnhand()` to avoid per-row calls; derive value from `default_unit_cost` when present.
- Keep search box and empty state; avoid additional filters to prevent clutter.

### Risks / Edge Considerations
- On-hand/value data may be missing; need sensible fallbacks that do not mislead.
- Large item counts should still render efficiently; prefer using a single on-hand fetch.
- Keep dark-mode parity and avoid over-styled progress bars that imply thresholds we do not track.

---

## Items List Card Refresh – Feature Analysis (Iteration 2)

### Changes made after iteration 1
- Replaced both tables with responsive card grids for Ingredients and Finished Beer.
- Added on-hand and estimated value per item using a single aggregated fetch from `LedgerRepository.getAllOnhand()`.
- Introduced compact badges (unit pill) and clearer “Edit item” CTAs inside each card; category shows in subtitle.
- Added light/dark-friendly item icons and card spacing to match the referenced style without clutter.

### Remaining considerations / follow-ups
- Estimated value depends on `default_unit_cost`; when missing, we show an em dash to avoid implying accuracy.
- We do not show thresholds/progress bars to avoid misleading users without reorder data; can add later if thresholds become available.
- Large catalogs still render multiple cards; if performance lags, we may need pagination or virtual list in the future.
