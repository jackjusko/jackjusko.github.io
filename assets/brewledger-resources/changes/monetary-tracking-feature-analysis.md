# Monetary Tracking & QBO – Feature Analysis

## Iteration 1 (current build)
- Coverage: item cost fields added; receiving UI captures vendor/invoice/unit cost; ledger entries carry `unit_cost`/`total_cost`; QBO backend endpoints + console Accounting tab scaffolded.
- Gaps/Risks:
  - Packaging supplies were not costed or rolled into batch totals.
  - Batch cost summary was not refreshed after packaging or additions, risking stale UI and sync payloads.
  - No manual hook to push a RECEIVE into QBO from the UI; mapping workflow lacked a quick entry point for testing Bills.
- Plan: tag packaging supply ledger entries with costs, recompute/store batch cost summaries on additions/packaging, and expose a manual RECEIVE→Bill push in the Accounting tab.

## Iteration 2 (post-fix)
- Changes made:
  - PackagingRunRepository now tags supply CONSUME entries with `unit_cost`, `total_cost`, `operation_type: 'packaging_supply'`, and BatchCostService consumes them; both mobile and console recompute/store `cost_summary` after additions and packaging runs.
  - Batch Detail refreshes and displays cost summaries; BatchCostService writes `cost_summary` to batches for sync.
  - Console Accounting tab adds a manual RECEIVE→Bill push input; QBO service supports the push API.
- Residual risks:
  - QBO auth remains manual (copy code/realmId); no automated vendor/account discovery—mappings require hand-entered IDs.
  - Console lacks a first-class receiving screen with cost capture (mobile only).
  - No multi-currency conversion; values assume a single currency per org.
  - QBO push relies on mapping presence; error handling is surfaced but no retry queue yet.
