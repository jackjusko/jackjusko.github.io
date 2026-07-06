# Beers Management Console Page

**Summary:** New desktop console page for managing the brewery’s finished beer products (items in the Finished Beer category), separate from general Inventory/Items. Any recipe automatically gets a corresponding finished beer item via “Sync from recipes.”

## Implemented

### 1. Beers view (`/beers`)
- **Route:** `/beers` (auth required).
- **Nav:** Sidebar “Beers” (🍻) between Inventory and Items.
- **List:** All items where `category === 'Finished Beer'` (same as `ItemRepository.getBeerItems()`).
- **Columns:** Name, Unit, Linked recipe (recipe name if `recipe_id` set), Actions (Edit, Delete when allowed).
- **Add Beer:** Link to `/items/add?category=Finished%20Beer`; ItemForm presets category from `route.query.category`; after creating a beer, redirect to `/beers`.
- **Sync from recipes:** Button runs `ensureBeersFromRecipes()`: for each recipe, if no beer item exists with that `recipe_id` or same name, creates an item with `name = recipe.name`, `category = 'Finished Beer'`, `unit = 'bbl'`, `recipe_id = recipe.id`. Handles recipes created on mobile or via sync.

### 2. Recipe → beer item link
- **Item `recipe_id`:** Items may carry optional `recipe_id` (stored in client and in server `items.data` JSON). Used to show “Linked recipe” on Beers page and to avoid creating duplicate beer items when syncing from recipes (match by `recipe_id` or by name).
- **Ensure logic:** On “Sync from recipes,” for each recipe we require a beer item either with `item.recipe_id === recipe.id` or `item.name === recipe.name` (case-insensitive). If none, we create one and set `recipe_id`.

### 3. Delete guard relaxation
- **Before:** Any item with `category === 'Finished Beer'` could not be deleted (client and server).
- **After:** Only the **default** Finished Beer item cannot be deleted: `name === 'Finished Beer'` and `category === 'Finished Beer'` (the one created by TTB migration / org registration). All other beer items (custom beers, recipe-linked beers) can be deleted.
- **Client:** `ItemRepository.delete()` throws only when `doc.name === 'Finished Beer' && doc.category === 'Finished Beer'`. `ItemForm` shows “Cannot delete” and hides Delete only for that default item (`isDefaultFinishedBeerItem`).
- **Server:** Sync rejects item soft-delete only when `category === 'Finished Beer'` and `name === 'Finished Beer'`.

### 4. ItemForm and navigation
- **Category preset:** Add Item with `?category=Finished Beer` presets the category (for “Add Beer” from Beers page).
- **Redirect after create:** If the created item has `category === 'Finished Beer'`, redirect to `/beers`; otherwise `/items`.

## Files touched

- **New:** `platforms/console/src/views/Beers.vue`
- **Modified (console):** `platforms/console/src/router/index.js` (route `/beers`, import Beers), `platforms/console/src/App.vue` (nav Beers, description), `platforms/console/src/views/ItemForm.vue` (query category preset, redirect to /beers when creating beer, delete only for default Finished Beer item), `platforms/console/src/repositories/ItemRepository.js` (delete guard: only default Finished Beer).
- **Modified (server):** `server/server.js` (sync reject delete only for default Finished Beer item).
- **Modified (mobile, consistency):** `platforms/brewledger-app/src/repositories/ItemRepository.js` (delete guard: only default Finished Beer), `platforms/brewledger-app/src/views/ItemForm.vue` (hide Delete only for default Finished Beer item via `isDefaultFinishedBeerItem`).

## Three-pass review fixes

1. **Sync logic (Pass 1 – bugs):** Only skip creating a beer when a beer already exists for that recipe (`byRecipeId.has(recipe.id)`). Removed skip-by-name so every recipe gets exactly one beer even if two recipes share the same name. Skip recipes with no name or whitespace-only name; use trimmed name when creating.
2. **ItemForm from=beers (Pass 2 – UX):** Edit link from Beers page now includes `?from=beers`. ItemForm breadcrumb shows "← Beers" and links to `/beers` when `from=beers`. After save (create or edit) or delete, redirect to `/beers` when coming from Beers so the user stays in the Beers flow.
3. **Sync feedback (Pass 3 – user perspective):** Added `syncMessage` ref: success ("Created N beer(s) from recipes."), info when no recipes ("No recipes found. Create recipes in the mobile app or add a beer manually."), or error. Message clears when the Beers page is mounted again (e.g. after navigating away and back). Removed unused `recipeMap` computed.

## Design notes

- Beers page is a **manager of items under the Finished Beer category**, not a new entity type. TTB and production complete continue to use beer items (category “Finished Beer”) as before.
- Recipe system lives on mobile; console has recipes in DB (sync) and uses them in BatchForm. “Sync from recipes” keeps beer items in sync with existing recipes so every recipe has a corresponding finished beer product.
- The default “Finished Beer” item remains for TTB and for orgs that do not use multiple beer products; multi-beer breweries use the Beers page to create and manage additional beers.
