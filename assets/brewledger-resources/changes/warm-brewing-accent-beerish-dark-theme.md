# Warm Brewing Accent + Beerish Dark Theme – Feature Analysis (Iteration 1)

## Goals

- Replace the desktop console primary palette (blue) with amber to align with the landing page warm brewing brand.
- Rework the dark theme to use warm, beer-inspired tones (stone) instead of cool blue-grays.
- Explicitly address form controls (inputs, selects, textareas, checkboxes, radios) and placeholder/disabled states.
- Ensure all visual edge cases (modals, data tables, filter pills, sidebar) are consistent.

## Findings

- **Primary palette**: Swapped `--primary-*` and Tailwind `primary` from blue to amber in `style.css` and `tailwind.config.js`. All existing `primary-*` usage (buttons, sidebar active, filter pills, focus rings) now renders amber.
- **Hardcoded blue values**: Updated `btn-primary` hover shadow and `.input:focus` box-shadow from blue rgba to amber. Fixed Dashboard trial banner (blue → primary) and ItemsList yeast category border.
- **Dark theme**: Replaced `.dark` block to use stone hex values (`#0c0a09`, `#1c1917`, `#292524`, etc.) for backgrounds, borders, and text. Console header backdrop uses warm dark `rgba(12, 10, 9, 0.95)`.
- **Sidebar and filter pills**: Updated `.dark .console-sidebar`, `.dark .console-sidebar-link:hover`, `.dark .console-sidebar-avatar`, `.dark .console-sidebar-btn`, `.dark .filter-pill` to use semantic vars (`--bg-secondary`, `--bg-elevated`, `--border-light`) which now resolve to stone in dark mode.
- **Component-level dark classes**: Systematically replaced `dark:bg-neutral-*`, `dark:border-neutral-*`, `dark:text-neutral-*` with `dark:bg-stone-*`, `dark:border-stone-*`, `dark:text-stone-*` across console views, auth pages, and shared components.
- **Form controls**: Added `.input::placeholder`, `input::placeholder`, `textarea::placeholder` with `color: var(--text-tertiary)` in `style.css`. Inline-styled inputs/selects/textareas updated to `dark:bg-stone-800`, `dark:border-stone-600`, `dark:text-stone-100`.
- **Checkboxes/radios**: BatchDetail checkboxes given `rounded border-neutral-300 dark:border-stone-500 bg-white dark:bg-stone-800 text-primary-600` for consistent dark styling.
- **ModalDialog**: Dark panel and footer use `dark:bg-stone-800`, `dark:bg-stone-900`; Cancel button uses stone borders and hover.

## Risks / Edge Cases

- **Ledger entry type badges (Dashboard)**: Kept semantic colors (Receive=green, Consume=orange, Transfer=blue) per plan recommendation; only primary accent changed to amber.
- **Reports.vue contextual colors**: TTB=purple, Removals=amber, Racking=slate, Losses=red left as-is for report-type distinction.
- **Blog/Tools/Landing**: Out of scope; already use amber/stone.
- **Native selects/datetime inputs**: Browser-controlled dropdown/picker UI; input wrapper styling ensures consistent bg/border.

## Proposed Adjustments (Phase 1)

- Verify BreweryInfoForm uses `bg-transparent` for inputs—ensure dark mode applies `dark:bg-stone-800` where needed (inputs should have explicit dark background).
- Verify MilestoneTemplateForm inputs with `bg-transparent`—add `dark:bg-stone-800` for dark mode.
- Scan remaining views (TTBForm, Removals, Receive, Ledger, ItemForm, BatchForm, RecipeForm, Beers, etc.) for any `dark:neutral-*` and replace with stone.

---

## Iteration 2 Additions

- Complete sweep of remaining console views for `dark:neutral-*` patterns.
- Confirm placeholder visibility in dark mode with `--text-tertiary` = stone-400.
- Document final color palette and dark theme strategy in `analysis.md`.

---

## Follow-Up Fixes (Post-User Feedback)

**Issue**: User reported trial banner still blue, main layout background still deep blue, sync status area still neutral, Reports page buttons lacking padding.

**Changes applied**:

1. **Dashboard trial banner**: Switched from `primary-*` to explicit `amber-*` classes so trial banner is unambiguously warm regardless of primary variable. Upgrade button uses `bg-amber-600 text-stone-900`.
2. **App.vue root and main background**: Changed `dark:bg-neutral-950` → `dark:bg-stone-950` on root div (line 2) and main content area so all console views have warm stone background.
3. **Sync status box**: Changed `dark:bg-neutral-800` → `dark:bg-stone-800`, `dark:border-neutral-700` → `dark:border-stone-700`, `dark:text-neutral-400` → `dark:text-stone-400` for consistency.
4. **Header text**: Updated `dark:text-neutral-100` → `dark:text-stone-100`, `dark:text-neutral-400` → `dark:text-stone-400` in console header.
5. **Reports page**:
   - Added `p-6` to all four report-type cards (TTB Form, Removals, Racking, Losses) for padding around content and generating buttons.
   - Added `py-3 px-4` to the Generate/Record buttons for better spacing.
   - Rollup section: `dark:border-neutral-700` → `dark:border-stone-700`, `dark:text-neutral-300` → `dark:text-stone-300` for consistency.

---

## Blue Removal Sweep (Post-User Feedback)

