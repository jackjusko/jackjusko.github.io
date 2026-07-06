# The Ledger Rebrand – Feature Analysis

## Overview

The blog system was rebranded from "BrewLedger Blog" to **The Ledger** with an editorial magazine look: masthead "The Ledger," serif headlines (Merriweather), hero cover story, bylines with optional headshots, key takeaways box, pull quotes, read time, "Featured in The Ledger" badge, and sidebar newsletter CTA. URLs remain `/blog` and `/blog/:slug` for SEO and existing links.

## Implementation Summary

### Naming and Masthead

- **BlogList.vue**: Masthead "The Ledger," tagline "Insights on brewery operations, trends, and best practices."
- **App.vue**: Blog header subtitle "The Ledger"; `pageTitles['/blog']` → "The Ledger | BrewLedger"; `.blog-layout :deep(.ledger-headline)` for serif.
- **Landing.vue**: Nav link label "The Ledger" (→/blog).
- **BlogPost.vue**: "Back to The Ledger," "More from The Ledger"; post title fallback "The Ledger | BrewLedger"; byline "Written by {author}" with optional `authorImage`; read time; takeaways box; featured badge when `post.featured`.
- **BlogSidebar.vue**: "Popular in The Ledger"; newsletter CTA; "Featured in The Ledger" badge link.
- **Router**: `/blog` and CSV Search meta titles reference "The Ledger | BrewLedger" / "The Ledger."
- **index.html**: Merriweather font added alongside Inter.

### Frontmatter and Loader

- **blogLoader.js**: New fields parsed: `coverStory`, `coverImage`, `coverHeadline`, `authorImage`, `takeaways` (comma-separated string → array), `featured`. Boolean handling for `coverStory` and `featured`.
- **takeaways**: Supported as comma-separated string in frontmatter; stored as array on post object; fallback when string (split by comma) when not already array.

### Hero / Cover Story

- **BlogList.vue**: `coverPost` = first post with `coverStory: true` or else first post (by date); `restPosts` = posts excluding cover. Hero block: large card with optional `coverImage` background, gradient fallback, overlay headline (`coverHeadline` or title), excerpt, "Read story" link. Below: "More from The Ledger" list.

### Article Page

- **BlogPost.vue**: Header shows date, read time (word count / 200), author; optional "Featured in The Ledger" badge when `post.featured`; byline with optional circular headshot (`authorImage`). Key Takeaways box when `post.takeaways?.length`; then MarkdownRenderer.

### Markdown and Pull Quotes

- **MarkdownRenderer.vue**: Blockquotes (`> ...` multiline) extracted before escaping, raw content stored; after bold/italic, content escaped and formatted, wrapped in `<blockquote>`, restored. Paragraph conversion treats `<blockquote>` as block element (no `<p>` wrap).
- **BlogPost.vue**: `.blog-post-content blockquote` styled as pull quote (Merriweather, larger font, left border, italic).

### Sidebar and Badge

- **BlogSidebar.vue**: Newsletter CTA ("Run a brewery? Join 500+ others receiving weekly operational insights.") with Subscribe button linking to `LEDGER_NEWSLETTER_URL` (config); "Featured in The Ledger" badge link to /blog.
- **config.js**: `LEDGER_NEWSLETTER_URL` (default `https://getbrewledger.com/#subscribe`) for The Ledger's own newsletter.
- **public/featured-in-the-ledger.svg**: Badge asset for external use (breweries can link to their article or The Ledger).

---

## Edge Cases and Considerations (First Iteration)

