# Feature Analysis: Mobile Registration – Remove Default Seed

## Summary

Mobile app (`Register.vue`) no longer calls `seedData()` after successful organization registration. New organizations created from mobile now start empty (after sync fetches server-side defaults: categories, milestone template). This aligns mobile with the desktop console, which never seeded default items/locations/inventory on registration.

## Change

- **Removed**: `await seedData()` call and `seedData` import from `platforms/brewledger-app/src/views/Register.vue`
- **Retained**: `seedData()` in `platforms/brewledger-app/src/utils/seed.js` for Demo Mode (Login.vue `demoMode()`)

## Rationale

- Consistency with desktop console registration flow
- Users should build their own items/locations/inventory rather than receiving sample data
- Server already seeds categories and milestone template; sync populates these after registration

## Edge Cases

- **Existing mobile users**: No change; they already have their data
- **New orgs from mobile**: Will have empty local data until first sync; sync populates categories, milestone template, etc. from server. No sample items or inventory.
- **Demo Mode**: Unchanged; `Login.vue` demo mode still calls `seedData()` for offline demo.
