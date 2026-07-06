# TTB Beer Ledger Implementation

**Design**: `ttb-beer-ledger-design.md`  
**Implementation log**: `TTB-BEER-LEDGER-IMPLEMENTATION-LOG.md` (root)

## Summary

Implemented beer-as-items ledger, batch linkage, and location staging so TTB Form 5130.9 can be populated from tracked operations (rows 1–34, column a; columns b–e for Lines 1 and 33). Builds on existing TTB implementation (column a only).

## Implemented

### 1. Beer item identification
- **Server**: On org registration, seed "Finished Beer" category (`is_system: true`) and single "Finished Beer" item (category "Finished Beer", unit bbl). Migration `server/migrate_ttb_beer_category.js` adds both for existing orgs.
- **CategoryRepository (mobile + console)**: Prevent delete when category name is "Finished Beer" or `is_system === true`.
- **ItemRepository**: `getBeerItems()` returns items where `category === 'Finished Beer'`.
- **TTBFormService**: `getBeerItemIds()`; beginning inventory (Line 1) and Line 2 (beer produced) filter to beer items only. Line 2 from RECEIVE with `data.source === 'production_complete'` (no milestone type).
- **Items UX**: Mobile ItemsList and console Inventory show "Ingredients" and "Finished Beer" sections; beers not in main ingredients list.

### 2. Production complete → RECEIVE + forced last milestone
- **BatchDetail (mobile + console)**: "Mark Production Complete" always creates a RECEIVE (beer item, cellar location, volume in barrels, `batch_id`, `data.source = 'production_complete'`). Then completes the **last** milestone definition (forced "Production Complete") for timeline/audit.
- **MilestoneTemplateRepository (mobile + console)**: `ensureForcedLastMilestone()` appends a system "Production Complete" milestone on template create/update. Exported `PRODUCTION_COMPLETE_LABEL`, `FORCED_LAST_MILESTONE`.
- **TTBFormService**: Line 2 = sum of RECEIVE entries (beer items, `data.source === 'production_complete'`). Gap detection uses RECEIVE count instead of FG_CONFIRMED milestones.

### 3. Batch on ledger
- **LedgerRepository.transfer (mobile + console)**: Optional `batchId`; both TRANSFER_OUT and TRANSFER_IN entries get `batch_id` and `batch_name`.
- **Racking (console)**: Passes `batchId: form.batch_id` to transfer.
- **Removals (console)**: Optional `form.batch_id` passed to addEntry for recall/traceability.

### 4. Location stage for columns b–e
- **LocationRepository (mobile + console)**: `LOCATION_STAGES`, default stage 'cellar'. getAll() normalizes missing `stage` to 'cellar'; create/update accept `stage`.
- **Console Settings**: New tab "Locations (TTB stage)" with table of locations and TTB Stage dropdown (Cellar Bulk, Racking Keg, Bottling Bulk, Case); updates via LocationRepository.update(id, { stage }).

### 5. TTBFormService column breakdown
- **getBeerOnhandByStage(asOfDate)**: Sums ledger entries for beer items up to asOfDate by location, maps locations to stage, returns { cellar, racking_keg, bottling_bulk, case }.
- **generateForm()**: Returns `columnsByLine.line1` and `columnsByLine.line33` with a, b, c, d, e (Line 1 = beginning inventory by stage; Line 33 = ending inventory by stage). Movement lines per-column not yet implemented.

### 6. PDF export for b–e
- **TTBPDFExportService**: Field mappings for line_1_b/c/d/e and line_33_b/c/d/e. fillPDFForm uses `formData.columnsByLine.line1` and `formData.columnsByLine.line33` when present to fill column a and b–e for Lines 1 and 33 (try/catch for missing PDF fields).

### 7. Documentation
- **analysis.md**: §13 updated with "TTB Beer Ledger" subsection (beer item identification, production complete, batch on ledger, location stage, column breakdown, PDF export).
- **TTB-BEER-LEDGER-IMPLEMENTATION-LOG.md**: High-level task tree and progress in repo root.

## Files touched (summary)

- **Server**: `server.js` (beer category + Finished Beer item on register), `migrate_ttb_beer_category.js` (new).
- **Mobile**: CategoryRepository, ItemRepository, LedgerRepository (transfer batchId), MilestoneTemplateRepository (forced last milestone), LocationRepository (stage), BatchDetail (RECEIVE + last milestone), ItemsList (Ingredients / Finished Beer sections).
- **Console**: Same repos + ItemRepository getBeerItems; TTBFormService (getBeerItemIds, getBeerOnhandByStage, Line 2 from RECEIVE, columnsByLine, gap detection); TTBPDFExportService (line1/33 b–e); LocationRepository (stage); Settings (Locations tab); BatchDetail (RECEIVE + last milestone); Removals (batch_id); Racking (batchId); Inventory (Finished Beer section); MilestoneTemplateRepository (forced last milestone).

## Three-pass analysis and bug fix (completed)

**Log:** `TTB-BEER-LEDGER-IMPLEMENTATION-LOG.md` (root).

### Pass 1
- **Mobile ensureDefaultTemplate**: Did not append forced "Production Complete" milestone → new orgs on mobile had no Production Complete def. **Fix:** use `ensureForcedLastMilestone(DEFAULT_MILESTONES.map(...))` when creating default template.
- **Removals (console)**: Loaded all items for beer dropdown. **Fix:** use `ItemRepository.getBeerItems()`.
- **Racking (console)**: Same. **Fix:** use `ItemRepository.getBeerItems()`.

### Pass 2
- **TTBFormService ledger-based lines**: Lines 4, 6, 7, 8, 14–20, 21, 22, 23, 24, 27, 28 used `getLedgerEntriesForPeriod` without beer filter → could include ingredient movements. **Fix:** added `getBeerLedgerEntriesForPeriod(periodStart, periodEnd, filters)` and used it in all ledger-based line calculations.
- **Variance-based lines (11, 30, 31)**: Did not filter by beer item_id. **Fix:** filter variance_events by `beerItemIds.has(variance.item_id)` in calculateInventoryOverage, calculateLosses, calculateInventoryShortage; use getBeerLedgerEntriesForPeriod in calculateLosses for CONSUME loss_theft.

### Pass 3
- **detectDataGaps**: Unclassified removals/transfers used all items. **Fix:** use getBeerLedgerEntriesForPeriod for unclassified removals and transfers; wording "beer removal(s)" / "beer transfer(s)".
- **Removals/Racking empty beer list**: No message when getBeerItems() returns []. **Fix:** show message "No beer items found. Sync or run TTB beer category migration (server: migrate_ttb_beer_category.js)."

## Deferred / follow-up

- Movement lines (e.g. 9, 10, 22, 23, 25, 26) column breakdown by source/destination stage.
- Recipe templates & items / custom brews separate item (design note).
