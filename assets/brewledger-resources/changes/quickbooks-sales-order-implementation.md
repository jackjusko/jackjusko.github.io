# QuickBooks Sales Order Implementation

## Summary

Added a **Distribution** section to the console sidebar with **Integrations** (QuickBooks connection) and **Sales Order** (removal + optional Invoice sync) views. Desktop-only. No storefront.

## What Was Added

### Server (server/server.js)

- **GET /api/integrations/qbo/customers**: Fetches QBO Customer list (paginated, handles single/array response). Used for Sales Order Customer dropdown.
- **POST /api/integrations/qbo/push/invoice**: Creates Invoice in QBO from a CONSUME ledger entry with `removal_purpose: 'sale'`. Requires `qbo_customer_id`, item mapping (`qbo_mappings`), idempotent (skips if `qbo_invoice_id` already set).
- **Ledger validation**: Added `qbo_customer_id` and `qbo_invoice_id` to sync validation (string or null).
- **Callback page**: Updated copy to "Distribution → Integrations" instead of "Settings → Accounting".

### Console

- **QBOService.js**: `getStatus`, `getAuthorizeUrl`, `exchangeCode`, `disconnect`, `getCustomers`, `pushInvoice`.
- **Integrations.vue**: QuickBooks connection status, Connect button (opens auth URL), manual code/realmId exchange form, Disconnect. Shows "QuickBooks not configured" when `!hasClientConfig`.
- **SalesOrder.vue**: Form with Customer (QBO dropdown, required when sync enabled), Inventory (Finished Beer items), Location, Quantity, Wholesale Price, "Create Invoice in QuickBooks?" checkbox. Creates CONSUME with `removal_purpose: 'sale'`, awaits sync, then optionally pushes Invoice. Re-validates on-hand at submit. Disables sync toggle when QBO not connected.
- **LedgerRepository**: Added `qbo_customer_id`, `qbo_invoice_id` to addEntry.
- **Router**: `/integrations`, `/sales-order` routes (requiresAuth: true).
- **App.vue**: Distribution nav group (Integrations, Sales Order), page descriptions, page titles.

## Feature Analysis

### First pass

- **Sync before push**: SalesOrder awaits `SyncService.sync()` before `pushInvoice` so server has the entry.
- **Idempotency**: Server checks `entry.qbo_invoice_id`; returns early if already synced.
- **Optimistic update**: After pushInvoice succeeds, client updates local ledger entry with `qbo_invoice_id`.
- **On-hand validation**: Re-check at submit; reject if quantity exceeds available.
- **Double submit**: Submit button disabled while `isSaving`.
- **Customer required**: When createInvoice is true, `qbo_customer_id` must be set (validation in isFormValid).
- **Empty states**: Messages with links when no beer items or locations.

### Second pass

- **QBO Customer pagination**: Server loops with STARTPOSITION/MAXRESULTS; first page uses `MAXRESULTS` only.
- **Customer single/array**: QBO may return Customer as object when one result; normalized to array.
- **Org scoping**: pushInvoice loads entry with `WHERE id = ? AND org_id = ?`.
- **Negative quantity**: CONSUME uses `quantity: -Math.abs(qty)`.
- **Subscription gating**: Distribution routes use requiresAuth: true; router guard applies same trial/subscription rules as other app routes.
