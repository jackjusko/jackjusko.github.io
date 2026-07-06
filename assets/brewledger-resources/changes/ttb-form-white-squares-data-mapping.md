# TTB Form 5130.9 – White Squares vs Data Collection

**Date:** 2026-02-11  
**Purpose:** Map every fillable (white) field on TTB Form 5130.9 to data collected or calculated in `platforms/console/`, `platforms/brewledger-app/`, and `server/`. Grey squares are not applicable and are excluded.

**Reference:** Form images (Part 1 Beer Summary, Part 1 continued + Prior Period Adjustments + Certification + Part 2 Cereal Beverage + Part 3 Remarks).

---

## I. Header – Brewery Information and Reporting Period

| Field | Collected / Source | Where |
|-------|---------------------|--------|
| Brewery name | ✅ Yes | `server`: `orgs.name` (GET/PUT brewery-info). Console: Settings → Brewery Information. |
| Number & Street | ✅ Yes | `orgs.brewery_address_street` |
| City | ✅ Yes | `orgs.brewery_address_city` |
| County | ✅ Yes | `orgs.brewery_address_county` |
| State | ✅ Yes | `orgs.brewery_address_state` |
| ZIP Code | ✅ Yes | `orgs.brewery_address_zip` |
| Reporting period – year | ✅ Yes | TTB Form view (console): year selector; stored in `formData.header.year` |
| Monthly report – month | ✅ Yes | Month selector when report type = monthly; `formData.header.period` (1–12) |
| Quarterly report – quarter | ✅ Yes | Quarter checkboxes (Jan–Mar, Apr–Jun, etc.); `formData.header.reportType` + `period` (1–4) |

**Gap:** EIN is collected (`orgs.brewery_ein`) and used in PDF export; the form image may also show EIN/TTB number – we have `ttb_brewery_number` and `brewery_phone` in server and PDF. **No header gap** for the fields visible in the images.

---

## II. Part 1 – Beer Summary Table (Lines 1–34)

Table columns on the form: **(a) Operations**, **(b) Cellar**, **(c) Racking – Bulk**, **(d) Racking – Keg**, **(e) Bottling – Bulk**, **(f) Bottling – Case**, **(g) Totals**.

Our implementation uses four stage columns: **Cellar (b), Racking Keg (c), Bottling Bulk (d), Case (e)**. We do **not** split “Racking – Bulk” vs “Racking – Keg” or “Bottling – Bulk” vs “Bottling – Case” as separate columns. So if the official form has six sub-columns (b)–(f), we currently map to four (b–e) and do not populate (f) or a fifth/sixth stage. See **Column mapping** below.

### Additions (Lines 1–13)

| Line | Description | Column (a) | Columns (b)–(g) | Data source |
|------|-------------|------------|------------------|-------------|
| 1 | On hand beginning of period | ✅ Calculated | ✅ b–e for Line 1 only (Line 33 from last period) | TTBFormService: `calculateBeginningInventory`; `getBeerOnhandByStage(periodStart, { inclusiveEnd: false })`. Ledger (beer items, `created_at < periodStart`). |
| 2 | Beer produced by fermentation | ✅ Calculated | ❌ Only (a) filled | RECEIVE with `data.source === 'production_complete'`. Console + mobile: BatchDetail “Mark Production Complete” creates RECEIVE. |
| 3 | Addition of water and other liquids | ✅ Calculated | ❌ Only (a) | `batch_additions` with event_type WATER_ADDITION / LIQUID_ADDITION. Console: BatchDetail “Add Water/Liquid”. |
| 4 | Beer received from racking and bottling | ✅ Calculated | ❌ Only (a) | Ledger TRANSFER_IN, `operation_type === 'racking'`. Console: Racking view. |
| 5 | Beer received in bond | ✅ Structure (0) | ❌ Only (a) | No classification yet; returns 0. Would need ledger/transfer classification. |
| 6 | Beer received from cellars | ✅ Calculated | ❌ Only (a) | Ledger TRANSFER_IN (heuristic: no racking, no return/cellar note). |
| 7 | Beer returned after removal from this brewery | ✅ Calculated | ❌ Only (a) | Ledger RECEIVE/TRANSFER_IN with `return_of_ledger_id`. |
| 8 | Beer returned from another brewery same ownership | ✅ Calculated | ❌ Only (a) | Ledger RECEIVE with `related_brewery_id`. |
| 9 | Racked | ✅ Calculated | ❌ Only (a) | Packaging runs (KEG) + volume. Console: Racking view; BatchDetail packaging. |
| 10 | Bottled | ✅ Calculated | ❌ Only (a) | Packaging runs (BOTTLE/CAN) + volume_bottled. Console: BatchDetail packaging. |
| 11 | Physical inventory disclosed an overage | ✅ Calculated | ❌ Only (a) | Variance events, `variance_type === 'overage'`, beer items. Console: variance/count; mobile: count session. |
| 12 | (Blank) | ✅ 0 | — | Hardcoded 0. |
| 13 | Total additions | ✅ Calculated | ✅ b–e only for Line 1; (g) not computed per column | Sum of lines 1–12. |

