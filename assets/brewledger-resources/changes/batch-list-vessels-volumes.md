# Batch list: vessels and volumes

## Change summary
The batch list screen (BatchesList.vue) now shows, for each batch, which vessels the batch is in and the current volume in each vessel.

## Implementation

### Data
- **BatchLocationRepository**: Added `getByBatchIds(batchIds)` to fetch all `batch_locations` for a set of batch IDs in one query (Dexie `where('parent_batch_id').anyOf(batchIds)`).
- **BatchesList.vue**:
  - Loads batches, then in parallel: vessels and batch_locations for those batch IDs.
  - Builds `vesselSummaries` per batch: `{ vesselName, current_volume }[]` from batch_locations + vessel name lookup.
  - Renders a second line under date/total volume: vessel name and volume per location, e.g. `FV-1 (50 L) · BBT-2 (25 L)`, using `batch.planned_volume_unit` (fallback `L`).

### UI (horizontal tree)
- **Volume tree**: Total volume shown as a root pill (gray background); when batch has vessel splits, a right-chevron connector then each vessel as a leaf pill (purple-tinted border/background) with vessel name and volume. Layout: `[Total 75 L] → [FV-1  50 L] [BBT-2  25 L]`.
- Vessel/volume row only shown when batch has total volume and/or vessel summaries.
- If only vessel summaries exist (no total), vessel pills are shown without a root node.

### Edge cases
- Batches with no batch_locations: no vessel line (unchanged from previous behavior; total volume still shown when available).
- Unknown vessel_id: displayed as "Unknown" with volume.
- Volume unit: uses batch’s `planned_volume_unit` or `"L"`.

## Documentation
- **analysis.md**: BatchesList subsection under "Vessel Split / Batch Locations" updated to describe vessel/volume list display and `getByBatchIds`.

## Related changes
- **batch-additions-vessel-selector.md**: Additions now support vessel selection (batch_location_id).
