# TTB Form Calculation and I/O Audit

**Date:** 2026-02-11  
**Scope:** TTBFormService calculations, period boundaries, validation, PDF export, and data flow for reliability.  
**References:** `ttb-beer-ledger-design.md`, `TTB-BEER-LEDGER-IMPLEMENTATION-LOG.md`, `changes/ttb-reporting-diagnostic.md`, `changes/ttb-form-and-pdf-column-review.md`

---

## 1. Audit Plan: Potential Issues Considered

### A. Date and period boundaries
- **A1** Beginning inventory (Line 1): Should include only entries **before** period start (`created_at < periodStart`). If `endDate: periodStart` is inclusive, entries at exactly midnight of period start would be counted in “beginning” and again in-period → double-count.
- **A2** Line 1 columns b–e (`getBeerOnhandByStage(periodStart)`): Same boundary; “beginning of period” must use strictly before period start.
- **A3** In-period queries: Use `startDate`/`endDate` with period end set to end-of-day (23:59:59.999) in TTBForm.vue → verified correct.

### B. Data sources and consistency
- **B1** Ledger `data.source === 'production_complete'`: Line 2 uses `entry.data.source`; server stores full entity in `data`; BatchDetail creates RECEIVE with `data.source = 'production_complete'` → consistent.
- **B2** Beer items: `ItemRepository.getBeerItems()` uses `category === 'Finished Beer'`; TTB filters by beer item IDs → correct.
- **B3** Ledger date field: All period filtering uses `created_at`. Reporting is by **creation** date, not a separate “occurred_at” on ledger entries (occurred_at exists on milestones/variances). Documented as current behavior.

### C. Calculation correctness
- **C1** Line 13 = sum of lines 1–12; line12 = 0 → correct.
- **C2** totalRemovals = sum of lines 14–32; line33 = line13 − totalRemovals; line34 = line13 → correct.
- **C3** validateFormData: Missing or non-numeric keys could produce NaN and break comparisons → harden with defensive access and Number().
- **C4** Line 31 (shortage): Variance `delta_qty` is negative; `beerQuantityBarrels()` uses Math.abs → positive shortage amount reported → correct.
- **C5** Line 6 (beer received from cellars): Heuristic (TRANSFER_IN, no racking, no note return/cellar). Left as-is; documented.

### D. Double-count prevention
- **D1** Line 4 vs 24: Line 4 = TRANSFER_IN with `operation_type === 'racking'` only; Line 24 = TRANSFER_IN with note return/cellar, **excluding** racking → mutually exclusive (per ttb-reporting-diagnostic).
- **D2** Line 14 vs 21: On-premises consumption excluded from line14 (`if (!onPremises) removals.line14 += quantity`); line21 counts only consumption with premises/on-site → no double-count.
- **D3** Line 20 vs 28: `unfit` is not added to line20 (case `unfit`: break); line28 counts destruction/unfit → no double-count.

### E. Units
- **E1** Beer ledger and variance: Use `beerQuantityBarrels()` (no gallonsToBarrels) per ttb-reporting-diagnostic → correct.
- **E2** Line 3 (water/liquid): batch_additions quantity in gallons → `gallonsToBarrels()` → correct.
- **E3** Packaging: `volume_bottled` in barrels when present; unit-based estimates use `gallonsToBarrels()` → correct.

### F. PDF and output
- **F1** formatBarrels: Handles null/undefined/NaN and clamps negative to 0 → correct.
- **F2** formatPeriod / formData.header: If `formData` or `header` is missing, PDF fill or data-only PDF could throw → guard with optional chaining and defaults.
- **F3** Data-only PDF: Uses `formData.additions?.['line'+i]` and `formData.removals?.['line'+i]` → safe. (Columns b–e for lines 1/33 in data-only PDF are a separate enhancement per ttb-form-and-pdf-column-review.)

### G. Edge cases
- **G1** Empty beer items: getBeerItemIds() returns empty Set; beer-filtered calculations return 0 or [] → correct.
- **G2** getOrgId() null: Calculations return 0 or [] as appropriate → correct.
- **G3** validateFormData with missing/invalid formData: Can produce NaN or throw → add null check and defensive add/rem helpers.
- **G4** Location without stage: getBeerOnhandByStage defaults to `'cellar'` → correct.
- **G5** Ledger entry without location_id: Previously aggregated into “cellar” by default. Now **skipped** in stage aggregation (only entries with `location_id != null` go into byLocation) so columns b–e are not inflated by orphan entries; column (a) still comes from full beginning/ending inventory.

