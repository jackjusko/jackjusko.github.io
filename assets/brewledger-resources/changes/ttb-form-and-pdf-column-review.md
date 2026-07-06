# TTB Form System and PDF Column Review

**Date:** 2026-02-11  
**Scope:** TTB form generation and PDF export on desktop console; alignment with `ttb-beer-ledger-design.md` and "fill all light boxes" goal.  
**References:** `ttb-beer-ledger-design.md`, `TTB-BEER-LEDGER-IMPLEMENTATION-LOG.md`, `ttb.pdf` (platforms/console/public/), `changes/ttb-pdf-export-fix.md`, `changes/ttb-beer-ledger-implementation.md`

---

## 1. Design Goals (Recap)

- **TTB Form 5130.9**: Rows 1–34, columns **(a) Operations, (b) Cellar Bulk, (c) Racking Keg, (d) Bottling Bulk, (e) Case, (f)–(g) totals**.
- **Goal:** Populate all **fillable** "light boxes" from tracked operations (beer-as-items, batch linkage, location staging).
- **Non-fillable cells:** Per design, certain line/column combos are greyed out on the official form; we must only write to fillable cells.
- **Data sources:** Ledger (beer RECEIVE/CONSUME/TRANSFER), packaging runs, variance events, location stage → columns b–e.

---

## 2. Current Implementation vs Goals

### 2.1 What Is Implemented

| Area | Status | Notes |
|------|--------|------|
| Column (a) all lines | ✅ | TTBFormService generates additions.line1–line13, removals.line14–line34; PDF fill and data-only use them. |
| Columns b–e Lines 1 & 33 | ✅ Generated, ⚠️ not fully exposed | `getBeerOnhandByStage()` → `columnsByLine.line1` and `line33` with a,b,c,d,e. Used only when **filling a template**; see gaps below. |
| Columns b–e movement lines | ❌ Deferred | Design and implementation log: "Movement lines per-column deferred". Lines 2–12, 14–32 have no b–e breakdown. |
| Column (f)/(g) totals | ❌ Not generated/filled | No computation or field mapping for totals columns. |
| Fillable template | ⚠️ Depends on PDF | If ttb.pdf has AcroForm fields, we try variants (`line_1_a`, `1a`, `Line1a`, etc.). |
| Data-only fallback | ✅ Used when 0 fields | When `form.getFields().length === 0`, we generate a data-only PDF. |

### 2.2 Gaps That Affect "Correct Columns Getting Filled"

1. **Template has no fillable fields (current ttb.pdf)**  
   - Per `changes/ttb-pdf-export-fix.md`, `ttb.pdf` has **no AcroForm fields** (flat PDF). So every export uses the **data-only** path.
   - The data-only PDF shows **only one value per line** (column (a)). It does **not** show the column breakdown (b, c, d, e) for Lines 1 and 33, even though we compute and have `formData.columnsByLine.line1` and `formData.columnsByLine.line33`.

2. **Data-only PDF ignores columns b–e for Lines 1 and 33**  
   - `generateDataOnlyPDF()` only uses `formData.additions?.['line' + i]` and `formData.removals?.['line' + i]` (single value per line).
   - It never reads `formData.columnsByLine.line1` or `formData.columnsByLine.line33`, so Cellar/Racking Keg/Bottling Bulk/Case are never shown in the fallback PDF.

3. **Preview does not show columns b–e**  
   - `TTBFormPreview.vue` has a single "Amount (Barrels)" column. It does not show (b)–(e) for Lines 1 and 33, so users cannot verify column staging in the UI.

4. **Fillable template field names unknown**  
   - If a fillable ttb.pdf is introduced later, actual field names may differ from our variants. The script `platforms/console/scripts/list-ttb-pdf-fields.mjs` can be run on the real template to list names and align mappings.

5. **Totals (f)/(g)**  
   - Design mentions (f)–(g) as totals. We do not compute or map them; would require TTB rules per line for which totals are fillable.

6. **Desktop vs mobile**  
   - Form **generation** and **PDF export** live on the **desktop console** (TTBFormService, TTBPDFExportService). Mobile is being brought to parity for **data collection** (removals, racking, production complete, etc.). So "correct columns not filled" is not due to migration from app to desktop; it’s due to the above logic and PDF behavior on the console.

---

## 3. Recommendations

1. **Data-only PDF: show columns b–e for Lines 1 and 33**  
   - In `generateDataOnlyPDF()`, after the single-column line list (or in a small table), add Lines 1 and 33 with columns (a) and (b)–(e) from `formData.columnsByLine.line1` and `formData.columnsByLine.line33` so the fallback PDF reflects all generated column data.

2. **Preview: show columns b–e for Lines 1 and 33**  
   - In `TTBFormPreview.vue`, for Line 1 and Line 33, show (a) and (b)–(e) when `formData.columnsByLine` is present (e.g. extra columns or a small sub-table) so users can confirm staging.

3. **Verify fillable template (when available)**  
   - When a fillable ttb.pdf is in use, run `node platforms/console/scripts/list-ttb-pdf-fields.mjs` and add any missing field name variants in `TTBPDFExportService.js` so all intended cells (including line_1_b/c/d/e, line_33_b/c/d/e) map correctly.

4. **Movement lines (b–e) and totals (f)–(g)**  
   - Leave as future work unless product priority changes: design explicitly deferred movement-line column breakdown; (f)/(g) need TTB-specific rules and possibly layout checks on the real form.

---

## 4. Summary

- **Column (a)** for all 34 lines is generated and used in both fill and data-only PDF.
- **Columns b–e for Lines 1 and 33** are generated in TTBFormService and used only on the **fill path**; they are **not** shown in the **data-only PDF** or in the **preview**, so the "correct columns" are not fully visible with the current flat ttb.pdf.
- Fixing the data-only PDF and the preview to include b–e for Lines 1 and 33 will align behavior with the design and make column staging visible end-to-end on the desktop console.
