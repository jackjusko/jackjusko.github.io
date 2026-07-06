# Serving vessels view, server-backed reporting, transfer coupling

## Iteration 1 – Findings
- Vessels overview needs a dedicated view to surface batch, volume, and last set-point per vessel in one place.
- Server-backed serving report should be preferred for long ranges; client fallback is needed for offline but UI must make the source clear.
- Transfer modal should nudge/require creating the packaged RECEIVE when moving beer into storage to avoid under-reporting packaged inventory.
- Set-volume workflow should warn when backdating and preview the delta that will be applied.
- History needs clearer location context on snapshots/transfers to disambiguate multi-site setups.
- Bulk on-hand should be groupable by location in the UI; vessel location metadata may be missing so we need a best-effort mapping.

## Iteration 1 – Actions
- Added a new `Vessels` view listing vessels with batch, current volume, last set volume, and quick links to batch detail.
- Wired a server-backed `/api/reports/serving` loader with local fallback and source badges; grouped bulk on-hand by inferred vessel location when available.
- Transfer modal now defaults ledger logging when a storage location is chosen and blocks saves without the packaged RECEIVE when moving into storage.
- Set-volume modal shows delta preview and warns on backdated timestamps; last set-point is displayed inline.
- History rows now show location/context on snapshots and transfers to improve readability.

## Iteration 2 – Findings
- Auto-refresh on date-range change will help keep server-backed reports fresh without extra clicks.
- Vessel location metadata may still be missing; grouping falls back to vessel name/type so cross-site clarity depends on data completeness.
- Vessels view is read-only; operators still navigate to batch detail to set volume, which is acceptable but should be noted.

## Iteration 2 – Actions
- Added watch-based auto-refresh for the serving report date range, skipping refresh while a fetch is in flight.
- Kept location grouping resilient: falls back to vessel name/type when explicit location metadata is absent.
- Left Vessels actions as links to Batch Detail to reuse existing set-volume workflow and avoid duplicate modals.
