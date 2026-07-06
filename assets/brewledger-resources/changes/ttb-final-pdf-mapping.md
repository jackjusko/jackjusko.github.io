# TTB Final PDF Mapping Implementation

**Date:** 2026-02-11  
**Task:** Update PDF export service to use `ttb-final.pdf` (fillable PDF with mapped field names) and correctly map all TTB form data to the PDF fields.

---

## What "Column Breakdowns" Mean

On the TTB form, each **line** (e.g. Line 1 "On hand beginning of this report period", Line 33 "Total amount of beer on hand at the end of this period") has **several columns**, not just one number:

- **(a) Operations** – The row label (e.g. "On hand beginning…").
- **(b) Cellar** – Beer in cellar/bulk.
- **(c) Racking Bulk** – Beer in bulk (racking stage).
- **(d) Racking Keg** – Beer in kegs after racking.
- **(e) Bottling Bulk** – Beer in bulk at bottling.
- **(f) Case** – Beer in cases (packaged).
- **(g) Totals** – Sum for that row.

So a "column breakdown" means: for that line we don’t only store one total; we store (or show) how much is in **each stage** (cellar, racking bulk, racking keg, bottling bulk, case). The form uses grayed-out cells for stages that don’t apply to that row; we only fill the white cells. In our app we currently have stage data only for **Line 1** (beginning inventory) and **Line 33** (end inventory) from location staging; other lines get a single total per line until we add per-stage movement data.

---

## Summary

Updated `TTBPDFExportService.js` to use the new `ttb-final.pdf` template which contains 144 fillable form fields with specific field names. The service now correctly maps brewery information, period data, and line 33 column breakdown (b-e) to the PDF fields.

---

## Changes Made

### 1. Updated PDF Template Loading

- Changed `loadTTBTemplate()` to load `/ttb-final.pdf` instead of `/ttb.pdf`
- Updated error messages to reference `ttb-final.pdf`

### 2. Field Name Mapping

Completely rewrote `getFormFieldNameVariants()` to map to actual field names in `ttb-final.pdf`:

**Header Fields:**
- `EIN` → brewery EIN
- `brew number` → TTB brewery number
- `brewery phone number` → brewery phone
- `brewery name` → brewery name
- `brewery address, number + street` → street address
- `brewery city` → city
- `brewery county` → county
- `brewery state` → state
- `brewery zip` → zip code
- `reporting period year` → report year
- `name of reporting month` → month name (for monthly reports)
- `Q1 checkbox`, `Q2 Checkbox`, `Q3 Checkbox`, `Q4 Checkbox` → quarter selection (for quarterly reports)

**Line Fields:**
- Mapped all available line/column combinations from the PDF (e.g., `2b`, `2g`, `11b`, `33b`, `33c`, `33d`, `33e`, etc.)
- Note: The PDF does not have column (a) fields for most lines; only specific columns (b, c, d, e, f, g) exist per line based on TTB form design

### 3. PDF Form Filling

Updated `fillPDFForm()` to fill available data:

**Currently Filled:**
- ✅ All header fields (brewery info, period, year, month/quarter)
- ✅ Line 33 columns b–g: (b) Cellar, (c) Racking Bulk = 0, (d) Racking Keg, (e) Bottling Bulk, (f) Case, (g) Totals (from `formData.columnsByLine.line33`; form layout per TTB F 5130.9)
- ✅ Remarks field (if present)

**Not Yet Filled (data not available):**
- Line 1 columns b-e (PDF doesn't have line 1 fields, or they may be calculated)
- Lines 2-32 column breakdowns (per design doc: "Movement lines per-column deferred")
- Column (f) and (g) totals (not computed yet)
- Lines 27-31, 34 column breakdowns (data not yet available)

### 4. Logging

- Updated console logging to reflect `ttb-final.pdf` usage
- Added success message showing number of fields filled

---

## Field Mapping Reference

The PDF contains 144 fillable fields. Key mappings:

| PDF Field Name | Data Source | Status |
|----------------|-------------|--------|
| `EIN` | `breweryInfo.brewery_ein` | ✅ Mapped |
| `brew number` | `breweryInfo.ttb_brewery_number` | ✅ Mapped |
| `brewery name` | `breweryInfo.brewery_name` | ✅ Mapped |
| `reporting period year` | `formData.header.year` | ✅ Mapped |
| `name of reporting month` | `formData.header` (monthly) | ✅ Mapped |
| `Q1 checkbox` - `Q4 Checkbox` | `formData.header.period` (quarterly) | ✅ Mapped |
| `33b`–`33g` | `formData.columnsByLine.line33` (b=cellar, c=0, d=racking_keg, e=bottling_bulk, f=case, g=sum) | ✅ Mapped |
| `remarks` | `formData.remarks` | ✅ Mapped |
| `2b`, `2g`, `3b`, etc. | Not yet available | ⏳ Future |
| `11b`-`11g`, `27b`-`27g`, etc. | Not yet available | ⏳ Future |

---

## Testing Notes

- The service will attempt to fill all mapped fields
- Fields that don't exist in the PDF or don't have data will be silently skipped (try/catch)
- If no fields are filled, a warning is logged with available field names for debugging
- If the PDF has no fillable fields, falls back to `generateDataOnlyPDF()`

---

## Future Enhancements

When column breakdown data becomes available for other lines (per TTB design doc), add mappings for:
- Lines 2-12, 14-32 column breakdowns (b-e)
- Column (f) and (g) totals
- Line 34 column breakdown

The field name mapping structure is already in place; just need to add the data mappings in `fillPDFForm()`.
