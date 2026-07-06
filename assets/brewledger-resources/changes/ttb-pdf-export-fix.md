# TTB PDF Export – Preview Numbers Not on PDF (Fix)

**First iteration**: Root cause (no form fields in template; silent fill failures). Fix: data-only PDF fallback + field name variants + debug logging.  
**Second iteration**: Verified data consistency, optional chaining, pagination, and logging; no further code changes.

## Summary

TTB form preview numbers were correct on the TTB form screen, but nothing appeared on the exported PDF. Root causes: (1) the project’s `ttb.pdf` template has **no fillable form fields** (flat PDF), so there was nothing to fill; (2) the export service used a single fixed field-name mapping and swallowed all errors, so mismatched or missing fields produced an empty PDF with no feedback.

## Root Cause

- **Template**: `platforms/console/public/ttb.pdf` was inspected with pdf-lib; `form.getFields().length === 0` and `hasXFA === false`. So the PDF is a flat/non-fillable form. pdf-lib can only fill AcroForm text/checkbox fields; with zero fields, every `getTextField(name)` would fail and the catch blocks did nothing, so no data was written.
- **Mapping**: The service assumed field names like `line_1_a`, `line_2_a`, etc. Any template using different names (e.g. `1a`, `2a`) would also result in no fields being filled, with errors silently caught.

## Changes Made

### 1. Fallback when template has no form fields

- In `exportTTBFormToPDF`, after loading the template, the service checks `form.getFields().length`.
- If it is **0**, the service does **not** try to fill the template. Instead it calls `generateDataOnlyPDF(formData, breweryInfo)` to build a new PDF from scratch with pdf-lib:
  - One or more pages with a clear title (“TTB Form 5130.9 – Report Data (no fillable template)”).
  - Brewery name, TTB number, period.
  - All addition lines (1–13) and removal lines (14–34) with values in barrels (same formatting as preview).
  - Pagination when content overflows (e.g. second page for “Removals (continued)”).
- The user always gets a downloadable PDF that contains the same numbers as the on-screen preview when the template is non-fillable.

### 2. Robust filling when the template has form fields

- **Field name variants**: Replaced the single-name mapping with `getFormFieldNameVariants()` that returns, for each logical key (e.g. `line1a`, `breweryName`), an array of candidate PDF field names (e.g. `['line_1_a', '1a', 'Line1a']`). The code tries each candidate in order and uses the first that exists and is a text/checkbox field.
- **Filling logic**: `fillPDFForm` now uses a small `setText(key, value)` helper that tries each variant with `form.getTextField(name).setText(...)` and stops on first success. Checkboxes use a similar `checkBox(key)` with `getCheckBox`. This allows templates that use different naming conventions to still be filled.
- **Debugging**: If no fields are filled but the template reports `getFields().length > 0`, the service logs the first 50 actual field names to the console so developers can align the template or add variants. If the template has zero fields, it logs a short message that the template has no fillable form fields and that the data-only PDF was used.

### 3. Optional: list script for template inspection

- Added `platforms/console/scripts/list-ttb-pdf-fields.mjs` to load `public/ttb.pdf` and print all form field names and types. Run with: `node scripts/list-ttb-pdf-fields.mjs` from `platforms/console`. Useful to verify a new fillable template’s field names before adding variants.

## Files Touched

- `platforms/console/src/services/TTBPDFExportService.js`: fallback data-only PDF, field name variants, `setText`/`checkBox` helpers, export flow branch on `fieldCount === 0`, `generateDataOnlyPDF()`.
- `platforms/console/scripts/list-ttb-pdf-fields.mjs`: new script to list PDF form field names.
- `changes/ttb-pdf-export-fix.md`: this document.
- `analysis.md`: updated TTB PDF export description (see below).

## Constraints / Assumptions

- The data-only PDF is a summary layout (header + line list), not a replica of the official TTB form layout. For official submission, users can use a fillable TTB template with AcroForm fields named as in the variants (e.g. `line_1_a` or `1a`) so the service fills the actual form.
- pdf-lib does not support XFA. If the official TTB form is XFA-only, it would still have zero AcroForm fields; the fallback data-only PDF ensures the numbers are still exported.

## Second pass (feature analysis)

- **Data consistency**: `generateDataOnlyPDF` uses the same `formData.additions`/`formData.removals` and `formatBarrels` as the preview and the fillable-path, so values match.
- **Missing formData**: Optional chaining (`formData.additions?.line1`, etc.) is used in both fill and data-only paths to avoid runtime errors if structure is missing.
- **Brewery info**: Data-only PDF uses `breweryInfo` for name and TTB number only; address/phone could be added to the header in a follow-up if desired.
- **Pagination**: Removals loop switches to a new page when `y < 100` and draws “Removals (continued)” and remaining lines on the new page; no lines are dropped.
- **Console logging**: Warnings are limited to field-name logging and the “no fillable form fields” message; no noisy per-field failure logs.

All of the above are already reflected in the implementation. No further code changes from the second pass.
