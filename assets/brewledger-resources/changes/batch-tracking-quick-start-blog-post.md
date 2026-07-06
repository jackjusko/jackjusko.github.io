# Feature Analysis: Batch Tracking Quick Start Blog Post

## Summary

Added **Batch Tracking Quick Start** (`batch-tracking-quick-start.md`) to `server/content/blog/` as the third user guide post. Covers batches as the primary way to track the brewing process: starting batches (manual or template), milestone templates, ingredient additions, tank readings, split/transfer, and Mark Production Complete.

## Content Structure

- **Intro**: Batches as primary brewing-process tracker; link to Brewer's Quick Start for setup context
- **Starting a Batch**: Batches page, manual vs template, milestone templates (default + custom in Settings)
- **Ingredient Additions and Readings**: Batch detail page; additions consume from inventory; readings (gravity, temp, pH, volume)
- **Split and Transfer**: Split/recombine across tanks via Split/Transfer button
- **Mark Production Complete**: Packaging menu—serving location/tank, keg off, can/bottle off

## Cross-Links

- What is BrewLedger: "Where to Start" now links to both Brewer's Quick Start and Batch Tracking Quick Start
- Brewer's Quick Start: Added "Ready to track your brewing process?" section at end linking to Batch Tracking Quick Start
- Batch Tracking Quick Start: Links to Brewer's Quick Start for setup context

## Integration

- No server code changes. Uses existing blog service and routes.
- `section: best-practices` (auto or explicit); `takeaways` in frontmatter for sidebar.
- Sitemap includes new post automatically via `loadAllPosts()`.
