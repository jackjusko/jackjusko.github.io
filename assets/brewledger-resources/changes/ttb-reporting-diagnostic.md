# TTB Form 5130.9 Reporting – Diagnostic

## Summary

Review of all TTB-related calculation logic found **incorrect units** (ledger/variance treated as gallons then converted, but they are stored in **barrels**), **double-counting** between lines (same TRANSFER_IN or CONSUME counted in multiple lines), and a **period boundary** nuance. Recommended fixes are listed and implemented where critical.

---

## 1. Units: Ledger and variance already in barrels

### Finding

- **Removals.vue**: Labels "Quantity (Barrels)" and stores `quantity: -Math.abs(form.quantity)`.
- **Racking.vue**: Labels "Quantity Racked (Barrels)"; transfer uses that quantity.
- **BatchDetail.vue** (production complete): Creates RECEIVE with `quantity: volumeBarrels`.
- **Losses.vue**: Uses same `form.quantity` for both ledger CONSUME and variance `delta_qty`.

So beer **ledger** quantities (CONSUME, TRANSFER_IN, TRANSFER_OUT, RECEIVE) and **variance** `delta_qty` from these flows are stored in **barrels**.

`TTBFormService` currently does:

- `calculateBeginningInventory` / `calculateBeerProduced`: use raw `entry.quantity` (correct for barrels).
- All other ledger-based calculations: wrap with `gallonsToBarrels(Math.abs(entry.quantity))`.
- Variance-based calculations (Lines 11, 30, 31): use `gallonsToBarrels(Math.abs(variance.delta_qty))`.

Applying `gallonsToBarrels` (÷31) to values already in barrels **understates** removals, transfers, and variances by a factor of 31.

### Correct convention

- **Ledger entries** (beer): quantity is in **barrels** → use `Math.abs(entry.quantity)` (no conversion).
- **Variance events** (beer): `delta_qty` is in **barrels** when from Losses/ledger flow → use `Math.abs(delta_qty)` (no conversion).
- **Batch additions** (Line 3 – water/liquid): quantity is in **gallons** → keep `gallonsToBarrels(quantity)`.
- **Packaging runs**: keep `volume_bottled` as barrels when present; keep `gallonsToBarrels(units_count * ...)` when estimating from units.

### Fix

In `TTBFormService.js`, for all **beer ledger** and **variance** calculations, use quantity/delta_qty in barrels directly (no `gallonsToBarrels`). Only Line 3 (water additions) and packaging run unit-based estimates should use `gallonsToBarrels`.

---

## 2. Double-counting: TRANSFER_IN in Line 4 vs Line 24

### Finding

- **Line 4** (beer received from racking and bottling): `TRANSFER_IN` where `operation_type === 'racking'` **or** `note` includes `'return'`.
- **Line 24** (beer returned to cellars): `TRANSFER_IN` where `note` includes `'return'` **or** `'cellar'`.

Any `TRANSFER_IN` with `note` containing "return" is counted in **both** Line 4 and Line 24.

### Fix

Make Line 4 and Line 24 mutually exclusive, e.g.:

- **Line 4**: `TRANSFER_IN` with `operation_type === 'racking'` only (returns from racking). Do **not** key off `note` "return" for Line 4, or exclude entries that will be counted in Line 24.
- **Line 24**: `TRANSFER_IN` with note "return" or "cellar" but **exclude** those already counted in Line 4 (e.g. exclude `operation_type === 'racking'`), so "return from racking" is only Line 4.

Or: Line 4 = racking returns only (`operation_type === 'racking'`); Line 24 = other returns to cellars (note return/cellar and not operation_type racking).

---

## 3. Double-counting: CONSUME in Lines 14/15 vs 21, and 20 vs 28

### Finding

- **Line 21** (beer consumed on premises): CONSUME with `removal_purpose === 'consumption'` **and** (note contains "premises" or "on-site").
- **calculateRemovalsByPurpose**: same CONSUME with `removal_purpose === 'consumption'` goes to **line14**.

So a CONSUME with purpose `consumption` and note "on premises" is counted in **both line14 and line21**.

- **Line 28** (beer destroyed): CONSUME with `removal_purpose === 'destruction'` or `'unfit'` or note "destroy"/"dispose".
- **calculateRemovalsByPurpose**: `removal_purpose === 'unfit'` goes to **line20**.

So a CONSUME with purpose `unfit` is counted in **both line20 and line28**.

### Fix

