# TTB System Upgrade – Feature Analysis

## Context
- Scope: per-line column breakdowns, packaging provenance, PDF/preview fill, in-bond capture, gap detection/reconciliation.
- Artifacts reviewed: `TTBFormService.js`, `TTBPDFExportService.js`, `TTBFormPreview.vue`, `Removals.vue`.

## Iteration 1
### Findings
1) Line 34 column total risk: column breakdown reused ending-inventory stage data; `line34.g` could diverge from total beer (line13/line34) when stage sums differ from additions total.

### Actions
- Set `line34.g` to the line34 total so PDF/preview totals match form math even if stage sums differ.

### Risks/Follow-ups
- Stage warning might be too lenient (only warns when multiple locations are present). Consider tightening to surface “all cellar” even for single-location orgs that still want column staging.

## Iteration 2
### Findings
1) Stage warning leniency: gap detection only warned when multiple locations existed; single-location orgs with all stages defaulted to cellar would not be prompted to set keg/bottling/case stages, limiting column breakdowns.

### Actions
- Tightened stage warning: if any beer ledger activity exists in the period and all known locations are set to `cellar`, surface a warning to configure stages for column b–f breakdowns.

### Residual Risks
- Stage mapping still defaults unknown location stages to `cellar`; if users intentionally keep a single-cellar operation, warning may be informational but harmless.

