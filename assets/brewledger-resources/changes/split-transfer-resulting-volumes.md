# Split / Transfer / Combine: Resulting Volumes (Volume In ≠ Volume Out)

## Summary

Split and combine operations previously assumed volume in equals volume out. Volumes can change during transfer (loss to trub, evaporation, spillage; or addition e.g. top-up). This change lets users set the **resulting volume(s)** at the end of a transfer or combine.

## Requirements

- **Split (1 → Many)**: User enters the **resulting volume** at each destination vessel. These can be less than source (loss), equal, or more than source (e.g. dilution). Source is reduced by the sum of destination volumes; if that sum exceeds source, source goes to zero (all transferred out).
- **Combine (Many → 1)**: Optional **resulting volume at destination**. If provided, the destination vessel is set to that volume; if omitted, behavior is unchanged (destination = sum of sources, or existing + sum when destination already had volume).

## Implementation

### Backend (BatchLocationRepository, both console and brewledger-app)

1. **transferSplit**
   - Removed validation that `sum(destinations.volume) <= source.current_volume`.
   - Destination volumes are treated as **resulting volumes**: each destination split is set to the given volume (not added). Source is reduced by `sum(destinations.volume)`; `newSourceVol = max(0, sourceVol - destSum)` so if sum exceeds source, source goes to zero.
   - When updating an existing destination split (same vessel), we now **set** `current_volume` to the given volume instead of adding to it, so the user’s value is the final volume at that vessel.

2. **combineSplits**
   - Added optional parameter `destinationVolume`.
   - If `destinationVolume` is provided and >= 0, the destination split’s `current_volume` is set to that value (for both new and existing destination). Otherwise, behavior is unchanged (new: totalVolume; existing: existing + totalVolume).

### UI (BatchDetail.vue, both console and brewledger-app)

1. **Split mode**
   - Label: "Destinations (resulting volume at each vessel)".
   - Removed client-side validation that sum of destination volumes cannot exceed source.
   - Hint text: "Source: X [unit]. Enter resulting volume per destination (can differ due to loss or addition)."

2. **Combine mode**
   - Added optional field: "Resulting volume at destination (optional)" with placeholder "Leave blank to use sum of sources".
   - Form state: `combineDestinationVolume: null`; reset in `openSplitTransferModal`.
   - On save, pass `destinationVolume: forms.splitTransfer.combineDestinationVolume` when set (number >= 0 or user input); otherwise `undefined`.

## Edge Cases Considered

- **Split with sum(dest) > source**: Allowed. Source goes to zero; extra volume at destinations is recorded (e.g. top-up with water).
- **Split with sum(dest) < source**: Source keeps the remainder (implicit loss).
- **Combine with destinationVolume < 0**: Backend ignores (treats as not provided); default behavior used.
- **Combine with empty optional field**: `undefined` passed; backend uses sum of sources (or existing + sum).
- **Existing destination vessel in split**: We set that vessel’s split to the entered volume (overwrite), not add. So the value is always the resulting volume at that vessel.

## Integration

- No API or schema changes; client-only repository and UI.
- Sync: batch_locations updates (create/update/delete) are already synced; no change to sync flow.
- TTB / reporting: batch location volumes are source of truth; no special handling.

## First-Iteration Review (Potential Weak Points)

1. **total_theoretical_volume**: Batch’s `total_theoretical_volume` is not recalculated when splits change. If it’s used elsewhere (e.g. display, reporting), it may drift. Mitigation: existing code already uses sum of batch_locations for display in many places (e.g. BatchesList, displayTotalVolume); total_theoretical_volume is often from creation. Consider whether a batch-level “total” should be updated on transfer/combine—currently not done.
2. **Combine destinationVolume when destination is one of the sources**: The UI does not allow selecting the same vessel as both source and destination (user selects sources by checkbox and a separate destination dropdown). So destination is either new or an existing vessel that is not in the source list. When it’s existing, we set volume to `destinationVolume` (if provided) or existing + totalVolume. No bug.
3. **Negative or zero destination volumes in split**: Backend skips `vol <= 0`; UI allows min="0". Zero is valid (vessel gets nothing). Negative is not sent as a positive volume; if user forces negative, backend skips that row. Acceptable.
4. **Unused computed (splitTransferDestSum)**: Still computed in both UIs but no longer used in template for validation. Could remove for cleanliness; leaving it does not affect behavior.

## Second-Iteration Additions

1. **total_theoretical_volume**: Confirmed that BatchDetail and list views use `displayTotalVolume` / sum of batch_locations or `total_theoretical_volume ?? planned_volume`. Batch table’s `total_theoretical_volume` is not updated on every split/combine; that’s consistent with “theoretical” (original plan). No change.
2. **Remove unused splitTransferDestSum**: Optional cleanup; leaving it in place in case future UI wants to show “Sum of destination volumes” again. Documented in analysis.
3. **Combine: destination same as a source**: Logic is correct; destination is a single vessel, sources are multiple; no overlap in current UI.

## Files Touched

- `platforms/console/src/repositories/BatchLocationRepository.js`: transferSplit, combineSplits
- `platforms/brewledger-app/src/repositories/BatchLocationRepository.js`: transferSplit, combineSplits
- `platforms/console/src/views/BatchDetail.vue`: split/combine modal labels, combine field, validation removal, openSplitTransferModal, saveSplitTransfer
- `platforms/brewledger-app/src/views/BatchDetail.vue`: same

## analysis.md Updates

- **BatchLocationRepository**: transferSplit no longer validates sum ≤ source; destinations are resulting volumes; source reduced by sum, min 0. combineSplits accepts optional destinationVolume.
- **Mobile UI / Console**: Split/Transfer modal: split uses “resulting volume” per destination (no sum ≤ source check); combine has optional “Resulting volume at destination”.
