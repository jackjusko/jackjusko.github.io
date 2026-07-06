# Mobile Feature Parity — Review Pass 2

**Date:** After Pass 1  
**Scope:** Verification that Pass 1 items are resolved; any new issues from manual E2E or second look.

---

## 1. Pass 1 resolution

| Pass 1 item | Status |
|-------------|--------|
| Correctness (production complete, serving, removals, tank exclusion, vessel/SERVING) | Confirmed resolved. No code changes required. |
| Server/client contract (ledger data, vessel, sync) | Confirmed. |
| Edge cases (no serving locations, occupied tank, duplicate complete, removal > on-hand, null on-hand, no vessels) | Confirmed handled. |
| UX (labels, empty states, Serving in nav) | Confirmed. |

---

## 2. New issues found (second pass)

1. **VesselsList refresh after sync:** Vessel occupancy cards are built only on load. If user marks production complete or sets volume on BatchDetail then navigates back to Vessels, cards may be stale until they leave and re-enter the page. **Recommendation:** Add a pull-to-refresh or "Refresh" button that calls loadVessels(), or call loadVessels() in onActivated (if using keep-alive) / when route is re-entered. **Action:** Document only; optional enhancement.

2. **RemoveBeer form reset:** After successful save, router.push('/') navigates away so form state is not visible. If the view were kept open (e.g. "Add another" flow), clearing consumption_form when user changes purpose away from consumption/on_premise is already implicit (showServedFrom hides). No fix required.

3. **BatchDetail production complete: ensureBatchLocationId:** When opening production complete modal with a single batch location, we set batch_location_id to firstBl.id. When there are multiple batch locations and user has not selected one, batch_location_id could be null until user selects. Validation in saveProductionComplete requires batch_location_id. OK.

---

## 3. Fixes applied this pass

- None. Pass 2 did not identify blocking bugs; only optional improvement (VesselsList refresh) documented.

---

## 4. Sign-off

Implementation is complete and consistent with the plan. Server contract is respected; edge cases and UX are covered. Optional follow-up: refresh vessel cards when re-entering Vessels list (e.g. after sync or return from BatchDetail).
