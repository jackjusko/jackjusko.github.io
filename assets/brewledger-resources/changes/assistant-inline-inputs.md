# Feature analysis: AI Assistant inline inputs

## Summary
The assistant was prompting for details (e.g. “Provide an item name and category”) without showing input fields, so users had no way to provide that information before “Approve & run”. This change adds per-card form state and inline inputs for all “need_*” states that require user-entered text or numbers.

## Implemented

1. **Form state and merge in `runAction`**
   - Before executing, `runAction` reads `actionStatuses[idx].form` (when present) and merges into `actionToRun.params`: `form.name` → `params.name`, `form.category` → `params.category`, `form.quantity` → `params.quantity`, `form.volume` → `params.plannedVolume`, `form.packagedVolume` → `params.packagedVolume`. Empty/blank form values are skipped; numbers are coerced with `Number()`.

2. **Storing action and form for input-required states**
   - When the executor returns `need_item_name`, `need_location_name`, `need_quantity`, `need_volume`, or `need_packaging_volume`, the UI now stores the action in `pendingFollowups[idx]` and sets `actionStatuses[idx]` with a `form` object so the card can show inputs and merge on next “Approve & run”.
   - `need_item_name`: `form = { name: '', category: 'Other' }`, plus `items` for “pick existing” buttons.
   - `need_location_name`: `form = { name: '' }`.
   - `need_quantity` / `need_volume`: `form = { quantity: '', volume: '' }` (only the relevant one is used per state).
   - `need_packaging_volume`: `form = { packagedVolume: '' }`.

3. **Template**
   - Replaced the text-only messages for these five states with:
     - **need_quantity**: number input bound to `actionStatuses[index].form.quantity`.
     - **need_volume**: number input for planned volume.
     - **need_packaging_volume**: number input for packaged volume.
     - **need_item_name**: “Pick existing item” buttons (when `items` exist) plus text input for new item name and category dropdown (Other, Beer, Wine, Spirit, Ingredient, Package).
     - **need_location_name**: text input for location name.
   - Inputs are only rendered when `actionStatuses[index]?.form` exists to avoid errors before form init.

## Edge cases and follow-ups

- **First run with no params**: For “create an item” with no name, the executor returns `need_item_name`; we now store the action and form so the card shows the name/category inputs and “Approve & run” merges them on submit. Verified flow.
- **Re-submit with empty name**: If the user clicks “Approve & run” without entering a name, we still call the executor; it returns `need_item_name` again and we re-store the same structure. No infinite loop; user can then fill the form. Optional improvement: client-side validation to disable “Approve & run” or show a hint when required field is empty.
- **Vue reactivity**: We mutate `actionStatuses[index].form.name` etc. via v-model. Because we set `actionStatuses.value[idx]` with a new object that includes `form`, Vue tracks the nested properties. No separate `actionFormInputs` ref was needed.
- **create_item vs create_location both use `form.name`**: Merge uses a single `form.name` for both; the label in the template differs (“New item name” vs “Location name”). No conflict.
- **Number inputs**: We use `v-model` (no `.number`) so the value stays string; we convert with `Number()` in the merge. Empty string yields `Number('') === 0`; for quantity/volume we might want to treat empty as “still missing” and let the executor return need_* again. Current behavior: we only merge when `form.quantity !== ''` etc., so we don’t overwrite with 0. Good.
- **Stage for create_location**: Not yet exposed in the UI (executor accepts `stage`). Could add a stage dropdown to the need_location_name card in a follow-up.

## Second pass

- **Legacy cards without form**: Messages created before this change (or if form failed to init) can have `state === 'need_item_name'` etc. but no `form`. The template now includes a fallback: when state is one of `need_quantity`, `need_volume`, `need_packaging_volume`, `need_item_name`, `need_location_name` and `form` is missing, we show `actionStatuses[index].message` or a generic “Provide the requested value, then approve & run.” so the user still sees guidance instead of an empty card.

## Integration

- **Executor**: No changes; it already returns `need_item_name`, `need_location_name`, `need_quantity`, `need_volume`, `need_packaging_volume` with messages. UI now consumes these and shows inputs.
- **analysis.md**: Updated with a bullet under AI Assistant describing inline inputs and the supported need_* states.