- **Line 21**: Count only CONSUME that are "on premises" consumption. **Exclude** from line14 those that are counted in line21 (e.g. in `calculateRemovalsByPurpose`, if purpose is `consumption` and note indicates on-premises, add to a separate bucket and do not add to line14; then line21 uses that bucket). Or define line21 as a **subset** of line14 and document that line14 = total consumption/sale, line21 = subset on premises; then **total removals** must not add both line14 and line21 for the same volume. Per TTB, line21 is typically a subset; so line14 should count all consumption/sale and line21 the same volume that is on-premises, and we must not double-add. So: in **totalRemovals**, line21 should not be added if it’s already included in line14. Current code adds both → double count. Fix: either (a) exclude on-premises consumption from line14 and only count it in line21, or (b) don’t add line21 to totalRemovals if it’s a subset of line14. Option (a) is cleaner: in `calculateRemovalsByPurpose`, for purpose `consumption`, if note has "premises" or "on-site", do **not** add to line14; then line21 counts those. So line14 + line21 total is correct.
- **Line 20 vs 28**: Same CONSUME with `removal_purpose === 'unfit'` must not be in both. Either: (a) line20 = unfit for sale (removed for manufacturing), line28 = destroyed at brewery; or (b) count `unfit` only in line28 and not in line20. TTB: Line 20 = "Removed without payment of tax as beer unfit for sale removed for use in manufacturing"; Line 28 = "Beer destroyed at brewery". So unfit-for-sale can be line20 (if for manufacturing) or line28 (if destroyed). If we don’t distinguish, we should put unfit in one place only. Simplest: put `unfit` only in **line28** (beer destroyed) and **exclude** `unfit` from line20 in `calculateRemovalsByPurpose`, so line20 is only other manufacturing-use cases if we ever add them.

---

## 4. Line 6 (beer received from cellars) overlap with Line 4 and 24

### Finding

- **Line 6**: `TRANSFER_IN` where `!entry.operation_type || entry.operation_type === 'transfer'`.
- So a `TRANSFER_IN` with no `operation_type` is counted in Line 6. If that same entry has note "return" or "cellar", it is also counted in Line 4 or Line 24.

So one TRANSFER_IN with no operation_type and note "return to cellar" could be in **Line 6 and Line 24** (and possibly Line 4 if "return" is in note). Triple count.

### Fix

Make Line 6 exclusive of 4 and 24: e.g. Line 6 = TRANSFER_IN with no operation_type or operation_type === 'transfer', and **exclude** entries whose note contains "return" or "cellar" (so cellar-to-cellar is Line 6; returns are only 4 or 24).

---

## 5. Period end boundary (last day of month/quarter)

### Finding

`TTBForm.vue` sets:

- `periodEnd = new Date(form.year, form.period, 0)` (last day of month at **00:00:00** local).
- `periodEnd.toISOString()` is then used in filters `created_at <= periodEnd`.

Entries on the last day of the period with `created_at` after midnight (e.g. 10:00) may have `created_at > periodEnd` in ISO string comparison (depending on timezone), so they can be **excluded** from the period.

### Fix

Use end-of-day for the period’s last day, e.g. `new Date(form.year, form.period, 0, 23, 59, 59, 999)` or set periodEnd to the start of the **next** day and use `created_at < periodEnd` (exclusive end). Prefer one consistent convention (e.g. period end = start of next day, filter `created_at < periodEnd`) so the last day is fully included.

---

## 6. Beer bottled on both additions and removals (Line 10 / Line 26)

### Finding

Same as the previous beer-racked issue: **Line 26** (removals) is set to the same value as **Line 10** (additions) via `calculateBeerBottledRemoval` → `calculateBeerBottled`. So "beer bottled" appears on both sides.

Removal side for bottling is already represented by **Line 23** (beer transferred for bottling). So Line 26 should not duplicate Line 10; otherwise the same volume is removed twice (Line 23 and Line 26).

### Fix

Set **Line 26** to **0** (same approach as Line 25 for beer racked), and rely on Line 23 for the removal side of bottling.

---

## 7. getBeerOnhandByStage and ledger units

### Finding

`getBeerOnhandByStage` uses raw `entry.quantity` (no conversion), which is correct if ledger is in barrels. So column breakdown for Lines 1 and 33 is consistent with "ledger in barrels". The bug is only in the line calculations that incorrectly apply `gallonsToBarrels` to ledger/variance.

---

## 8. Summary of recommended code changes

