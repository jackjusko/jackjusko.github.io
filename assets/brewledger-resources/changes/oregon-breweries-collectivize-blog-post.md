# Oregon Breweries Collectivize Blog Post

## Summary

Added a new blog post to The Ledger: "Oregon Breweries Are Banding Together—And It's Working" (slug: `oregon-breweries-collectivize`). The post covers two Oregon announcements—the Oregon Beverage Collective (OBC) and GoSelfDistro—and argues that collectivization is emerging as a strategy for small breweries in the contracting market.

## Implementation

- **Files created:**
  - `platforms/console/src/blog/posts/oregon-breweries-collectivize.md`
  - `server/content/blog/oregon-breweries-collectivize.md`
- **Author:** Jack Jusko
- **Section:** Industry
- **Date:** 2025-02-26

## Content Overview

The post synthesizes two news items:
1. **Go Self Distro** – Adam Milne's self-distribution collective for craft breweries/cideries in Oregon, with national aspirations.
2. **Oregon Beverage Collective** – Cascade Lakes' acquisition of Crux plus a coalition of five Central Oregon brands (Cascade Lakes, Crux, Silver Moon, GoodLife, Tumalo Cider) sharing production at Crux's facility.

Key themes: shared production as a capital-efficiency play, the decoupling of "brewery" from physical brewhouse (taproom era), and distribution as a separate collectivization opportunity. The post teases a future deep-dive on GoSelfDistro.

## Integration Notes

- Both console (Vite glob) and server (blog service) load from their respective content paths; no code changes required.
- Frontmatter matches existing post format (title, slug, date, author, authorImage, section, excerpt).
- CTA at end follows Ledger convention (BrewLedger soft pitch).
