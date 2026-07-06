# Blog Author Names and Pictures Fix

## Problem
Author names and headshot pictures were not showing on the blog (The Ledger) in `platforms/console/src/blog/` — both in the post list and on individual post pages.

## Root Causes Addressed

1. **Frontmatter parsing robustness**  
   - Lines were split only by `\n`; on Windows or with mixed line endings, keys/values could retain `\r` or inconsistent trimming.  
   - Empty lines in frontmatter were still processed.  
   - **Change:** Split on `\r?\n`, skip empty lines (`if (!trimmed) return`), and parse only `trimmed` lines so keys and values are consistent.

2. **Author/authorImage consistency**  
   - Author and authorImage were taken directly from `meta` without explicit string normalization; some posts omit `authorImage` in frontmatter.  
   - **Change:** Explicit `author` and `authorImage` derivation: trim `meta.author`, and use `AUTHOR_HEADSHOTS[author]` as fallback when `meta.authorImage` is missing so known authors (Jack Jusko, Michael Stroener, Kyle Flaci) get a headshot even without frontmatter.

3. **Asset URL base path**  
   - Image `src` and CSS `url()` used paths like `/headshots/...` and `/logo.png` directly. When the app is served under a non-root base (e.g. `https://site.com/console/`), those requests go to the wrong path and 404.  
   - **Change:** Introduced `resolveAssetUrl(path)` in `BlogPost.vue` and `BlogList.vue` that prepends `import.meta.env.BASE_URL` to paths starting with `/`, and used it for all author images, cover images, list/lead/figure images, and logo.

## Files Changed

- **`platforms/console/src/utils/blogLoader.js`**
  - Added `AUTHOR_HEADSHOTS` map (Jack Jusko, Michael Stroener, Kyle Flaci → `/headshots/...`).
  - `parseFrontmatter`: split on `\r?\n`, skip empty lines, parse `trimmed` line only.
  - When building each post: set `author` and `authorImage` explicitly; use `AUTHOR_HEADSHOTS[author]` when `meta.authorImage` is empty.

- **`platforms/console/src/views/BlogPost.vue`**
  - Added `resolveAssetUrl(path)`.
  - Byline logo: `:src="resolveAssetUrl('/logo.png')"`.
  - Author headshot: `:src="resolveAssetUrl(post.authorImage)"`.
  - Lead image: `:src="resolveAssetUrl(postLeadImage)"`.
  - Figure image: `:src="resolveAssetUrl(post.figureImage)"`.

- **`platforms/console/src/views/BlogList.vue`**
  - Added `resolveAssetUrl(path)`.
  - Cover story: `backgroundImage: url(${resolveAssetUrl(coverPost.coverImage)})`, cover author photo and logo use `resolveAssetUrl`.
  - Card author photos: `:src="resolveAssetUrl(post.authorImage)"`.
  - `cardImageStyle(post)`: uses `resolveAssetUrl(url)` for list/cover image.

## Edge Cases Considered

- **Lucas Gerrity:** No file in `public/headshots/`, so not added to `AUTHOR_HEADSHOTS`; posts with only `author: Lucas Gerrity` and no `authorImage` continue to show initials.
- **BrewLedger Team:** Unchanged; still uses logo and `isBrewLedgerTeam()`.
- **Prerender:** Same loader and components are used; base URL is applied at runtime so prerendered HTML gets correct asset URLs for the configured base.

## Verification

- Lint: no new errors in `blogLoader.js`, `BlogPost.vue`, `BlogList.vue`.
- Author names come from `author` (with fallback "The Ledger"); author images from `authorImage` or `AUTHOR_HEADSHOTS`; all image paths go through `resolveAssetUrl` so they work with `base: '/'` and with a non-root base.

## Troubleshooting

If author names or pictures still do not show: (1) Ensure each post frontmatter has `author: Full Name` (and optionally `authorImage: /headshots/Filename.ext`). (2) Ensure `public/headshots/` contains the image files referenced in frontmatter or in `AUTHOR_HEADSHOTS`. (3) To add a new author headshot, add the file under `public/headshots/` and add an entry to `AUTHOR_HEADSHOTS` in `blogLoader.js` (e.g. `'Lucas Gerrity': '/headshots/LucasGerrity.png'`).
