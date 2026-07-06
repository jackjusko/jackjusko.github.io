## Receive desktop UI refresh

### Iteration 1 analysis
- Form and line items sit inside one card with a grey summary sidebar, which feels misaligned with the newer console patterns (`console-toolbar`, stacked cards, and elevated summary panels). The hero/pills crowd the card header.
- Line items look flat and cramped: no numbering, no inline unit hint, and the line total sits inside a muted box that competes with the rest of the fields instead of aligning on the right.
- Summary/info panel uses a bare neutral background instead of a card, so the right column reads like a disabled area and the primary action lacks prominence.
- Loading/empty guidance is light: when no location is selected, the prompt is small, and there is no quick glance meta (lines, est. total) near the save button.

#### Planned changes after iteration 1
- Introduce a console toolbar header with clearer title/description and compact meta pills (location, est. total, vendor/invoice) to orient the page.
- Split the main area into stacked cards: one for receipt metadata (location/vendor/invoice/note), one for line items, and a dedicated summary/action card on the right.
- Restyle line items with numbering, clearer spacing, inline unit hint, and a right-aligned line total chip for better readability.
- Elevate the summary/action card with hierarchy (info row, stats, primary action) and strengthen empty-state guidance for selecting a location before adding lines.

### Iteration 2 analysis
- The "Add item" control and line inputs still allow interaction before a location is chosen; this conflicts with the guidance text and can confuse users about where items will land.
- Toolbar meta omits invoice/bill context and the summary panel does not surface vendor/invoice, making it easy to miss which receipt metadata is being saved.
- Line cards rely solely on disabled states without a subtle visual cue when blocked (no location / loading), so the form can look active while actions are disabled.

#### Planned changes after iteration 2
- Gate add/remove and line inputs on having a location selected, and visually mute the line-items body when blocked.
- Add invoice/bill metadata to the toolbar/snapshot and mirror vendor/invoice details in the summary card for quick confirmation.
- Lightly dim line cards when blocked to align visual affordance with the disabled state.
