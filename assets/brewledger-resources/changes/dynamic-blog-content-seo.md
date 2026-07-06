# Dynamic Blog Platform with SEO Preservation

## Summary

The blog (The Ledger) was migrated from build-time MD files with Vite prerender to a **backend-served, server-rendered** blog. Posts are now served as full HTML from the Express server, enabling content updates without frontend deploys while preserving SEO (content in initial HTML for crawlers).

## Changes Implemented

### Phase 0: Server Refactor
- **`server/lib/db.js`**: Extracted `connect`, `createRun`, `createGet`, `createAll`, `getOrgMaxLocations`, `countActiveLocations`
- **`server/middleware/auth.js`**: Extracted `authMiddleware`, `generateToken`, `authLimiter`
- **`server/middleware/validation.js`**: Extracted `createValidateEntity`
- **`server/server.js`**: Now uses lib/middleware; inline DB helpers and auth removed
- Route handlers use `authMiddlewareFn` from `authMiddleware(get, run)`

### Phase 1: Backend Blog
- **`server/content/blog/`**: 28 MD posts migrated from `platforms/console/src/blog/posts/`
- **`server/services/blog.js`**: Loads posts from filesystem, parses frontmatter, renders with `marked`
- **`server/routes/blog.js`**: 
  - GET `/blog` — list with cover story and section links
  - GET `/blog/section/:key` — section page
  - GET `/blog/:slug` — single post (calls `next()` for `/blog/about`, `/blog/subscribe` so SPA handles them)
  - GET `/blog/admin` — simple HTML form to add posts
  - POST `/api/blog/posts` — create/update post (auth via `BLOG_ADMIN_PASSWORD`)
  - GET `/sitemap.xml` — generates sitemap from posts (implemented in server/routes/blog.js)
- **`server/templates/blog-layout.js`**: Shared HTML layout with title, meta, canonical

### Phase 2: Admin API (implemented 2026-02-24)
- **POST /api/blog/posts**: Accepts JSON (`slug`, `title`, `body`, optional: `author`, `date`, `excerpt`, `section`, `popular`). Auth: `Authorization: Bearer <password>` or `password` in body. Compares to `BLOG_ADMIN_PASSWORD` env var.
- **GET /blog/admin**: Simple HTML form (no React/Vue). Use `?slug=existing-slug` to pre-fill for editing. Form submits via fetch; shows success/error.

### Phase 3: Frontend Cleanup
- **`platforms/console/vite.config.js`**: Removed `vite-plugin-prerender` entirely
- **`platforms/console/src/router/index.js`**: 
  - Removed `BlogList`, `BlogPost`, `LedgerSection` routes
  - Kept `LedgerAbout`, `LedgerSubscribe` (SPA pages)
  - Added `beforeEnter` redirects for `/blog`, `/blog/section/:key`, `/blog/:slug` → full page load to server

### Item Templates (Legacy Removal)
- Item template routes (`GET /api/item-templates`, etc.) were planned for removal but left in place due to file sync constraints. `ItemTemplateRepository.js` can be deleted when confirmed unused.

## Verification Notes

1. **Route order**: Blog routes mounted before `express.static` so `/blog*` is server-handled.
2. **SPA slugs**: `/blog/about` and `/blog/subscribe` call `next()` so static/SPA fallback serves index.html; Vue router shows LedgerAbout/LedgerSubscribe.
3. **CSS**: Blog layout links to `/assets/index.css`; inline fallback styles for prose. Production may need to resolve hashed asset paths from built index.html.
4. **BLOG_ADMIN_PASSWORD**: Set in `.env` to protect admin. If unset, POST /api/blog/posts returns 401.

## Files Changed

| File | Change |
|------|--------|
| `server/lib/db.js` | NEW |
| `server/middleware/auth.js` | NEW |
| `server/middleware/validation.js` | NEW |
| `server/services/blog.js` | NEW |
| `server/routes/blog.js` | NEW |
| `server/templates/blog-layout.js` | NEW |
| `server/content/blog/*.md` | NEW (28 files migrated) |
| `server/server.js` | Refactored to use lib; blog routes mounted |
| `server/package.json` | Added `marked` |
| `platforms/console/vite.config.js` | Removed prerender |
| `platforms/console/src/router/index.js` | Blog routes adjusted |
