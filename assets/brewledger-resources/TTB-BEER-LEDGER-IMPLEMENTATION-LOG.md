# TTB Beer Ledger Implementation – Systems / Integrations Log

**Design source:** `ttb-beer-ledger-design.md`  
**Updated:** three-pass analysis and bug fix complete

## High-level overview

Implement beer-as-items ledger, batch linkage, location staging, and full TTB Form 5130.9 population (rows 1–34, columns a–g). Build on existing TTB implementation (column (a) only).

---

## Task tree

```
TTB Beer Ledger Implementation
├── 1. Beer item identification ✅
│   ├── 1.1 Default beer category (system, undeletable) ✅ server register + CategoryRepository.delete guard
│   ├── 1.2 Single Finished Beer item (org creation/migration) ✅ server register + migrate_ttb_beer_category.js
│   ├── 1.3 TTBFormService / inventory filter by beer category ✅ getBeerItemIds, Line 1 & 2 beer-only
│   ├── 1.4 Items page: beers in separate section (not main dropdown) ✅ ItemsList (mobile), Inventory (console)
│   └── 1.5 Recipe templates & items; custom brews separate item (deferred; design note only)
├── 2. Production complete → RECEIVE + forced last milestone ✅
│   ├── 2.1 Mark Production Complete → always create RECEIVE ✅ (mobile + console BatchDetail)
│   ├── 2.2 Forced last "Production Complete" milestone ✅ MilestoneTemplateRepository create/update append
│   ├── 2.3 TTBFormService Line 2 from RECEIVE only ✅; gap detection uses RECEIVE ✅
│   └── 2.4 BatchDetail completes last milestone (not FG Confirmed) ✅
├── 3. Batch on ledger ✅
│   ├── 3.1 Racking: set batch_id on ledger entries ✅ LedgerRepository.transfer(batchId); Racking.vue passes batchId
│   ├── 3.2 Packaging: batch_id in PackagingRunRepository CONSUME (supplies) ✅
│   └── 3.3 Removals: optional batch_id ✅ form.batch_id in addEntry
├── 4. Location stage for columns b–e ✅
│   ├── 4.1 locations.stage (cellar | racking_keg | bottling_bulk | case) ✅ LocationRepository getAll/create/update
│   ├── 4.2 Default existing locations: cellar ✅ DEFAULT_STAGE in getAll
│   └── 4.3 UI: Settings → Locations (TTB stage) ✅
├── 5. TTBFormService column breakdown ✅
│   ├── 5.1 Lines 1, 33: on-hand by location → aggregate by stage → columnsByLine.line1/line33 (a–e) ✅
│   └── 5.2 Movement lines: per-column deferred (design note; can extend later)
├── 6. PDF export for columns b–e ✅
│   └── 6.1 TTBPDFExportService: line_1_b/c/d/e, line_33_b/c/d/e from formData.columnsByLine ✅
└── 7. Documentation and analysis ✅
    ├── 7.1 Update analysis.md §13 ✅
    └── 7.2 changes/ttb-beer-ledger-implementation.md ✅ (two-iteration feature analysis per AGENTS.md can follow)
```

---

## Discovery (existing code)

- **TTBFormService (console):** Line 2 uses FG_CONFIRMED / milestone_type / note; beginning inventory sums all entries (no beer filter). Line 2 in `calculateBeerProduced()` (lines 82–114).
- **BatchDetail (mobile):** `saveProductionComplete` only creates/updates milestone (FG Confirmed); does **not** create RECEIVE. Volume in barrels from form.
- **LedgerRepository (both):** `addEntry` spreads `entry`; supports `batch_id`, `operation_type`, etc. Entry can include `data` (e.g. `{ source: 'production_complete' }`).
- **Categories:** Server register-org seeds standards only (Malt / Grain, Hops, … Other). No beer category. CategoryRepository.delete does not check system category.
- **Items:** Stored with `name`, `category` (string). No beer item. ItemRepository has getAll(), no getBeerItems().
- **MilestoneTemplateRepository:** Templates have `milestones` array; no forced last "Production Complete" milestone. DEFAULT_MILESTONES includes "FG Confirmed" at sort_order 3.
- **Server ledger sync:** Ledger entity stored with full JSON in `data` column; `entity.quantity` used for cache. So `entity.data.source` will be in persisted blob.
- **Locations:** No `stage` / `ttb_column` in schema or UI yet.
- **TTBPDFExportService:** Has line1a–line34a (column a); no b–e mappings yet.

