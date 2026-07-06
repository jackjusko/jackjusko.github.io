# Serving risk fixes (transfer history, server reports, keg pulls)

## Iteration 1 – Findings
- Transfer history was not visible in Batch Detail, leaving vessel moves opaque for audits.
- Long-range reporting was limited to client cache (last 100 ledger rows), so period rollups could be incomplete.
- Packaged keg pulls from serving tanks were not reflected in the ledger, risking inventory/reporting gaps.

### Changes applied (Iteration 1)
- Added transfer and volume snapshot events to Batch Detail history (console + mobile) with refresh of transfers/snapshots.
- Added server endpoint `/api/reports/serving` to compute brewed volume by location, monthly deltas (batch/brand), bulk on-hand by vessel, and packaged by location using full server data.
- Added optional ledger logging on transfer modals (console + mobile) to create RECEIVE entries for Finished Beer at destination locations.

## Iteration 2 – Findings
- Needed default Finished Beer selection to reduce form friction and avoid empty ledger item.
- Snapshot/transfer history should show destination names and methods to improve clarity.
- Server report filters must honor both start and end dates.

### Changes applied (Iteration 2)
- Defaulted ledger item to Finished Beer, and guarded transfer logging with required item/location.
- History events include destination vessel/location and snapshot method; volume snapshots reject negative values server/client.
- Server reporting endpoint tightened date range filtering to honor both start and end bounds.
