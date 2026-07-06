# Recipe Consume: Batch History and Batch Cost

## Summary

Recipe consumption (BatchRecipeConsume) was correctly logging CONSUME ledger entries with `batch_id` and performing item removals, but (1) those events did not appear in the batch's History tab, and (2) they were not included in batch cost. Manual "Add Ingredient" creates both a batch_addition and a ledger CONSUME; to avoid double-counting, batch cost now uses ledger CONSUME as the single source for consumption materials and only counts batch_additions for water/liquid.

## Changes Implemented

### 1. BatchCostService (console + mobile)

- **CONSUME in cost:** For each ledger entry with `batch_id` and `type === 'CONSUME'`, cost is resolved from `entry.total_cost`, else `entry.unit_cost * Math.abs(entry.quantity)`, else `item.default_unit_cost * Math.abs(entry.quantity)`. Cost is classified by item category (Packaging → packaging, else materials/other) and added with `Math.abs(cost)`.
- **batch_additions restricted:** Only additions with `event_type === 'WATER_ADDITION'` or `event_type === 'LIQUID_ADDITION'` are included in materials/other. All other addition types (ingredient additions) are omitted because they also create a CONSUME entry and would otherwise be double-counted.
- **packaging_supply:** Unchanged; ledger entries with `operation_type === 'packaging_supply'` still contribute to packaging.

### 2. BatchRecipeConsume (console + mobile)

- After successfully posting all CONSUME entries, `BatchCostService.computeAndStore(batchId)` is called before sync and redirect so the batch's stored cost_summary includes recipe ingredients and syncs to the server.

### 3. Batch Detail History (console + mobile)

- Added `batchLedgerEntries` ref; in loadData, `LedgerRepository.getEntries({ batch_id: id })` is fetched and assigned.
- In `allHistoryEvents` computed, CONSUME entries are mapped to events: id `ledger-${entry.id}`, date `entry.created_at`, title "Ingredient consumed", subtitle from item name + quantity + optional note, icon 🌾, type 'CONSUME'. Existing sort by date keeps chronological order.

### 4. Documentation

- **analysis.md:** Batch cost rollups and Batch Consumption bullets updated to describe CONSUME in materials, water/liquid-only batch_additions, History tab CONSUME events, and recipe-consume cost refresh. This change doc referenced.

## First-Iteration Feature Analysis

**Edge cases / weak points considered:**

1. **Cost: null/undefined entry fields** – CONSUME handling skips when cost is null (total_cost, unit_cost, and item default all null). No change needed.
2. **History: ledger entries not refreshed after add** – Batch Detail loadData runs on mount and on sync (watch syncTrigger / lastSyncTimestamp). After recipe consume the user is redirected to batch detail; if they landed from the same session, loadData may have run before the new CONSUMEs were written. On next load or sync, batchLedgerEntries is refetched. Optional improvement: after saving an addition in BatchDetail, refetch batchLedgerEntries so History updates without full reload; same could apply when returning from BatchRecipeConsume if we ever keep the user on the same view. Deferred as non-blocking.
3. **Mobile LedgerRepository.getEntries** – Mobile app has LedgerRepository with getEntries and batch_id filter (same API as console). Verified in implementation.
4. **Water/liquid without cost** – batch_additions for WATER_ADDITION/LIQUID_ADDITION may have null unit_cost/total_cost; existing logic continues to skip when total is null. No change.
5. **Currency** – CONSUME and batch_additions both set currency from item when present; last-write-wins in the loop. Acceptable for single-currency orgs; multi-currency would need a separate strategy.

**Conclusion:** Implementation is consistent; no code changes from first-iteration analysis. Second iteration below.

## Second-Iteration Feature Analysis

**Additional review:**

6. **Refresh of cost summary after manual addition** – BatchDetail already calls `refreshCostSummary()` after saveAddition, which refetches the batch and updates costSummary from batch.cost_summary. BatchAdditionRepository.add still calls computeAndStore(batch_id), so the stored cost_summary includes the new CONSUME from that addition. No gap.
7. **History event id collision** – CONSUME events use `ledger-${entry.id}` (UUID); readings/additions/etc. use their own prefixes. No collision.
8. **getItemName when item deleted** – History uses entry.item_name (snapshot on ledger) or getItemName(entry.item_id). If item is deleted, getItemName returns "Unknown Item". Acceptable.
9. **Server sync of cost_summary** – cost_summary is stored on the batch document and synced like other batch fields; server does not recompute it. Client is source of truth for cost_summary. Documented in analysis.

**Final:** No further code changes. analysis.md and this change doc are the documentation; AGENTS.md two-iteration process completed.
