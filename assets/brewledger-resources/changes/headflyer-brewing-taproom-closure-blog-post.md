# Feature Analysis: HeadFlyer Brewing Taproom Closure Blog Post

## Summary

Added a news editorial blog post about HeadFlyer Brewing closing its Northeast Minneapolis taproom on April 5, 2026. The post synthesizes reporting from the Star Tribune, Hoodline, and Bring Me The News; quotes the owners' Instagram announcement; and includes an extended analysis section on the taproom-vs-brewery split.

## Implementation

### Files Created

1. **`server/content/blog/headflyer-brewing-taproom-closure.md`** — Server-side blog content (sitemap, SSR)
2. **`platforms/console/src/blog/posts/headflyer-brewing-taproom-closure.md`** — Console SPA blog content (Vite glob)

### Content Structure

- **Frontmatter**: title, slug, date, author, authorImage, section (Industry), excerpt
- **News synthesis**: Announcement, space/rumors (Dangerous Man), Northeast Minneapolis brewery churn
- **Quotes**: Two blockquotes from Instagram post (as reported by Star Tribune/Hoodline)
- **Extended analysis**: "Closing the Taproom, Keeping the Brewery" — real estate/labor, focus, distribution, taproom-first model under pressure
- **The View From Here**: Editorial close tying to industry rationalization

### Sources Used

- [Star Tribune](https://www.startribune.com/headflyer-brewing-to-close-taproom-northeast-minneapolis-hennepin-dangerous-man/601589541) — primary
- [Hoodline](https://hoodline.com/2026/02/headflyer-pulls-taproom-plug-after-9-years-in-northeast-minneapolis/) — additional context
- [Instagram post](https://www.instagram.com/p/DVPJk9hkTFW/) — quoted (content from Star Tribune/Hoodline; direct fetch returned 403)
- Bring Me The News — referenced via web search; fetch timed out; content overlaps with Star Tribune/Hoodline

## First-Iteration Review: Potential Weak Points

### 1. **Dual content sync**

Posts exist in both `server/content/blog/` and `platforms/console/src/blog/posts/`. Future edits must be applied to both files. No automation exists to keep them in sync. **Mitigation**: Document in analysis.md; consider future sync script or single source of truth.

### 2. **Section auto-derivation**

The blog service derives section from slug when frontmatter `section` is missing. Slug `headflyer-brewing-taproom-closure` contains "closure" which maps to `industry`. Frontmatter explicitly sets `section: Industry`. **Status**: Correct; no issue.

### 3. **Sitemap inclusion**

`blogService.loadAllPosts()` reads from `server/content/blog/`. New post will appear in sitemap automatically. **Status**: No change required.

### 4. **Source attribution**

Instagram quote is attributed as "post on Instagram" with link. Content was taken from Star Tribune/Hoodline reporting (direct Instagram fetch failed). This is standard practice for quoting social media. **Status**: Acceptable.

### 5. **Where will HeadFlyer brew?**

The post states HeadFlyer will "continue developing new beers" and distribute to liquor stores, bars, restaurants. It does not specify where production will occur—contract brewing, another facility, or the same Miller Textile building. Star Tribune says "beers will still be made elsewhere." **Consideration**: Could add a sentence clarifying production location if/when known; current draft focuses on the taproom-vs-brewery distinction and is sufficient.

### 6. **The Great Northern Festival**

User mentioned thegreatnorthernfestival.com as a source. Fetch returned minimal content (page title only). No substantive info was extracted. **Status**: Omitted; not critical for the article.

### 7. **Lead image**

Post has no `leadImage` or `leadCaption`. Other posts (e.g. PBR) use lead images. **Consideration**: Optional enhancement; user did not provide an image. Can add later if one is supplied.

### 8. **Cover story / popular**

No `coverStory` or `popular` flags. Post will appear in list/section but not as cover story. **Status**: Intentional; latest/cover can be set manually if desired.

## Second-Iteration Review

### Implemented After First Pass

- **Production location**: Added sentence clarifying beers will be made elsewhere (per Star Tribune) and taproom space may be taken over. Addresses the "where will HeadFlyer brew?" gap.

### Second-Iteration Verification

- **Section mapping**: Slug `headflyer-brewing-taproom-closure` contains "closure" → industry. Frontmatter `section: Industry` is explicit. Both server (`blog.js` services) and console (`blogLoader.js`) include `closure` in industry keyword list. ✓
- **Dual content**: Both files updated in lockstep for the production-location addition. ✓
- **Sitemap**: Server `blogService.loadAllPosts()` reads `server/content/blog/`; new post included. ✓
- **No regressions**: Post follows existing format (Oregon, PBR, industry-consolidation). ✓

### Documentation

- analysis.md will be updated to document the new post and the HeadFlyer taproom-closure editorial pattern.
