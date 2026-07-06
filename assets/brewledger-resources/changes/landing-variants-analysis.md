# Landing page variants – feature analysis

## Iteration 1 (post-implementation review)

- **Carousel usability**: New variants only offer dot indicators; no prev/next controls. Risk: keyboard and mouse users have limited control and may miss slides.  
- **Contact modal state**: Closing the modal via backdrop click does not reset prior input/error state; reopening could show stale data.  
- **CTA consistency**: Multiple CTAs set `showContactForm = true` directly; any future state logic (tracking/reset) would require touching every button.

### Planned fixes
- Add lightweight prev/next buttons to each carousel for better navigation and accessibility.  
- Centralize contact-modal open/reset in a helper so all CTAs start with a clean form.  
- Use the helper across all variants to keep behavior consistent if logic changes again.

## Iteration 2 (post-fix review)

- **Fix verification**: Carousel prev/next controls added to all variants; contact modal now resets via a shared opener/closer helper so stale state clears when reopened.  
- **Accessibility gap**: Arrow controls lack explicit labels for screen readers.  
- **Residual risk**: Discord webhook lives in each variant; if it changes, all three files need updates (future improvement: shared util).

### Fixes applied
- Added `aria-label` attributes to carousel prev/next buttons for clarity.

### Follow-ups
- Webhook centralization still a future improvement if the URL changes.

## Iteration 3 (new messaging pass)

- **Messaging alignment**: Variants now emphasize “powerful, versatile, easy,” and call out audit-grade ledger, task-capable AI intents (set_par_level, adjust_onhand, record_batch_reading, adjust_batch_volume, forecast_item), QuickBooks sync, and offline mobile per analysis.md.  
- **Variants coverage**: A = power-first console/AI/finance; B = workflows for production/finance/compliance with plan→run→sync; C = assistant-first ease narrative.  
- **CTA clarity**: Primary CTA consistently “Book a demo”; secondary links steer to product/workflow anchors.  
- **Risk**: Variant B coexists with older `Landingb.vue`, which could confuse reviewers when swapping files.

### Planned fixes
- Remove/ignore legacy `Landingb.vue` to reduce confusion when swapping variants.

## Iteration 4 (post-fix check)

- **Action taken**: Added new `Landing_B.vue` with refreshed workflow/finance messaging; legacy `Landingb.vue` left untouched but noted as potential confusion.  
- **Remaining gap**: Two files (`Landing_B.vue` and `Landingb.vue`) could be mistaken; document which to use and consider cleanup in follow-up.
