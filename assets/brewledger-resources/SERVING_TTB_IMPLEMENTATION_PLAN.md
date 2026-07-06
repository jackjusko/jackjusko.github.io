# Serving, Production Complete, and TTB — Detailed Phase-by-Phase Implementation Plan

This document is the **implementation-ready** plan. It incorporates the current plan plus these decisions:

- **Production complete:** First ask **Serving** or **Storage**. If Serving → show all serving locations (including tank locations). If Storage → show only non-serving locations (no tank locations).
- **No manual transfer to serving tanks:** Users cannot manually transfer to a serving tank. The only way beer enters a serving tank is via **production complete** (one RECEIVE at that location). Transfer UI must exclude or block destination = serving tank (vessel with `location_id`).
- **Phase ordering (10.5):** Phase 4’s tank CONSUME path (Adjust Volume down → CONSUME, Serving page Record removal) is **implemented and shipped together with or before** Phase 3 rollback. Do not roll back “log serving removal” until that path exists.
- **Reconcile (10.6):** Compute delta (target − current on-hand); post **CONSUME** (delta) if delta < 0, **RECEIVE** (delta) if delta > 0. No COUNT_ADJUST.
- **UX (10.7):** Set Volume and Adjust Volume modals show context-specific copy and tests for vessel-with-location vs vessel-without-location.
- **One batch per tank:** Multiple batches **cannot** occupy one serving tank. Enforce: a vessel with `location_id` may have at most one batch (one batch_location) at a time; production complete to a tank that already has a batch is blocked or tank is excluded from list.

---

## Reference: Target State (summary)

- Ledger = single source of truth for tank inventory; display volume for tanks = ledger on-hand at that location.
- Only **serving** vessels have `location_id`. One location per serving tank; one batch per tank.
- Tank locations: hidden from Receive, Par levels, and **Transfer destination**; visible on Removals, Serving page, Batch Detail, Locations admin.
- Production complete: one RECEIVE (or single ledger record) at chosen location; **no** separate manual transfer to serving tanks.
- Set Volume (tank) = reconcile ledger via delta CONSUME/RECEIVE. Adjust Volume down (tank) = post CONSUME from that location.
- Removals: tank locations visible with ledger on-hand; removal from tank = CONSUME. “Served from” = Cellar | Keg | Case for Line 21.

---

# Phase 1 — consumption_form and Line 21 (cellar / keg / case)

**Goal:** Tag on-premise consumption by form (cellar / keg / case) and include tank pours in Line 21. No rollback yet.

## 1.1 Ledger: add `consumption_form`

- **Client:** [LedgerRepository.js](platforms/console/src/repositories/LedgerRepository.js) — In `addEntry` (or wherever CONSUME is created), accept optional `consumption_form` = `'cellar'` | `'keg'` | `'case'`. Persist in entry `data` (e.g. `data.consumption_form`) so it syncs.
- **Server:** [server/server.js](server/server.js) — In ledger validation / processChange for ledger entries, allow and persist `consumption_form` in `data` (no new DB column if `data` is JSON).
- **Check:** Existing CONSUME entries without `consumption_form` remain valid; TTB will fall back to location stage.

## 1.2 TTB Line 21: include serving/on_premise and use consumption_form for columns

- **File:** [TTBFormService.js](platforms/console/src/services/TTBFormService.js)
- **Who counts as Line 21:** Extend the filter for `line21Entries` (and for `calculateBeerConsumedOnPremises`) to include:
  - Existing: `removal_purpose === 'consumption'` and (note contains "premises" or "on-site")
  - New: `removal_purpose === 'serving'`
  - New: `removal_purpose === 'on_premise'`
- **Column breakdown (b, d, f):** Where Line 21 columns are built (e.g. `aggregateByStage('line21', line21Entries, ...)`):
  - If entry has `consumption_form` (or `data.consumption_form`): map `cellar` → b, `keg` → d, `case` → f.
  - Else: keep current behavior using `getStage(entry.location_id)`.
- **calculateBeerConsumedOnPremises:** Add the same removal_purpose conditions so the Line 21 total includes tank pours and on_premise.

## 1.3 Batch Detail: set consumption_form when creating CONSUME from Adjust/Set Volume

- **File:** [BatchDetail.vue](platforms/console/src/views/BatchDetail.vue)
- In `saveAdjustVolume` and `saveSetVolume`, when creating the CONSUME entry (current “log serving removal” flow), set `consumption_form: 'cellar'` (or pass in `data`) so those removals map to Line 21 column b.
- (This block is removed in Phase 3; until then, existing CONSUME-from-Adjust/Set get the right column.)

