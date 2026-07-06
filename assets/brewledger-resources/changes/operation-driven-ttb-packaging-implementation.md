# Feature Analysis: TTB Stage Operation-Driven Rework & Packaging/Keg Implementation

## Implementation Summary

This document captures the feature analysis for the TTB Stage Operation-Driven Rework and Packaging/Keg TTB implementation per the design plan (`operation_driven_Rework`) and implementation plan (`packaging-keg-ttb-implementation-plan.md`).

### Completed Phases

**Phase 1: Operation-Driven Stage for TTB Column Assignment**
- TTBFormService: Added `getStageForEntry(entry, stageMap, isDestination)` — derives column from `operation_type` (production_complete→cellar, racking→racking_keg for destination, bottling/canning→case) with fallback to location stage
- LedgerRepository: `operation_type` and `ttb_stage` merged into `data` for sync
- BatchDetail: Production complete RECEIVE now sets `operation_type: 'production_complete'`
- All movement lines (2, 4–8, 22–24, 27–31) use `getStageForEntry`; Line 1 and 33 (inventory at rest) keep location stage

**Phase 2a: Vessel = Location for Fermenters and Brites**
- Vessels.vue (console + mobile): Create location for all vessel types on create; stage = serving for SERVING, cellar for FERMENTER/BRITE/OTHER
- Server + validation middleware: Batch assignment rejects only when vessel type is SERVING (not all vessels with location_id)
- BatchForm: `vesselsForBatch` excludes only SERVING vessels (not vessels with location_id)
- BatchDetail: `transferDestinationVessels` excludes only SERVING vessels

**Phase 2b: Packaged Beer Items and volume_per_unit**
- ItemForm: Added `volume_per_unit` (bbl per ea) for Finished Beer + unit ea/each
- ItemRepository: `getOrCreatePackagedBeerItem(baseBeerItem, formatKey, volumePerUnit)` — creates packaged beer items (e.g. "House IPA 1/6 bbl")
- TTBFormService: `beerQuantityBarrels(entry, item)` — converts ea to bbl when item has `volume_per_unit`
- TTBFormService: Line 9 and 10 now include ledger RECEIVE with operation_type racking/bottling/canning (plus legacy packaging_runs)
- All TTB calculations pass `itemMap` for packaged beer conversion

**Phase 3: Remove Racking View, Deprecate Packaging Modal**
- Removed `/racking` route and Racking.vue
- Removed Racking from App.vue nav, Dashboard quick actions, Reports page
- Removed "Record Packaging" button and packaging modal from BatchDetail
- Packaging runs table: no new writes; legacy data still used for Line 9/10 until ledger-only

**Phase 4: Location Stage Clarification**
- LocationForm: Added helper text — "Stage is used for inventory at rest (TTB Lines 1 and 33). For movements, the operation type determines the TTB column."

### Deferred / Not Implemented

**Phase 2c: Mark Production Complete Packaging Flow (keg/case)**
- Full packaging flow (packaged_keg, packaged_case) with supply lines UI was not implemented in this pass
- Infrastructure is in place: `getOrCreatePackagedBeerItem`, TTB from ledger for Line 9/10, vessel locations for fermenters/brites
- Future work: Add destChoice packaged_keg/packaged_case to production complete modal, supply lines UI, keg format presets, ledger entry creation (RECEIVE bulk, TRANSFER, CONSUME bulk, RECEIVE packaged, CONSUME empty kegs)

---

## First Iteration — Potential Weak Points

### 1. Ledger operation_type persistence
- **Risk**: Server may not persist `operation_type` in ledger `data` if validation strips unknown fields
- **Mitigation**: Server ledger validation passes `data` as JSON; no schema change. Audit server processChange for ledger — typically stores data as-is
- **Action**: Verify server accepts operation_type in ledger sync payload

### 2. Packaged beer item creation
- **Risk**: `getOrCreatePackagedBeerItem` creates items with `volume_per_unit` in `data`; ItemRepository.create/update must merge correctly
- **Mitigation**: Create/update explicitly merge volume_per_unit and base_beer_item_id into data
- **Action**: Test packaged beer item creation during packaging flow (when Phase 2c is implemented)

### 3. Batch assignment for new vessels
- **Risk**: New fermenters/brites get location_id; BatchForm excludes SERVING only. If a vessel type is mis-set, batch assignment could fail
- **Mitigation**: Filter is `type !== 'SERVING'`; FERMENTER/BRITE/OTHER all allowed
- **Action**: Manual test: create fermenter (gets location), assign batch — should succeed

### 4. TTB Line 9/10 dual source
- **Risk**: Line 9/10 now sum ledger + packaging_runs; risk of double-count if same event recorded both ways
- **Mitigation**: New packaging flow (Phase 2c) will create ledger only; packaging_runs deprecated. Until then, no overlap — packaging modal removed, so no new packaging_runs
- **Action**: Document that packaging_runs are legacy; new packaging = ledger only

### 5. Mobile parity
- **Risk**: Mobile VesselsList updated for vessel locations; mobile BatchDetail may still have packaging modal
- **Mitigation**: Implementation plan says "Mobile BatchDetail packaging flow parity" — packaging modal removal should be mirrored on mobile
- **Action**: Check mobile BatchDetail for packaging modal; remove if present

### 6. Tutorial / onboarding
- **Risk**: Tutorial may reference Racking
- **Mitigation**: Implementation plan §9.6 says update tutorial steps
- **Action**: Audit tutorialSteps.js for Racking references; update or remove

---

## Second Iteration — Additional Considerations

### 7. ItemForm volume_per_unit loading
- **Issue**: When editing an item, form loads `volume_per_unit` from `item.data?.volume_per_unit`
- **Mitigation**: Implemented in onMounted load
- **Action**: Verify edit flow shows volume_per_unit for packaged beer items

### 8. VesselsList mobile — watch removal
- **Issue**: Removed `watch` that cleared location_id when type changed from SERVING
- **Mitigation**: All vessel types can have location; no need to clear
- **Action**: Test mobile vessel create/edit — ensure location persists for non-SERVING

### 9. Reports page — Racking card removal
- **Issue**: Removed Racking card; page may have layout gap
- **Mitigation**: Removed entire card block; layout should flow
- **Action**: Visual check Reports page

### 10. App.vue route descriptions
- **Issue**: Removed `/racking` from descriptions and pageTitles; may leave trailing comma
- **Mitigation**: Removed line; check for syntax
- **Action**: Lint App.vue

---

## Documentation Updates (analysis.md)

The following updates were applied to `analysis.md`:
- Dashboard: Removed "racking" from Quick Actions; noted Racking removed (2026-03-01)
- Reports View: Removed Racking link; noted packaging now via Mark Production Complete
- Batch Detail View: Removed "Record Packaging" from actions; added removal note
- Console UI (TTB): Updated "Removals, Racking, Losses" to "Removals, Losses views (Racking removed 2026-03-01)"

**Manual addition recommended** for TTB Form section: Add bullet describing operation-driven TTB stage, vessel locations, packaged beer volume_per_unit, and Racking/Packaging modal removal.

---

## Two-Pass Systems Analysis (2026-03-01)

See `changes/operation-driven-ttb-systems-analysis.md` for:
- Integration flow verification
- Bugs fixed: mobile LedgerRepository data merge, mobile ItemForm volume_per_unit, mobile ItemRepository create/update, mobile LocationForm stage helper, groupTransfersByPair operation-driven stage
