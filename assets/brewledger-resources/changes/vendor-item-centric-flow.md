# Vendor Item-Centric Flow

## Overview
Refactor vendor from a per-receipt input to an item-level property. Users set vendor when creating/editing items; Receive derives vendor from each line item instead of a receipt-level input.

## Implementation Summary

### 1. ItemForm (console + mobile)
- Added "Vendor (optional)" input field to both platforms
- Vendor stored in item JSON via ItemRepository (no schema change)
- Placed after Unit, before Default Unit Cost

### 2. Receive (console + mobile)
- Removed vendor input from receipt metadata
- Added `getItemVendor(id)` helper to look up vendor from items list
- Each RECEIVE ledger entry gets `vendor: getItemVendor(line.item_id) || null`
- Removed vendor pill from console toolbar; removed standalone Vendor card from sidebar and confirmation
- Confirmation summary shows vendor per line (location · vendor) when present

### 3. init_db cleanup
- Removed `item_templates` CREATE TABLE and interval ALTER from init_db.js
- Legacy table—no UI uses it; existing DBs keep their data; new installs won't create it

## Data Flow
- **Item create/edit**: Form → ItemRepository.create/update → item stored with vendor in JSON
- **Receive**: For each line, lookup item by item_id → use item.vendor → pass to LedgerRepository.addEntry
- **Display**: Inventory shows item.vendor; Ledger entries store vendor per line; confirmation shows vendor per line

## Feature Analysis (First Iteration)

### Potential issues
1. **Items without vendor**: When receiving items that have no vendor set, ledger entry gets `null`. Acceptable—optional field.
2. **Mixed vendor receipt**: Multiple line items from different vendors—each entry gets its own vendor. No single "Vendor" card in confirmation; per-line display handles this.
3. **Legacy item_templates**: process_csv_items.js and server routes still reference item_templates. If table doesn't exist (fresh DB), those routes fail. No UI calls them; acceptable for now.

### Integration points
- ItemRepository: Already spreads all fields; vendor flows through
- LedgerRepository: Already accepts and stores vendor
- Server validation: Already validates entity.vendor for items and ledger
- Inventory: Already displays item.vendor, sortable/filterable

### Edge cases
- Editing existing item: form loads with `form.value = { ...item }`—vendor included if present
- New item: vendor defaults to `''`; empty string persists; server accepts null/string
- buildSummaryEntry (console): Ensures vendor on summary entry from ledger entry or getItemVendor fallback

## Feature Analysis (Second Iteration)

### Review of first iteration
- All integration points verified
- buildSummaryEntry correctly includes vendor (from entry or fallback)

### Additional considerations
1. **Mobile createdEntries**: Mobile pushes raw LedgerRepository response. Entry has vendor from our passed value. item_name and location_name come from LedgerRepository's DB lookups. No buildSummaryEntry on mobile—entry object has all needed fields.
2. **Sync**: Ledger entries with vendor sync normally; server already validates and stores
3. **QBO push**: QBO Bill uses mapping.qbo_vendor_id, not ledger entry vendor. No change needed.
4. **process_csv_items.js**: Still inserts into item_templates. Table may not exist on fresh DB after our init_db change. Script would need to create table or init_db would need to run first with old code. User said don't delete existing data—removing from init_db means new DBs won't have the table. process_csv_items is a separate script; if run against a fresh DB it may fail. Document as known limitation or leave for future cleanup.

## Documentation
- analysis.md: Update Receive and Receiving sections to reflect item-centric vendor
- Add entry for init_db item_templates removal
