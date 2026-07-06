# Fix: Stale Stock Data, Validation Issues, and Double-Consumption in Batch Recipe Consume Page

## Problem

The "Consume Ingredients" page (`BatchRecipeConsume.vue`) had multiple issues:

### Issue 1: Stale Stock Data
The `onhandCache` was fetched only once during `onMounted`. When users navigated away to add ingredients and returned, the component showed old stock data.

### Issue 2: Undefined Selection Access
The `getStatus()` function accessed `selections[index].location_id` without checking if `selections[index]` existed, causing validation to fail silently if selections weren't fully initialized.

### Issue 3: Template Errors
The template accessed `selections[index].location_id` in v-if directives without optional chaining, which could cause runtime errors.

### Issue 4: Double-Consumption Risk (CRITICAL)
When users manually "Add Ingredient" via BatchDetail, it creates a CONSUME ledger entry. When they later "resume consumption" from the recipe, the consume page would create **additional** CONSUME entries for the same items, effectively double-consuming ingredients.

**The flow that caused double-consumption:**
1. Start batch with recipe
2. Go to consume page (insufficient stock)
3. Navigate back, click "Add Ingredient" manually (creates CONSUME entry)
4. Click "resume consumption" 
5. Recipe consume creates **another** CONSUME entry for the same ingredient

### Issue 5: Race Condition on Submit (CRITICAL)
The submit button could be clicked multiple times before the async operations completed, causing:
- Multiple sets of CONSUME entries created
- Inventory over-consumption
- Duplicate batch cost calculations
- Data corruption

**The race condition:**
1. User clicks "Consume & Start Brew"
2. First click starts async `LedgerRepository.addEntry()` calls
3. Before first click finishes, user clicks again
4. Second click also creates CONSUME entries (no guard in place)
5. Result: Double (or triple) consumption

## Solution

### 1-3: Stale Data & Validation Fixes
Added automatic and manual stock refresh capabilities, defensive validation, and optional chaining.

### 4: Double-Consumption Prevention
**New Logic:**
1. Fetch existing ledger entries for the batch on page load
2. Filter for CONSUME entries (that aren't reversed)
3. Check each recipe item against existing CONSUME entries
4. Mark items as `alreadyConsumed` if sufficient quantity already consumed
5. Skip already-consumed items during submit
6. Show "Already Added" status in UI

**Implementation:**
```javascript
// Track existing CONSUME entries
existingConsumes.value = ledgerEntries.filter(e => e.type === 'CONSUME' && !e.reversed)

// Check each item
items.value.forEach((item, index) => {
  const alreadyConsumed = existingConsumes.value.filter(e => e.item_id === item.item_id)
  const consumedQty = alreadyConsumed.reduce((sum, e) => sum + Math.abs(e.quantity), 0)
  
  if (consumedQty >= requiredQty) {
    selections[index].alreadyConsumed = true
    selections[index].consumedQty = consumedQty
  }
})

// Skip during submit
const submit = async () => {
  for (let i = 0; i < items.value.length; i++) {
    if (selections[i]?.alreadyConsumed) continue  // Skip already consumed
    // ... create CONSUME entry
  }
}
```

### 5: Submission Race Condition Fix
Added a `submitting` flag to prevent concurrent submissions:

**Implementation:**
```javascript
const submitting = ref(false)

const submit = async () => {
  if (!allValid.value || submitting.value) return  // Guard against concurrent submissions
  submitting.value = true  // Lock
  
  try {
    // ... process consumption
  } finally {
    submitting.value = false  // Unlock
  }
}
```

**Button changes:**
- Disable button when `submitting` is true
- Show "Processing..." text during submission
- Button is disabled during the entire async operation (ledger entries + cost calc + sync)

## Files Modified

- `platforms/console/src/views/BatchRecipeConsume.vue`
- `platforms/brewledger-app/src/views/BatchRecipeConsume.vue`

## Key Features

1. **Automatic Stock Refresh**: When navigating back to the consume page, stock is automatically refreshed
2. **Manual Refresh**: Users can click "Refresh Stock" button to update on-demand
3. **Double-Consumption Guard**: Already-consumed items are automatically skipped
4. **Submission Lock**: Button is disabled during submission to prevent race conditions
5. **UI Feedback**: Loading state shows "Processing..." during submission
6. **Selection Validation**: After refresh, invalid selections are cleared
7. **Selection Preservation**: Previously selected locations are preserved if still valid

## Testing

1. Start a batch with recipe consumption
2. Go to consume page (button may be disabled due to insufficient stock)
3. Navigate to Receive page and add stock for required ingredients
4. Return to consume page - stock should automatically refresh
5. Select locations for all required ingredients
6. Click "Consume & Start Brew" - button should show "Processing..." and be disabled
7. Rapid clicking should not create duplicate entries
8. Items already added via "Add Ingredient" should show "Already Added" and be skipped

## UI Changes

### Already Consumed Items
- Show "✓ Already Added" badge instead of "✓ Ready"
- Message: "This ingredient was already added to the batch. Quantity consumed: X unit"
- Location selector is hidden
- Automatically considered valid for submit button

### Submit Button States
- Normal: "Consume & Start Brew" (enabled when allValid)
- Submitting: "Processing..." (disabled during submission)
- Disabled: standard disabled styling when invalid or submitting
