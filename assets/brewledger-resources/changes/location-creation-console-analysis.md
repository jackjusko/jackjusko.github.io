# Location creation in console

## Iteration 1 analysis
- New `/locations` list plus add/edit form mirrors mobile flow with stage and delete, but inputs trust UI; trimming/validation would prevent blank/invalid values.
- Edit form renders immediately with defaults; while data loads, delete and submit remain enabled, allowing actions before record retrieval or after a missing/404.
- Stage value is taken directly from v-model; if an unexpected value is injected (manual DOM edit), we could save an invalid stage instead of clamping to supported stages.

Planned changes after iteration 1
- Trim and revalidate name before save; block empty-after-trim names.
- Add loading/disabled guard while fetching an existing location to avoid acting on stale defaults.
- Clamp stage to allowed values (fallback to default) before save and update.

## Iteration 2 analysis
- Stage labels/options are duplicated in multiple components and are not derived from the canonical stage list; this risks drift if the allowed stages change.
- Location list swallows load failures (console-only), leaving users without feedback if fetch fails.
- Edit form disables submit/delete while loading but inputs stay editable, which can mislead users during slow fetches.

Planned changes after iteration 2
- Derive stage options/labels from the shared stage constants to avoid drift.
- Surface a lightweight error state on the Locations list when the fetch fails.
- Disable form inputs while an existing location is still loading.
