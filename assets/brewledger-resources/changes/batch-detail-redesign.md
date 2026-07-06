# Batch Detail View Redesign – Feature Analysis

## Summary

The Batch Detail page at `platforms/console/src/views/BatchDetail.vue` was redesigned from a mobile-style single-column layout to a desktop-optimized layout. The goal was to avoid the “mobile view hastily adapted to desktop” appearance and align with the console design system (cards, data tables, buttons, badges).

## Changes Implemented

### 1. Page structure
- **Breadcrumb**: Replaced “← Back to Batches” with a proper nav and `aria-label="Breadcrumb"` for accessibility.
- **Loading / not found**: Wrapped in `.card` and use a spinner; “Back to Batches” uses `btn btn-primary`.
- **Hero**: Single header block with batch name (larger, `heading-refined`), date + total volume as meta, and status badge on the same row. No card around the hero to reduce visual clutter.

### 2. Actions toolbar
- **Primary vs secondary**: “Log Reading” is the single primary action (`btn btn-primary`); all other actions use `btn btn-secondary`.
- **Order**: Log Reading → Update Status → Add Ingredient → Record Packaging → Add Water / Liquid → Mark Production Complete.
- **Mark Production Complete**: Styled with success color (border/hover) to distinguish it as a milestone action.
- **No emojis** on secondary buttons (only on Log Reading for consistency with existing usage).

### 3. Two-column layout
- **Grid**: `grid-cols-1 xl:grid-cols-3` so on large screens the vessels block spans 2 columns and the Timeline/History card spans 1.
- **Vessels**: Moved into a dedicated card with `card-header` (title + “Split / Transfer” link) and `card-body p-0` for a full-bleed table.
- **Vessels table**: Uses global `.data-table` with columns: Vessel (name + optional status line), Volume, Gravity, Temp, pH, Actions (Adjust | Log). Empty state message when no vessels, with CTA to use Split / Transfer.
- **Right column**: Single card containing Timeline and History tabs. Tab bar has a light background to separate it from content. Content uses `card-body flex-1 min-h-0 overflow-auto` for scroll when needed. Card has `min-h-[320px]` so the right column doesn’t collapse on desktop.

### 4. Timeline tab
- **Milestones**: Same behavior (toggle, status classes). Layout tightened: smaller type, vertical line, milestone descriptions as supporting text. `type="button"` on milestone buttons for semantics.

### 5. History tab
- **Table instead of cards**: History events are shown in a `.data-table` with columns Date, Event (icon + title), Details (subtitle with `title` for full text on truncation). Same data source (`allHistoryEvents`); only presentation changed.
- **Empty state**: In-table message when no events.

### 6. Design system alignment
- Uses `desktop-container`, `card`, `card-header`, `card-body`, `data-table`, `btn`, `btn-primary`, `btn-secondary`, `badge`, `heading-refined` from `style.css`.
- Consistent spacing (`gap-6`, `mb-6`, `mb-8`), transitions on interactive elements, and neutral/primary/success semantics.

## First-Pass Risk and Edge-Case Analysis

### Functionality
- **Modals**: All modals remain as siblings under the root container; `batch` can be null when showing “not found” or loading, but modals are only opened when `batch` exists, so no regression.
- **Vessels table**: Uses same `batchLocations` and `getVesselName(split.vessel_id)`; empty state and “Split / Transfer” flow unchanged.
- **Timeline**: `milestoneDefinitions`, `toggleMilestone`, `getMilestoneStatusClass`, `isMilestoneCompleted`, `isNextMilestone`, `getMilestoneDate` unchanged; only markup and layout changed.
- **History**: `allHistoryEvents` computed unchanged; table columns map to `event.date`, `event.title`, `event.icon`, `event.subtitle`. Long subtitles are truncated with `title` for tooltip.

### Layout and responsiveness
- **Narrow viewports**: On `< xl`, grid becomes single column; order is hero → actions → vessels card → Timeline/History card. Vessels table can scroll horizontally via `overflow-x-auto`. No dedicated mobile breakpoints were added; the layout remains usable on smaller desktop widths.
- **Many vessels**: Table grows vertically; no virtualization. Acceptable for typical batch vessel counts.
- **Many history events**: Table grows; same as before (previously a long list of cards). Scroll lives in the card body.

### Accessibility
- **Breadcrumb**: `aria-label="Breadcrumb"` and decorative arrow in `aria-hidden="true"`.
- **Tab panel**: Tab buttons are not wrapped in a role="tablist" / role="tab" / role="tabpanel" structure. If the console later adopts ARIA tabs, this should be updated.
- **Tables**: Vessels and History use semantic `<table>`; screen readers can navigate by row/column. Details column uses `title` for full subtitle.

### Integration
- **BatchesList**: Links to `/batches/:id` unchanged; no route or prop changes.
- **Styles**: Only Tailwind and existing `style.css` classes; no new global or scoped CSS. Dark mode uses existing neutral/primary/success tokens.
- **Sync / data**: No changes to repositories, SyncService, or loadData; redesign is view-only.

## Potential Weak Points (First Iteration)

1. **Tab semantics**: Tabs are styled but not exposed as tabs to assistive tech. Consider adding `role="tablist"`, `role="tab"`, `aria-selected`, and `role="tabpanel"` with `aria-labelledby` in a follow-up.
2. **Right column height**: `min-h-[320px]` is arbitrary; on very tall viewports the right card might feel short. Could consider `min-h-[min(320px,40vh)]` or similar if needed.
3. **History table on small screens**: Truncated “Details” and narrow columns might be tight on small desktops; horizontal scroll is available but not ideal. Acceptable for a desktop-first redesign.
4. **Production Complete button**: Custom success styling (`border-success-*`, `hover:bg-success-50`) is inline; if the design system gains a `btn-success` later, this should be switched.
5. **No keyboard shortcut** for “Log Reading”; could be added later for power users.

## Second Iteration: Fixes Applied

### ARIA for tabs
- **Tab list**: Wrapper has `role="tablist"` and `aria-label="Batch timeline and history"`.
- **Tab buttons**: Each has `role="tab"`, `aria-selected` (true/false), `id="batch-tab-timeline"` / `batch-tab-history`, and `aria-controls="batch-panel-timeline"` / `batch-panel-history`.
- **Panels**: Timeline and History panels have `id="batch-panel-timeline"` / `batch-panel-history`, `role="tabpanel"`, and `aria-labelledby` pointing to the corresponding tab id.
- Keyboard navigation (Arrow keys, Home/End) is not implemented; screen readers can still use the tab/panel association. Full tab pattern could be added later if needed.

### btn-success
- **Design system**: Added `.btn-success` and `.btn-success:hover` in `platforms/console/src/style.css` (success-600/700 background, white text, lift and shadow on hover).
- **Batch Detail**: “Mark Production Complete” now uses `btn btn-success` instead of custom success-colored secondary button.

## Recommendations for Future

- Consider adding arrow-key and Home/End handling for the Timeline/History tabs for full keyboard tab pattern.
- Confirm with product that the single primary action (Log Reading) is correct; if “Update Status” or “Record Packaging” should be primary in certain contexts, consider context-specific primary or a compact “More actions” menu on smaller widths.