## 1.4 Removals: “Served from” dropdown

- **File:** [Removals.vue](platforms/console/src/views/Removals.vue)
- When removal purpose is on-premise (e.g. Consumption, On-premise consumption), show **“Served from”** dropdown: **Cellar (tank)** | **Keg** | **Case**.
- On save, pass selected value to LedgerRepository.addEntry as `consumption_form` (or in `data`).
- If user does not set it, leave `consumption_form` unset; TTB continues to use location stage.

**Phase 1 exit criteria:** CONSUME can carry consumption_form; Line 21 includes serving/on_premise and uses consumption_form for b/d/f; Removals has “Served from”; Batch Detail CONSUME (until rollback) sets cellar.

---

# Phase 2 — Production complete: Serving vs Storage, then location list

**Goal:** User first chooses **Serving** or **Storage**; then sees only the relevant locations (serving = all serving locations including tanks; storage = only non-serving locations). One RECEIVE (or single ledger record) on save; no manual transfer to serving tanks later.

## 2.1 Production complete modal: two-step flow

- **File:** [BatchDetail.vue](platforms/console/src/views/BatchDetail.vue)
- **Step 1 — Choice:** After vessel and volume produced, show a **required** choice (e.g. radio or segmented control): **“Serving”** (beer going on tap) or **“Storage”** (beer going to cellar/keg/case).
- **Step 2 — Location dropdown:**
  - If **Serving:** Show locations that are “serving” type:
    - All locations whose **stage** is `serving`, **and**
    - All **tank locations** (locations linked to a vessel via `vessel.location_id`), so tank locations appear even if stage is cellar.
    - Group by stage or show as “Serving tanks” and “Serving (other)” if useful. Include current ledger on-hand for tanks (and optionally show “Empty” or “Has batch” for one-batch-per-tank clarity).
  - If **Storage:** Show only locations that are **not** tank locations (not linked by any vessel). These are cellar (bulk), racking_keg, bottling_bulk, case — i.e. “locations for generic use” / non-tank. Group by stage (Cellar, Racking keg, Case, etc.) with optgroups.
- **Prefill:** If the selected batch location’s vessel has `location_id`, and user has not changed the choice, default to **Serving** and prefill location to that vessel’s location (if it’s in the Serving list).

## 2.2 One RECEIVE only; no manual transfer to serving tanks

- **Production complete:** On “Mark Complete”, create **one** RECEIVE at the chosen location (as today). No separate transfer step. Beer “arrives” at that location via this single record.
- **Transfer modal (Batch Detail):** Ensure that **destination** cannot be a serving tank when the user is doing a manual transfer:
  - **Option A (recommended):** In the transfer destination list (vessels and/or locations), **exclude** vessels that have `location_id` (serving tanks). So “Transfer to vessel” dropdown does not list serving tanks; if destination is by location, exclude tank locations from the destination location dropdown. Users can only put beer into a serving tank via Production Complete.
  - **Option B:** Show serving tanks but disable or show validation error: “Beer can only be moved to serving tanks via Mark Production Complete.”
- Implement Option A: use “locations for generic use” (non-tank) for **Transfer destination location**; for **destination vessel**, filter out vessels that have `location_id`. Document in Phase 4.

## 2.3 Copy and validation

- Intro copy: “This records production for TTB. Choose **Serving** (on tap) or **Storage** (cellar/keg/case), then pick the location.”
- Validation: “Please choose Serving or Storage and select a location.”
- Helper under location dropdown: “Serving = on tap (includes serving tanks). Storage = cellar, keg, or case locations.”

## 2.4 One batch per tank: enforce in production complete

- When building the **Serving** location list, **exclude** any tank location (vessel-linked location) that **already has a batch** in it. “Already has a batch” = there exists a batch_location for that vessel with non-zero volume (or vessel is linked and ledger on-hand > 0 and we treat that as “occupied”). Simpler rule: a vessel with `location_id` has at most one batch_location with current_volume > 0 (or at most one batch ever, if we don’t allow emptying and re-use in the same release). So when listing “Serving” locations that are tank locations, filter to tanks that are “empty” (no batch in vessel, or ledger on-hand 0).
- **Validation on save:** If user somehow picks a tank location that already has a batch, server or client validates and returns an error: “This serving tank already has a batch. One batch per tank.”
- **Data model:** No schema change required if we enforce in UI and API: when creating production-complete RECEIVE for a tank location, check that no other batch has that vessel’s batch_location with volume (or that ledger at that location is 0 before this RECEIVE). Alternatively, enforce “one batch_location per vessel with location_id” in business logic (e.g. when assigning batch to vessel, reject if vessel has location_id and already has a batch).

