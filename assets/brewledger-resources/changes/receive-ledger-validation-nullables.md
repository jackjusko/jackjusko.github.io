## Receive ledger validation (desktop) — analysis

### Iteration 1 (root cause & plan)
- Observed server `/api/sync` rejects desktop RECEIVE entries with `console.warn("Invalid ledger received ...")`.
- Payload from console includes optional metadata: `vendor` string, `invoice_number: null`, `unit_cost`/`total_cost` numbers.
- Current `validateEntity('ledger')` treats optional fields as invalid when `null` (expects string/number only), causing rejection for `invoice_number: null` (and would for `unit_cost: null` or `total_cost: null`).
- Risk: Any ledger entry that omits invoice/vendor/cost by setting `null` fails validation and sync, blocking receive workflow and leaving on-hand stale.
- Plan: Allow optional ledger metadata fields (`vendor`, `invoice_number`, `unit_cost`, `total_cost`, `qbo_bill_id`) to be null/undefined, retaining type checks when provided. Keep referential checks unchanged.

### Iteration 2 (post-fix review)
- Updated server ledger validation to accept `null` for optional cost/vendor/invoice/QBO fields while still enforcing correct types when values exist.
- Rechecked receive flow expectations: desktop receive may omit invoice/cost; referential checks (item/location) remain enforced, so on-hand integrity is preserved.
- Residual risk: QBO bill push still requires costs to create bills; allowing null simply skips bill push scenarios, which aligns with “no invoice/unit cost required” guidance. No further server changes needed now.
