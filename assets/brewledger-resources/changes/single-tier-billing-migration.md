# Single-Tier Billing Migration – Feature Analysis

## Summary of change
Billing was migrated from a 3-tier subscription (Essential/Standard/Growth) to a single subscription. One Stripe price ID is used; max locations are 100 for all orgs; landing and billing UIs show one price and a “Get Started” CTA.

## Implementation summary

### Server (`server/`)
- **Webhook**: Map only `price_1SwR4oPzAOv62FoydSUATwxQ` → plan name `subscription`. Removed essential/standard/growth price mappings.
- **create-checkout-session**: No `plan` body param. Uses single `line_items: [{ price: BILLING_PRICE_ID, quantity: 1 }]`. Metadata only `orgId`.
- **confirm-subscription**: Sets `subscription_plan = 'subscription'` (no plan from metadata).
- **cancel-subscription**: Sets `subscription_plan = 'subscription'` when reverting after cancel.
- **create-portal-session**: Portal configuration created with `subscription_update: { enabled: false }` so plan switching is removed; cancel, invoice history, payment method update remain.
- **Auth**: Register INSERT includes `subscription_plan = 'subscription'`, `max_locations = 100`. Login and register responses use default `maxLocations: 100` and `subscriptionPlan: 'subscription'` when missing. `getOrgMaxLocations` default fallback 100.
- **init_db**: `max_locations INTEGER DEFAULT 100`, `subscription_plan TEXT DEFAULT 'subscription'`. ALTER for `max_locations` uses DEFAULT 100.
- **migrate_max_locations_100.js**: New script; runs `UPDATE orgs SET max_locations = 100` for all existing orgs.
- **migrate_billing.js**: Updated to DEFAULT 'subscription' for subscription_plan when column is added via ALTER (aligns with single plan).

### Frontend – Mobile (`platforms/brewledger-app/`)
- **Billing.vue**: Single tier card: $49.99/mo, description “Includes full access to all BrewLedger features, including batch tracking, inventory management, and full access to the desktop management console.” One “Get Started” button; no plan param to checkout. Success/expired messaging simplified. `subscribe()` posts create-checkout-session with no body `plan`.
- **Settings.vue**: Plan display shows “Subscription” when `subscriptionPlan === 'subscription'`, fallback “Subscription”.

### Frontend – Console (`platforms/console/`)
- **Landing.vue**: Pricing section replaced with one block: $49.99/mo, same description string, “Get Started” → `/register`.
- **Settings.vue**: Plan display “Subscription” when plan is `subscription`, fallback “Subscription”.

## Edge cases and risks

1. **Existing DBs**: Orgs created before this change may have `max_locations` = 3 or 10. Run `node server/migrate_max_locations_100.js` so all orgs get 100. New orgs from register get 100 via INSERT; new tables from init_db get DEFAULT 100.
2. **Existing Stripe subscriptions**: Orgs with old price IDs (essential/standard/growth) will not match the single price in the webhook; webhook will log “Unknown Price ID” and update only status, not plan. They keep existing `subscription_plan` in DB. UI shows “Subscription” for `subscription`; old plan names (essential/standard/growth) still display as stored. No data migration of existing customers was required per user.
3. **Portal config per session**: Each create-portal-session creates a new Stripe billing portal configuration. Acceptable for “no plan switch”; if rate limits become an issue, consider creating one configuration and reusing its ID.
4. **Billing.vue success flow**: On return with `session_id`, we re-fetch session if null before confirm. Ensures auth header is present for confirm-subscription.
5. **Backend tests**: Any tests that stub create-checkout-session with `plan` or assert three tiers / old price IDs need updating to single price and no plan param.
6. **Router guards**: Guards that check subscription or plan still work; they rely on `subscription_status` and optionally plan. Single plan name `subscription` is sufficient.
7. **FAQ on landing**: “Do all plans include the same features?” remains; answer is still correct (single plan, same features).

## Second-pass considerations

- **Tests**: Grep for billing tests, create-checkout-session, plan, essential/standard/growth, max_locations 3 or 10; update or add cases for single tier and max_locations 100.
- **Documentation**: README or runbooks that mention “three tiers” or “Essential/Standard/Growth” should be updated to single subscription and 100 locations.
- **Stripe Dashboard**: Ensure the price `price_1SwR4oPzAOv62FoydSUATwxQ` exists and is $49.99/mo in the correct Stripe mode (test/live).
- **migrate_billing.js**: Updated to DEFAULT 'subscription' for subscription_plan when column is added via ALTER.
- **analysis.md**: Section 10 (Billing), subscription flow, subscription enforcement, Development Utilities, and landing content description updated to reflect single tier and max_locations 100.

---

## Debugging pass (final)

- **backfill_trials.js**: Was still setting `subscription_plan = 'essential'` when backfilling trial data. Updated to `subscription_plan = 'subscription'` so backfilled orgs match the single plan.
- **analysis.md line 1201**: "Subscription Limits: Location count enforcement based on plan tier" was outdated. Updated to "single limit of 100 locations per org (`max_locations`)".
- **analysis.md Section 10**: Expanded per AGENTS.md with a **Single-Tier Billing (Current Model)** subsection: detailed description of the feature, functionality (checkout → webhook/confirm → location enforcement → portal), and constraints/assumptions (Stripe price requirement, migration requirement, legacy subscriptions, backfill consistency).
