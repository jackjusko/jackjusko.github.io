# Recipes functionality ported from mobile to console

**Summary:** Recipe list and recipe form (create/edit) are now available on the desktop console app, matching the mobile app’s recipe functionality. Recipes sync between platforms via existing SyncService and RecipeRepository/RecipeItemRepository.

## Implemented

### 1. RecipeList.vue (`/recipes`)
- List all recipes with name, description, base volume (and unit), ingredient count.
- Search filter by name or description.
- Actions: Edit (link to `/recipes/:id/edit`), Delete (confirmation modal, then RecipeRepository.delete + SyncService.sync).
- Empty state with link to “Create first recipe”.
- Uses `useSync()` so list refreshes after sync.

### 2. RecipeForm.vue (`/recipes/add`, `/recipes/:id/edit`)
- **Basic info:** Name (required), base volume (number), base volume unit (text, e.g. bbl), description (textarea).
- **Ingredients:** Table of item, quantity, unit; “+ Add ingredient” opens a modal to pick item (from ItemRepository.getAll()), quantity, and unit (defaults from selected item).
- Save: RecipeRepository.create or update with recipe fields and items array; SyncService.sync; redirect to `/recipes`.
- Optional confirm when saving with no ingredients.
- Styling aligned with console (desktop-container, card, data-table, btn, input).

### 3. Routes and nav
- **Routes:** `/recipes` (RecipeList), `/recipes/add` (RecipeForm), `/recipes/:id/edit` (RecipeForm).
- **Nav:** Under “Production”: Recipes (ri-book-2-line), Batches.
- **Page descriptions and titles:** Added for /recipes, /recipes/add, and edit recipe in App.vue (currentPageDescription and pageTitles).

## Data and sync

- **RecipeRepository** and **RecipeItemRepository** already existed on console; no changes. They support name, base_volume, base_volume_unit, description (spread into recipe object; Dexie stores full object).
- Recipes and recipe_items sync with server; mobile and console share the same entities. Creating/editing a recipe on console syncs and appears on mobile (and vice versa).

## Files

- **New:** `platforms/console/src/views/RecipeList.vue`, `platforms/console/src/views/RecipeForm.vue`
- **Modified:** `platforms/console/src/router/index.js` (imports + routes), `platforms/console/src/App.vue` (Production nav + descriptions/titles)

## Relation to Beers

- Beers page “Sync from recipes” creates one Finished Beer item per recipe (by recipe_id/name). With Recipes on console, users can create recipes on desktop and then sync to Beers so each recipe has a corresponding beer product.
