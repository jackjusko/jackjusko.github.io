# Steelhead Brewing Eugene Closing & Legacy Blog Post – Feature Analysis

## Summary

New blog post created about Steelhead Brewing Company in Eugene, Oregon—its March 10, 2024 closure after 32 years, owner Cordy Jensen's retirement, the transition to a steakhouse with McKenzie Brewing tasting room, and the brewery's legacy in Oregon craft beer.

## Implementation

- **Server content**: `server/content/blog/steelhead-brewing-eugene-closing-legacy.md`
- **Console SPA content**: `platforms/console/src/blog/posts/steelhead-brewing-eugene-closing-legacy.md`
- **Cover image**: https://upload.wikimedia.org/wikipedia/commons/9/91/Steelhead_Brewing_Company.jpg (Wikimedia Commons, CC BY-SA 3.0)
- **In-article image**: Same image with caption crediting Visitor7
- **Section**: Industry
- **Date**: 2026-03-04

## Sources Cited

1. **[KVAL](https://kval.com/news/local/gallery/steelhead-brewery-in-eugene-closing-its-doors-after-three-decades?photo=1)** – Closure announcement, March 10, 2024
2. **[KEZI](https://www.kezi.com/news/historic-brew-pub-in-eugene-closing-doors-after-32-years-of-business/article_7787a8ec-dc26-11ee-a359-7b9792dea86b.html)** – Historic brewpub closure coverage
3. **[That Oregon Life](https://thatoregonlife.com/2024/03/steelhead-brewery-closing/)** – Jensen family history, Mark Byrum transition, employee impact, community reaction
4. **[Who Owns My Beer](https://www.whoownsmybeer.com/beer/steelhead/)** – Brewery ownership, beer lineup, McKenzie Brewing connection
5. **[The Brew Site](https://www.thebrewsite.com/steelhead_brewing/)** – Location, operations, Jamie Floyd, Teri Fahrendorf
6. **[BrewPublic](https://brewpublic.com/brewpubs/eugenes-steelhead-brewing/)** – Eugene brewpub context
7. **Internal**: Link to BrewLedger blog post on industry consolidation closures

## Potential Issues

- **Internal link**: References `https://getbrewledger.com/blog/industry-consolidation-closures`—ensure base URL matches deployment.
- **Wikimedia image**: CC BY-SA 3.0 requires attribution; caption includes "Visitor7, Wikimedia Commons, CC BY-SA 3.0."
- **Dual content sync**: Edits must be applied to both server and console locations.

## Recommendations

- Content-only addition; no code changes required.
- analysis.md updated with feature analysis reference and dual-content example.
