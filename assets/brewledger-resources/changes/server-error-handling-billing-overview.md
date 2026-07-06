# Server Error Handling & Billing Overview

## 0. Stripe Integration Check (server/server.js)

### 0.1 Webhook

- **Signature**: Reject with 400 when `webhookSecret` is set but `stripe-signature` header is missing (no attempt to parse body without verification).
- **Customer/subscription IDs**: Normalize `customer` and `subscription` (and invoice `customer`) to string IDs in all handlers: `typeof x === 'string' ? x : x?.id`, so expanded objects from Stripe do not break DB lookups.
- **Status mapping**: In `customer.subscription.*` events, map Stripe `past_due` and `unpaid` to our `past_due` (not `cancelled`), so status stays consistent with `invoice.payment_failed`.
- **Price ID**: Single constant `STRIPE_PRICE_ID` at top of `createApp` used by both checkout session creation and webhook (no duplicated literal).
- **checkout.session.completed**: Verify org exists (`get('SELECT id FROM orgs WHERE id = ?', [orgId])`) before UPDATE; skip update if org not found.
- **Plan/price handling**: In subscription handler, support both `items.data[0].price` as object (`.id`) or string, and legacy `subscription.plan` as object or string, when matching to `STRIPE_PRICE_ID`.

### 0.2 Checkout & Confirm

- **create-checkout-session**: Uses `STRIPE_PRICE_ID` for `line_items[0].price`.
- **confirm-subscription**: Retrieve session with `expand: ['customer', 'subscription']` so IDs are populated reliably; existing code already handles both string and object.

### 0.3 No Code Change (Verified)

- **Webhook body**: Route uses `bodyParser.raw({ type: 'application/json' })`; signature verification receives raw buffer. Correct.
- **Webhook response**: Always returns 200 with `{ received: true }` after processing (errors logged only); avoids Stripe retries. Correct.
- **cancel-subscription**: Null check for org already added; Stripe cancel then DB update. Correct.
- **create-portal-session**: Uses default portal; no per-request config. Correct.

---

## 1. Error Handling Overview (server/server.js)

### 1.1 Current State

- **Route-level try/catch**: Most async routes wrap logic in try/catch and return 400/401/403/500 with JSON `{ error: '...' }`.
- **No global error handler**: There is no four-argument Express error middleware (`(err, req, res, next)`). Unhandled rejections or thrown errors in async routes can leave the client hanging (no response) or cause "Cannot set headers after they are sent" if a response was already sent.
- **authMiddleware**: In the catch block it sends `res.status(500).json({ error: 'Database error' })` but does **not** `return`. Execution stops only because there is no code after the catch; adding code later could double-send. Should use `return res.status(500).json(...)`.
- **Database connection**: The SQLite `db` constructor callback only logs errors; the app continues. Acceptable if DB is optional for health checks; if DB is required, consider exiting or marking unhealthy.
- **Webhook**: Stripe webhook verifies signature (returns 400 on failure), then processes events in try/catch. Processing errors are logged but the handler still returns `200` with `{ received: true }` so Stripe does not retry. Intentional; no change needed for webhook semantics.
- **Error message leakage**: Some billing routes return `error: e.message` or `'Stripe error: ' + e.message`, exposing Stripe or internal details to the client. Prefer generic messages in production and log details server-side.

### 1.2 Recommended Fixes

1. **Add global error handler**: Register an error middleware at the end of the middleware chain (before `return app`) to catch any unhandled errors and async rejections that are forwarded via `next(err)`. Respond with 500 and a generic message; log the actual error.
2. **authMiddleware**: Use `return res.status(500).json({ error: 'Database error' });` in the catch block.
3. **Optional**: In async route handlers, wrap in a higher-order wrapper that calls `next(err)` on rejection so the global handler can respond. Current pattern of try/catch in every route is acceptable if consistently applied; the global handler is a safety net for missed cases.

---

## 2. Billing Issues & Fixes

### 2.1 cancel-subscription: Null org

- **Issue**: `const org = await get('SELECT ... FROM orgs WHERE id = ?', [orgId]);` can return `undefined` if the org does not exist (e.g. deleted org, bad data). The code then accesses `org.stripe_subscription_id` and `org.stripe_customer_id`, causing `TypeError: Cannot read properties of undefined`.
- **Fix**: After fetching `org`, if `!org` return `404` or `400` with a clear message (e.g. "Organization not found") and do not access `org.*`.

### 2.2 create-portal-session: New config on every request

- **Issue**: The route creates a new Stripe billing portal configuration on every request (`stripe.billingPortal.configurations.create(...)`). This is inefficient and can create many configurations in the Stripe dashboard; Stripe may rate-limit or discourage this.
- **Fix**: Use the Stripe account default portal by omitting `configuration`, or create one configuration (e.g. at startup or first use) and reuse its ID (e.g. env var or in-memory cache). Simplest: remove the custom configuration block and use the default portal (no `configuration` parameter).

### 2.3 invoice.payment_failed webhook

- **Issue**: The handler is a no-op (`break`). Failed payments are not reflected in org status (e.g. `past_due`), and there is no logging.
- **Fix**: At minimum log the event and customer/invoice id. Optionally set `subscription_status` to `past_due` for the org when the invoice is subscription-related (and optionally revert to `active` on `invoice.payment_succeeded` — already done).

### 2.4 Billing error responses leaking internal/Stripe messages

- **Issue**: Routes return `error: e.message` or `'Stripe error: ' + e.message`. This can expose Stripe error strings or internal details to the client.
- **Fix**: Log the full error (with message/code) server-side. Respond with a generic user-facing message (e.g. "Billing operation failed. Please try again or contact support.") and avoid including raw `e.message` in the JSON response (or restrict to known safe codes if desired).

---

## 3. Implementation Summary

| Area | Change |
|------|--------|
| Global | Add `app.use((err, req, res, next) => { ... })` before `return app`. |
| authMiddleware | `return res.status(500).json(...)` in catch. |
| cancel-subscription | Null check for `org`; return 404 when org not found. |
| create-portal-session | Use default Stripe portal (remove per-request config create) or cache single config. |
| invoice.payment_failed | Log event; optionally update org to `past_due`. |
| Billing routes | Sanitize error responses (generic message, log detail). |

---

## 4. Second-Pass Notes

- **Async rejections**: Express 4 does not automatically catch unhandled promise rejections in async route handlers. The global error handler only runs when a route calls `next(err)`. Routes that use try/catch (as currently) are fine; the global handler is a safety net for any future route that forwards errors via `next(err)`.
- **Portal configuration**: Using the default Stripe portal (no custom `configuration`) means behavior is controlled by the Stripe Dashboard portal settings. If you need to disable subscription plan switching or set cancellation options, configure the portal in Stripe Dashboard, or create a single configuration (e.g. via script or at startup) and pass its ID in `portalConfig.configuration`.
- **invoice.payment_failed**: Setting `past_due` is consistent with `invoice.payment_succeeded` setting `active`; both are scoped to subscription invoices and existing orgs.

---

## 5. Edge Cases Considered

- **Webhook idempotency**: Stripe may retry. Webhook handler already returns 200 after processing; DB updates are idempotent by event id where applicable. No change.
- **confirm-subscription race**: User might call before webhook runs. Current 400 "Subscription not ready yet" is appropriate; no change.
- **Double response**: Ensured all error paths in authMiddleware and billing use `return res.status(...).json(...)` where applicable.
- **DB unavailable**: Global error handler will catch rejections from `run`/`get`/`all` if a route forgets try/catch and uses `next(err)`.
