# Storage Option Commented Out in Mark Production Complete

## Summary

The **Storage** destination option in the Mark Production Complete modal has been commented out (UI hidden) in both console and mobile BatchDetail. The underlying code is retained for potential future use.

## Rationale

User feedback indicated that the Storage option is rarely or never needed. When finishing a batch, beer either goes to a serving tank (Serving) or gets packaged (keg/case). The Storage option was for bulk beer going to a generic cellar location (not a vessel). This workflow is an edge case for most breweries.

## Implementation

- **Console** `platforms/console/src/views/BatchDetail.vue`: Storage radio and Storage optgroup commented out. Intro copy and validation messages updated to "Serving or Packaged".
- **Mobile** `platforms/brewledger-app/src/views/BatchDetail.vue`: Storage radio and Storage template block commented out. Intro copy and validation messages updated.

## Code Retained

- `productionCompleteStorageLocations` computed/ref — still used for Packaged (keg/case) destination selection
- `destChoice === 'storage'` logic in watchers and save flow — remains in place; no selection path to it while UI is commented out
- Server and TTB logic — no changes; Storage was client-side only

## Restoring

To restore the Storage option, uncomment the radio and optgroup/template blocks in both BatchDetail.vue files and revert the copy/validation message changes.