### Removals (Lines 14–34)

| Line | Description | Column (a) | Columns (b)–(g) | Data source |
|------|-------------|------------|------------------|-------------|
| 14–20 | Removals by purpose (sale, tavern, export, supplies, R&D, other brewery, unfit) | ✅ Calculated | ❌ Only (a) | Ledger CONSUME, `removal_purpose`. Console: Removals view. Mobile: TTB removal purpose when implemented. |
| 21 | Beer consumed on premises | ✅ Calculated | ❌ Only (a) | CONSUME, purpose consumption + note premises/on-site. |
| 22 | Beer transferred for racking | ✅ Calculated | ❌ Only (a) | TRANSFER_OUT, `operation_type === 'racking'`. Console: Racking. |
| 23 | Beer transferred for bottling | ✅ Calculated | ❌ Only (a) | TRANSFER_OUT, operation_type bottling or note. |
| 24 | Beer returned to cellars | ✅ Calculated | ❌ Only (a) | TRANSFER_IN, note return/cellar, exclude racking. |
| 25 | Beer racked | ✅ 0 (removal side) | ❌ Only (a) | By design: removal side = 0; Line 22 captures transfer for racking. |
| 26 | Beer bottled | ✅ 0 (removal side) | ❌ Only (a) | By design: Line 23 captures transfer for bottling. |
| 27 | Laboratory samples | ✅ Calculated | ❌ Only (a) | CONSUME, purpose sample or note sample/lab. |
| 28 | Beer destroyed at brewery | ✅ Calculated | ❌ Only (a) | CONSUME, purpose destruction/unfit or note destroy/dispose. |
| 29 | Beer transferred to DSP | ✅ Structure (0) | ❌ Only (a) | CONSUME, `removal_purpose === 'dsp_transfer'`. No UI default; can be set if supported. |
| 30 | Losses, including theft | ✅ Calculated | ❌ Only (a) | CONSUME loss_theft or note; Losses view (console). |
| 31 | Physical inventory disclosed a shortage | ✅ Calculated | ❌ Only (a) | Variance events, shortage, beer items. |
| 32 | (Blank) | ✅ 0 | — | Hardcoded 0. |
| 33 | Total beer on hand end of period | ✅ Calculated | ✅ b–e for Line 33 | line13 − totalRemovals; `getBeerOnhandByStage(periodEnd, { inclusiveEnd: true })`. |
| 34 | Total beer | ✅ Calculated | ❌ Only (a) | = Line 13. |

**Summary Part 1:**  
- **Column (a)** for all lines 1–34: we have data and calculations; PDF export and data-only PDF fill (a).  
- **Columns (b)–(e)** for lines 1 and 33 only: we compute and fill from location stage (cellar, racking_keg, bottling_bulk, case).  
- **Column (f)** and **(g)** on the form: we do not currently compute or fill (f) or column totals (g). Our design doc uses (b)–(e) plus (a); the form image shows (b)–(f) and (g).  
- **Movement lines (2–12, 14–32):** We do not compute or fill (b)–(f) per line; design deferred “movement lines per-column.”

---

## III. Column Mapping: Form vs Implementation

- **Form (from images):** (a) Operations, (b) Cellar, (c) Racking – Bulk, (d) Racking – Keg, (e) Bottling – Bulk, (f) Bottling – Case, (g) Totals.  
- **Our stages:** `cellar`, `racking_keg`, `bottling_bulk`, `case` (four stages).  