**Phase 2 exit criteria:** Production complete asks Serving vs Storage; Serving shows all serving locations including tanks (excluding occupied tanks); Storage shows only non-tank locations; one RECEIVE on save; Transfer cannot target serving tanks; one batch per tank enforced.

---

# Phase 3 — Rollback “log serving removal” (after Phase 4 tank path exists)

**Goal:** Remove the “log serving removal” toggle and CONSUME creation from Adjust Volume and Set Volume. **Must be done only after** Phase 4 (and optionally Phase 5) so that tank pours can still be recorded via “Adjust Volume down → CONSUME” and/or Serving page “Record removal.”

## 3.1 Dependency (10.5)

- **Order:** Implement **Phase 4.5, 4.6, and Phase 5** (Serving page) **before or together with** Phase 3. Do **not** ship Phase 3 alone; otherwise users have no way to record tank CONSUME after rollback.
- **Cutover:** Optionally ship Phase 4 + Phase 5 first, then Phase 3 in the same release so the cutover is atomic.

## 3.2 Remove Adjust Volume “log serving removal”

- **File:** [BatchDetail.vue](platforms/console/src/views/BatchDetail.vue)
- Remove form fields: `log_removal`, `removal_location_id` (and any watchers that set them).
- Remove the LedgerRepository.addEntry CONSUME block from `saveAdjustVolume`.
- Keep: volume change, BatchVolumeAdjustmentRepository update, BatchLocationRepository update for `current_volume` (for vessels **without** location_id; for vessels with location_id, Phase 4 will post CONSUME and optionally not write batch_location or still update it for non-ledger display — per plan we derive tank display from ledger so we may not update batch_location for tank vessels).

## 3.3 Remove Set Volume “log serving removal”

- Same in BatchDetail.vue: remove `log_removal`, `removal_location_id`, watchers, and CONSUME creation from `saveSetVolume`. Keep snapshot and volume update for non-tank vessels; for tank vessels Phase 4 handles reconcile.

## 3.4 Docs

- Update [analysis.md](analysis.md) and [changes/serving-volume-ledger-alignment-analysis.md](changes/serving-volume-ledger-alignment-analysis.md): state that “log serving removal” was removed; tank volume changes are recorded via Phase 4 (reconcile or CONSUME) and Removals/Serving page.

**Phase 3 exit criteria:** No “log serving removal” in Adjust/Set Volume; tank CONSUME path is only via Phase 4 (Adjust down → CONSUME) and Removals/Serving page.

---

# Phase 4 — Option A: vessel–location, no transfer to tanks, reconcile = delta CONSUME/RECEIVE, UX copy, one batch per tank

**Goal:** Only serving vessels have `location_id`. Tank locations hidden from Receive, Par levels, and **Transfer destination**. Set Volume for tanks = reconcile via CONSUME/RECEIVE delta. Adjust Volume down for tanks = post CONSUME. In-modal UX copy and tests. One batch per tank enforced.

## 4.1 Schema and API: `location_id` on vessels (serving only)

- **Client schema:** Add optional `location_id` (UUID) to vessel entity. [VesselRepository](platforms/console/src/repositories/VesselRepository.js): read/write `location_id`.
- **Server:** Add `location_id` to vessel table (migration if needed). Validate: location exists; optionally restrict to stage cellar or serving. Only **serving** vessels should have `location_id` (fermenters and other vessels do not).
- **Vessel create/edit UI:** Allow assigning a location **only when** the vessel is intended as a serving tank (dropdown of locations with stage cellar or serving). Do not set location_id for fermenters.

## 4.2 “Locations for generic use” and where tank locations appear

- **Generic list:** Locations that are **not** linked by any vessel (`vessel.location_id`). Use this list in:
  - **Receive** (location for receiving)
  - **Par levels** (location selector)
  - **Transfer destination** (both destination vessel and destination location): **exclude** serving tanks so users cannot manually transfer to a serving tank.
- **Removals:** Do **not** filter out tank locations. Show all locations with current inventory (ledger on-hand). Tank locations appear with their ledger on-hand; removal from tank = CONSUME.
- **Production complete:** Uses its own logic (Phase 2): Serving = serving + tank locations; Storage = generic only.
- **Serving page, Batch Detail, Locations admin:** Tank locations appear as today.

## 4.3 Set Volume when vessel has location: reconcile with CONSUME/RECEIVE (10.6)

