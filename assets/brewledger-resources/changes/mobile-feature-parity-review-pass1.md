# Mobile Feature Parity — Review Pass 1 (Critical Senior Dev)

**Date:** Implementation completion  
**Scope:** Phases 1–7 (schema, production complete, removals TTB Line 21, serving, inventory costs, tank exclusion, vessel occupancy)

---

## 1. Correctness

| Item | Status | Notes |
|------|--------|--------|
| Production complete creates exactly one RECEIVE | OK | saveProductionComplete checks duplicate via ledger entries with data.source === 'production_complete'; creates single RECEIVE then deletes source batch_location. |
| Source batch_location deleted after production complete | OK | BatchLocationRepository.delete(forms.productionComplete.batch_location_id) called; batchLocations reloaded. |
| Serving Set volume / Record removal math and validation | OK | Set volume: delta = measured - onHand; CONSUME (negative) or RECEIVE (positive). Record removal: quantity <= onHand enforced via recordRemovalExceedsOnHand, button disabled. |
| Removals consumption_form sent and stored in data | OK | LedgerRepository.addEntry merges entry.data and entry.consumption_form into data; RemoveBeer passes consumption_form when purpose is consumption/on_premise. |
| Tank exclusion applied (Receive, ReorderList, BatchDetail transfer/production complete) | OK | Receive and ReorderList filter locations by vessel location_id; BatchDetail uses transferDestinationLocations, transferDestinationVessels, productionCompleteServingLocations, productionCompleteStorageLocations. |
| Vessel location_id and SERVING type wired end-to-end | OK | Dexie v15 adds vessels.location_id; VesselsList form has SERVING type and location dropdown; Serving.vue loads tanks by vessel.location_id; sync passes entity through. |

**Issues found:** None. Logic matches console and plan.

---

## 2. Server / client contract

| Item | Status | Notes |
|------|--------|--------|
| Ledger entries have data.consumption_form and data.source | OK | LedgerRepository addEntry builds data: { ...entry.data, ...(consumption_form != null ? { consumption_form } : {}) }; RECEIVE with data: { source: 'production_complete' } from BatchDetail and Serving. |
| Vessel and batch_location payloads match server validation | OK | Vessel create/update send location_id (optional). BatchLocationRepository.create rejects vessel_id when vessel.location_id set; server validates same. |
| Sync and applyRemoteUpsert handle new fields | OK | VesselRepository applies full vessel object; LedgerRepository writes full newEntry including data. No schema strip. |

**Issues found:** None.

---

## 3. Edge cases

| Case | Status | Notes |
|------|--------|--------|
| No serving locations available | OK | Production complete modal shows "No serving locations or tanks available. Add a serving tank on Vessels...". Serving page shows empty state with link to Vessels. |
| Occupied tank | OK | openProductionCompleteModal excludes occupied tanks from productionCompleteServingLocations; saveProductionComplete validates one batch per tank. |
| Duplicate production complete | OK | saveProductionComplete checks ledger for existing RECEIVE with data.source === 'production_complete' and returns error. |
| Record removal > on-hand | OK | recordRemovalExceedsOnHand computed; Record button disabled and save blocked in saveRecordRemoval. |
| Null on-hand for tanks | OK | Serving and VesselsList display "0" when onHand is null; Set volume prefills measured_volume with tank.onHand ?? 0. |
| Receive/Reorder with no vessels (tankLocationIds empty) | OK | Filter is locations.filter(l => !tankLocationIds.has(l.id)); when no vessels have location_id, tankLocationIds is empty, all locations shown. |

**Issues found:** None.

---

## 4. UX

| Item | Status | Notes |
|------|--------|--------|
| Labels and validation messages | OK | Production complete: "Please choose Serving or Storage.", "Please choose Serving or Storage and select a location."; Serving: "Cannot remove more than current on-hand (X bbl)." |
| Empty states | OK | Serving page and production complete modal have clear empty-state copy and link to Vessels. |
| Navigation (Serving in nav) | OK | /serving route added; BottomNav includes Serving between Remove and Count. |

**Issues found:** None.

---

## 5. Fixes applied this pass

- None required. All checklist items passed.

---

## 6. Follow-up recommendations

- Manual E2E: Create batch → Mark Production Complete to Serving → open Serving page → Set volume and Record removal → Removals with Served from → verify TTB form on console. Receive and Reorder: confirm only non-tank locations in dropdowns. Vessels: confirm occupancy cards and Edit (SERVING + location) flow.
- Consider adding a "Refresh" control on VesselsList to recompute vesselCards after sync (e.g. after returning from BatchDetail). Currently user must navigate away and back to refresh occupancy.