Reasonable mapping today: our **cellar → (b)**, **racking_keg → (c) or (d)** (we don’t split Bulk vs Keg), **bottling_bulk → (e)**, **case → (f)**. So we can fill (b), (c), (d), (e) for lines 1 and 33 if the PDF has four stage columns; if the form has six, we’d need either a fifth/sixth stage in the data model or a convention (e.g. put racking_keg in (d) and leave (c) blank). **Action:** Confirm with the actual fillable PDF field names (e.g. via `list-pdf-form-fields.mjs`) and align TTBPDFExportService and, if needed, location stages.

---

## IV. Prior Period Adjustments (Lines 35–36)

| Field | Collected / Calculated | Where |
|-------|------------------------|--------|
| 35. Additions to beer inventory: (+) | ❌ No | Not in TTBFormService or PDF. |
| 35. Additions to beer inventory: (-) | ❌ No | Not in TTBFormService or PDF. |
| 36. Removals from beer inventory: (+) | ❌ No | Not in TTBFormService or PDF. |
| 36. Removals from beer inventory: (-) | ❌ No | Not in TTBFormService or PDF. |

**Gap:** Prior period adjustments are **not** collected or exported. They would require either manual entry on the form or new fields (e.g. prior period addition/removal adjustments) in the app and in form data/PDF.

---

## V. Certification

| Field | Collected / Calculated | Where |
|-------|------------------------|--------|
| Signature | ❌ No | Not stored in server or console. |
| Title | ❌ No | Not stored. |
| Date (signed) | ❌ No | Not stored. |

**Gap:** Certification is **not** collected in the app. Users must sign/date on paper or in a PDF editor after export.

---

## VI. Part 2 – Cereal Beverage Summary (Items 1–6)

| Field | Collected / Calculated | Where |
|-------|------------------------|--------|
| 1. Produced | ❌ No (0) | `formData.cerealBeverages.line1 = 0`; no tracking of &lt;0.5% ABV production. |
| 2. Removed | ❌ No (0) | `formData.cerealBeverages.line2 = 0`. |
| 3. Received | ❌ No (0) | `formData.cerealBeverages.line3 = 0`. |
| 4. Loss and wastage | ❌ No (0) | `formData.cerealBeverages.line4 = 0`. |
| 5. (Blank) | ✅ 0 | Hardcoded. |
| 6. Total on hand end of period | ❌ No (0) | `formData.cerealBeverages.line6 = 0`. |

**Gap:** Cereal beverage (products &lt;0.5% ABV) is **not** tracked. No items, ledger, or packaging dedicated to cereal beverage; no UI to enter these amounts. Form data and PDF would need cereal beverage fields and, if we support it, data model + UI.

---

## VII. Part 3 – Remarks

| Field | Collected / Calculated | Where |
|-------|------------------------|--------|
| Remarks (free text) | ⚠️ Structure only | `formData.remarks = ''` in TTBFormService; no UI in console or mobile to set remarks; PDF export does not write remarks. |

**Gap:** Remarks are **not** user-editable in the app and are not filled on export. Would need a text field on the TTB form view and mapping in TTBPDFExportService.

---

## VIII. Summary – Can We Fill All White Squares?

| Section | Status | Notes |
|---------|--------|--------|
| **Header** | ✅ Yes | Brewery info in server/console; period in TTB form view. |
| **Part 1 Lines 1–34, column (a)** | ✅ Yes | All lines calculated from ledger, packaging, variance; console + mobile feed data. |
| **Part 1 Lines 1 & 33, columns (b)–(e)** | ✅ Yes | From location stage; only 4 stages vs form’s possible 6 columns (b)–(f); (g) totals not computed. |
| **Part 1 Lines 2–32, columns (b)–(g)** | ❌ No | Movement-line column breakdown deferred; (f) and (g) not in our model. |
| **Prior period adjustments (35–36)** | ❌ No | Not in app or PDF. |
| **Certification** | ❌ No | Signature, title, date not collected. |
| **Part 2 Cereal beverage** | ❌ No | All zeros; no tracking or UI. |
| **Part 3 Remarks** | ❌ No | No UI or PDF mapping. |

**Conclusion:** We collect enough to fill **header**, **Part 1 column (a) for all 34 lines**, and **Part 1 columns (b)–(e) for lines 1 and 33 only**. We do **not** currently support: prior period adjustments (35–36), certification, Part 2 cereal beverage, Part 3 remarks, column (f)/(g) for the table, or per-line (b)–(f) for movement lines. Aligning the form’s six sub-columns (b)–(f) with our four location stages may require either extending the stage model or a fixed mapping when filling the PDF.
