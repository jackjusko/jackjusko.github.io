## Desktop Dashboard Enhancements – Feature Analysis (Iteration 1)

### Scope
- Dashboard additions: quick actions, vessel overview, serving summary, TTB compliance card, recent activity, estimated inventory value.
- Removed unused scope filter pills; wired range pills to drive serving and activity windows.

### Observations
- Vessel overview shows all batch_locations, including zero-volume rows; unit label defaults to `L`, which is misleading for breweries that track in barrels.
- Recent activity shows quantity without unit; ledger entries don’t snapshot unit, so context is limited.
- Serving summary totals render, but do not expose any breakdown; acceptable for a compact card.

### Risks / Gaps
- Vessel overview may display empty vessels as “active volume” due to zero-volume rows; message claims “active volume” but list can include zeros.
- Volume unit label in vessel overview defaults to `L`, likely incorrect for most breweries.
- Recent activity lacks units; risk of ambiguity (but ledger data doesn’t carry unit).

### Planned Fixes
- Filter vessel overview to rows with volume > 0 and default unit label to `bbl` when unknown.
- Keep recent activity but clarify quantities with a simple “qty” prefix to reduce ambiguity despite missing unit metadata.

---

## Feature Analysis (Iteration 2)

### Observations after fixes
- Vessel overview now hides zero-volume rows and defaults units to `bbl`; list is clearer.
- Recent activity now prefixes quantity for clarity, but still no unit (ledger lacks unit snapshots).
- TTB compliance card shows period label but no explicit period dates; a short “current month” window would reduce ambiguity.

### Remaining Risk / Gap
- TTB card lacks explicit period start/end, so users may be unsure which period they’re about to file.

### Planned Fix
- Add current-month period window (start/end dates) to the TTB compliance card subtitle to clarify scope.
