# Serving & Finished Beer System — Review and Fix Report

## Scope of review
All recent migrations to the serving and finished-beer system: one-beer-per-location (console + mobile), ServingOccupancyService, production-complete confirmation dialog, Serving page per-tank beer and Set empty, and related Batch Detail / ledger / TTB integration.

---

## 1. Implementation summary

### 1.1 One-beer-per-location model
- **Occupancy source**: Ledger on-hand only. For each serving location we determine which Finished Beer item(s) have `onHand > 0`; exactly one = current beer, multiple = conflict, zero = empty.
- **Console**: `ServingOccupancyService` (`getCurrentBeerAtLocation`, `getBeerItemForServingLocation`). Used by BatchDetail production complete and Serving.vue.
- **Mobile**: Same service and helpers in `platforms/brewledger-app/src/services/ServingOccupancyService.js`. Used by BatchDetail production complete and Serving.vue.
- **Batch link**: No longer used for serving occupancy. Production complete and Serving do not rely on `batch_location` to decide “what beer is in the tank”; Set empty does not delete `batch_location`.

### 1.2 Production complete
- **Serving list**: Built with occupancy per location; options show current beer name, “Empty”, or “Multiple beers – resolve…” (disabled when conflict).
- **Confirm when occupied**: If user selects a serving location that already has one beer item, a 3-button dialog appears: Same beer – add on top (RECEIVE to that item), Remove first (prompt), Cancel. If conflict, selection is blocked.
- **RECEIVE**: Uses existing item when “add on top”; otherwise `ItemRepository.getOrCreateBeerItemForBatch(batch)`. Source vessel still cleared via `BatchLocationRepository.delete(batch_location_id)`.

### 1.3 Serving page (console and mobile)
- **Tank list**: Each tank has `beerItem`, `beerItemName`, `onHand`, `conflict` from `getCurrentBeerAtLocation(locationId)`.
- **Set volume / Record removal / Set empty**: Use `tank.beerItem` for ledger; buttons disabled when `tank.conflict || !tank.beerItem`. Set empty zeros current beer at location (CONSUME only; no batch_location delete).
- **Ledger entries**: No `batch_id` on serving CONSUME/RECEIVE from Serving page (optional for TTB; item + location are the source of truth).

### 1.4 Other integrations (unchanged or verified)
- **Removals.vue / Losses.vue**: Use `ItemRepository.getBeerItems()` (all beer items). No dependency on a single default item. OK.
- **TTBFormService**: `getBeerItemIds()` uses `getBeerItems({ includeDeleted: true })`; all beer items included. `detectDataGaps()` flags missing beer items with a generic message. OK.
- **LedgerRepository.cleanupBeerItemsAtZero**: Skips item with `name === 'Finished Beer' && category === 'Finished Beer'` (server-created default). Still correct; server continues to create and protect that item.
- **Server**: Org registration creates default “Finished Beer” item; sync rejects deletion of that item and of “Finished Beer” category. No change required for one-beer-per-location.

---

## 2. Edge cases and systems integration

### 2.1 Console Batch Detail — tank flows (fixed)
- **Issue**: Adjust volume (tank) and Set volume (tank) used `getDefaultFinishedBeerItem()` (first beer item) for ledger CONSUME/RECEIVE and for on-hand display. That is inconsistent with one-beer-per-location and wrong when multiple beer items exist (only one is “in” the tank).
- **Fix**: Use `getCurrentBeerAtLocation(vessel.location_id)` / `getBeerItemForServingLocation(vessel.location_id)` for:
  - **Adjust volume (tank)**: Resolve current beer; on conflict show error; on empty and negative change show “No beer at this location to reduce”; on empty and positive change use `getOrCreateBeerItemForBatch(batch)`.
  - **Set volume (tank)**: Same resolution; initial volume and `setVolumeTankOnHand` come from per-location beer; conflict blocks; empty + negative delta blocked; empty + positive delta use `getOrCreateBeerItemForBatch(batch)`.
- **Transfer modal**: Default `ledger_item_id` remains first beer item (user can change). No change; destination can be any location and is not limited to serving tanks.

### 2.2 Mobile Batch Detail — tank flows
- **Finding**: Mobile Batch Detail has no tank-specific ledger path. Adjust volume only updates `batch_location.current_volume`; Set volume only records a snapshot. No `getDefaultFinishedBeerItem` in tank ledger flows. No fix needed.

### 2.3 Race / multi-device
- Production complete re-checks occupancy in `onProductionCompleteConfirm` before opening the 3-button dialog or saving. If a second device adds another beer to the same location in between, the next check sees conflict and blocks. OK.

### 2.4 Set empty and batch_location
- Set empty (Serving page) only zeros ledger for the current beer at that location; it does not delete `batch_location`. So vessel–batch link can remain; occupancy and “current beer” are defined by ledger only. Documented and consistent.

### 2.5 TTB and default item
- TTB reporting uses all beer items (by category and includeDeleted). No dependency on a single default item. Gap message is generic (“No beer items (Finished Beer) found…”). OK.

### 2.6 ItemRepository / LedgerRepository
- `cleanupBeerItemsAtZero` still skips the default “Finished Beer” item. Aligns with server still creating and protecting that item. No change.

---

## 3. Fixes applied

| Location | Change |
|----------|--------|
| `platforms/console/src/views/BatchDetail.vue` | Import `getBeerItemForServingLocation`. Adjust volume (tank): resolve beer via `getCurrentBeerAtLocation`; conflict → error; empty + negative → error; empty + positive → `getOrCreateBeerItemForBatch`. Set volume (tank): same resolution for on-hand and for RECEIVE/CONSUME; watch for `setVolumeTankOnHand` and `openSetVolumeModal` use `getBeerItemForServingLocation`. |

---

## 4. Recommendations

- **Transfer default**: Optionally default `ledger_item_id` to the current beer at the selected destination when the destination is a serving location (e.g. via `getBeerItemForServingLocation(destination_location_id)`). Low priority; user can select item.
- **Mobile Batch Detail**: If a tank-specific Set volume / Adjust volume ledger path is added later, use the same per-location beer resolution as console.
- **Documentation**: `analysis.md` and `changes/serving-one-beer-per-location.md` already describe the model; this report and the Batch Detail tank fix are recorded in `changes/serving-finished-beer-review.md`.

---

## 5. Files touched in this review

- **Reviewed**: Serving.vue (console + mobile), BatchDetail.vue (console + mobile), ServingOccupancyService (both), ItemRepository, LedgerRepository, TTBFormService, Removals.vue, Losses.vue, server (server.js, migrations, seed).
- **Modified**: `platforms/console/src/views/BatchDetail.vue` (tank flows use per-location beer).
- **Created**: `changes/serving-finished-beer-review.md` (this report).
