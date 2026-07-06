## Batches Page Refresh – Feature Analysis (Iteration 1)

### Goals
- Make the Batches list easier to scan with richer cards (status, volume, vessels) without feeling cluttered.
- Add lightweight search/filter controls to jump to relevant batches quickly.
- Provide clearer progress indication and quick metadata (brew date, volume, vessels).

### Current Pain Points
- Cards are sparse: only name, status badge, date/volume text, and a thin progress bar.
- No search or filtering; long lists require scrolling with little guidance.
- Vessel info is a comma list; hard to parse at a glance.
- Progress bar lacks labels and context; statuses are abstract percentages.

### Proposed Adjustments
- Add toolbar with search and status filter; show batch count for context.
- Enhance cards: subtitle row with brew date + total volume + vessel pills, clearer status badge, labeled progress/phase text, and a primary “View details” affordance.
- Keep grid layout but tighten spacing; ensure hover/active states remain clear.

### Risks / Edge Cases
- Status-to-progress mapping is approximate; label should show status name to avoid implying exact completion.
- Some batches may not have volume or vessels; must display graceful fallbacks.
- Large lists: filters should operate client-side without additional queries.

---

## Batches Page Refresh – Feature Analysis (Iteration 2)

### Changes made after iteration 1
- Added console toolbar with search and status filter plus count context.
- Refreshed batch cards with metadata pills (date, volume, vessels), clearer status badge, labeled progress, and a “View details” affordance.
- Added relative updated-at hint and capped vessel pills (with “+N more”) to avoid clutter.

### Remaining considerations
- Progress percentages remain heuristic; status text is shown alongside width to avoid misinterpretation.
- No server-side filtering; if lists get very large, we may need pagination or server filters later.

---

## Batches Page Refresh – Feature Analysis (Iteration 3)

### New change (remove legacy statuses)
- Removed status filter, badges, and progress bar since batch statuses are legacy and no longer used.
- Simplified toolbar to search only; cards now focus on date, volume, vessels, and updated-at hint with a clear “View details” affordance.

### Notes
- Progress depiction is removed to avoid implying workflow states we no longer track.
- If we reintroduce states later (e.g., via milestones), we can add a non-legacy progress indicator tied to real data.
