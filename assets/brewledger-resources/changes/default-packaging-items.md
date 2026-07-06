# Default Packaging Items for Organizations

## Summary

Two default packaging items are now created for every organization:
- **Empty 1/6th bbl keg**
- **Empty 1/2 bbl keg**

These support the Mark Production Complete packaging flow (packaged keg destination).

## Implementation

### New Organizations (register-org)

In `server/server.js`, after creating categories and milestone template, the register-org endpoint now creates these two Packaging items for each new organization. They use category "Packaging", unit "ea", and currency "USD".

### Existing Organizations (migration)

`server/migrate_backfill_vessel_locations.js` now includes **Phase 2**: for each existing org, if the Packaging category exists and the org does not already have these items, they are created. Idempotent—skips orgs that already have items with these exact names.

### BatchDetail Prefilling

The Mark Production Complete modal prefills the supply line when packaging to kegs. The logic matches Packaging items whose name includes "keg" and the format key (e.g. "1/6" for 1/6 bbl). The new names "Empty 1/6th bbl keg" and "Empty 1/2 bbl keg" match this logic. Console `KEG_FORMAT_PRESETS` `packagingItemName` updated to the new default names for documentation.

## Usage

```bash
# Run migration (creates default items for existing orgs)
node server/migrate_backfill_vessel_locations.js

# Dry run first
DRY_RUN=1 node server/migrate_backfill_vessel_locations.js
```

## Notes

- Items have no `default_unit_cost`; users can set cost when receiving.
- No initial inventory; users receive empty kegs via Receive before packaging.
- Seed test account (`seed_test_account.js`) uses different names (Keg 1/6 bbl, Keg 1/2 bbl) for its test data; no change to seed.
