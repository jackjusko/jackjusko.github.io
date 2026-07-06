# Ledger Theme Shift: Brewing Industry & Beer News (Operations as Focus)

## Summary

The Ledger’s positioning was shifted **away from “brewery operations” as the primary identity** toward **general brewing industry news and beer news**, with **operations as one emphasis** (not the main focus). Copy, meta, and About/Subscribe content were updated across blog-related views and components.

## Rationale

- Broaden appeal to beer lovers and industry readers, not only operators.
- Keep operations as a distinct angle (section, content, audience) without defining the whole brand.
- Align masthead, SEO, and marketing copy with “brewing industry & beer news” first, “operations” second.

## Changes Made

### 1. BlogList.vue

- **Masthead**: “Craft beer & brewery” → **“Brewing industry & beer news”**; “News, operations, trends” → **“Industry, beer, operations”**.
- **Meta**: `title` and `og:title` → “The Ledger | Brewing Industry & Beer News | BrewLedger”.
- **Meta description**: “Craft beer and brewery insights for brewers, brewery owners, and beer drinkers…” → “Brewing industry and beer news for the trade and beer lovers. The Ledger covers industry, beer, and operations from BrewLedger.”

### 2. LedgerAbout.vue

- **Subtitle**: “The industry publication for craft beer and brewery operations.” → **“Brewing industry and beer news, with a focus on operations.”**
- **Reader line**: “Read by 500+ brewery operators each week.” → **“Read by 500+ brewery and beer industry readers each week.”**
- **Body**: Reframed from “news and insight site for brewery owners, production managers…” to “brewing industry and beer news for the trade and beer lovers” with “a particular focus on operations: inventory, TTB, cellar workflows…” Second paragraph softened to “From beer and brand news to the stuff that affects margins and compliance…” and removed duplicate “Our contributors include…” (kept in preceding paragraph).
- **Meta description**: Updated to “brewing industry and beer news from BrewLedger, with a focus on operations.”

### 3. BlogSidebar.vue

- **CTA blurb**: “news and insights for brewery operations” → **“brewing industry and beer news, with a focus on operations.”**

### 4. LedgerSubscribe.vue

- **Header**: “Weekly insights for brewery operators.” → **“Weekly brewing industry and beer news. No spam, no fluff.”**
- **Body**: “Join 500+ brewers and operations leads who get…” → **“Join 500+ readers who get a short roundup every week: new Ledger articles, industry and beer news, regulatory notes, and practical tips.”**
- **Meta description**: “weekly craft beer and brewery operations insights” → **“weekly brewing industry and beer news.”**

### 5. LedgerSection.vue

- **Meta description**: “craft beer and brewery operations insights” → **“brewing industry and beer news.”**

### 6. BlogPost.vue

- **Fallback title**: “The Ledger | Craft Beer & Brewery | BrewLedger” → **“The Ledger | Brewing Industry & Beer News | BrewLedger”.**
- **Fallback description**: “Craft beer and brewery insights for brewers and beer drinkers…” → **“Brewing industry and beer news. Read more on The Ledger from BrewLedger.”**

### 7. App.vue

- **pageTitles**: `/blog` entry → “The Ledger | Brewing Industry & Beer News | BrewLedger”.

### 8. router/index.js

- **Blog route meta.title**: Same as above.

### 9. analysis.md

- **The Ledger purpose**: “Industry news and insight site for brewery operations” → “Brewing industry and beer news publication—… with a focus on operations”.
- **Front page masthead**: “Craft beer & brewery · News, operations, trends” → “Brewing industry & beer news · Industry, beer, operations”.
- **SEO bullet**: Meta descriptions and titles now documented as emphasizing “brewing industry and beer news”.
- **Feature Analysis**: Added reference to `changes/ledger-theme-brewing-industry-beer-news.md`.

## What Was Not Changed

- **Section names**: Operations, Trends, Industry, Best Practices left as-is (still one of four sections).
- **Product/console copy**: Landing, Reports, Racking, TTBForm, AIAssistant, etc. remain operations/product-focused; only Ledger/blog positioning was shifted. Grep for “brewery operations” or “craft beer” in console still finds those phrases only in product surfaces (e.g. Landing “brewery operations platform”), not in blog/Ledger views.
- **blogLoader.js**: Section keys and labels unchanged.
- **LedgerCtaSidebar.vue**: No copy changes (already “Write for The Ledger” / “Recommend a brewer or brewery” without operations-heavy tagline).

## Edge Cases & Follow-ups

1. **Consistency**: All user-facing Ledger copy and meta now lead with “brewing industry” / “beer news” and mention operations as a focus. No remaining “brewery operations” as primary identity in blog surfaces.
2. **Subscribe page**: Currently unlinked; if re-linked, the new copy is already aligned with the theme.
3. **External links**: Any third-party references to “Craft Beer & Brewery” or “brewery operations publication” would need to be updated outside this repo.
4. **Email constant**: Editorial Head email (`kflaci@getbrewledger.com`) remains in LedgerCtaSidebar and LedgerAbout; centralizing in `config.js` is optional future work.

## Verification

- Grep for “brewery operations” and “Craft beer” in blog-related files (BlogList, LedgerAbout, BlogSidebar, LedgerSubscribe, LedgerSection, BlogPost, App blog title, router blog route) shows no remaining primary-positioning use.
- Section labels and routes unchanged; operations remains a visible section and content pillar.
