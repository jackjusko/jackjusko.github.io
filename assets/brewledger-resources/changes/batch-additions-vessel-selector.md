# Batch additions: vessel selector

## Change summary
The "Add Ingredient" modal now allows selecting a specific vessel or "All vessels" when logging an ingredient addition to a batch.

## Implementation

### Schema
- **batch_additions**: Added optional `batch_location_id` field. When null, the addition applies to all vessels (batch-level). When set, the addition is specific to that vessel (batch_location).
- No Dexie schema change needed (field stored in entity data; no index required yet).
- Server: `batch_location_id` stored in `data` JSON; no validation change (field is optional).

### UI (BatchDetail.vue)
- **Add Ingredient modal**: 
  - **Category dropdown**: Now defaults to "Any" (shows all items in organization). User can filter by specific category if desired.
  - **Item dropdown**: Shows all items when "Any" is selected; filters by category otherwise. When item is selected, triggers `updateLocationAvailability()`.
  - **From Location dropdown**: Shows availability amounts for each location in the dropdown text (e.g. "Cooler (15 available)"). Availability is fetched for all locations when an item is selected.
  - **Add To dropdown**: "All vessels" (batch_location_id=null) or specific vessel (batch_location_id set).
  - Help text: "Choose a specific vessel or apply to all vessels".
- **openAdditionModal**: Initializes `forms.addition.event_type = 'Any'`, `batch_location_id = null`, and clears `locationAvailability` map.
- **updateLocationAvailability**: When item is selected, fetches on-hand quantity for that item at all locations and populates `locationAvailability` Map.
- **getLocationLabel**: Returns location name with availability (e.g. "Cooler (15 available)") when item is selected and availability is known.
- **filteredItems**: Returns all items when event_type is "Any"; otherwise filters by category.
- **History tab**: Additions now show vessel in subtitle: `${quantity} · ${event_type} · ${vesselName}` or `· All vessels`.
- **Helper**: `getVesselNameForBatchLocation(batchLocationId)` added to look up vessel name from batch_location_id.

### Edge cases
- Additions with no batch_location_id (legacy or "all vessels"): displayed as "· All vessels" in history.
- Additions with batch_location_id: displayed with vessel name (e.g. "· FV-1").
- If batch_location_id references a deleted batch_location (edge case from combine/split), vessel name will be null and display as "· All vessels" (graceful degradation).

## Use cases
- **Dry hopping one vessel**: User selects specific fermenter when adding hops.
- **Batch-level additions**: User selects "All vessels" for ingredients added before split (e.g. during brew day).
- **Tracking per-vessel ingredients**: Enables future analytics on ingredient usage per vessel/split.

## Documentation
- **analysis.md**: "Vessel Split / Batch Locations" section updated to describe additions per vessel.
