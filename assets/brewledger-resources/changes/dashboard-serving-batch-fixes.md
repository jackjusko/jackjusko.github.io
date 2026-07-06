# Dashboard, Serving, and Batch Detail Fixes — Feature Analysis

**Date**: 2026-02-16  
**Scope**: Desktop console — Dashboard recent activity styling, Serving page success feedback + Set empty, Batch detail not-found handling.

---

## Summary of Changes

1. **Dashboard — Recent activity**
   - Recent activity (ledger preview) now uses the same visual language as the Ledger page: type badges (RECEIVE/ADJUST→green, CONSUME/NEG→orange, TRANSFER→blue, default neutral) and quantity styling (green for positive, red for negative with +/- prefix).
   - Added `getTypeClass(type)` helper aligned with `Ledger.vue`; entry row shows badge + item name, location/date meta unchanged.

2. **Serving page**
   - **Success feedback**: Set volume and Record removal now show success via the global modal (`inject('modal').alert`) instead of no feedback; errors still use the same modal with variant `danger`.
   - **Set empty**: New action for tanks that have a batch assigned. Button "Set empty" opens a confirm modal; on confirm: (1) if on-hand > 0, post CONSUME to reconcile Finished Beer at the tank location to 0; (2) soft-delete the `batch_location` so the vessel is free; (3) refresh tanks list and trigger sync; (4) show success alert. Tank card shows "Set empty" only when `tank.batchLocationId` is set.

3. **Batch detail**
   - When `BatchRepository.getById(id)` returns null (e.g. batch deleted or invalid ID), set `batchNotFound = true` and return so the template shows "Batch not found" instead of a blank state.
   - Reset `batchNotFound` at start of `loadData` when id is valid. Added `watch(route.params.id)` to reload when navigating between batch IDs (and reset loading/batch/batchNotFound) so changing the URL or clicking another batch from the list works correctly.

---

## First-Pass Analysis (Risks & Edge Cases)

- **Dashboard**
  - **Entry type**: If `entry.type` is missing or an unknown type, `getTypeClass` returns neutral; display uses `entry.type?.replace('_', ' ') || '—'` so no crash.
  - **Quantity**: Zero quantity gets red styling (negative branch); acceptable for consistency with Ledger. No change to data loading or range.

- **Serving**
  - **Modal inject**: If `modal` is null (e.g. outside app chrome), `showAlert` falls back to `alert()`. App.vue provides modal for all non-landing, non-blog routes so Serving always has it.
  - **Set empty with zero on-hand**: If tank already has 0 on-hand, we skip the CONSUME and only delete `batch_location`; tank still clears and becomes available.
  - **Set empty failure**: If CONSUME succeeds but `BatchLocationRepository.delete` fails, ledger is already at 0 but batch_location remains; user can retry Set empty to retry delete only (CONSUME delta 0). Consider: same as other flows that don’t roll back ledger on partial failure; acceptable.
  - **Sync**: Delete of batch_location is pending until sync; other devices will free the vessel when they apply the update (batch_location tombstones sync per analysis).

- **Batch detail**
  - **Route watch**: On first mount, `loadData` runs from `onMounted`; the watch also runs when `route.params.id` is set. That can cause double load for the same id. Vue’s watch does not run before mount, so we get: mount → loadData (onMounted); then when id is already there, watch might fire. To avoid double load we could skip the first watch run or guard loadData with a “current loading id” check. **Mitigation**: Accept one possible extra load on mount, or add a guard so we don’t call loadData if `route.params.id === batch.value?.id` and batch is already loaded. Optional refinement.
  - **Stale batch after not-found**: If user navigates from not-found (e.g. /batches/bad-id) to a valid id, we set `batch = null` in the watch and then loadData; so we don’t show stale batch. Good.

---

## Second-Pass Analysis (Integration & Polish)

- **Dashboard**
  - Confirmed: no dependency on Ledger.vue; duplicate helper is intentional so Dashboard doesn’t pull in Ledger’s repository/context. Badge/quantity styles use Tailwind classes already used in Ledger and in global `style.css` (e.g. `.badge`).

- **Serving**
  - **Set empty and “Mark Production Complete”**: Production complete clears the *source* batch_location when beer is sent to a serving tank. Set empty clears the batch_location for the *serving tank* and zeros ledger. No conflict; both paths use `BatchLocationRepository.delete` and sync.
  - **Vessel exclusivity**: After Set empty, the vessel has no batch_location; it can be assigned again only via Production complete (serving tanks cannot be assigned in Split/Transfer). Correct.

- **Batch detail**
  - **Double load**: On initial navigation to `/batches/:id`, only `onMounted` runs loadData. The watch runs when `route.params.id` *changes*, so when going from list to batch A we get one load. When going from batch A to batch B we get watch firing, state reset, and one load. So we only get a double load if the component is reused and the watch fires with the same id as current—e.g. going from batch A to list to batch A again. In that case we’d reset batch to null and call loadData again, which is correct (we want fresh data). No need to add a “skip first run” or same-id guard unless profiling shows cost.
  - **Loading state**: When watch fires we set `loading = true` and `batch = null`, so the user sees the loading spinner when switching batches. Good.

---

## Files Touched

- `platforms/console/src/views/Dashboard.vue` — recent activity template + `getTypeClass`, quantity styling.
- `platforms/console/src/views/Serving.vue` — modal inject, success alerts, Set empty button/modal/save flow.
- `platforms/console/src/views/BatchDetail.vue` — set `batchNotFound` when batch missing; watch `route.params.id` to reload on id change.
- `analysis.md` — three new bullets under Desktop UI Design System for these fixes and reference to this doc.

---

## Verification Checklist

- [ ] Dashboard: Recent activity shows type badges (green/orange/blue/neutral) and +/- quantities in green/red; range and empty/loading unchanged.
- [ ] Serving: Set volume → success modal; Record removal → success modal; Set empty (tank with batch) → confirm → ledger 0, tank cleared, success modal; errors show in modal.
- [ ] Batch detail: Open invalid or deleted batch ID → “Batch not found” card; navigate to valid batch → data loads; switch between two batches → each loads correctly.
