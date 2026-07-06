# TTB Column Breakdowns: Data Tracking Implementation Plan

**Date:** 2026-02-11  
**Goal:** Track the data needed in BrewLedger so we can fill TTB Form 5130.9 column breakdowns (b–g) for movement lines 2–12 and 14–32, not just lines 1 and 33.

**References:** `ttb-beer-ledger-design.md`, `TTBFormService.js`, `LedgerRepository.js`, `LocationRepository.js`, `changes/ttb-form-and-pdf-column-review.md`, `changes/ttb-final-pdf-mapping.md`.

---

## 1. Current State

### What we have today

- **Lines 1 and 33:** Column breakdown (b–e) is already computed via `getBeerOnhandByStage(asOfDate)`. It sums beer on hand by location, maps each location to a stage (`cellar` | `racking_keg` | `bottling_bulk` | `case`), and returns totals per stage. Data source: ledger entries + location `stage`.
- **Locations:** Each location has a `stage` (default `cellar`). Settings → Locations allows setting TTB stage per location.
- **Ledger entries:** Every RECEIVE, CONSUME, and TRANSFER has a `location_id`. For transfers, we create two entries: TRANSFER_OUT with `location_id = fromLocationId`, TRANSFER_IN with `location_id = toLocationId`. So we have **from** and **to** location (and thus stage) for every transfer.
- **Line totals (column a):** All movement lines (2–12, 14–32) are computed from ledger, packaging runs, and variance events; we return a single total per line. No per-column breakdown is returned for those lines yet.

### What we need

- For each **movement line** (2–12, 14–32), we need to know how much volume falls into each **fillable** column (b, c, d, e, f as applicable; g = total). The official form has grayed-out cells per line; we must only fill white cells (see design doc “non-fillable columns” table).
- Data flow: **Every beer movement** (RECEIVE, CONSUME, TRANSFER, packaging, variance) should be attributable to a **stage** (or from-stage → to-stage) so we can aggregate by column.

---

## 2. Data Model Readiness

| Data source              | Has location/stage? | Notes |
|--------------------------|---------------------|--------|
| Ledger RECEIVE           | Yes (`location_id`) | Production complete → cellar. Other RECEIVEs have location. |
| Ledger CONSUME            | Yes (`location_id`) | Removals: we have location → stage for “removed from” stage. |
| Ledger TRANSFER_OUT / IN | Yes (OUT=from, IN=to) | Pair by `transfer_group_id` to get (from_stage, to_stage). |
| Packaging runs           | No `location_id`   | Runs have batch_id, format, volume_bottled. No source/dest location. |
| Variance events          | Yes (`location_id`) | Overage/shortage at a location → stage. |

Conclusion: **Ledger and variance already have what we need.** Packaging runs do not yet have location/stage; we have two options: (1) add optional `location_id` (source location) to packaging runs and/or (2) infer stage from operation (e.g. keg run → dest = racking_keg; bottle/can → dest = case) and optionally link run to a ledger TRANSFER that has from/to.

---

## 3. TTB Line → Stage Mapping (Fillable Columns Only)

From the design doc and form layout, which columns are **fillable** per line (grayed-out columns are omitted):

| Line | Fillable columns | Movement / data source |
|------|------------------|-------------------------|
| 2    | b, g             | Beer produced → RECEIVE to cellar (all in b). |
| 3    | b, g             | Water/liquid additions → cellar (b). |
| 4    | b, g             | Beer from racking/bottling → by destination stage (c,d,e,f then g). |
| 5    | b, d, f, g       | In bond → multiple stages possible. |
| 6    | c, e, g          | Beer from cellars → by destination stage. |
| 7, 8 | b, d, f, g       | Returns → by destination stage. |
| 9    | d, g             | Racked → destination racking (c/d); we have racking_keg → d. |
| 10   | f, g             | Bottled → destination case (f). |
| 11   | b, c, d, e, f, g | Overage → by variance location stage. |
| 12/13| b–g              | Totals / blank; 13 = sum of 1–12. |
| 14   | d, f, g          | Removed for consumption/sale → by CONSUME location stage. |
| 15/16| b, d, f, g       | Tavern / export → by CONSUME location stage. |
| 17   | d, f, g          | Supplies → by CONSUME location stage. |
| 18, 19| b, d, f, g      | R&D / other brewery → by CONSUME location stage. |
| 20   | b, g             | Unfit → by CONSUME location stage. |
| 21   | b, d, f, g       | Consumed on premises → by CONSUME location stage. |
| 22, 23| b, g             | Transferred for racking/bottling → by TRANSFER_OUT location (from) stage. |
| 24   | c, e, g          | Returned to cellars → by TRANSFER_IN (to) stage. |
| 25   | c, g             | Beer racked (removal side) → we use 0; Line 22 is the transfer. |
| 26   | e, g             | Beer bottled (removal side) → by packaging or transfer. |
| 27–31| b, c, d, e, f, g | Samples, destroyed, DSP, losses, shortage → by CONSUME/variance location stage. |
| 33   | b–g              | Already implemented (on-hand by stage). |
| 34   | b–g              | Total beer; same as 33 for our purposes or sum. |

