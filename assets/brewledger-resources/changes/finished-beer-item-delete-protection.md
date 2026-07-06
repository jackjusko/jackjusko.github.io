# Finished Beer Item Delete Protection — Feature Analysis

## Task
Prevent deletion of the default "Finished Beer" item (created at org registration / migration, required for TTB tracking). Mirror the existing protection for the Finished Beer **category**.

## First Iteration Analysis

### Implementation Summary
1. **Server (`server/server.js`)**: In sync `processChange` for type `'item'`, when `entity.deleted_at` is set, reject the change if the item's category is `'Finished Beer'` (using existing entity or incoming entity), with a console.warn and return.
2. **Console & mobile `ItemRepository.delete(id)`**: Before performing delete, load the item; if `doc.category === 'Finished Beer'`, throw a clear error so the UI can show it. Moved the get(id) to the top so we validate before zeroing inventory.
3. **Console & mobile `ItemForm.vue`**: Added computed `isFinishedBeerItem` (true when `form.category === 'Finished Beer'`). When editing, hide the "Delete Item" button for the Finished Beer item and show a short note that it cannot be deleted and why.

### Edge Cases Considered
- **Identification**: The TTB-required item is the one in category "Finished Beer" (single per org). Name is also "Finished Beer" at creation but we use category for consistency with how TTBFormService identifies beer items.
- **Sync**: A client could send a delete for the Finished Beer item; the server now rejects it, so the item stays in DB and will re-sync to clients. No need to "undo" on client — the delete simply doesn't apply.
- **Repository**: If someone calls `ItemRepository.delete(id)` programmatically (e.g. from another UI path), the throw ensures the delete never proceeds; UI should catch and show the error (ItemForm already catches and shows alert).
- **Form UX**: If the user changes the item's category away from "Finished Beer" in the form but has not saved, the Delete button could appear; if they then click Delete, the repository still loads the item from DB (category still "Finished Beer") and throws — so delete is still blocked. Safe.
- **Malicious/buggy client**: If a client first sends an update that changes the item's category to something else, then sends a delete, the server would accept both (item no longer has category Finished Beer). Protection is best-effort based on current category; we do not persist an `is_system` flag on the item today. Acceptable for intended use.

### Potential Gaps (to address in second pass if needed)
- Items list or other entry points: If there is another way to delete an item (e.g. bulk delete, context menu), those paths must also use `ItemRepository.delete()` and will thus get the throw; confirm no alternate delete code paths.
- Consistency: Category delete is guarded by name === 'Finished Beer' || is_system; item delete is guarded by category === 'Finished Beer'. Document in analysis.md.

## Second Iteration (after first pass implementation)

### Additional checks
- **Other delete paths**: Grep for `ItemRepository.delete` / `.delete(` on item — only ItemForm.vue (console and mobile) call it for items; no bulk or other entry points found. Safe.
- **Server existing entity**: In processChange we have `existingRow` and for items we parse `existingEntity` from row.data; the guard uses `(existingEntity && existingEntity.category) || entity.category` so we correctly use server state when available.
- **Documentation**: analysis.md updated to state that the Finished Beer item cannot be deleted (server rejects in sync; clients throw in repository; console and mobile ItemForm hide Delete and show note). BUGS-AND-FIXES-LOG updated with this fix.

### No further code changes required after second iteration.
