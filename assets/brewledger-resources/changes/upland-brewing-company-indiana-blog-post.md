# Upland Brewing Company Indiana Blog Post – Feature Analysis

## Summary

Added a server-only blog post about Upland Brewing Company: history, sour program, Champagne Velvet revival, and "The Other Midwest" brand identity. 2000+ words, 5 sources, SEO title.

## Implementation

- **File**: `server/content/blog/upland-brewing-company-indiana-history-sours-champagne-velvet.md`
- **Section**: Industry
- **Word count**: ~2,028
- **Sources**: Upland Beer (About Us, Local Love Oliver Winery, Champagne Velvet), Wikipedia, Indianapolis Monthly, Indianapolis Business Journal

## Content Structure

1. **Intro** – Upland as Indiana's third-largest brewery, with a deeper story (sours, Champagne Velvet, The Other Midwest)
2. **Founding (1998)** – Bloomington, founders, first beers, statewide distribution by 2004, ownership change 2006
3. **Sour Program** – Beer-for-barrels trade with Oliver Winery, Wood Shop, international distribution, Vinosynth collaborations
4. **Champagne Velvet** – Terre Haute history, recipe rediscovery, Upland revival for 15th anniversary
5. **The Other Midwest** – Brand concept, Bloomington identity, retail-as-linchpin strategy
6. **Growth & Distribution** – Scale, locations, revenue, future outlook
7. **Notable Beers & Sour Wild Funk Fest**
8. **Why Upland Matters** – Synthesis and BrewLedger CTA

## Personalized Twist

- **Bootstrap mentality**: Beer for barrels, beer for propylene glycol—craft as community
- **The Other Midwest**: Bloomington as progressive, not flyover; Upland as reflection of place
- **Program depth over trends**: Sours and Champagne Velvet as long-term commitments, not fads
- **Retail as brand**: Each location tells a story; "everybody's comfortable"

## Edge Cases & Integration

- **Server-only**: No console SPA copy; follows shandy, porter, whiskey ginger pattern
- **Section**: `Industry`—brewery profile fits existing section taxonomy
- **Sitemap**: Post auto-included via `blogService.loadAllPosts()` from `server/content/blog/`
- **SEO**: Title includes "Indiana," "History," "Sours," "Champagne Velvet" for search

## Documentation

- `analysis.md` updated with Upland post reference in dual content / server-only list
