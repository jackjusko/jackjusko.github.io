# Seed Test Account Enhancement – Feature Analysis

## Summary

Updated `server/seed_test_account.js` to provide richer, more realistic test data that simulates an actual brewery workflow. Key changes: remove default Finished Beer item (per plan), expand ingredient inventory across locations, add batches with correct workflow (finished vs active), create per-batch beer items and RECEIVE production_complete for finished batches, and ensure batch additions consume inventory via CONSUME ledger entries.

## Implementation Overview

### 1. Clear Org Seed Data

- Extended `clearOrgSeedData` to delete batch-related tables in dependency order before items/locations/vessels.
- Tables cleared: `batch_volume_adjustments`, `batch_volume_snapshots`, `batch_location_transfers`, `batch_additions`, `batch_readings`, `packaging_runs`, `batch_milestones`, `batch_locations`, `batches`, then existing: `onhand_cache`, `ledger_entries`, `vessels`, `locations`, `items`.

### 2. No Finished Beer Item

- Removed creation of default "Finished Beer" item from both `ensureTestAccount` (new org) and `seedData`.
- Finished Beer **category** retained for TTB/registration parity.
- No ledger entries or on-hand cache entries for beer.
- Aligns with current design: beer items created per-recipe/per-batch when marking production complete.

### 3. Expanded Inventory

- **16 items** (up from 11): added Carapils, Chocolate Malt, Citra Hops, Columbus Hops, Star San.
- **Distribution** across multiple locations per item:
  - Malt: Dry Storage, Cold Room, Brewery Cellar
  - Hops: Cold Room
  - Yeast: Cold Room, Brewery Cellar
  - Packaging: Keg Storage, Brewery Cellar, Case Storage
  - Chemicals: Dry Storage, Brewery Cellar

### 4. Milestone Template

- New orgs: default milestone template created in `ensureTestAccount` (mirrors server registration).
- Existing orgs: `seedData` ensures a milestone template exists before creating batches; creates one if missing.

### 5. Batches (Workflow-Correct)

- **5 batches total** (3 finished, 2 active):
  - **Finished** (production complete; no batch_locations—vessels were cleared): House IPA, Pale Ale, Stout.
    - Per-batch beer items created (House IPA, Pale Ale, Stout in Finished Beer category).
    - RECEIVE with `data.source = 'production_complete'` at destination: House IPA → Taproom (serving), Pale Ale → Keg Storage, Stout → Brewery Cellar.
    - Appear in Batches "Finished" section; beer shows in inventory/Serving.
  - **Active** (still in vessels; have batch_locations): IPA Batch 2 (FV-2), Lager (FV-3).
- Batch readings: GRAVITY 1.048, TEMP 18 on IPA Batch 2.
- Batch additions: Pale Ale had 50 lb Pale Malt and 2 lb Cascade; creates CONSUME ledger entries and reduces Cold Room on-hand (2000→1950 Pale Malt, 80→78 Cascade).

## Potential Issues & Edge Cases

### 1. Location Name Typos

- `itemsToCreate` uses `locationName` (e.g. 'Dry Storage', 'Cold Room') that must match `locationsToCreate`.
- **Mitigation**: `locationByName[d.locationName]`; if no match, `console.warn` and skip. A typo would drop inventory for that location.

### 2. clearOrgSeedData Does Not Clear Milestone Templates

- Milestone templates are preserved across `--force` re-seed.
- **Rationale**: Templates are org-level configuration; re-seeding data should not remove them.
- **Edge case**: If templates were corrupted or changed, re-seed would not reset them. Acceptable.

### 3. Sync After Seed

- Seed writes directly to SQLite. Clients sync to get data.
- **Note**: Clients must run sync after seed to populate IndexedDB. Existing behavior; no change.

### 4. Reading Type Casing

- Batch readings use `reading_type: 'GRAVITY'`, `'TEMP'` (uppercase) to match client (BatchDetail compares `r.reading_type === 'GRAVITY'`).

### 5. New Org Without seedData

- When a brand-new org is created by `ensureTestAccount`, `seedData` runs only if `hasSeed` is false (no locations).
- New org has no locations, so `hasSeed` is false and `seedData` runs. Correct.

## Second Iteration – Additional Considerations

### 6. Location Name Validation

- **Addressed**: Added `console.warn` when a distribution references a non-existent location. Catches typos without failing the entire seed.

### 7. clearOrgSeedData Table Existence

- If a migration has not run, some tables (e.g. batch_volume_adjustments) might not exist. `DELETE FROM` on non-existent table would throw.
- **Mitigation**: `init_db.js` creates all tables; seed typically runs after migrations. If running against old DB, init_db or migrations should be run first. Documented in script header.

### 8. Workflow Fix (Post-Plan)

- **Problem**: Original seed had batches but no beer in inventory; batch additions did not consume; serving tanks empty.
- **Fix**: Finished batches create per-batch beer items + RECEIVE production_complete at destinations (House IPA → Taproom, Pale Ale → Keg Storage, Stout → Brewery Cellar). Batch additions for Pale Ale create CONSUME entries and reduce on-hand. Finished batches have no batch_locations (vessels cleared on production complete).

## Integration Notes

- **Server**: No API changes; seed is a standalone script.
- **Console / Mobile**: No code changes; they consume seeded data via sync.
- **TTB / Reports**: Finished Beer category exists but no default beer item; reports that expect at least one beer item may show empty or need migration (`migrate_restore_finished_beer_item.js`) if required.
