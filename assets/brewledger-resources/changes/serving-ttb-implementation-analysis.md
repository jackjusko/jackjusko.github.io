# Serving, Production Complete, and TTB Implementation — Feature Analysis (Iteration 1)

## Summary of implementation

Implementation followed `SERVING_TTB_IMPLEMENTATION_PLAN.md` in dependency order:

1. **Phase 1**: `consumption_form` on CONSUME (LedgerRepository, stored in `data.consumption_form`); TTB Line 21 extended to include `removal_purpose === 'serving'` and `'on_premise'`, and column breakdown uses `consumption_form` (cellar→b, keg→d, case→f) when present; Removals "Served from" dropdown for Consumption/On-premise; Batch Detail CONSUME from Adjust/Set Volume set `consumption_form: 'cellar'` (until Phase 3 rollback).
2. **Phase 4.1**: Vessel `location_id` (Dexie v15, server validation, Vessels.vue Serving location dropdown for type SERVING).
3. **Phase 2**: Production complete two-step (Serving vs Storage), location lists (Serving = stage serving + tank locations excluding occupied; Storage = generic only); one RECEIVE; transfer destination excludes serving tanks (vessels with `location_id` and tank locations); one batch per tank enforced (list filter + save validation).
4. **Phase 4 rest**: Set Volume for tank = reconcile (delta CONSUME/RECEIVE, display from ledger); Adjust Volume for tank = CONSUME/RECEIVE at vessel location; UX copy in Set/Adjust modals; transfer destinations already excluded in Phase 2.
5. **Phase 5**: Serving page (`/serving`, Serving.vue) listing tanks (vessel + location, ledger on-hand), Set volume and Record removal modals.
6. **Phase 3**: Removed "log serving removal" toggle and CONSUME creation from Adjust Volume and Set Volume (non-tank path). Tank path remains the only way to record tank CONSUME from Batch Detail and Serving page.

---

## Potential issues and edge cases (first pass)

### 1. Ledger entry `data` and sync
- **Risk**: Client builds `newEntry.data = { ...entry.data, consumption_form }`. If existing code elsewhere sends `entry.data` with other keys, they are preserved. If someone sends only top-level `consumption_form` and no `data`, we merge correctly. **Mitigation**: Server stores full entity JSON; no schema change. Existing CONSUME without `consumption_form` remain valid; TTB falls back to location stage.

### 2. TTB Line 21 and `on_premise` vs line15
- **Change**: `on_premise` and `serving` no longer add to line15 in `calculateRemovalsByPurpose`; they contribute only to Line 21 via `calculateBeerConsumedOnPremises`. **Risk**: Any report or validation that assumed on_premise in line15 could be affected. **Mitigation**: Plan explicitly required Line 21 to include on_premise and serving; line15 is "tavern" only.

### 3. Production complete: occupied tank definition
- **Logic**: Occupied = vessel has a batch_location with `current_volume > 0` and `parent_batch_id !== current batch`. **Edge case**: Same batch completing again to same tank (e.g. re-opening modal and saving again) is blocked by "already complete" RECEIVE check, not by occupied. **Risk**: If a tank is emptied (current_volume set to 0) but batch_location still exists, we still consider it "occupied" for other batches because we check any batch_location with volume. Actually we check `parent_batch_id !== batch.value.id`, so our own batch in that tank is allowed. Good.

### 4. Set Volume tank: no snapshot
- **Decision**: For tanks we do not call `BatchVolumeSnapshotRepository.recordSnapshot`; we only post CONSUME/RECEIVE. **Risk**: History of "set volume" actions for tanks is only in ledger, not in batch_volume_snapshots. **Mitigation**: Acceptable per plan (ledger = source of truth for tanks). Optional future: write a snapshot record for audit without using it for volume.

### 5. Adjust Volume tank: positive change
- **Implementation**: For tank with positive volume change we post RECEIVE and do not update `batch_location.current_volume`. **Consistency**: Display for tank is from ledger, so no inconsistency. We do create `BatchVolumeAdjustmentRepository` record for audit.

### 6. Transfer modal: `log_to_ledger` and `ledger_item_id`
- **Note**: Forms.transfer still has `log_to_ledger` and `ledger_item_id` used by template; they are not in the reactive initial state but are set by watcher and v-model. No change needed.

### 7. Serving.vue: getBeerItems async
- **Check**: `ItemRepository.getBeerItems()` is async; we await it in loadTanks and in saveSetVolume/saveRecordRemoval. Correct.

