# Design: Beer inventory and TTB — simplified model

## The problem

We have two parallel systems that we keep patching together:

1. **Ledger** — item + location + quantity. TTB and on-hand reports use this. Locations have a **stage** (cellar, serving, racking_keg, case) that maps to TTB columns (b, d, f, etc.).

2. **Vessels / batch_locations** — batch + vessel + current_volume. Used for brewing workflow (readings, transfers, packaging) and for “what’s in the tank.” No required link to ledger or location.

So: production complete creates a RECEIVE at a location (ledger), but vessel volume is separate. We added “log serving removal” when you adjust volume down so ledger and tank don’t diverge. That’s a patch. We also have to infer “cellar vs keg vs case” from location stage, which breaks when one location has both tanks and kegs. The system was not designed for a clear tank vs keg vs case divide.

## What TTB actually needs

- **Inventory (Lines 1, 33, 34)**: Beer on hand, broken down by **storage type** = location stage (cellar, racking keg, bottling bulk, case). So “how much beer at cellar locations,” “at keg locations,” “at case locations.”
- **Production (Line 2)**: Beer produced (fermentation) — RECEIVE at a location; column from that location’s stage.
- **Removals (Lines 14–21, etc.)**: Beer removed by **purpose** (sale, consumption, export, …). For Line 21 (consumed on premises), TTB wants a **column breakdown** (cellar / keg / case) = **where** the beer was when removed (or **form**: draft from tank = cellar, from keg = keg, from case = case).

So TTB’s model is: **beer lives at locations; locations have a type (stage); movements are ledger entries; reporting is by purpose and by stage.**

## Principle: one source of truth for beer inventory

**Beer inventory = ledger only.**  
For Finished Beer, “how much is at location X” = sum of ledger (RECEIVE, CONSUME, TRANSFER_IN/OUT) for that location. No second “tank volume” that we try to keep in sync with ledger.

That implies:

- **Tanks that hold beer for TTB** are represented as **locations** (e.g. “Taproom Brite 1”, stage cellar or serving). When beer goes into that tank, we RECEIVE at that location. When beer leaves (pour, transfer), we CONSUME or TRANSFER_OUT from that location.
- **Vessels** stay for **brewing workflow**: which batch is in which vessel, readings, transfers between vessels, packaging from vessel. So batch_locations (vessel + batch + volume) remain operational. The design choice is how vessel volume relates to ledger.

## Two design directions

### Option A: Vessel = location (tank is a location; vessel bound to it)

- Each **serving tank** (or any tank that holds “inventoried” beer) has a **location** (e.g. “Taproom Brite 1”, stage cellar). The **vessel** has a required `location_id` pointing to that location.
- **Ledger at that location** = tank inventory for TTB. So we have a single number: on-hand at “Taproom Brite 1” = tank inventory.
- **Set volume**: Reconcile ledger to the measured volume (e.g. post a COUNT_ADJUST or a single “set to X” entry so on-hand at that location = X). No separate “batch_location.current_volume” as the source of truth for inventory; we can keep it as a **display/cache** derived from the last set or from ledger if we want.
- **Adjust volume down** (pour/loss): Post a **CONSUME** from that location. No optional “log removal” — the only way to reduce tank volume in the system is to record the removal (CONSUME). So the flow is: “I measured the tank; it’s 5 bbl now” → Set volume to 5 (reconcile ledger), **or** “we poured 2 bbl” → record CONSUME 2 bbl from this location.
- **Production complete**: RECEIVE at the **location** where the beer is going (cellar or tank location). Batch/vessel is still tracked for brewing; the RECEIVE puts inventory at that location.
- **Removals page**: Single place for all CONSUME. For on-premise, user picks **location** and **form** (cellar / keg / case) so Line 21 columns are correct. No “log serving removal” in Batch Detail; Batch Detail can link to “Record removal” for this vessel’s location or user goes to Removals.

