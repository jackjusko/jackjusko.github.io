# Feature Analysis: TTB Preview Columns b–e (First Iteration)

**Task:** Implement `changes/ttb-preview-columns-b-e.md` — show columns (b) Cellar Bulk, (c) Racking Keg, (d) Bottling Bulk, (e) Case for Lines 1 and 33 in TTBFormPreview.vue.

**Implementation:** `platforms/console/src/components/TTBFormPreview.vue` updated to conditionally show extra column headers and cells when `formData.columnsByLine.line1` or `formData.columnsByLine.line33` exists.

---

## 1. Implementation Summary

- **Additions table:** When `hasLine1Columns` (i.e. `formData.columnsByLine?.line1`), header shows "Amount (a)" plus "Cellar (b)", "Racking Keg (c)", "Bottling Bulk (d)", "Case (e)". Only the Line 1 row gets five numeric cells (a,b,c,d,e); other rows get one amount cell plus four empty cells so column count matches.
- **Removals table:** Same for Line 33 with `hasLine33Columns` and `formData.columnsByLine.line33`.
- **Fallback:** Column (a) for line 1/33 uses `getLine1Amount` / `getLine33Amount`: `columnsByLine.line1.a` or `line33.a` when present, else `formData.additions.line1` / `formData.removals.line33`.
- **Formatting:** All barrel values use existing `formatBarrels` (0 → "0.00", else `Number(value).toFixed(2)`).

---

## 2. Potential Issues & Edge Cases

### 2.1 Data shape and safety

- **columnsByLine optional:** The template only accesses `formData.columnsByLine.line1.b/c/d/e` and `formData.columnsByLine.line33.b/c/d/e` when `hasLine1Columns` / `hasLine33Columns` is true, which requires `columnsByLine?.line1` / `columnsByLine?.line33`. So we never read `.line1` or `.line33` when undefined. Safe.
- **Missing b/c/d/e on line1/line33:** If TTBFormService ever returns `columnsByLine.line1` with only `a` (e.g. partial object), `formatBarrels(undefined)` would yield `"NaN"` (Number(undefined).toFixed(2)). Mitigation: ensure TTBFormService always returns full { a, b, c, d, e } for line1 and line33 (already does). Optional hardening: in the component, use `formatBarrels(formData.columnsByLine.line1?.b ?? 0)` etc. for b–e to avoid NaN display.

### 2.2 Table layout and accessibility

- **Empty cells for non–line1/line33:** Rows 2–13 (additions) and 14–32, 34 (removals) get four empty `<td></td>` when the extra columns are shown. This keeps column alignment correct. Screen readers will hear empty cells; acceptable for a data table. No need for "—" or "0.00" in those cells per spec (other lines keep single amount).
- **Colspan not used:** We use multiple `<td>`s rather than colspan so that (a) and (b)–(e) columns align across rows. Correct.

### 2.3 Consistency with TTBFormService

- **Always present:** `generateForm()` always returns `columnsByLine: { line1: {...}, line33: {...} }` (see TTBFormService.js). So in practice `hasLine1Columns` and `hasLine33Columns` will almost always be true when formData is from generateForm. If formData were ever from another source (e.g. stub), the fallback to single column is correct.

### 2.4 Responsive / overflow

- **Horizontal scroll:** The Additions/Removals tables are already inside `overflow-x-auto` divs, so extra columns will scroll on narrow viewports. No change needed.

---

## 3. Recommendations for Second Pass

1. **Harden b–e display:** Use optional chaining and nullish coalescing for b, c, d, e when rendering (e.g. `formatBarrels(formData.columnsByLine.line1?.b ?? 0)`) so that partial or future data shapes never show "NaN".
2. **Leave table structure as-is:** No colspan; empty cells for non–line1/line33 when extra columns are shown is correct for alignment and matches the spec.
3. **No change to TTBFormService:** Data shape is already correct; no backend change required.

---

## 4. First-Iteration Fix Applied

- **b–e NaN hardening:** Template updated to use `formData.columnsByLine.line1?.b ?? 0` (and same for c, d, e and for line33) so that missing or partial column data never produces `formatBarrels(undefined)` → "NaN". `formatBarrels(0)` already returns `"0.00"`.

---

## 5. Second Iteration Review

### 5.1 Data and fallbacks

- **getLine1Amount / getLine33Amount:** Use `props.formData.columnsByLine?.line1?.a ?? fallback` and `.line33?.a ?? fallback`. When `hasLine1Columns`/`hasLine33Columns` is true we know the line object exists, but `.a` could theoretically be missing; fallback to additions/removals value is correct.
- **Empty columnsByLine:** If `formData.columnsByLine` is `{}` or absent, both flags are false; tables show single "Amount (Barrels)" column and no extra headers. Correct.
- **Stale/cached formData:** Same as above; no crash, graceful single-column display.

### 5.2 UI and consistency

- **Header label:** When extra columns are shown, first column is "Amount (a)" to match TTB column (a); when not shown, "Amount (Barrels)" is unchanged. Matches spec.
- **Empty cells:** Other lines get four empty `<td>` when b–e columns are present; column count is consistent and table alignment is correct.

### 5.3 Integration

- **TTBForm.vue:** Passes `form-data="formData"`; formData comes from `TTBFormService.generateForm()`, which always returns `columnsByLine.line1` and `line33`. No change required.
- **analysis.md:** Updated with a bullet under TTB Beer Ledger describing form preview columns b–e and referencing this change doc.

### 5.4 No further code changes

- No colspan or layout change; no change to TTBFormService or PDF export. Feature is complete after first-iteration hardening.

---

## 6. Summary

Implementation meets the spec: Lines 1 and 33 show (a) plus (b)–(e) when `columnsByLine` exists, with correct fallback for (a) and single-column behavior for other lines. Hardening (b–e default to 0 via `?.` and `?? 0`) is applied. Second pass confirms data safety, fallbacks, and integration; no additional code changes. Documentation is in `analysis.md` and `changes/ttb-preview-columns-b-e.md`.
