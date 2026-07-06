# TTB Form Preview: Show Columns b–e for Lines 1 and 33

**Task:** Update the TTB form preview so Lines 1 and 33 show the column breakdown (a) plus (b) Cellar Bulk, (c) Racking Keg, (d) Bottling Bulk, (e) Case when that data exists.

**File to edit:** `platforms/console/src/components/TTBFormPreview.vue`

**Context:** `TTBFormService.generateForm()` returns `formData.columnsByLine.line1` and `formData.columnsByLine.line33`, each with `{ a, b, c, d, e }` in barrels. The preview currently only shows a single "Amount (Barrels)" column (column a). Expose b–e for those two lines so users can verify TTB staging.

**Requirements:**

1. Keep the existing table for additions (lines 1–13) and removals (lines 14–34) with Line, Description, and one amount column.
2. For **Line 1** (additions) and **Line 33** (removals) only: if `formData.columnsByLine?.line1` or `formData.columnsByLine?.line33` exists, show extra columns for (b), (c), (d), (e) — e.g. add columns "Cellar (b)", "Racking Keg (c)", "Bottling Bulk (d)", "Case (e)" with the same barrel formatting (`toFixed(2)`). Use the existing `formatBarrels`-style formatting.
3. For all other lines, keep current behavior (single amount = column a).
4. Optional: show column (a) explicitly for line 1 and 33 from `columnsByLine.line1.a` / `columnsByLine.line33.a` so the first column stays consistent; if `columnsByLine` is missing for that line, fall back to `formData.additions.line1` / `formData.removals.line33` as today.

**Reference:** `changes/ttb-form-and-pdf-column-review.md` (why b–e matter); data shape in `platforms/console/src/services/TTBFormService.js` (`columnsByLine` in the return value of `generateForm()`).