### H. Entry types in inventory
- **H1** RECEIVE, TRANSFER_IN, TRANSFER_OUT, CONSUME: Handled explicitly.
- **H2** REVERSAL: Implemented as same type with negated quantity → already reflected in totals.
- **H3** COUNT_ADJUST / CORRECTION: If present with signed quantity, beginning inventory and getBeerOnhandByStage now include them via `else { total += Number(entry.quantity) || 0 }` and the same in byLocation delta.

---

## 2. Fixes Applied

### 2.1 TTBFormService.js

1. **Beginning inventory (Line 1) – period boundary**  
   - After `getEntries({ endDate: periodStart })`, filter to `entriesBeforePeriod = allEntries.filter(e => e.created_at < periodStart)` and sum over that list.  
   - Ensures “on hand at beginning of period” does not include entries at the first moment of the period.

2. **Beginning inventory – other entry types**  
   - Added `else { total += Number(entry.quantity) || 0 }` so COUNT_ADJUST, CORRECTION, or any other type with signed quantity is included.

3. **getBeerOnhandByStage – optional exclusive end**  
   - New second parameter `opts = { inclusiveEnd: true }`.  
   - When `inclusiveEnd === false`, filter entries to `created_at < asOfDate` (for Line 1 “beginning of period”).  
   - Line 1 columns b–e: `getBeerOnhandByStage(periodStart, { inclusiveEnd: false })`.  
   - Line 33 columns b–e: `getBeerOnhandByStage(periodEnd, { inclusiveEnd: true })`.

4. **getBeerOnhandByStage – other types and null location**  
   - Delta for RECEIVE/TRANSFER_IN is +qty; TRANSFER_OUT/CONSUME is −qty; else `delta = Number(entry.quantity) || 0`.  
   - Only add to `byLocation` when `locId != null` so entries without location_id do not affect columns b–e.

5. **validateFormData – defensive**  
   - Early return with error if `!formData || !formData.additions || !formData.removals`.  
   - Helpers `add(key)` and `rem(key)` use `Number(formData.additions[key]) || 0` (and removals) so missing or non-numeric keys do not produce NaN.  
   - Negative/value checks use `Number(value)` and `Number.isNaN(v)` where appropriate.

### 2.2 TTBPDFExportService.js

1. **fillPDFForm – header**  
   - `const header = formData?.header || {}` and use `header` for reportYear, reportType, and formatPeriod so missing header does not throw.

2. **formatPeriod**  
   - If `!header` return `''`.  
   - Use `(header.period || 1) - 1` with `Math.max(0, …)` and `?? ''` so invalid period does not produce undefined.

3. **generateDataOnlyPDF**  
   - Use `breweryInfo?.brewery_name` and `breweryInfo?.ttb_brewery_number`.  
   - `const header = formData?.header || {}` and `formatPeriod(header)` and `header.year ?? ''` so missing formData/header does not throw.

---

## 3. Items Verified (No Code Change)

- Line 4 vs 24 and Line 14 vs 21 and Line 20 vs 28 mutual exclusivity (see D1–D3).
- Units: beer in barrels, water in gallons converted (see E1–E3).
- Line 13, line33, line34 formulas and totalRemovals sum.
- formatBarrels and beerQuantityBarrels behavior.
- Empty beer items and null getOrgId() handling.
- Location stage default `'cellar'`.

---

## 4. Known Limitations (Documented, Not Changed)

- **Reporting date:** Period filtering uses ledger `created_at`; there is no separate “occurred_at” on ledger entries. If entries are backdated, creation date is still used for period inclusion.
- **Line 6 (beer received from cellars):** Heuristic (TRANSFER_IN without racking and without note “return”/“cellar”). May not match every brewery’s categorization.
- **Line 5 (in bond) / Line 29 (DSP):** Return 0 until ledger has explicit classification.
- **Data-only PDF:** Does not yet include columns b–e for lines 1 and 33 (see ttb-form-and-pdf-column-review.md).

---

## 5. Files Touched

- `platforms/console/src/services/TTBFormService.js`: beginning inventory boundary and entry types; getBeerOnhandByStage inclusiveEnd and null location_id; validateFormData defensive.
- `platforms/console/src/services/TTBPDFExportService.js`: header and formatPeriod guards; optional chaining for breweryInfo and formData.header.

---

## 6. Summary

Audit covered period boundaries, double-count rules, units, validation robustness, and PDF input handling. Fixes ensure beginning inventory and Line 1 columns b–e use a strict “before period start” boundary; Line 33 remains inclusive of period end; validation and PDF export tolerate missing or malformed data; and entries without location do not distort stage columns. Other entry types (e.g. COUNT_ADJUST) are included in beginning inventory and stage totals when present.