- **File:** BatchDetail.vue (and Serving page when it reuses this logic).
- If the selected batch location’s **vessel** has `location_id`:
  - **Display:** Show “current volume” from **ledger on-hand** at that vessel’s location (do not read `batch_locations.current_volume` for tanks).
  - **On save:** Compute **delta** = (entered measured value) − (current on-hand at vessel’s location). Units in barrels.
  - If **delta < 0:** Post **CONSUME** at that location with quantity = |delta|, note e.g. “Set volume reconcile (measured value X)”, and optional `data.operation_type` or similar so it’s not confused with production.
  - If **delta > 0:** Post **RECEIVE** at that location with quantity = delta, note e.g. “Set volume reconcile (measured value X)”, and `data.source: 'set_volume_reconcile'` or similar so it’s not counted as production complete.
  - **Do not** write `batch_locations.current_volume` for this vessel; display is always from ledger.
- If vessel has **no** location_id: keep current behavior (update batch_location and snapshot only).

## 4.4 Adjust Volume when vessel has location: negative = CONSUME

- If vessel has `location_id` and user enters a **negative** volume change:
  - Post a **CONSUME** at that vessel’s location with quantity = |volume_change|, `removal_purpose: 'serving'`, `consumption_form: 'cellar'`, note referencing the adjustment.
  - Optionally still update batch_location.current_volume for internal consistency, or leave it derived from ledger; plan says derive display from ledger so prefer not writing batch_location for tank.
- If vessel has no location_id: keep current behavior (update batch_location and adjustment record only; no ledger).

## 4.5 Transfer: never to serving tanks (10.4 clarified)

- **Batch Detail Transfer modal:** Destination vessel dropdown: **exclude** vessels that have `location_id`. Destination location dropdown (if used): use “locations for generic use” only, so tank locations are not selectable. Thus users **cannot** manually transfer beer into a serving tank; the only way beer enters a serving tank is production complete (one RECEIVE).
- **Server:** If a transfer or ledger entry is submitted that would add beer to a vessel’s location (e.g. TRANSFER_IN to a location that is a tank location), optionally reject with a clear message: “Transfers to serving tanks are not allowed. Use Mark Production Complete to send beer to a serving tank.”

## 4.6 Production complete prefill

- When opening production complete modal, if the selected (or first) batch location’s vessel has `location_id`, set the choice to **Serving** and prefill the location dropdown to that vessel’s location (if it’s in the Serving list and not already occupied by another batch).

## 4.7 One batch per tank: enforce (10.8 resolved)

- **Definition:** A “serving tank” (vessel with `location_id`) may have **at most one batch** at a time. So at most one batch_location with that vessel_id and current_volume > 0 (or at most one batch that has ever been production-completed to that tank and not yet fully removed).
- **Production complete:** When building the Serving location list, exclude tank locations that are “occupied”: e.g. vessel has a batch_location with current_volume > 0 for a **different** batch, or ledger on-hand at that location > 0 and the batch we’re completing is not the one already there. Simplest: exclude any tank (vessel with location_id) that already has any batch_location with current_volume > 0. When saving production complete to a tank location, validate (client and optionally server): this vessel must not already have another batch.
- **Transfer / other flows:** We already disallow transfer to serving tanks; so no need to check “target tank has batch” there. For production complete, the list and save validation above suffice.

## 4.8 Set Volume / Adjust Volume: UX copy and tests (10.7)

- **Set Volume modal:** When the selected vessel **has** `location_id`, show in-modal copy: “This will reconcile ledger at **[Location Name]** to the entered value. Current on-hand: **X** bbl.” When vessel has **no** location_id: “Updates vessel volume only (no ledger change).”
- **Adjust Volume modal:** When vessel **has** `location_id` and user enters a **negative** change: “This will record a **removal** from **[Location Name]** (ledger CONSUME) and reduce on-hand there.” When vessel has no location_id or positive change: keep current copy (e.g. “Updates vessel volume”).
- **Tests:** Add unit or integration tests for (1) Set Volume with vessel that has location_id → reconcile creates CONSUME or RECEIVE; (2) Set Volume with vessel without location_id → only batch_location/snapshot updated; (3) Adjust Volume negative with vessel that has location_id → CONSUME created; (4) Adjust Volume with vessel without location_id → no CONSUME.

**Phase 4 exit criteria:** Only serving vessels have location_id; Transfer cannot target serving tanks; Set Volume (tank) = delta CONSUME/RECEIVE; Adjust Volume down (tank) = CONSUME; display volume for tanks from ledger; in-modal copy and tests in place; one batch per tank enforced on production complete.

---

# Phase 5 — Serving page (tank serving only)

