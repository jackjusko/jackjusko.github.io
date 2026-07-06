# Vessels & Packaging Bug Hunt Fixes

## Summary

Proactive bug hunt for vessels, kegging, and packaging flows. Fixes applied per plan item 4.1.

## 4.1 Packaging volume vs vessel capacity — with manual override

**Issue:** Packaging flow did not validate that `volumeBarrels` (numKegs × format size or numCases × format size) is ≤ the selected vessel's `current_volume`. Users could enter 100 kegs when the vessel only had 5 bbl, creating ledger entries that over-report production.

**Fix:** Before save, compare `volumeBarrels` to the selected batch_location's `current_volume` with unit conversion (bbl, gal, L). If packaging volume exceeds vessel volume, show a confirmation dialog: "Packaging volume (X bbl) exceeds vessel volume (Y bbl). Continue anyway?" with Cancel and Override options.

**Implementation:**
- **Console** `platforms/console/src/views/BatchDetail.vue`: Added `productionCompleteVolumeOverrideConfirmOpen`, `productionCompleteVolumeExceedData`, `productionCompleteVolumeOverride` refs; volume check in `saveProductionComplete`; override dialog and handlers.
- **Mobile** `platforms/brewledger-app/src/views/BatchDetail.vue`: Same changes for parity.

**Unit conversion:** Vessel volume uses batch `planned_volume_unit` (bbl, gal, L). Conversion to barrels: bbl = 1:1; gal → bbl = /31; L → bbl = /117.35.