1. **Cover story with no posts**: `coverPost` is null when `posts.length === 0`; hero is not rendered; empty state already handled.
2. **Single post**: `coverPost` is that post; `restPosts` is empty; "More from The Ledger" section shows nothing (no list items). Acceptable.
3. **Cover image URL**: `coverImage` can be relative (e.g. `/covers/foo.jpg`) or absolute; used in `style="backgroundImage: url(...)"`. No sanitization beyond frontmatter source; author-controlled content.
4. **authorImage URL**: Same as coverImage; used in `<img :src="post.authorImage">`. Relative or absolute; author-controlled.
5. **takeaways parsing**: Comma-separated string in frontmatter; if YAML list format used (multi-line), current line-by-line parser does not collect list items; only comma-separated string is supported. Document in blog README.
6. **Read time**: Computed from `post.body` word count; duplicate h1 strip happens in `postBody`, so word count includes full body. Formula `Math.max(1, Math.ceil(words / 200))`; minimum 1 min.
7. **Blockquote restoration order**: Blockquotes restored after bold/italic so inline formatting applies inside blockquote content; placeholders prevent double-escaping.
8. **LEDGER_NEWSLETTER_URL**: External link (target="_blank", rel="noopener noreferrer"); configurable; default points to site anchor for signup.
9. **Featured badge on article**: Renders only when `post.featured === true`; no layout shift when absent.
10. **Serif scoping**: Merriweather applied only under `.blog-layout`; rest of app unchanged.

---

## Integration Notes

- **Router guard**: Still allows `/blog` and `/blog/:slug` for both authenticated and unauthenticated users; no change.
- **SEO**: BlogList and BlogPost `useHead()` titles and descriptions updated to "The Ledger"; canonicals unchanged.
- **Sitemap**: No URL change; sitemap remains valid. Update when adding posts as before.
- **blog/README.md**: Should document new frontmatter fields (coverStory, coverImage, coverHeadline, authorImage, takeaways, featured) and takeaways format (comma-separated).

---

## Second Iteration (Review and Expansion)

### Additional Edge Cases

11. **Cover image load failure**: If `coverImage` is a broken or slow URL, hero still shows gradient and text; no explicit error state for image—acceptable for editorial content.
12. **authorImage load failure**: Broken image shows broken icon; consider optional `@error` handler to hide img or show initials. Low priority; can add later.
13. **Empty takeaways array**: Frontmatter `takeaways: ""` or invalid format may yield empty array; `post.takeaways?.length` is falsy, box not rendered. Safe.
14. **Blockquote with code or images**: Blockquote content is escaped then bold/italic applied; code blocks and images inside blockquotes were already extracted earlier, so blockquote raw content does not contain them. If author puts ``` inside a blockquote, it would be escaped as text. Acceptable.
15. **Multiple coverStory: true**: `coverPost` is first in list (by date desc); others appear in "More from The Ledger." No deduplication of "cover" behavior; consider documenting that only one post should have coverStory: true for predictable hero.
16. **Sticky sidebar on long pages**: Sidebar CTA and badge are in document flow; `lg:sticky lg:top-8` on the aside keeps whole sidebar sticky. No change from prior behavior.
17. **Mobile hero**: Hero min-height and padding scale (min-h-[280px] sm:min-h-[360px], p-6 sm:p-10); gradient or image covers; text remains readable. No separate mobile image.

### Constraints and Assumptions

- Blog is console-only; no mobile app blog.
- Content is static; no CMS.
- Newsletter signup is external (URL in config); no inline form in app.
- Featured badge asset is for brewery use; optional display on article when `featured: true`.
- Takeaways format: comma-separated string in frontmatter; YAML array not parsed by current loader.

### Documentation

- **analysis.md**: Updated "The Ledger (Console App)" section with full Ledger behavior and frontmatter.
- **blog README**: Should list new frontmatter fields and examples (see below).

---

## Recommended Follow-ups

1. **blog/README.md**: Add coverStory, coverImage, coverHeadline, authorImage, takeaways (comma-separated), featured with short examples.
2. **Optional**: authorImage `@error` to hide broken image or show initials.
3. **Optional**: Document in a short "For breweries" or footer that featured breweries can use `featured-in-the-ledger.svg` and link to their article or The Ledger.
