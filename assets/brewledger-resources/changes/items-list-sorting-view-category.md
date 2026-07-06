# Items List — Sorting, List/Grid View, and Category Color Coding

## Summary of implementation

Console Items view (`platforms/console/src/views/ItemsList.vue`) was updated to reduce repetition and improve scanability:

1. **Toolbar**: Replaced standalone search with a `console-toolbar` containing title "Items", item count, search field, sort dropdown, and list/grid view toggle.
2. **Sort options**: Sort by Name A–Z, Name Z–A, On hand (high/low), Value (high/low), Category. Applied to both Ingredients and Finished Beer; each section uses the same sort.
3. **View modes**:
   - **List (compressed)**: Single data table with columns Name, Category, Unit, On hand, Est. value, and Edit. Ingredients then Finished Beer rows. Category and icon color-coded.
   - **Grid (expanded)**: Existing card layout by section (Ingredients, Finished Beer) with category-colored left border and icon/pill styling.
4. **Category color coding**: Aligned with `Inventory.vue`:
   - Pills: `getCategoryClass(category)` for Finished Beer (amber), Hops (purple), Grains (amber), Yeast (blue), Chemicals (red), Packaging (green), Clarifiers (indigo), Other/uncategorized (neutral).
   - Card left border and icon background: same palette via `getCategoryIconClass` and `.item-card-category-*` / `.item-icon-*` classes (light and dark).
5. **Default view**: List view is default to reduce repetition; grid remains available for card-style browsing.

---

## First iteration — potential issues and edge cases

### 1. Sort key and reactivity
- **Implementation**: `sortItems(list)` is a function used inside computed `sortedIngredientItems` and `sortedBeerItems`; it reads `sortBy.value` and calls `getOnhand(item.id)`. `onhandMap` is reactive, so recompute happens when sort or on-hand data changes. **Risk**: None; dependency chain is correct.

### 2. Category slug for unknown categories
- **Implementation**: `categorySlug(category)` does `(category || 'other').toLowerCase().replace(/\s+/g, '-')`. Custom category names (e.g. "My Category") become "my-category"; we have no CSS for that, so card gets default left border (neutral). **Mitigation**: Acceptable; only known categories get custom border; unknown get neutral.

### 3. List view: Ingredients vs Beer order
- **Implementation**: Table renders Ingredients rows first, then Beer rows. Sort is applied per section, not globally. So "Sort by Category" groups within Ingredients and within Beer, but Ingredients always appear before Beer. **Risk**: User might expect a single sorted list. **Mitigation**: Kept section split for consistency with grid and with existing mental model (Ingredients / Finished Beer). Optional future: add "Single list" view that merges and sorts all.

### 4. Accessibility
- **Implementation**: Sort select has `aria-label="Sort by"`; view toggle has `role="group"` and `aria-label="View mode"`, buttons have `:aria-pressed`. Table has proper th/td. **Risk**: None identified.

### 5. Mobile / narrow layout
- **Implementation**: Toolbar uses `flex-wrap`; list table has `overflow-x-auto`. On very narrow screens the toolbar may stack. **Risk**: Low; console is desktop-first.

### 6. Empty state
- **Implementation**: Empty state ("No items found") is shown when `filteredItems.length === 0` regardless of view mode. Grid view when empty still shows the grid template (with zero cards) and then the empty card. **Risk**: Slight redundancy in DOM; no visual bug.

---

## Second iteration — expanded review

### 7. Persistence of view mode and sort
- **Gap**: `viewMode` and `sortBy` are not persisted (e.g. localStorage). User loses preference on refresh. **Action**: Document as future enhancement; not required for initial release.

### 8. Category list consistency
- **Check**: `getCategoryClass` and `getCategoryIconClass` include Finished Beer, Hops, Grains, Yeast, Chemicals, Packaging, Clarifiers, Other. Inventory.vue uses same pill map (without Finished Beer in its map; it uses a separate badge). Items list now includes Finished Beer in both so beer items get amber pill and icon. **Consistency**: Aligned.

### 9. List view Edit button
- **Implementation**: Edit is a `router-link` with classes `btn btn-secondary btn-sm py-1.5 px-2 text-xs`. Global `.btn-sm` may not be defined; Tailwind size classes still make the button compact. **Action**: No change; if design system adds `.btn-sm` later, it will apply.

### 10. Performance
- **Check**: Sorting runs on filtered arrays (already computed); no extra API calls. List view renders one table with two v-for blocks (ingredients, then beer). Acceptable for typical item counts.

---

## Integration checklist

- [x] Toolbar with search, sort, view toggle
- [x] Sorted computed lists for Ingredients and Finished Beer
- [x] List view: single table, category pills and icon color
- [x] Grid view: cards with category left border and icon/pill color
- [x] getCategoryClass / getCategoryIconClass / categorySlug
- [x] Scoped styles for list table, icon sizes, category borders and icon backgrounds (light/dark)
- [x] Default view list; empty state unchanged

---

## Documentation

- **analysis.md**: Extended "Items list card refresh" bullet to include sorting, list/grid view, and category color coding (see below).