**Issue**: User reported blue still visible in Settings (selected tab, org input, buttons), Dashboard (stat cards, quick actions, links), Inventory (table headings, type badges), Locations, Items (selected view mode), and various selected/active states.

**Changes applied**:

1. **Settings.vue**: Selected tab uses explicit `amber-*`; org name input and all form inputs use `dark:bg-stone-800` (was `dark:bg-neutral-700`); all primary buttons use `bg-amber-600`; `dark:border-neutral-700` → `dark:border-stone-700`, `dark:text-neutral-400` → `dark:text-stone-400`.

2. **Quick actions (Dashboard)**: Replaced `btn-secondary` with new `btn-warm` class for complementary amber styling. Added `.btn-warm` to `style.css` using primary (amber) vars.

3. **Dashboard links/stats**: All `text-primary-600`, `hover:text-primary-700`, `group-hover:text-primary-*` switched to explicit `amber-*`. Tour banner uses `amber-*`. Transfer ledger badge: `blue-*` → `slate-*`.

4. **style.css**: `.dark .console-sidebar-avatar` uses `var(--border-light)` instead of `neutral-700`. `.dark .stat-card-icon-neutral` uses `var(--border-light)` and `var(--text-tertiary)`. `.dark .meta-pill` uses `var(--bg-elevated)`. `.dark .compact-list-row:hover` uses `var(--bg-secondary)`.

5. **Inventory.vue**: Table headers (sortable-th) use `var(--text-secondary)` / `var(--text-primary)`; `dark .data-table th` uses `var(--text-secondary)` and `var(--bg-secondary)`. Type badge (e.g. Yeast): `blue-*` → `slate-*`. Category/status fallbacks: `dark:bg-neutral-800` → `dark:bg-stone-800`. Row hover/expand: `dark:bg-neutral-800` → `dark:bg-stone-800`.

6. **LocationsList.vue**: `dark:bg-neutral-800` → `dark:bg-stone-800`, `dark:border-neutral-700` → `dark:border-stone-700`, Edit link `primary-*` → `amber-*`, stage badge uses `stone-*`.

7. **ItemsList.vue**: View mode toggle (list/grid) selected state: `primary-*` → `amber-*`. Yeast category: `blue-*` → `slate-*`.

8. **Explicit blue → slate** (semantic badges): Dashboard/Ledger TRANSFER badge; BatchDetail/BatchesList FG Confirmed, Cold Crash, Transferred, Serving, Packaging Started; Inventory/ItemsList Yeast category; Inventory type_class badge.

9. **AIAssistant.vue**: Info/neutral action status icon `text-blue-600` → `text-amber-600`.

---

## Iteration 3 – Contrast, Stony Actions, Final Blue Removal (Post-User Feedback)

**Issue**: Quick action buttons looked awful (double-tone orange, poor contrast); Take the tour button needed fixing; Open TTB form looked weird; Record Racking/Losses icons and buttons still blue; Inventory column headers and "showing inventory items"; Receive page; TTB form margins; Billing Get started; Create user flow; Items list/grid selector; ItemsList Yeast icons (blue).

**Changes applied**:

1. **Quick actions (Dashboard)**: Replaced `btn-warm` with stony inline style matching sync button: `bg-neutral-100 dark:bg-stone-800 border border-neutral-200 dark:border-stone-700 text-neutral-800 dark:text-stone-200` for strong contrast (dark text on light bg).

2. **Take the tour**: Changed from `btn-secondary` to `btn-primary` so it stands out (amber/white).

3. **Open TTB form (Dashboard)**: Explicit `bg-amber-600 hover:bg-amber-500 text-white` for clear primary action styling.

4. **Reports page**:
   - TTB Form card: Added `p-6`; Generate button uses explicit purple (no btn-primary base).
   - Record Racking: Icon `bg-slate-*` → `bg-stone-200 dark:bg-stone-700/50 text-stone-700`; Button `bg-slate-600` → `bg-stone-600` (removes blue-ish slate).
   - Record Losses: Button uses explicit `bg-red-600` (no btn-primary override).
   - Record Removals: Explicit `bg-amber-600`.
   - Refresh (Serving & Inventory rollup): Explicit `bg-amber-600`.

5. **TTBForm.vue**: Inputs `dark:bg-neutral-700` → `dark:bg-stone-800`; Generate button `bg-amber-600`; Icon `text-amber-600`; `dark:text-neutral-100` → `dark:text-stone-100`; Form preview card `dark:bg-stone-800`; `card-body space-y-6` for margins.

6. **Receive.vue**: Breadcrumb hover `amber-*`; Summary box `primary-*` → `amber-*`; `dark:bg-neutral-900` → `dark:bg-stone-900`.

7. **Inventory.vue**: "Inventory Items" header and all `dark:text-neutral-100` → `dark:text-stone-100`; Table headers use `var(--text-secondary)` and `var(--bg-secondary)`; Row/expand states `dark:bg-stone-800`; "Showing X items" footer; Category/status fallbacks.

8. **ItemsList.vue**: List/grid toggle selected state `amber-*` → `stone-*` for consistency with quick actions. Scoped styles: item-icon and item-icon-yeast use stone (#e7e5e4, #57534e) instead of blue (#dbeafe, #1d4ed8); `var(--primary-600)` → `var(--text-secondary)` and `var(--bg-elevated)`.

9. **Settings.vue**: All remaining `bg-primary-600` → `bg-amber-600` (Manage Subscription, Subscribe, Add user).
