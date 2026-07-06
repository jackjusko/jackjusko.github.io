# Desktop Inventory: Locations and Par Status per Item

## Summary

The console Inventory view (`platforms/console/src/views/Inventory.vue`) was enhanced so each inventory item row can show all locations where the item exists (or has a par level), with per-location par status and global par level status.

## Changes

### Data Model (per item)

- **`item.locations`**: Array of `{ locationId, locationName, quantity, parMin, status }` where:
  - Locations are the union of (1) locations where the item has quantity > 0 and (2) locations where the item has a per-location par level.
  - `quantity` is from `LedgerRepository.getAllOnhand()` (onhand_cache).
  - `parMin` is from `ParLevelRepository.getAll()` for that item/location; `null` if no par.
  - `status`: `'In Stock'` (qty ≥ par), `'Low Stock'` (qty < par), or `'No par'` (no par set).
- **`item.globalPar`**: `null` or `{ minQty, totalOnhand, status }` where:
  - Global par is from `par_levels` with `location_id` null for the item.
  - `status`: `'In Stock'` or `'Low Stock'` (compared to total on-hand).

### UI

- **Table**: Added a leading column with expand/collapse control (▶/▼). Only shown when the item has at least one location or a global par.
- **Locations column**: Replaces single "Location". Shows "N location(s)" and "+ global" when a global par exists; "—" when no locations and no global par.
- **Expanded row**: When expanded, shows:
  - **Global par level** (left card): Total on-hand, min, and status badge; or "No global par set".
  - **By location** (right card): Table with Location, Qty, Par (min), Status. Sorted by location name. Empty state: "No locations with stock or par levels".

### Implementation Notes

- `expandedItems` is a `Set` of item IDs; `toggleExpanded(itemId)` toggles membership.
- Row-level low-stock logic unchanged: an item counts as low stock if any per-location or global par is breached.
- `getStatusClass()` is reused for status badges; `'No par'` gets the default neutral class.
- Quantity display in expanded section uses `formatQuantityWithInterval` when item has interval/unit.

## Documentation

- **analysis.md**: Inventory View section updated with "Locations and Par Status (Expandable Rows)" under Features.
