# Receive inventory – console

## Iteration 1 analysis
- Data dependencies (locations/items) load silently; inputs disable but there is no explicit loading or retry affordance, so users can be confused or stuck if the fetch fails.
- Save guard relies on button disable, but line quantity/cost are not coerced before validation; `NaN` from cleared fields could slip past checks if values are stringy.
- Load errors are shown but do not prevent attempting a save, and there is no quick retry to refetch lists after a transient failure.

Planned changes after iteration 1
- Add an explicit loading state/notice and block the form while dependencies load.
- Coerce numeric inputs before validation to avoid `NaN` passing through.
- Surface a retry action and block submission when data failed to load.

## Iteration 2 analysis
- Start-new flow does not refresh items/locations; if an item/location is added elsewhere after the first receipt, the second receipt could be missing it until a hard reload.

Planned changes after iteration 2
- Refresh dependencies when starting a new receipt so item/location lists stay current.
