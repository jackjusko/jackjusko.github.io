# Sales Order Context-Aware Product & Location Inventory

## Summary

Added context-aware inventory display on the Sales Order page so users see how much of a finished product exists at each location before and after selecting product and location.

## What Was Added

### LedgerRepository

- **`getOnhandByItem(itemId)`**: Returns array of `{ location_id, quantity }` for all locations where the item has on-hand quantity. Used for per-location availability in dropdowns.

### SalesOrder.vue

- **Product selected first**: Location dropdown shows each location with its available quantity, e.g. "Cold Storage – 12.00 bbl", "Warehouse – 5.00 bbl", "Keg Room – 0.00 bbl".
- **Both product and location selected**: Toolbar meta pill (existing) shows total available; quantity field helper text shows "Available at this location: X.XX bbl".
- **`onhandByLocation`**: Reactive map of `location_id -> quantity` populated when product changes via `getOnhandByItem`.
- **Helper text**: Location dropdown hint changes to "Shows available quantity per location" when product is selected; quantity hint shows specific available amount when both selected.

## Feature Analysis

### First pass

- **Data source**: Uses local `onhand_cache` via LedgerRepository; no server round-trip. Aligns with local-first architecture.
- **Locations with zero**: All locations shown with "0.00 bbl" for items with no stock there; users can still select (e.g. for transfers or corrections).
- **Order of selection**: Works whether user picks product first or location first; when product changes, `onhandByLocation` refreshes; location dropdown updates immediately.
- **Formatting**: Quantities use `.toFixed(2)` for consistency with existing "bbl" display.
- **Edge case**: When product cleared, `onhandByLocation` resets to `{}`; location dropdown reverts to plain names.

### Second pass

- **Async watch**: `getOnhandByItem` is async; `onhandByLocation` updates when resolved. No loading spinner needed—dropdown shows "0.00 bbl" until data loads for locations without cache entries.
- **Race condition**: When user switches product before previous fetch completes, we guard with `if (form.item_id !== requestedItemId) return` so stale data is not applied.
- **Cache consistency**: `onhand_cache` is updated by LedgerRepository on every ledger change; Sales Order reads from same cache used by submit validation.
- **Submit validation**: Existing `LedgerRepository.getOnhand` at submit still enforces sufficient quantity; no change to server validation.
- **Mobile parity**: Sales Order is console-only (Distribution section); no mobile equivalent to update.
