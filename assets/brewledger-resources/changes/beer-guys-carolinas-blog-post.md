# Beer Guys Carolinas Blog Post – Feature Analysis

## Summary

New blog post created about Beer Guys Carolinas—friends of the author who are passionate about beer artwork preservation. The post highlights their website (https://beerguyscarolinas.com/) and its features: daily new beer releases and labels, an archive of beer label artwork, and search functionality.

## Implementation

- **Server content**: `server/content/blog/beer-guys-carolinas.md`
- **Console SPA content**: `platforms/console/src/blog/posts/beer-guys-carolinas.md`
- **Cover image**: https://beerguyscarolinas.com/labels/26037001000310.jpg
- **In-article image**: Same URL with caption "Nuts N' Bolts" from Erie Brewing Company
- **Section**: Industry
- **Date**: 2026-03-04

## Iteration 1 – Potential Issues & Edge Cases

1. **External image availability**: The cover and in-article images are hosted on beerguyscarolinas.com. If their server is down or the image URL changes, the post will show broken images. Consider documenting this dependency.

2. **Dual content sync**: Per analysis.md, blog posts must exist in both `server/content/blog/` and `platforms/console/src/blog/posts/`. Both locations have been updated. Future edits require manual sync to both.

3. **Image alt text**: The in-article image uses alt text "Nuts N' Bolts from Erie Brewing Company" which matches the caption. Good for accessibility.

4. **Sitemap**: The server's dynamic sitemap (from `server/content/blog/`) will automatically include the new post. No code changes needed.

5. **Console blog loader**: Uses `import.meta.glob` to load posts—new files are picked up automatically at build time. No config changes needed.

6. **Link validity**: Both links to https://beerguyscarolinas.com/ are correct. External links open in new tab per MarkdownRenderer behavior.

## Iteration 2 – Expanded Analysis

- **analysis.md integration**: Feature analysis reference and dual-content example added to analysis.md. No further documentation needed for a content-only post.

- **Blogrip exclusion**: The `blogrip/` directory is a standalone generic blog replica, not connected to the main BrewLedger app. Content in `server/content/blog/` and `platforms/console/src/blog/posts/` is sufficient. No blogrip sync required.

- **SEO**: Post has unique slug `beer-guys-carolinas`, excerpt for meta description, and Industry section. Canonical URL will be `/blog/beer-guys-carolinas`. Title follows pattern: primary keyword (Beer Guys Carolinas) near front, benefit (Preserving Beer Artwork) clear.

- **No FAQ schema needed**: Post is a short feature/profile piece; H2-derived FAQ would be redundant. No `faq` frontmatter added.

- **External image CORS**: Images from beerguyscarolinas.com may be subject to CORS; typical `<img src="...">` requests do not trigger CORS for same-origin display. No issue expected.

## Final Recommendations

- Content-only addition; no code changes required.
- analysis.md updated with feature analysis reference and dual-content example.
- If Beer Guys Carolinas changes image URLs in the future, update both `server/content/blog/beer-guys-carolinas.md` and `platforms/console/src/blog/posts/beer-guys-carolinas.md`.