### 8. Receive / Par levels / Removals: tank locations
- **Plan**: Receive and Par levels use "locations for generic use" (no tank locations). Removals show all locations including tank locations. **Implementation**: Receive and Par levels are not yet changed to exclude tank locations in this pass; only Production complete and Transfer use the filtered lists. **Gap**: Plan §4.2 says "Use this list in: Receive (location for receiving), Par levels (location selector), Transfer destination". So we should filter Receive and Par levels to exclude tank locations. **Action**: Add in second iteration.

### 9. Mobile app
- **Plan**: "If mobile has removals or Set/Adjust, add 'Served from' and same Option A rules in a later pass." No mobile changes in this implementation.

### 10. Vessel display: tank volume from ledger
- **Places**: Batch Detail vessel table, Vessels view, Serving page. Batch Detail and Serving page use ledger on-hand for tanks when in Set Volume / tank context. Vessels view already shows `locationName` from vessel.location_id; volume there is still from batch_location. **Gap**: For vessels with location_id, Vessels view and Batch Detail vessel table could show ledger on-hand instead of batch_location.current_volume for consistency. **Action**: Consider in second iteration (or document as known deviation for non-Serving views).

---

## Integration checklist (first pass)

- [x] LedgerRepository: `data.consumption_form` merged and synced
- [x] Server: ledger entity stored as JSON (no change); vessel validation for optional `location_id`
- [x] TTBFormService: Line 21 filter and total; column breakdown via `consumption_form`; calculateBeerConsumedOnPremises extended
- [x] Removals: "Served from" and `consumption_form` passed to addEntry
- [x] BatchDetail: Production complete two-step; transfer destinations filtered; Set/Adjust tank logic; Phase 3 rollback
- [x] VesselRepository: no code change (location_id passed through create/update)
- [x] Vessels.vue: Serving location dropdown; form and save include location_id
- [x] Receive.vue: location list restricted to generic only (exclude tank locations) — second iteration
- [x] Par levels: location list restricted to generic only — second iteration
- [x] BatchLocationRepository: getByVesselIds added for occupied-tank check
- [x] Serving.vue: new view and route; Set volume reconcile and Record removal CONSUME

---

## Second-iteration actions (from first analysis)

1. **Receive and Par levels**: Implemented. Receive.vue and ParLevels.vue now load VesselRepository.getAll(), compute tank location ids (vessels with location_id), and filter location list to exclude those so only generic locations appear.
2. **Vessels / Batch Detail vessel table**: Left as acceptable. Tank volume in list/table can remain from batch_location for now; Set Volume and Serving page use ledger. Full consistency (ledger everywhere for tanks) can be a later enhancement.
3. **Tests**: Not added in this pass. Plan §4.8 recommends unit/integration tests for Set Volume (tank vs non-tank) and Adjust Volume (tank CONSUME); to be added in a follow-up.

---

## Second full review (iteration 2)

- **Data flow**: consumption_form is stored in entry.data and synced; server persists full entity. No backfill; TTB falls back to location stage when missing.
- **Production complete prefill**: When selected batch location’s vessel has location_id and that tank is not occupied, choice defaults to Serving and location to that vessel’s location. Confirmed in openProductionCompleteModal.
- **One batch per tank**: Enforced by excluding occupied tanks from Serving list and by validating on save (vessel with location_id may not have another batch with volume). BatchLocationRepository.getByVesselIds used for occupancy check.
- **Serving.vue**: Uses ItemRepository.getBeerItems() (async) and LedgerRepository.getOnhand; Set volume posts CONSUME or RECEIVE with data.source = 'set_volume_reconcile'; Record removal posts CONSUME with removal_purpose 'serving', consumption_form 'cellar'.
- **Removals**: Tank locations remain visible (plan: Removals do not filter out tank locations). Receive and Par levels now hide tank locations.
- **Documentation**: analysis.md updated with Serving/TTB Option A summary and Line 21 consumption_form bullet; serving-ttb-implementation-analysis.md records decisions and follow-ups.

---

## Iteration 3 — End-user flow and intuitiveness