| # | Issue | Action | Status |
|---|--------|--------|--------|
| 1 | Ledger/variance quantities in barrels but converted with gallonsToBarrels | Use beerQuantityBarrels (no conversion) for all beer ledger and variance; keep gallonsToBarrels only for Line 3 (water) and packaging unit estimates. | Done |
| 2 | Line 4 vs Line 24 double-count (TRANSFER_IN "return") | Line 4 = racking returns only (operation_type === 'racking'); Line 24 = other returns (note return/cellar), exclude operation_type === 'racking'. | Done |
| 3 | Line 6 overlap with 4/24 | Line 6: exclude TRANSFER_IN with note "return" or "cellar". | Done |
| 4 | Line 14 vs Line 21 (consumption) | calculateRemovalsByPurpose: do not add to line14 when purpose consumption and note on-premises; Line 21 counts those. | Done |
| 5 | Line 20 vs Line 28 (unfit) | Exclude `unfit` from line20; count only in line28. | Done |
| 6 | Line 26 = Line 10 (beer bottled both sides) | Set Line 26 to 0 (like Line 25). | Done |
| 7 | Period end boundary | Use end-of-day (23:59:59.999) for periodEnd so last-day entries are included. | Done |

---

## Files touched

- `platforms/console/src/services/TTBFormService.js`: Added beerQuantityBarrels(); units fix; Line 4/6/24 exclusivity; Line 14/21 and 20/28 exclusivity; Line 26 = 0.
- `platforms/console/src/views/TTBForm.vue`: periodEnd set to end of last day (23:59:59.999).
- `analysis.md`: link to this diagnostic and summarize fixes.

---

## Second pass (form generation logic review)

### 1. Line 30 double-count (loss_theft)

**Finding:** Losses.vue creates both a variance event (shortage + loss_type) and a CONSUME entry (removal_purpose: loss_theft) for the same loss. `calculateLosses` was summing both, so the same volume was counted twice on Line 30.

**Fix:** Line 30 now uses only CONSUME with removal_purpose === 'loss_theft' (ledger as single source). Variance shortage+loss_type is no longer added to Line 30.

### 2. Line 7 (beer returned after removal)

**Finding:** Line 7 summed any entry with return_of_ledger_id. CONSUME/TRANSFER_OUT with that field would have negative quantity; we use beerQuantityBarrels (abs), so we would still add a positive amount. Returns should be RECEIVE or TRANSFER_IN only.

**Fix:** Line 7 now counts only entries with type RECEIVE or TRANSFER_IN and return_of_ledger_id.

### 3. Default branch in calculateRemovalsByPurpose

**Finding:** Unclassified CONSUME (no removal_purpose) falls into default and is added to line14 or line15. If the note contains "sample", "lab", "destroy", "loss", etc., the same entry could also be counted in Line 27, 28, or 30 by note-based logic, causing double-count.

**Fix:** In the default branch, skip adding to line14/15 when the note suggests the entry belongs in Lines 27–30 (note includes sample, lab, destroy, dispose, loss, theft).

### 4. Optional enhancement (not implemented)

- **Reconciliation check:** Compare calculated Line 33 (line13 − totalRemovals) to the actual ledger-derived total at periodEnd (e.g. sum of getBeerOnhandByStage(periodEnd)). If they differ, surface a warning (e.g. "Ending inventory (Line 33) does not match ledger balance; check that all movements are classified."). Would require async validation or a separate check after generate.

---

## Third pass

### 1. Line 7 vs Line 4/24 (double-count)

**Finding:** A TRANSFER_IN with return_of_ledger_id could also have operation_type === 'racking' (Line 4) or note return/cellar (Line 24), so the same entry could be counted in Line 7 and Line 4 or Line 24.

**Fix:** Line 7 now excludes TRANSFER_IN that are already in Line 4 (operation_type racking) or Line 24 (note return/cellar). RECEIVE with return_of_ledger_id still counted in Line 7 only.

### 2. Line 30 unclassified loss

**Finding:** CONSUME with no removal_purpose but note "loss"/"theft" is skipped in default (noteHint) so not added to line14/15, and Line 30 only checked removal_purpose === 'loss_theft', so such entries were not counted anywhere.

**Fix:** Line 30 now also counts CONSUME with no removal_purpose when note includes 'loss' or 'theft'.

### 3. Negative Line 33

**Fix:** validateFormData now adds a warning when ending inventory (Line 33) is negative.

### 4. loss_theft in removals-by-purpose switch

**Finding:** removal_purpose 'loss_theft' had no case in the switch and fell to default; if note didn't contain "loss"/"theft", it would be added to line14/15 and also counted in Line 30 (double-count).

**Fix:** Added explicit case 'loss_theft': break (counted in Line 30 only).

---

## Fourth and fifth passes

No further issues found. Review covered: all CONSUME purposes explicitly handled or defaulted; Line 7 exclusivity with 4/24; Line 30 single source and unclassified-loss note fallback; validation warning for negative Line 33; loss_theft excluded from lines 14–20. **Fourth and fifth passes were virtually identical (no new changes).**
