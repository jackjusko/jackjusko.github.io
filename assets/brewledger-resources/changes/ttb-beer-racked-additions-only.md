# TTB: Beer Racked on Additions Only (Line 25 Fix)

## Issue
Beer racked was appearing on both **additions** (Line 9) and **removals** (Line 25) with the same value. `calculateBeerRackedRemoval()` was returning `calculateBeerRacked()`, so the same volume was counted in both sections and looked like double-counting.

## Root cause
- **Line 9 (additions)**: "Beer racked" — from packaging runs with format KEG (`calculateBeerRacked()`).
- **Line 25 (removals)**: Was set to the same value as Line 9.
- **Line 22 (removals)**: "Beer transferred for racking" — from ledger `TRANSFER_OUT` with `operation_type: 'racking'`.

The removal side of racking is already represented by **Line 22** (beer transferred for racking). Showing the same volume again as "Beer racked" on Line 25 caused "beer racked" to appear on both additions and removals.

## Change
- **TTBFormService**: `calculateBeerRackedRemoval()` now returns `0` instead of calling `calculateBeerRacked()`.
- "Beer racked" appears only in **additions** (Line 9).
- The removal from cellar for racking is represented only by **Line 22** (beer transferred for racking).

## Form balance
- Ending inventory (Line 33) = Line 13 (total additions) − total removals.
- Total removals no longer include Line 25, but do include Line 22.
- For the form to balance, record **beer transferred for racking** (ledger transfer with `operation_type: 'racking'`) so Line 22 captures the volume. Line 9 is still driven by packaging runs (KEG). If only packaging runs are logged and no transfer for racking, Line 9 will have value and Line 22 may be zero; in that case ending inventory can be overstated until transfers are logged.

## Files touched
- `platforms/console/src/services/TTBFormService.js`: `calculateBeerRackedRemoval()` returns 0 with comment.

## Note on Line 26 (Beer bottled)
The same pattern existed for beer bottled: Line 10 (additions) and Line 26 (removals) both used `calculateBeerBottled()`. This fix applies only to beer racked (Line 9 / Line 25). If beer bottled is ever reported on both sides and should show only in additions, the same approach can be used for Line 26 (return 0 from the removals-side calculator and rely on Line 23 for the removal side).

## Documentation
- `analysis.md`: Bug/fix log updated with this fix.
