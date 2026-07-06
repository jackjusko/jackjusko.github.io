# Ingredient-Level Costing Blog Post - Feature Analysis

## Overview

Added a new blog post titled "Ingredient-Level Costing: Why Batch Cost Visibility Matters for Craft Breweries" to the BrewLedger blog. The post targets current industry search trends (COGS optimization, cost visibility, batch costing) and aligns with BrewLedger's inventory and batch tracking capabilities.

## Implementation Summary

### Content

- **File**: `platforms/console/src/blog/posts/ingredient-level-costing-craft-breweries.md`
- **Slug**: `ingredient-level-costing-craft-breweries` (URL: `/blog/ingredient-level-costing-craft-breweries`)
- **Date**: 2026-02-12
- **Author**: BrewLedger Team

### Topics Covered

- The problem of aggregate vs. per-batch COGS visibility
- Key drivers of batch cost variance (hops, grain bills, yeast, yield)
- Requirements for ingredient-level costing (unit costs, actual usage, traceability)
- How batch-level cost data informs pricing, recipe rationalization, procurement, and production planning
- Operational requirements (consistent logging, inventory-to-batch linking, reconciliation)

### Tone and Format

- Professional, information-rich tone; no flashy marketing language
- Structured with clear headings and actionable takeaways
- Short CTA for BrewLedger at the end; no specific links per request

### Supporting Updates

- **Sitemap**: Added `/blog/ingredient-level-costing-craft-breweries` to `platforms/console/public/sitemap.xml` per blog system documentation (sitemap updated manually when adding posts)

## Edge Cases & Considerations

- **SEO**: Post uses standard frontmatter; slug is URL-friendly; excerpt is concise for listings.
- **Build**: `blogLoader.js` uses `import.meta.glob` for build-time inclusion; new markdown file is automatically picked up without code changes.
- **Popular posts**: `popular` is not set; post will not appear in sidebar unless manually enabled later.
- **Links**: Post contains no hyperlinks per user request; CTA is soft ("See how it works when you are ready").

## Integration

- Post follows existing format (YAML frontmatter, markdown content, BrewLedger CTA section).
- Content aligns with BrewLedger product capabilities (batches, inventory movements, item tracking, consumption-to-batch linking).
