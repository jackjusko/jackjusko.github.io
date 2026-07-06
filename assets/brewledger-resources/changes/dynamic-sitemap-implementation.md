# Dynamic Sitemap Implementation

## Summary

Implemented GET `/sitemap.xml` on the server to generate the sitemap dynamically from blog posts and static routes. No manual updates needed when adding posts.

## Implementation

**File**: `server/routes/blog.js`

- Route: `GET /sitemap.xml`
- Mounted before `express.static`, so it overrides the static `public/sitemap.xml` when the server is running
- Base URL: `APP_BASE_URL` or `RESET_BASE_URL` or `https://getbrewledger.com`
- Content-Type: `application/xml`

## URLs Included

| Path | changefreq | priority |
|------|------------|----------|
| / | weekly | 1.0 |
| /blog | weekly | 0.8 |
| /blog/about | monthly | 0.5 |
| /blog/subscribe | monthly | 0.5 |
| /blog/section/operations | weekly | 0.7 |
| /blog/section/trends | weekly | 0.7 |
| /blog/section/industry | weekly | 0.7 |
| /blog/section/best-practices | weekly | 0.7 |
| /tools | monthly | 0.6 |
| /tools/bbl-to-case | monthly | 0.5 |
| /tools/csv-search | monthly | 0.5 |
| /blog/:slug (each post) | monthly | 0.6 |

Blog posts use `lastmod` from post `date` when available.
