# Individual & Global Par Levels - Feature Analysis

## Overview

Implement support for both **individual (per-location)** and **global** par levels. Individual par levels require stock at a specific location to be above a threshold. Global par levels require the **total on-hand across all locations** to be above a threshold. Low stock notifications will appear on the dashboard for both types.

## Legacy Code Audit

### Legacy Reorder/Stock System (Migrated Away From)

1. **LowStock.vue** (`platforms/brewledger-app/src/views/LowStock.vue`)
   - Uses `item.reorder_threshold` (a field on the item entity) - global threshold
   - Compares `totalOnhand <= reorder_threshold`
   - **Status**: Imported in router but NO route defined - effectively orphaned
   - **Action**: Update to use par levels (both types) or remove; will update to use ParLevelRepository

2. **item.reorder_threshold**
   - Legacy field that may exist on items in the database
   - Not set by ItemForm (no UI)
   - **Action**: Ignore - no migration needed; new par_levels replace it

3. **ReorderList.vue**
   - Already uses ParLevelRepository for per-location par levels
   - Has "Set par levels" modal with location selector
   - **Status**: Current implementation - extend for global

### Current Par Level Implementation

- **ParLevelRepository**: `item_id` + `location_id` required; `min_qty`, `max_qty`
- **Server validation**: `!entity.location_id` returns false - must change for global
- **Dexie schema**: `par_levels: 'id, item_id, location_id, org_id, sync_status'`
- **DB (init_db)**: Generic entity table - `location_id` in data blob

## Design Decisions

### Global Par Level Representation

- **Option A**: `location_id = null` for global par levels
- **Option B**: Separate table `global_par_levels`
- **Chosen**: Option A - reuse par_levels with `location_id: null`. Simpler, single table, same sync flow.

### Uniqueness

- **Individual**: One par level per (item_id, location_id)
- **Global**: One par level per (item_id) where location_id is null
- An item can have BOTH a global par AND per-location pars

### Low Stock Logic

- **Individual breach**: item X at location Y has onhand < par.min_qty
- **Global breach**: item X has totalOnhand (sum across all locations) < global_par.min_qty
- Dashboard count: Distinct items that have at least one breach (individual or global). If same item breaches both, count once.

## Implementation Plan

### 1. Database & Server

- **init_db.js**: No schema change - par_levels entity table stores data as JSON; `location_id` can be null in data
- **server.js validateEntity**: Change par_level case to allow `location_id` to be null/undefined for global; require `item_id` and `min_qty`

### 2. Client DB (Dexie)

- **db.js**: Dexie index on `location_id` - null is valid in IndexedDB
- May need `getByItem` or `getGlobalPars` - filter where !location_id

### 3. ParLevelRepository (both platforms)

- `setParLevel(itemId, locationId, minQty, maxQty)` - existing; locationId required for individual
- `setGlobalParLevel(itemId, minQty, maxQty)` - new; creates/updates with location_id: null
- `getByItem(itemId)` - new; returns all pars for item (individual + global)
- `getGlobalPars()` - new; returns all global pars
- `getIndividualPars()` - filter where location_id is not null
- `applyRemoteUpsert` - already handles any par_level; no change if we store location_id: null

### 4. ReorderList (Mobile)

- Add "Global" option in location selector (e.g. "All Locations (Global)")
- When Global selected: show items with global par, edit min qty
- Reorder items list: include BOTH individual breaches (item+location) AND global breaches (item, no location)
- Visual distinction: e.g. badge "Global" vs "Location: X"

### 5. Dashboard (Mobile & Console)

- Low stock count: items with individual OR global breach (deduplicated by item)
- Low stock list: show both types with clear labeling
- Console Dashboard & Inventory: same logic

### 6. LowStock.vue (Legacy)

- Update to use ParLevelRepository for both types (replacing reorder_threshold)
- Add route `/low-stock` if we want to expose it, or remove from router import
- **Decision**: Update to use par levels; keep file for potential use. Router has no route - leave as is.

### 7. Console Platform

- Console has no ReorderList - add "Set par levels" to Inventory or Dashboard
- Or add a "Par Levels" / "Reorder" link that could open a similar modal
- **Decision**: Add "Manage Par Levels" button to Inventory that opens a modal (similar to mobile ReorderList)

## Edge Cases

1. **Item deleted**: Par levels reference deleted item - filter out in UI and low stock calc
2. **Location deleted**: Individual par with deleted location - filter out
3. **Both global and individual for same item**: Valid - show both breaches if applicable
4. **Global par = 0**: Effectively disables; we could treat as "no par" or allow
5. **Sync**: Server must accept location_id null; existing sync flow should work

## Files to Modify

| File | Changes |
|------|---------|
| server/server.js | validateEntity par_level: allow location_id null |
| platforms/brewledger-app/src/repositories/ParLevelRepository.js | setGlobalParLevel, getGlobalPars, getByItem |
| platforms/console/src/repositories/ParLevelRepository.js | Same |
| platforms/brewledger-app/src/views/ReorderList.vue | Global option, both breach types |
| platforms/brewledger-app/src/views/Dashboard.vue | Both breach types in count & display |
| platforms/console/src/views/Dashboard.vue | Same |
| platforms/console/src/views/Inventory.vue | Both breach types, add par level modal |
| platforms/brewledger-app/src/views/LowStock.vue | Use ParLevelRepository (both types) |

## First Iteration Risks / Gaps

1. **Dexie query for null location_id**: `where('location_id').equals(null)` - may need `.filter(p => !p.location_id)` instead
2. **Console par level editing**: Console doesn't have ReorderList - need full modal implementation
3. **applyRemoteUpsert**: Par levels from server may have different structure - ensure location_id null is preserved
4. **Server processChange**: Ensure par_levels with null location_id are stored correctly in SQLite JSON