**Roll back / change:** Remove “log serving removal” from Adjust Volume and Set Volume. Add vessel → location binding. Set Volume becomes “reconcile ledger at this vessel’s location to this value.” Adjust Volume down could either (1) require recording a CONSUME (e.g. open Removals with location prefilled) or (2) be removed in favor of “Set volume” only (new reading = new set point; any decrease is explicitly a removal).

**Pros:** One source of truth (ledger). TTB and UI always match. Clear rule: tank inventory = on-hand at that location.  
**Cons:** Requires vessel–location link and a clear “tank locations” concept; Set Volume semantics change (reconcile vs “just store a number”).

### Option B: Vessels stay operational; ledger and removals only for TTB

- **Vessel volume** (batch_locations) stays as-is: operational “what’s in the tank.” No ledger sync. Set/Adjust volume only update vessel volume and snapshots/adjustments.
- **Ledger** is used only for TTB and for **packaged** beer (keg/case) at locations. So: production complete still creates a RECEIVE at a **location** (e.g. “Cellar” or “Taproom”). That location’s on-hand is the “finished beer ready to serve/sell.” We **don’t** try to keep tank volume and that RECEIVE in sync.
- **Serving from tank**: When they pour, they don’t reduce ledger from a “tank location.” Instead, they periodically (or per pour) record a **removal** on the Removals page: CONSUME from the location that represents “draft beer” (e.g. “Taproom” or “Cellar”), and tag it as **cellar** (draft) for Line 21. So tank volume and ledger can diverge; ledger is “what we’re reporting to TTB” and vessel volume is “what’s actually in the tank.”
- **Serving from keg/case**: Beer was received or transferred to a keg/case location. CONSUME from that location; tag as keg or case for Line 21.
- **Roll back:** Remove “log serving removal” from Adjust/Set Volume. Production complete = RECEIVE at one location (conceptually “beer produced into cellar”). Removals page: add “Served from” (cellar / keg / case) for on-premise so Line 21 columns are correct.

**Pros:** Minimal change to vessels and batch_locations. Clear split: operations vs TTB.  
**Cons:** Two numbers (tank volume vs ledger) can diverge; user must remember to record removals for TTB separately from adjusting tank volume.

## Recommendation

**Option A** is the cleaner long-term design: one source of truth (ledger), tank = location, Set Volume = reconcile, removals = CONSUME only. It fits TTB’s model (beer at locations by type; movements as entries) and removes the “patch” of syncing two systems.

**Option B** is the lighter-touch redesign: keep vessel volume as operational, stop syncing it to ledger, and make Removals the single place to record CONSUME with a clear “cellar / keg / case” for Line 21.

## What to roll back (either option)

- **Batch Detail:** Remove the “log serving removal” toggle and the CONSUME creation from Adjust Volume and Set Volume modals. (Option A would replace with “reconcile to this volume” for Set and “record removal” for decrease; Option B would leave Set/Adjust as vessel-only.)
- **Production complete:** Keep RECEIVE at a location; optionally tighten copy so it’s clear that location is “where this beer is for inventory” (cellar or tank location). No change to duplicate-RECEIVE guard.
- **Removals:** Add “Served from” (cellar / keg / case) for on-premise consumption so Line 21 column breakdown is correct. Store as `consumption_form` (or equivalent) on CONSUME; TTBFormService uses it for Line 21 columns when present.
- **TTB:** Include removal_purpose `serving` (and on_premise) in Line 21 count; use consumption_form for column (b/d/f) when present, else location stage.

## Summary

| Current (patchy) | Option A (ledger = truth) | Option B (two layers) |
|------------------|---------------------------|-------------------------|
| Two truths: vessel volume + ledger | Ledger only; tank = location | Vessel = ops; ledger = TTB |
| “Log removal” when adjusting volume | Set Volume = reconcile ledger; decrease = CONSUME | No ledger from Adjust/Set; record removals on Removals |
| Line 21 column from location stage | Same; vessel’s location used | Same; + consumption_form (cellar/keg/case) on Removals |

Next step: choose Option A or B, then implement the chosen design (vessel–location binding and reconcile flow for A; Removals + consumption_form for both) and remove the “log serving removal” patch from Batch Detail.
