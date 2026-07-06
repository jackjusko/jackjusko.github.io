# Serving tank snapshots, transfers, and reporting

## Iteration 1 – Findings
- New set-volume workflow must ensure measured volume cannot be negative and snapshots derive clean deltas without double-counting when backfilled.
- Transfers need persistence and sync coverage so vessel moves and keg pulls do not get lost cross-device.
- Location taxonomy needs a serving-friendly stage that still maps to TTB cellar columns to avoid breaking reports.
- Reporting needs explicit aggregations for brewed volume, monthly deltas (batch + brand), bulk on-hand, and packaged on-hand by location.

### Actions after Iteration 1
- Added dedicated tables/stores for `batch_volume_snapshots` and `batch_location_transfers` with sync wiring (server, console, mobile).
- Added set-volume UI (console + mobile) that records snapshots, rebuilds derived adjustments, and refreshes vessel volumes; added transfer logging modal per vessel.
- Introduced `serving` location stage (mapped to cellar) across server validation, settings/location forms, and TTB column mapping.
- Added `ServingReportsService` to compute the four requested aggregates client-side.

## Iteration 2 – Findings
- Snapshot inputs still needed guardrails for negative volumes; transfers rely on volume availability checks to prevent underflow.
- Transfer history is stored but not yet visualized alongside timeline/history; ledger tie-ins for packaged draws remain a follow-up for deeper costing/TTB rollups.
- Reporting service uses local ledger cache; ledger sync is capped to the most recent entries, so long-range periods may need server-side endpoints later.

### Actions after Iteration 2
- Hardened snapshot validation (non-negative) and server-side validation; kept chronological rebuild to avoid duplicate deltas on backfilled setpoints.
- Added per-vessel last-set summary, serving-stage option in mobile LocationForm, and ensured transfers/snapshots sync on both clients.
- Documented remaining risks: add UI surfacing for transfer history, consider server-driven reporting for periods beyond cached ledger history, and integrate ledger moves for packaged keg pulls if compliance needs it.
