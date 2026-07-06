# Feature Analysis: Blog Layout Dense / WSJ-Style (First Iteration)

## Summary
The Ledger blog in `platforms/console/` was redesigned to feel more dense and valuable—"Wall Street Journal for craft beer"—rather than a marketing feed. This document captures the first iteration of feature analysis: potential bugs, edge cases, and integration concerns.

## Changes Implemented

### BlogList.vue
- **Masthead**: Reduced from large hero to compact editorial masthead. Single line: "The Ledger" + "Craft beer & brewery" + "Operations, trends, best practices". Smaller padding, border-left accent retained.
- **Cover story**: Shorter min-height (200px / 240px vs 320px / 400px); single-line meta (date · author · read time); removed large byline block and "Read the story" CTA from cover.
- **Removed**: Full-width "Get the weekly" CTA strip from main content (newsletter remains in sidebar only).
- **In this issue**: Replaced large article cards (avatars, excerpts, "Read article" per row) with a dense table-of-contents style: bordered/rounded list, each row = date (short) | title | author · X min. Whole row is link; no per-article avatars or excerpts.
- **Helpers**: Added `formatDateShort()` for compact dates (e.g. "Feb 7, 2026"); removed `LEDGER_NEWSLETTER_URL` import from BlogList.

### BlogPost.vue
- **Article card**: Smaller padding, thinner border, reduced shadow. Header: tighter byline (smaller avatar, single-line "Written by" removed in favor of name only in compact bar).
- **Takeaways**: Smaller box (padding, text size).
- **Body**: Slightly smaller base font (0.9375rem), tighter line-height (1.65); reduced margins on h1/h2/h3/p and blockquotes for denser reading.

### BlogSidebar.vue
- **Popular**: Renamed label to "Popular"; smaller text (text-xs), tighter spacing.
- **Newsletter**: Single compact block—"Weekly insights" + "Subscribe →" link + one-line blurb; no large button.
- **About**: Shorter copy; "BrewLedger →" text link instead of button. Reduced padding and gap between blocks; narrower sidebar in App.vue (lg:w-56 xl:w-64).

### App.vue (blog layout)
- **Header**: Smaller logo and text; removed "Craft beer & brewery insights" subline; tighter padding (py-3, px-5/6/8).
- **Main**: Reduced vertical/horizontal padding and gap between main column and sidebar; sidebar width reduced; sticky top-6.

## First-Iteration Analysis: Risks & Edge Cases

### 1. **Responsive behavior**
- **Risk**: Dense TOC rows (date | title | author · min) may wrap awkwardly on very narrow viewports; long titles could push author/read time to next line.
- **Mitigation**: Used `flex flex-col sm:flex-row` and `min-w-0 flex-1` on title so layout stacks on small screens and title truncates if needed. Tabular-nums and shrink-0 on date/min keep columns aligned on larger screens.
- **Follow-up**: Confirm on 320px–400px width that "In this issue" remains readable; consider `line-clamp-1` on title for extreme cases if needed.

### 2. **Accessibility**
- **Risk**: Smaller tap targets (sidebar "Subscribe →", "BrewLedger →") and denser links might affect touch/click usability.
- **Mitigation**: Whole TOC row is the link (large click area). Sidebar links remain focusable; font sizes stay at or above 11px.
- **Follow-up**: Ensure focus visible states remain clear; check color contrast for "Subscribe →" and "BrewLedger →" against background.

### 3. **SEO & meta**
- **Risk**: No structural changes to routes or head; canonical, titles, and descriptions unchanged. No new risk.
- **Note**: BlogList still uses `useHead` with same title/description; BlogPost unchanged. No action.

### 4. **Empty / single-post states**
- **Risk**: If `restPosts` is empty (only one post total), "In this issue" section is not rendered; cover story still links to that post. No empty table shown.
- **Mitigation**: `v-if="restPosts.length"` avoids rendering an empty bordered list. Single-post index still shows masthead + cover only. Acceptable.

### 5. **Popular posts in sidebar**
- **Risk**: Sidebar "Popular" uses `loadPopularPosts()` (posts with `popular: true`). If none, block is hidden. Label changed from "In this issue" to "Popular" to avoid confusion with main column "In this issue."
- **Mitigation**: Clear distinction: main = full list (minus cover); sidebar = curated "Popular". No conflict.

### 6. **Newsletter CTA visibility**
- **Risk**: Removing the large "Get the weekly" strip from index may reduce newsletter signups.
- **Mitigation**: Newsletter remains in sidebar with "Subscribe →" and one-line blurb. Editorial tone prioritizes content density; signup still present. Can A/B test later if needed.

