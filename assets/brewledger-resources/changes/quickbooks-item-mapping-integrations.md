# QuickBooks Item Mapping in Integrations

## Summary

Added an **Item Mapping** flow to the Integrations page within the QuickBooks Online section. When QuickBooks is connected, users can map BrewLedger beer items to QuickBooks items via two clear options: **Link to existing QuickBooks item** (dropdown + Link) or **Create new in QuickBooks**. Sales Order enforces mapping when "Create Invoice" is checked.

## QBO Item Create Fix (400 error)

- Switched from `Type: Inventory` to `Type: NonInventory`—Inventory requires IncomeAccountRef, ExpenseAccountRef, AssetAccountRef.
- Removed invalid properties: TrackQtyOnHand, QtyOnHand, InvStartDate, account refs.
- Minimal payload: Name, Type, optional UnitPrice.

## What Was Added

### Server (server/server.js)

- **GET /api/integrations/qbo/items**: Fetches QBO Item list (paginated, same pattern as customers). Returns `{ items: [...] }` with QBO Item objects (Id, Name, Type, etc.). Requires `ensureQboAccess`.

### QBOService (platforms/console/src/services/QBOService.js)

- **getMappings()**: `GET /api/integrations/qbo/mappings` → `data.mappings`
- **getItems()**: `GET /api/integrations/qbo/items` → `data.items`
- **saveMapping({ brew_item_id, qbo_item_id })**: `POST /api/integrations/qbo/mappings` (qbo_item_id can be null to clear)
- **pushItem(itemId)**: `POST /api/integrations/qbo/items/:itemId/push` (creates item in QBO, upserts mapping)

### Integrations.vue

- **Item Mapping section** (when `status?.connected`): Below connection block, bordered separator.
- **Header**: "Item Mapping" with copy: "Map your beer items to QuickBooks so Sales Orders can sync as Invoices."
- **Data loading**: `loadMappingData()` fetches beer items (ItemRepository.getBeerItems), mappings (QBOService.getMappings), QBO items (QBOService.getItems). Triggered by watch on `status?.connected`.
- **Card per beer**: Each beer in a card. **When unmapped**: Two clear options—(1) "Link to existing:" dropdown + Link button; (2) "Create new:" Create new in QuickBooks button. **When mapped**: "Linked to: [name]" with Change and Unlink buttons.
- **Link**: Saves mapping when user selects QBO item from dropdown and clicks Link.
- **Create new in QuickBooks**: Calls `pushItem`; on success, refreshes QBO items and mappings; new item appears and is auto-linked.
- **Change**: Unlinks mapping so user can link to a different item.
- **Unlink**: Clears mapping via `saveMapping` with `qbo_item_id: null`.
- **Empty state**: "No beer items. Add beers in Beers or via Mark Production Complete first." with link to `/beers`.
- **Loading/error**: Loading state and error message surfaced.

### SalesOrder.vue

- **Mappings load**: Fetches mappings via QBOService.getMappings when QBO connected (in loadData).
- **selectedBeerHasMapping**: Computed—true when selected beer has a mapping with qbo_item_id.
- **Hint block**: When `createInvoice && form.item_id && !selectedBeerHasMapping`, shows amber alert: "Map this beer in Distribution → Integrations before syncing to QuickBooks." with link to `/integrations`.
- **Submit disabled**: `isFormValid` requires `selectedBeerHasMapping` when createInvoice is true.

## Feature Analysis

### First pass

- **Server qbo_item_id null**: `upsertQboMapping` already accepts `qbo_item_id: null`; clearing selection sends null to remove mapping.
- **QBO Item query**: Uses `SELECT * FROM Item` with pagination; QueryResponse.Item normalized to array (single/array handling like customers).
- **Create in QuickBooks**: Server push creates Inventory item with beer name, QtyOnHand 0; returns qbo_item_id; mapping upserted server-side.
- **Race on connect**: Watch fires when status.connected becomes true; loadMappingData runs; no duplicate load on initial mount (watch handles it).

### Second pass

- **Push failure** (e.g. duplicate name in QBO): Error surfaced via alert; user can map to existing item instead.
- **Mappings not synced**: qbo_mappings is server-only (not in sync protocol); Integrations and Sales Order fetch from server.
- **Beer items from local**: ItemRepository.getBeerItems reads from IndexedDB (synced items); mappings from server. Consistent for mapping UI.
