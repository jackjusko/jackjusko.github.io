# Settings: Locations & TTB stage copy clarity

## Summary
Clarified the Settings → Locations panel copy so end users understand what "TTB stage" is and why they set it.

## Changes
- **Section title**: "Locations & TTB Stage" → "Location stages for TTB reporting"
- **Description**: Replaced jargon ("Set TTB column stage for each location (used for Form 5130.9 columns b–e)") with plain-language copy that:
  - States what to do: assign each location to a TTB reporting category (Cellar, Serving, Racking Keg, Bottling Bulk, or Case)
  - Names the form: TTB Form 5130.9 (Monthly/Quarterly Report of Operations)
  - Explains why: so inventory and removals are reported correctly to the TTB (columns b–e)
- **Sidebar**: Tab label remains "Locations & TTB stage" for brevity.

## Files
- `platforms/console/src/views/Settings.vue` (template copy only)
- `analysis.md` (Location stage bullet updated with copy note)

## Rationale
Users who are not familiar with TTB form numbers or column letters could not infer the purpose of the stage dropdown. The new copy makes the compliance/reporting purpose explicit without removing the form reference.

## Review (second pass)
- Verified the category names in the description (Cellar, Serving, Racking Keg, Bottling Bulk, Case) match the dropdown option labels in the same view. No code or integration changes required beyond copy and analysis.md.