---

## Implementation progress

| Part | Status | Notes |
|------|--------|--------|
| 1   | done | Beer category + Finished Beer; Items UX; TTB filter; RECEIVE on production complete (mobile + console) |
| 2   | done | RECEIVE on complete; forced last milestone; Line 2 from RECEIVE; gap detection |
| 3   | done | batch_id on racking, packaging, removals |
| 4   | done | location stage; Settings Locations tab |
| 5   | done | TTBFormService columnsByLine (Lines 1, 33 by stage) |
| 6   | done | PDF line_1/33 b–e from columnsByLine |
| 7   | done | analysis.md §13 + changes/ttb-beer-ledger-implementation.md |

---

## Three-pass analysis and bug fix

### Pass 1 – Findings
1. **Mobile ensureDefaultTemplate**: Does NOT call `ensureForcedLastMilestone()` when creating the default template, so new orgs on mobile get a template without "Production Complete" → Mark Production Complete would complete "Batch Closed" instead.
2. **Removals (console)**: Loads all items via `getAll()` for beer dropdown; design says beer removals → should use `getBeerItems()`.
3. **Racking (console)**: Loads all items via `getAll()` for beer item dropdown; should use `getBeerItems()` for consistency and TTB alignment.
4. **LocationRepository.update (console)**: Passing `{ stage }` only – Dexie merges, so OK; `getById` after update returns merged record (stage present). Verified OK.
5. **Ledger entry `data`**: Client spreads `entry` into newEntry; server stores full entity in data column; TTBFormService reads `entry.data.source`. Verified OK.

### Pass 1 – Fixes applied
- [x] Mobile MilestoneTemplateRepository.ensureDefaultTemplate: use ensureForcedLastMilestone(DEFAULT_MILESTONES.map(...)).
- [x] Console Removals loadData: beerItems = await ItemRepository.getBeerItems().
- [x] Console Racking loadData: beerItems = await ItemRepository.getBeerItems().

### Pass 2 – Findings
1. **TTBFormService ledger-based lines**: Design says "restrict to beer items where the source is ledger/transfers/packaging/variance". Lines 4, 6, 7, 8, 14–20, 21, 22, 23, 24, 27, 28 use getLedgerEntriesForPeriod without beer filter → can include ingredient movements.
2. **TTBFormService variance-based lines**: Lines 11 (overage), 30 (losses), 31 (shortage) use variance_events without filtering by beer item_id.
3. **getBeerLedgerEntriesForPeriod**: Add helper that gets ledger entries for period and filters to beer item_ids; use in all ledger-based line calculations.
4. **Variance calculations**: Filter variance_events by item_id in getBeerItemIds() for Lines 11, 30, 31.

### Pass 2 – Fixes applied
- [x] Add getBeerLedgerEntriesForPeriod(periodStart, periodEnd, filters); use in Line 4, 6, 7, 8, 14–20, 21, 22, 23, 24, 27, 28.
- [x] Filter variance_events by beer item_id in calculateInventoryOverage, calculateLosses, calculateInventoryShortage.

### Pass 3 – Findings
1. **detectDataGaps unclassified removals/transfers**: Currently uses getLedgerEntriesForPeriod (all items). For TTB relevance, filter to beer items when counting unclassified removals/transfers so warnings reflect beer-only gaps.
2. **Removals/Racking empty beer list**: If getBeerItems() returns [] (no migration run), dropdown is empty and user cannot submit. Add empty-state message.
3. **BatchDetail (mobile) lastDef when defs empty**: If milestoneDefinitions.value is empty, lastDef is null and we don't create/update milestone – RECEIVE still created. OK.
4. **Ledger entry `data` on server**: Server stores full entity in ledger_entries.data; client sends entry with top-level data. Verified – server JSON.stringify(entity) includes data. OK.
5. **categories/is_system on client**: Delete guard checks both name and is_system. OK.

### Pass 3 – Fixes applied
- [x] detectDataGaps: use getBeerLedgerEntriesForPeriod for unclassified removals and unclassified transfers; wording "beer removal(s)" / "beer transfer(s)".
- [x] Removals: show message when beerItems.length === 0 (sync or run migrate_ttb_beer_category.js).
- [x] Racking: show message when beerItems.length === 0 (same).