### 7. **Dark mode**
- **Risk**: All new/updated classes use dark: variants (slate, neutral, amber). No new component; same palette as before.
- **Mitigation**: Existing dark styles retained; borders and text colors use dark: equivalents. Spot-check recommended.

### 8. **Animation**
- **Risk**: BlogList article rows use staggered `ledger-fade-in` with shorter delay steps. No layout shift; animation is subtle.
- **Mitigation**: Kept animation; reduced delay steps for faster perceived load. No change to layout stability.

## Integration Checklist
- [x] BlogList.vue: masthead, cover, TOC list, formatDateShort, no newsletter strip
- [x] BlogPost.vue: compact header, takeaways, body typography
- [x] BlogSidebar.vue: Popular, compact newsletter, compact About
- [x] App.vue: blog header and main spacing, sidebar width
- [ ] Manual test: /blog and /blog/:slug on desktop and narrow viewport
- [ ] Manual test: dark mode on index and post

## Second Iteration: Expanded Analysis

### Additional Edge Cases Considered

1. **Very long post titles in TOC**
   - **Risk**: Long titles could wrap and break the dense single-row feel or push "author · min" to next line on sm+.
   - **Mitigation**: Applied `truncate` and `title` attribute on the title `<h3>` so the title stays one line with ellipsis and full text is available on hover/screen readers.

2. **Focus visible / keyboard nav**
   - **Risk**: Dense links (whole row, sidebar text links) must remain clearly focusable.
   - **Mitigation**: No removal of focus outlines; router-link and `<a>` retain browser/site focus styles. Sidebar and TOC rows are full link areas, so focus target is large.

3. **RTL**
   - **Risk**: Border-left accents and "date | title | author" order may need RTL tweaks if the app is localized.
   - **Mitigation**: Not in scope for this change; Ledger is currently LTR. If RTL is added later, use logical properties (e.g. border-inline-start) for masthead and TOC row accents.

4. **Cover story with no excerpt**
   - **Risk**: Cover already uses single-line meta (date · author · read time); no excerpt on cover. No change from first iteration.
   - **Mitigation**: None needed; cover remains compact.

5. **Empty Popular in sidebar**
   - **Risk**: When no posts have `popular: true`, the Popular block is hidden; sidebar shows newsletter, About, badge only. No empty "Popular" section.
   - **Mitigation**: `v-if="popular.length"` already in place. Acceptable.

### Implementation Follow-Ups Applied
- TOC title: added `truncate` and `:title="post.title"` so long titles stay one line and full text is available on hover.

## Documentation Update
- `analysis.md` Ledger section updated to describe the dense/editorial (WSJ-style) layout: compact masthead, compact cover, TOC-style "In this issue" list, dense sidebar, tighter blog header and main spacing.

---

# Multi-Column Layout & Image Slots (Follow-Up)

## Summary
The Ledger index and article views were updated to use multi-column layout and dedicated image slots: newspaper-style column flow for "In this issue", an "In focus" image strip on the index, and lead + figure image slots on article pages.

## Changes Implemented

### blogLoader.js
- **New frontmatter**: `listImage` (index "In focus" strip and optional TOC thumbnail), `leadImage` (article lead image below header), `leadCaption`, `figureImage` (article sidebar/figure image), `figureCaption`. All passed through and unquoted where string.

### BlogList.vue
- **In focus**: New section above "In this issue"—grid 1 col mobile, 2 sm, 3 xl. Posts with `listImage` or `coverImage` (excluding cover) fill slots; up to 6 cards. Remaining slots (minimum 3 total) show placeholder boxes (dashed border, "Image" label) so the layout is always 3+ slots. Each card: image area (aspect 4/3, background or img), date, title; links to post.
- **In this issue**: Multi-column flow via CSS `column-count`: 1 (default), 2 at md, 3 at xl. List items use `break-inside: avoid` so rows don’t split across columns.

### BlogPost.vue
- **Lead image**: When `leadImage` or `coverImage` is set, a full-width lead image block below the header (aspect 21/9 or 3/1), optional `leadCaption` below.
- **Figure/sidebar image**: When `figureImage` is set, article body uses a two-column layout (prose + aside). Aside: image (aspect 4/3), optional `figureCaption`. On desktop aside is right (lg:w-72 xl:w-80); on mobile figure appears below prose (`order-last lg:order-none`).

## Edge Cases
- **No image posts**: "In focus" shows 3 placeholder slots so the grid is always visible.
- **Lead image**: Uses `leadImage` if set, else `coverImage`; no lead block if neither is set.
- **Figure**: Only rendered when `figureImage` is set; layout stays single column when not set.
