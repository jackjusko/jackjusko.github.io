# Feature Analysis: Packaged Beer Visibility Fix

## Summary

After kegging off a batch via Mark Production Complete (packaged_keg/packaged_case), users reported:
1. The packaged beer item does not appear to be created
2. Units of stored, packaged beer are not visible

## Root Causes Identified

1. **Items not refreshed after save**: BatchDetail's `items` ref was not refreshed after `saveProductionComplete`. The new packaged beer item (e.g. "House IPA 1/6 bbl") is created and stored in IndexedDB, but the batch's ledger display uses `getItemName(entry.item_id)` which looks up from `items.value`. Since the new item was never added to `items`, the RECEIVE entry showed "Unknown Item".

2. **Inventory/Beers not refreshing**: When packaging completes, `SyncService.sync()` is called but it is async. Views that watch `syncTrigger` (Inventory, Beers) only reload when sync completes and `incrementSyncTrigger()` runs. Users navigating to Inventory immediately after packaging would see stale data until sync finished.

3. **cleanupBeerItemsAtZero could delete packaged beer**: The cleanup soft-deletes Finished Beer items at zero on-hand. Packaged beer items (keg/case SKUs with `base_beer_item_id`) are product formats that should persist even when sold out. The cleanup did not exclude them; in edge cases (e.g. if cache was stale or a bug caused incorrect zero), packaged beer could be incorrectly deleted.

## Implementation

### Console BatchDetail.vue
- Refresh `items.value = await ItemRepository.getAll()` after saveProductionComplete so the batch ledger shows the correct packaged beer item name.
- Call `incrementSyncTrigger()` immediately after save so any open Inventory/Beers tabs reload without waiting for sync.

### Mobile BatchDetail.vue
- Refresh `items.value = await ItemRepository.getAll()` after saveProductionComplete (mobile does not have syncTrigger; navigation typically triggers fresh load).

### LedgerRepository (console + mobile)
- In `cleanupBeerItemsAtZero`, skip items with `item.data?.base_beer_item_id` (packaged beer SKUs). These represent product formats (e.g. "House IPA 1/6 bbl") that should remain in the system even when inventory is zero.

## Files Modified

- `platforms/console/src/views/BatchDetail.vue` – items refresh, incrementSyncTrigger import and call
- `platforms/console/src/repositories/LedgerRepository.js` – cleanupBeerItemsAtZero exclude packaged beer
- `platforms/brewledger-app/src/views/BatchDetail.vue` – items refresh
- `platforms/brewledger-app/src/repositories/LedgerRepository.js` – cleanupBeerItemsAtZero exclude packaged beer

## Edge Cases

- **Offline**: Items and ledger entries are stored locally. Refresh from ItemRepository.getAll() and LedgerRepository returns local data. Sync will push when online.
- **Multiple tabs**: incrementSyncTrigger causes all watching views to reload; they fetch from local DB and will see the new packaged beer.
- **Packaged beer at zero**: No longer auto-deleted; SKU persists for future production and sales.
