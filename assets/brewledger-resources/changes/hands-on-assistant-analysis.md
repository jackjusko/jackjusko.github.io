# Hands-on Assistant Feature Analysis

## Iteration 1 (current state)
- **Action parsing**: Added JSON action extraction (plain JSON or ```json blocks) and system prompt hints. Regex corrected to avoid double-escaping. Frontend shows action cards with run controls.
- **Handlers**: Executor supports set_par_level, adjust_onhand, record_batch_reading, adjust_batch_volume, forecast_item with best-effort name/ID resolution and sync kick-off.
- **UI**: Assistant view renders action cards with run/dismiss, and posts result messages.

### Risks / gaps
- **Styling tokens**: Action status badges use `text-success-600/text-danger-600` which may not exist in the console palette; prefer safe Tailwind greens/reds to avoid missing styles.
- **Forecast signal**: Forecast uses only CONSUME entries; transfers/negative adjustments also drive depletion and should be included so projections match on-hand trends.
- **Volume target selection**: Batch location resolver falls back to the first split when no name/id is given; mildly risky but acceptable for MVP. No change needed now.

### Planned fixes after review
1) Swap status colors to Tailwind-safe green/red/neutral classes.  
2) Expand forecast consumption to include negative quantities across ledger entries (CONSUME, TRANSFER_OUT, COUNT_ADJUST negatives) so depletion matches reality.

### Fixes applied after iteration 1
- Updated action status styling to use Tailwind-safe green/red/blue text classes.
- Forecast now counts any negative quantity (plus CONSUME/TRANSFER_OUT positives) within the horizon, improving depletion projections.

## Iteration 2
- Reviewed forecast inputs for NaN/huge horizons; clamped days to 1–180 with a 30-day default before calculating cutoff to avoid invalid dates and silent zeroing.
- No additional UI regressions found; action cards remain dismissible and reuse existing Markdown rendering.
