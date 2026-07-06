## Receive desktop fixes — feature analysis

### Iteration 1 (investigation + plan)
- **Invoice/Bill visibility**: Input exists but users report it missing; ensure it’s clearly visible post-submit (summary) so they can confirm capture.
- **Inventory not updating**: Ledger entry saves, but on-hand not reflecting. Risk: cache drift or sync snapshot overwriting local cache. Need a deterministic cache refresh after save to guarantee UI reflects the new quantities.
- **Post-submit UI**: Form stays visible after confirmation; should collapse to the “receipt complete” state to avoid duplicate submissions/confusion.

### Planned changes after Iteration 1
- Wrap the main receive form in a submitted guard so it hides once confirmed, leaving only the receipt-complete card.
- Surface vendor/invoice metadata in the confirmation summary to prove it was captured.
- Add an explicit on-hand cache recompute after saving to eliminate inventory drift if prior cache state was stale.

### Iteration 2 (post-implementation review)
- Form now hides when submitted; confirmation shows location/vendor/invoice, reducing ambiguity. No overlap observed.
- Recompute cache after save adds a safety net; inventory should reflect the entry even if prior cache drifted.
- No further UI regressions spotted in the receive flow; loading/error states unchanged.

### Planned changes after Iteration 2
- Monitor for performance impact of cache recompute (should be light at current scale). No additional code changes planned.
