# Par Levels Item Search – Feature Analysis

## Summary
Added an item search feature to the Par Levels page (`platforms/console/src/views/ParLevels.vue`) so users can quickly filter items by name or category when setting par levels for a scope (Global or per-location).

## Implementation

### Changes
1. **Search input**: Added a search field in the card header, visible when a scope is selected. Uses the same styling as Inventory (search icon, `input` class, placeholder "Search items..."). `aria-label="Search items by name or category"` for accessibility.
2. **Filtered items**: `filteredItems` computed property filters `items` by `searchQuery`—matches item name or category (case-insensitive, substring).
3. **Empty state**: When search returns no matches, shows "No items match your search" with a search icon instead of the generic "No items found".
4. **Result count**: When search is active, shows "Showing X of Y items" above the list.
5. **Scope change**: Search query is cleared when scope changes so the user starts fresh per scope.

### Files Modified
- `platforms/console/src/views/ParLevels.vue`

## First Iteration – Potential Issues

### 1. Save behavior with filtered view
- **Observation**: `saveParLevels` iterates over `tempPars.value`, which holds par values for all items (including those not visible when filtered). Saving while filtered does not lose data—all edited values are persisted.
- **Conclusion**: No change needed. Filtering only affects display; `tempPars` is keyed by item ID and persists edits for all items.

### 2. Item unit or vendor search
- **Observation**: Search currently matches only name and category. ItemsList and Inventory may search additional fields (e.g., vendor, unit).
- **Conclusion**: Name and category cover the main use case. Unit/vendor can be added later if requested.

### 3. Mobile parity
- **Observation**: Par Levels search is console-only. Mobile ReorderList does not have search.
- **Conclusion**: Out of scope for this change. Mobile can be enhanced separately.

### 4. Accessibility
- **Observation**: Search input has no explicit label; placeholder provides context. Icon is decorative (`aria-hidden="true"`).
- **Conclusion**: Added `aria-label="Search items by name or category"` for screen readers.

### 5. Performance
- **Observation**: `filteredItems` is a computed that runs on every keystroke. With hundreds of items, `Array.filter` is cheap.
- **Conclusion**: No performance concern for typical brewery item counts.

## Second Iteration – Follow-up

### 1. Debounce
- **Observation**: No debounce on search. Each keystroke recomputes immediately.
- **Conclusion**: Not needed for client-side filter over a small list; instant feedback is preferable.

### 2. Result count
- **Observation**: No indication of how many items match (e.g., "Showing 12 of 45 items").
- **Conclusion**: Added "Showing X of Y items" when search is active to improve clarity.

### 3. Clear button
- **Observation**: No explicit clear (X) button in the search field.
- **Conclusion**: User can clear by selecting all and deleting. Optional enhancement.

## Documentation
- `analysis.md` updated to document the Par Levels item search feature.