**Goal:** One place to see serving tanks (vessel + location, current volume from ledger), Set volume (reconcile), and Record removal (pour). No multiple batches per tank (already enforced in Phase 4).

## 5.1 New view and route

- Add [Serving.vue](platforms/console/src/views/Serving.vue) (or equivalent path). Register route `/serving`. Add sidebar entry “Serving” (e.g. under Production or Inventory).

## 5.2 Content

- **Explanation:** Short copy that serving tanks are tied to a location; inventory = ledger at that location; set volume when you measure; record removal when beer is poured or lost.
- **List:** Serving tanks = vessels that have `location_id`. For each: vessel name, linked location name, **current volume = ledger on-hand at that location** (from LedgerRepository.getOnhand or equivalent for Finished Beer at that location), and batch name if any (from batch_location for that vessel).
- **Actions per tank:**  
  - **Set volume:** Open same reconcile flow as Batch Detail (enter measured value; compute delta; post CONSUME or RECEIVE). Reuse logic from Phase 4.5.  
  - **Record removal (pour):** Open Removals with that location and consumption_form cellar prefilled (e.g. query/route params), or a small modal that posts CONSUME from that location with `removal_purpose: 'serving'`, `consumption_form: 'cellar'`.
- **Optional:** Link to Locations admin and vessel edit to add/manage tank locations or link vessel to location.

## 5.3 UX

- Copy and layout make “volume and serving” clear; users can see which tanks have beer and where to set volume or record a pour.

**Phase 5 exit criteria:** Serving page exists; lists tanks with ledger-derived volume; Set volume and Record removal work; nav and docs updated.

---

# Phase 6 — Documentation and edge cases

- **analysis.md:** Document Option A (vessel–location, one batch per tank, display from ledger, no transfer to serving tanks); production complete Serving vs Storage; consumption_form and Line 21; Removals “Served from”; Set/Adjust reconcile and CONSUME; Serving page. Remove or update “log serving removal” references.
- **Change docs:** Update serving-volume-ledger-alignment-analysis.md; add serving-storage-ttb-line21.md (or similar) for consumption_form and Line 21.
- **Existing CONSUME:** No backfill; TTB falls back to location stage when consumption_form missing.
- **Mobile:** If mobile has removals or Set/Adjust, add “Served from” and same Option A rules in a later pass.
- **Serving reports / dashboard:** For vessels with location_id, derive on-hand from ledger at vessel’s location. Do not use batch_locations.current_volume for tank display.
- **Fermenters:** Only serving vessels have location_id; fermenters stay location-less.

---

# Dependency order (implementation sequence)

1. **Phase 1** — consumption_form + Line 21 + Removals “Served from” + Batch Detail cellar tag. No dependency on vessel location_id.
2. **Phase 2** — Production complete Serving vs Storage, location lists, one RECEIVE, no transfer to tanks, one batch per tank. Can depend on “tank locations” concept (vessel.location_id); if Phase 4 not yet done, “Serving” list can be stage=serving only until Phase 4 adds vessel-linked locations.
3. **Phase 4** — Vessel location_id, “locations for generic use,” Transfer exclude serving tanks, Set Volume reconcile (CONSUME/RECEIVE), Adjust Volume CONSUME, UX copy, one batch per tank. Depends on schema and VesselRepository.
4. **Phase 5** — Serving page. Depends on Phase 4 (vessels with location_id).
5. **Phase 3** — Rollback “log serving removal.” **Must come after Phase 4 (and ideally Phase 5)** so tank CONSUME path exists.
6. **Phase 6** — Docs and edge cases; ongoing and final pass after 1–5.

---

# Files summary

| Area | Files |
|------|--------|
| Phase 1 | LedgerRepository.js, TTBFormService.js, server.js (ledger), BatchDetail.vue, Removals.vue |
| Phase 2 | BatchDetail.vue (production complete modal, transfer destination filter) |
| Phase 3 | BatchDetail.vue, analysis.md, serving-volume-ledger-alignment-analysis.md |
| Phase 4 | Vessel schema + server, VesselRepository.js, vessel create/edit UI, LocationRepository or shared “locations for generic use” and “tank locations” helpers, BatchDetail.vue (Set Volume reconcile, Adjust Volume CONSUME, Transfer exclude tanks, UX copy), Receive.vue, Removals.vue, Par levels, Transfer flow |
| Phase 5 | Serving.vue, router, nav, Removals.vue (prefill support) |
| Phase 6 | analysis.md, change docs |

---

This implementation plan is the single detailed reference for building the full serving, production complete, and TTB Option A flow with the constraints above.