So the **tracking** we need is: for every movement that feeds a line, we must know either (a) a single stage (e.g. RECEIVE to location → that location’s stage), or (b) from-stage and to-stage (e.g. TRANSFER_OUT from cellar, TRANSFER_IN to racking_keg).

---

## 4. Implementation Phases

### Phase 1: Ensure all beer movements have stage context (audit + small fixes)

**1.1 Ledger**

- **RECEIVE:** Already has `location_id` → stage. Ensure production-complete RECEIVEs use a cellar location (or document that they do). No schema change.
- **CONSUME:** Already has `location_id` → “removed from” stage. No change.
- **TRANSFER:** We have OUT (from) and IN (to). Add a small helper in TTBFormService (or shared util) that, given a transfer pair (same `transfer_group_id`), returns `from_stage` and `to_stage` using LocationRepository stage. No schema change.

**1.2 Variance events**

- Already have `location_id` → stage. No change.

**1.3 Packaging runs**

- **Option A (minimal):** Do not add location to runs. For Line 9 (racked): treat all keg volume as “to racking_keg” (column d). For Line 10 (bottled): treat all bottle/can volume as “to case” (column f). We lose “from” stage unless we later link runs to ledger.
- **Option B (recommended for accuracy):** Add optional `source_location_id` to packaging runs (or store in `data`). When recording a packaging run, user (or system) selects source location (e.g. cellar or bottling bulk). Then we can attribute Line 9/10 by from-stage and to-stage.
- **Option C:** When creating a packaging run, also create a ledger TRANSFER (e.g. cellar → racking_keg for keg; bottling_bulk → case for bottle). Then Line 9/10 can be computed from ledger by transfer type and stage, and packaging run remains a separate record for units/cases. This keeps one source of truth (ledger) for TTB column breakdown.

Recommendation: **Phase 1 implement Option A** (infer stage from operation type for packaging) so we can ship column breakdown for ledger-driven lines without schema change. **Phase 2** add Option B or C for packaging if we want accurate 9/10 breakdown.

---

### Phase 2: Compute per-line, per-column amounts in TTBFormService

**2.1 Helpers**

- `getLocationStageMap()`: Return `Map<locationId, stage>` for the org (from LocationRepository).
- `getTransferPairStages(transferGroupId, entries)`: Given ledger entries with the same `transfer_group_id`, return `{ fromStage, toStage }` using OUT entry’s location and IN entry’s location.

**2.2 Line calculators return breakdown where applicable**

For each line that has fillable columns other than just (a) or (g):

- **Line 2 (beer produced):** Sum RECEIVE with `data.source === 'production_complete'` by `location_id` → stage. All should be cellar (b). Return `{ total, byStage: { b, g } }`.
- **Line 3 (water):** Same idea; by location → stage (cellar b).
- **Line 4 (received from racking/bottling):** TRANSFER_IN with operation_type racking/bottling; use `to_stage` (destination). Aggregate by stage → columns b,c,d,e,f then g.
- **Lines 5–8:** Similar: identify entries that feed the line, then aggregate by destination (or source) stage per form rules.
- **Line 9 (racked):** Today from packaging runs (KEG). Option A: all to `racking_keg` → column d only. Option B/C: from ledger TRANSFERs (cellar → racking_keg) or runs with source location.
- **Line 10 (bottled):** Same: packaging runs (BOTTLE/CAN) → case (f); or from ledger.
- **Line 11 (overage):** Variance events with `variance_type === 'overage'`; group by `location_id` → stage. Return byStage for b,c,d,e,f,g.
- **Removals (14–21, 27–31):** CONSUME entries; group by `location_id` → stage. For each removal line (by purpose/note), return `{ total, byStage }` for that line’s fillable columns only.
- **Line 22 (transferred for racking):** TRANSFER_OUT with operation_type racking; use **from** location stage (b). Same for Line 23 (bottling).
- **Line 24 (returned to cellars):** TRANSFER_IN (return/cellar); use **to** location stage (c,e if applicable).
- **Lines 25, 26:** Racked/bottled removal side; can be 0 and d/e/g from ledger if we ever split.

