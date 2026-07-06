## Removals UI Refresh – Feature Analysis (Iteration 1)

### Current pain points
- Form stretches full width and vertically stacks every field, leading to excessive scroll and weak grouping.
- Recent removals table sits far below the fold and lacks a card shell consistent with other pages.
- No quick context about TTB classification or available quantity; guidance is buried in helper text.
- Actions/filters are absent; there is no visual anchor at the top of the page.
- Density is uneven: some fields could share a row (item/location, quantity/purpose) without clutter.

### Risks / edge cases
- Collapsing fields into grids could harm readability on small screens if breakpoints are too aggressive.
- Cards must remain concise to avoid clutter and respect light/dark parity.
- Table height should be capped to avoid another long scroll while keeping columns legible.

### Proposed adjustments
- Add a concise toolbar/header with context and a quick hint about TTB classifications.
- Use a responsive grid to place “Record Removal” and “In-Bond Receipt” cards side by side on large screens, stacking on mobile.
- Inside forms, use two-column layouts for compatible fields (item/location, quantity/purpose, date/tax) and keep notes full width.
- Add a card shell for recent removals with capped height and data-table styling for consistency.
- Surface available quantity and helper hints inline with metadata pills instead of long paragraphs.

---

## Removals UI Refresh – Feature Analysis (Iteration 2)

### What changed after iteration 1
- Added console toolbar with TTB context and quick “last 30 days” anchor.
- Split the two forms into a responsive two-column grid; tightened field layouts into paired rows to reduce scroll.
- Introduced meta pills for available quantity and compliance, reused shared input/button styles, and converted the recent table to a card with capped height and data-table styling.

### Remaining observations / risks
- Available quantity pill shows a placeholder until both item and location are selected; make the placeholder explicit.
- Toolbar pills are static (not wired to filters); acceptable for now but should not imply active filtering.

### Follow-up tweaks to apply now
- Clarify the available-quantity pill when data is not ready.
- Keep the layout uncluttered: avoid adding more controls; rely on existing helper copy.