### Production complete modal
- **Stale location when switching**: If user picks Storage and a location, then switches to Serving, `location_id` can still point to a storage location. The dropdown only shows serving options, so the bound value may be invalid or show blank. **Fix**: Watch `destChoice` and clear `location_id` when it changes so user must re-select a valid location.
- **Empty Serving list**: If user selects Serving but there are no serving locations or tanks (all occupied or none set up), the location dropdown is empty with no explanation. **Fix**: Show helper text when Serving is selected and `productionCompleteServingLocations.length === 0`.
- **"Vessel" ambiguity**: The "Vessel" dropdown is the batch location (which vessel in this batch we're recording volume for), not the destination tank. Users might think it's "destination vessel." **Fix**: Relabel to "Vessel (in this batch)" and add short helper: "Which vessel's volume you're recording."

### Serving page
- **Record removal quantity**: User could enter an amount greater than on-hand (e.g. 100 bbl when tank has 2). That would post a large CONSUME and could go negative in reporting. **Fix**: Label "Amount to remove (bbl)" and validate: if quantity > onHand, show warning and block save (or allow with confirmation). Prefer blocking with clear message: "Cannot remove more than current on-hand (X bbl)."
- **Set volume when onHand is null**: Display "—" for null on-hand can look like a bug. **Fix**: Display "0" when onHand is null for consistency with "empty tank."

### Batch Detail — Adjust Volume (tank, positive)
- **Positive change**: We show explanatory copy only for negative (removal). For positive we post RECEIVE but don't explain. **Fix**: When tank and positive change, show: "This will add to ledger at [Location] (RECEIVE)."

### Removals — Served from
- **Technical helper**: "TTB Line 21 column: Cellar→b, Keg→d, Case→f" is correct but not user-friendly. **Fix**: Add a plain-language line above or beside: "Where was the beer served from?" and keep the TTB line as secondary or shorten to "For TTB reporting (Line 21)."

### Iteration 3 fixes implemented
- Production complete: Watch `destChoice` and clear `location_id` only when user *changes* choice (not on initial open; use oldVal check). Empty Serving list: show helper with link to Vessels when `productionCompleteServingLocations.length === 0`. Label "Vessel (in this batch)" and helper "Which vessel's volume you're recording."
- Serving page: Record removal label "Amount to remove (bbl)"; computed `recordRemovalExceedsOnHand`; block save and disable button when quantity > onHand; show inline message "Cannot remove more than current on-hand (X bbl)." Set volume: display "0" when onHand is null; openSetVolume prefill measured_volume to tank.onHand ?? 0.
- Batch Detail: Adjust Volume tank positive — show copy "This will add to ledger at [Location] (RECEIVE) and increase on-hand there." Set Volume tank: display "0" when current volume is null.
- Removals: Served from helper text changed to "Where was the beer served from? (For TTB Line 21 reporting.)"

---

## Iteration 4 — Second end-user flow pass

### Flow: New user, first time marking production complete
- They may have no serving tanks (no vessels with location_id). They select Serving and see "No serving locations or tanks available..." with link to Vessels. **Good.** They might then go to Vessels, create a Serving Tank, and link a location. After that, Production Complete → Serving will show that tank. **Edge case**: If they have only one batch location and it's a fermenter (no location_id), we don't prefill Serving; they might not know they need to create a serving tank first. The empty-state message covers the case when they *do* pick Serving. No change.

### Flow: Switching Serving ↔ Storage
- User picks Storage, selects "Cellar 1", then changes mind and picks Serving. We now clear location_id so they must pick a serving location. **Good.** If the list of serving locations is empty, they see the helper. **Good.**

### Flow: Serving page — tank with 0 on-hand
- User clicks "Record removal". Modal opens. Amount to remove: they type 1. We show "Cannot remove more than current on-hand (0 bbl)." and disable Record. **Good.** They can still "Set volume" to reconcile (e.g. enter 0 or a measured value). **Good.**

### Flow: Batch Detail — vessel table volume for tanks
- For a batch location whose vessel has location_id, the table still shows `bl.current_volume` (from batch_location). So if they never ran Set Volume on the tank, batch_location might have a value from production complete or an old snapshot, while ledger might differ. **Known**: Plan says display for tanks from ledger; we didn't change the vessel table to show ledger on-hand per row (would require async load per row). So the vessel table can show batch_location volume for tanks. When they open Set Volume for that tank, we show ledger on-hand and reconcile. **Document only**; optional future: show ledger on-hand in vessel table for tanks.

### Flow: Removals — user picks "Consumption" then doesn't pick "Served from"
- We allow saving with consumption_form unset. TTB falls back to location stage. **Good.** Helper text is now friendlier. **Good.**

### Flow: Production complete — "Vessel (in this batch)" with one vessel
- When there's only one batch location, we prefill batch_location_id. So the dropdown shows one option. User might not understand why "Vessel" is there. The helper "Which vessel's volume you're recording" helps. **Acceptable.**

### Additional iteration 4 checks
- **Confirm button label**: Production complete modal: "Mark Complete". **Good.** Serving Set volume: "Save". Record removal: "Record". **Good.**
- **Cancel/close**: All modals have cancel or close. **Good.**
- **Validation messages**: Production complete: "Please choose Serving or Storage.", "Please choose Serving or Storage and select a location." **Good.** Serving Record removal: inline "Cannot remove more than..." **Good.**
- **Router link in Production complete**: We use `<router-link to="/vessels">`. Inside a modal this may work but could open in same tab (navigating away and closing the flow). **Consider**: Use a simple text "Vessels page" or open in new tab: `<router-link to="/vessels" target="_blank">`. For in-app flow, opening in same tab is disruptive. **Fix**: Use `target="_blank"` so they can open Vessels in new tab and keep the modal open, or just keep as-is and document that clicking the link navigates away (user can use back). Prefer not opening new tab by default (can be annoying). Leave as-is; the message is clear.
- **Set Volume (tank) — no "Measured at" on Serving page**: On Batch Detail, Set Volume has Measured at, Method, Note. On Serving page we only have "Measured volume (bbl)". For consistency and audit we could add optional note to Serving Set volume. **Optional**; not required for iteration 4. Omit for now.

### Iteration 4 fixes implemented
- **Serving.vue Record removal**: Added computed `recordRemovalExceedsOnHand`; Record button disabled and save blocked when quantity > on-hand; inline message "Cannot remove more than current on-hand (X bbl)" already in template.
- **Serving.vue Set volume**: When opening Set volume modal, prefill measured_volume with `tank.onHand ?? 0` so empty tanks show 0; display "0" when on-hand is null in the helper text.
- **Serving.vue tank cards**: On-hand in list shows "0" instead of "—" when null (consistent with modals and "empty tank").
- **BatchDetail.vue Set volume (tank)**: Current on-hand helper shows "0" instead of "—" when ledger volume is null for consistency with Serving page.

---

## End-user flow assessment (summary)

**Verdict: The flow is good and well thought through.** Iterations 3–4 addressed the main UX risks.

**What works well**
- **Production complete**: Serving vs Storage is clear; location clears when switching so users can’t submit a wrong combo; empty Serving state explains “no tanks” and links to Vessels; “Vessel (in this batch)” + helper removes ambiguity.
- **Serving page**: Purpose is stated at the top; Set volume (reconcile) vs Record removal (pour/loss) is clear; over-removal is blocked with a clear message; empty tanks show 0 everywhere (list + modals); empty state points to Vessels.
- **Removals**: “Where was the beer served from?” is user-friendly; TTB Line 21 is secondary; optional Served from with fallback is acceptable.
- **Batch Detail (tanks)**: Set/Adjust Volume explain ledger impact; null on-hand shows as 0; positive Adjust explains RECEIVE.

**Minor trade-offs (acceptable)**
- **Discovery**: Users only see “No serving locations or tanks” after choosing Production Complete → Serving. They then get a clear link to Vessels. Slightly “fail then recover” but the message is good; no change.
- **Vessel table volume**: Tank rows still show batch_location volume; Set Volume modal shows ledger. Documented as known; optional future improvement.
- **Production complete link**: Link to Vessels opens in same tab (navigates away from modal). Kept as-is to avoid forced new tabs; message is clear.

**Conclusion**: The end-user flow pass was done well. The flow is intuitive for “mark complete → Serving/Storage,” “Serving page → Set volume / Record removal,” and “Removals → Served from.” Validation and copy support correct use and prevent obvious mistakes (e.g. removing more than on-hand).

---

## Production complete: serving-tank exclusivity and source vessel clear (2026-02-12)

### Requirements
1. Batches must not be able to go into serving tanks except via the final Production Complete step.
2. When Production Complete succeeds, the vessel the brew was in (source) should go back to empty with no batch associated.

### Implementation

**1. No batch_locations for serving tanks**
- **Console**: `BatchLocationRepository.create()` looks up the vessel; if `vessel.location_id` is set (serving tank), throws: "Batches cannot be assigned to serving tanks. Use Mark Production Complete to send beer to a serving tank." Transfer/Split/Combine already exclude serving tanks from destination vessels and locations; this blocks any other code path (e.g. legacy batch.vessel_id, setSplitsForBatch, combineSplits) from creating a batch_location for a serving tank.
- **Server**: In `batch_location` validation, when not a delete, fetch vessel by `entity.vessel_id`; if vessel data has `location_id`, return false (reject the change). Sync from other clients cannot create/update a batch_location for a serving tank.

**2. Clear source vessel on Production Complete**
- In `saveProductionComplete` (BatchDetail.vue), after creating the RECEIVE and updating the milestone: call `BatchLocationRepository.delete(forms.productionComplete.batch_location_id)` to soft-delete the source batch_location, then reload `batchLocations`. The vessel that was completed from is now empty and has no batch (getByVesselIds / getByBatchId exclude deleted_at). Success message updated to mention "Source vessel cleared."