**2.3 Form data shape**

- Extend `formData.columnsByLine` from `{ line1, line33 }` to include movement lines that have breakdown, e.g.:
  - `columnsByLine.line2 = { a, b, g }` (only fillable)
  - `columnsByLine.line9 = { a, d, g }`
  - `columnsByLine.line14 = { a, d, f, g }`
  - etc.
- Keep `additions.lineN` and `removals.lineN` as the total (column a or row total) for backward compatibility. Preview and PDF already have field names (2b, 2g, 9d, 14d, 14f, 14g, etc.); we just fill them when `columnsByLine.lineN` is present.

**2.4 Non-fillable columns**

- When building `byStage`, only populate keys for columns that are **fillable** for that line (see design doc table). Do not write to grayed-out columns. PDF and preview only render fields that exist in the template; we simply don’t set values for columns we’re not supposed to fill.

---

### Phase 3: UI and validation (optional but recommended)

- **Settings → Locations:** Already have TTB stage. Ensure all locations used for beer have a stage set (warn if default “cellar” is used for keg/case locations).
- **Gap detection:** Extend `detectDataGaps()` to warn when movement lines have no breakdown (e.g. CONSUME with no location_id, or packaging run with no source location if we add it).
- **Preview:** Already shows b–e for lines 1 and 33. When we add `columnsByLine` for other lines, we can extend the preview to show breakdown for those lines (e.g. line 9, 10, 14) in the same way.

---

### Phase 4: PDF and export

- **TTBPDFExportService:** Already has field names for 2b, 2g, 3b, 4b, 9d, 9g, 10f, 10g, 11b–11g, 14d, 14f, 14g, …, 33b–33g, 34b–34g. Once `formData.columnsByLine` includes those lines, extend `fillPDFForm()` to set each field from `formData.columnsByLine.lineN.<col>` when present. Respect the form’s column layout (e.g. 33b=cellar, 33c=0, 33d=racking_keg, 33e=bottling_bulk, 33f=case, 33g=total) as already implemented.

---

## 5. Suggested Order of Work

1. **Phase 1.1–1.2:** Audit ledger + variance; add `getLocationStageMap` and `getTransferPairStages` (or equivalent) in TTBFormService. No API or schema change.
2. **Phase 2.2 (pilot):** Implement column breakdown for **Line 2** (beer produced) and **Line 14** (removed for consumption/sale). Both are high-value and straightforward: Line 2 = RECEIVE by location stage (all b); Line 14 = CONSUME by location stage for purpose sale/consumption. Return `columnsByLine.line2` and `columnsByLine.line14` from `generateForm()`.
3. **Phase 4 (pilot):** In TTBPDFExportService, fill 2b, 2g and 14d, 14f, 14g from the new columnsByLine. Verify in ttb-final.pdf.
4. **Phase 2.2 (expand):** Add breakdown for remaining movement lines in order of business value (e.g. 9, 10, 11, then 15–21, 22–26, 27–31). Each line: identify entries, group by stage, build only fillable columns.
5. **Phase 1.3 (packaging):** Decide Option A vs B vs C for packaging runs; implement chosen option so Line 9/10 have correct column attribution.
6. **Phase 3:** Location validation and gap warnings; extend preview for movement-line breakdown if desired.

---

## 6. Summary

| Item | Action |
|------|--------|
| **Ledger** | Already has location_id and transfer from/to. Use it to derive stage for RECEIVE, CONSUME, TRANSFER. |
| **Variance** | Already has location_id. Use for Line 11 byStage. |
| **Packaging** | No location today. Phase 1 use inference (keg→d, bottle→f); Phase 2 optional add source location or ledger TRANSFER. |
| **TTBFormService** | Add helpers (stage map, transfer pair stages). For each movement line, aggregate by stage and return only fillable columns in `columnsByLine.lineN`. |
| **Form data** | Extend `columnsByLine` to line2–line32 (and 34) where applicable. |
| **PDF / Preview** | Fill existing ttb-final.pdf fields from columnsByLine; extend preview table for movement lines when data exists. |

This plan tracks the data needed for TTB column breakdowns inside the existing BrewLedger model (locations.stage + ledger location_id and transfer pairs). The main work is in TTBFormService: per-line aggregation by stage and exposing results in `columnsByLine` for the PDF and preview to consume.
