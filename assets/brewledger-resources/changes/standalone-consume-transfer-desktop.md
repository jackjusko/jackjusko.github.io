# Standalone Consume and Transfer Pages (Desktop)

## Summary

The desktop console now includes standalone **Consume** and **Transfer** pages, matching the mobile app's functionality. Both use new domain repositories (`ConsumeRepository`, `TransferRepository`) that wrap `LedgerRepository`, and follow the console design system (`.card`, `.input`, `.btn`, `console-toolbar`).

## What Was Added

### Repositories

- **ConsumeRepository.js** (`platforms/console/src/repositories/ConsumeRepository.js`):
  - `recordConsume({ batchId, locationId, lines, note })` – records CONSUME ledger entries for each line
  - `getRecentConsumes({ limit, startDate, endDate })` – fetches recent CONSUME entries (for future history tables)

- **TransferRepository.js** (`platforms/console/src/repositories/TransferRepository.js`):
  - `recordTransfer({ itemId, fromLocationId, toLocationId, quantity, note, operationType })` – delegates to `LedgerRepository.transfer`
  - `getRecentTransfers({ limit, startDate, endDate })` – fetches recent TRANSFER_OUT entries (for future history tables)

### Views

- **Consume.vue** (`platforms/console/src/views/Consume.vue`):
  - Batch picker (required), location picker (required)
  - Dynamic item lines: item select + quantity; add/remove lines
  - On-hand validation per line via `LedgerRepository.getOnhand`
  - Uses `ConsumeRepository.recordConsume`; calls `SyncService.sync()` after save
  - Success: alert, navigate to batch detail
  - Link to `/batches/add` next to batch picker

- **Transfer.vue** (`platforms/console/src/views/Transfer.vue`):
  - Item picker, from/to location selects (from shows available qty)
  - Quantity, note, operation type (transfer, racking, bottling, return, other)
  - Smart watcher: note keywords suggest operation type
  - Insufficient stock: confirm modal before proceeding
  - Uses `TransferRepository.recordTransfer`; calls `SyncService.sync()` after save
  - Success: alert, `router.back()`

### Routing and Navigation

- **Router**: Added `/consume` and `/transfer` routes with auth and title meta
- **Sidebar**: Consume and Transfer added to Inventory nav group (after Receive)
- **Dashboard**: Consume and Transfer added to Quick Actions card

## Feature Analysis

### First pass

- **LedgerRepository**: No changes; ConsumeRepository and TransferRepository wrap existing `addEntry` and `transfer` methods.
- **Modal**: Both views use `inject('modal')` for alerts and confirms; App.vue provides this.
- **Sync**: Both call `SyncService.sync()` after successful save.
- **Validation**: Consume validates quantity ≤ on-hand per line; Transfer shows insufficient-stock confirm when quantity > available.

### Second pass

- **Mobile parity**: Desktop Consume and Transfer mirror mobile logic; mobile still uses LedgerRepository directly. Future: consider adding ConsumeRepository/TransferRepository to mobile for consistency.
- **getRecentConsumes / getRecentTransfers**: Implemented but not yet used in UI. Ready for future "Recent consumes" / "Recent transfers" tables on the pages.
- **Tutorial**: TUTORIAL_ROUTE_PATHS in router does not include `/consume` or `/transfer`; tutorial may not guide users there. Optional follow-up.
