# Feature Analysis: Finished Beer Per-Batch Items

## Summary
When a batch is marked production complete, the system now resolves or creates a **per-beer** Finished Beer item (by recipe or by batch name) instead of using a single default beer item. When total on-hand for a Finished Beer item reaches zero across all locations, the item is soft-deleted automatically; the default "Finished Beer" item is never auto-deleted.

## Implementation (Iteration 1)

### 1. Beer item resolution (production complete)
- **ItemRepository.getOrCreateBeerItemForBatch(batch)** (console + mobile):
  - If `batch.recipe_id` is set: return the existing beer item with that `recipe_id` (same product as other batches from that recipe).
  - Else: match by normalized batch name (trim, collapse whitespace, case-insensitive). Two batches with the exact same name share one beer item.
  - If no match: create a new item with `category: 'Finished Beer'`, `unit: 'bbl'`, `name` = batch name (preserve casing), `recipe_id` when present.
- **BatchDetail.vue** (console + mobile): Replaced "first beer item" with `ItemRepository.getOrCreateBeerItemForBatch(batch.value)` before creating the RECEIVE entry. Duplicate production-complete check and `data.source = 'production_complete'` unchanged.
- **BatchForm.vue** (console + mobile): Batch create now passes `recipe_id` so batches created from a recipe persist it for resolution.

### 2. Zero-on-hand cleanup
- **LedgerRepository.cleanupBeerItemsAtZero()** (console + mobile):
  - Loads all active Finished Beer items (excluding soft-deleted).
  - Skips the default item (name === 'Finished Beer' && category === 'Finished Beer').
  - For each other beer item, computes total on-hand via `getTotalOnhand(item.id)`; if total <= 0, soft-deletes the item (sets `deleted_at`, `updated_at`, `sync_status: 'pending'`, bumps `version`). No CONSUME entries are created; ledger history is preserved.
- Cleanup is invoked after:
  - **addEntry**: when the entry’s item is a Finished Beer item.
  - **transfer**: when the transferred item is a Finished Beer item.
  - **reverseEntry**: when the reversed entry’s item is a Finished Beer item.

### 3. UI and sync
- **Beers.vue** and **ItemsList** (and mobile equivalents) already use `ItemRepository.getBeerItems()` / `getAll()`, which filter `!deleted_at`, so soft-deleted beers are hidden.
- Server already rejects soft-delete only for the default Finished Beer item; other beer items’ `deleted_at` updates sync normally.

## Risks and edge cases (Iteration 1)

1. **Race / ordering**: Cleanup runs after the ledger transaction. If two operations run in quick succession (e.g. two CONSUMEs that together zero the item), both might see total > 0 before the other commits; the second run will then see zero and soft-delete. Acceptable.
2. **Name collisions**: Normalization is trim + collapse spaces + toLowerCase. Different display names that normalize the same (e.g. "Amber Ale" vs "amber ale") map to one beer item. Intentional.
3. **Recipe vs name**: When `batch.recipe_id` is set, resolution is by recipe only; batch name is ignored for matching. When `recipe_id` is null, resolution is by name only. No mixed fallback (e.g. recipe first, then name) beyond the current order.
4. **Default item**: We never create a second "Finished Beer" item when the batch name is empty; we create with name `batchName || 'Finished Beer'`. If the org has no default item yet (e.g. pre-migration), getBeerItems could be empty and getOrCreateBeerItemForBatch would create an item named "Finished Beer" without the default protection. Mitigation: TTB migration and registration ensure the default item exists; getOrCreateBeerItemForBatch does not special-case it for creation.
5. **Sync order**: Item create/update (including soft-delete) is pushed with sync; order of ledger vs item changes in the same sync batch could theoretically matter. Server applies changes; no strict ordering dependency identified.
6. **Batch recipe_id**: Batches created before this change may not have `recipe_id` set; resolution falls back to name. Batches created from BatchForm with a recipe now store `recipe_id`.

## Iteration 2 review

- **Apply remote entry**: **Done.** `applyRemoteEntry` now calls `cleanupBeerItemsAtZero()` when the applied entry’s item is a Finished Beer item, so sync-applied CONSUME/TRANSFER that zeros a beer item will soft-delete it on that client.
- **Recompute cache**: If the client ever calls `recomputeCache()`, on-hand is rebuilt from ledger; cleanup is not run. A one-off recompute could leave zero-on-hand beer items active until the next beer-affecting write. Acceptable for now; recompute is typically used after reset/repair.
- **TTB reporting**: TTBFormService and reports filter by beer category and use ledger/onhand; soft-deleted items have no on-hand, so they disappear from inventory totals. Historical ledger entries still reference the item id; snapshot names (item_name) preserve display in history. No change required for TTB form logic.

## Iteration 2 implementation

- **applyRemoteEntry** (LedgerRepository, console + mobile): After adding a remote entry and updating cache, if the entry’s item is a Finished Beer item, call `cleanupBeerItemsAtZero()`.
- Document in analysis.md: resolution rules (recipe-first, else name), zero-on-hand soft-delete, default item protection, and that Beers/Items lists filter deleted_at.
