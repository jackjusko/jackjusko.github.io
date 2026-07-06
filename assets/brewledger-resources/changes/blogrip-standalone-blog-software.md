# Blogrip – Standalone Blog Software

## Overview

Created a new self-contained blog system in `blogrip/` at the repository root. It is a generic extraction of the server-side blog functionality from BrewLedger—not connected to the main application. Intended for reuse as a standalone markdown-based blog.

## Implementation

### Structure

```
blogrip/
├── config.js           # Site configuration (port, baseUrl, siteName, siteTagline, sections)
├── server.js           # Express entry point
├── package.json        # express, marked only
├── content/blog/       # Markdown posts
├── routes/blog.js      # /, /blog, /blog/section/:key, /blog/:slug, /sitemap.xml
├── services/blog.js    # Post loading, frontmatter parsing, markdown rendering
├── templates/blog-layout.js  # HTML layout (generic, no BrewLedger branding)
├── public/             # Optional static assets
└── README.md
```

### Features

- **Markdown posts** with YAML frontmatter (`title`, `slug`, `date`, `author`, `excerpt`, `section`, `popular`, `coverStory`, `leadImage`, `takeaways`, etc.)
- **Sections** for grouping (Operations, Trends, Industry, Best Practices by default; configurable)
- **Dynamic sitemap** at `/sitemap.xml`
- **Server-rendered HTML** with Tailwind CSS via CDN
- **Configurable** via `config.js` or env vars (`PORT`, `BASE_URL`, `SITE_NAME`, `SITE_TAGLINE`)

### Differences from BrewLedger Blog

| Aspect | BrewLedger | Blogrip |
|--------|------------|---------|
| Branding | The Ledger, BrewLedger | Configurable site name/tagline |
| Left sidebar | CTA tiles (Write for The Ledger, Recommend) | Removed |
| Right sidebar | Sections, In focus, Popular, About, Featured badge | Sections, In focus, Popular, About (generic) |
| Navigation | Home, sections, About, Tools, BrewLedger → | Home, sections only |
| SPA routes | /blog/about, /blog/subscribe fall through to Vue | Not included (standalone) |
| Logo | BrewLedger logo | Text-only header |
| Content path | server/content/blog/ | blogrip/content/blog/ |

### Dependencies

- **express** ^5.2.1
- **marked** ^17.0.3

No database, no build step.

## Feature Analysis (Iteration 1)

### Potential Issues

1. **Section label fallback**: Custom sections from config may not have labels in `blogService.SECTION_LABELS`. Fixed by looking up label from `config.sections` first.
2. **Empty content dir**: If `content/blog/` is missing, `loadAllPosts()` returns `[]`; no crash. Good.
3. **Image URLs**: Post images use absolute URLs (e.g. `https://...`) or relative paths. Relative paths like `/headshots/...` require a `public/` directory or static serving. Blogrip has `public/` for optional assets; users must place images there or use absolute URLs.
4. **Base path**: All routes assume root `/`. No support for subpath deployment (e.g. `/blogrip/`) without code changes.
5. **404 for /blog/**: Trailing slash on `/blog/` may not match `/blog`—Express typically normalizes, but worth noting.
6. **Layout options**: The layout receives `options.config` but the list route passes `sectionLinks` separately; both work. The layout correctly uses `config.sections` when `sectionLinks` not in options.

### Edge Cases

- **Malformed frontmatter**: `parseFrontmatter` returns `{ meta: {}, body: raw }` when no `---` match; post gets slug from filename, title from first H1 or "Untitled".
- **Duplicate slugs**: If two files have same slug, `loadPost` returns first match. No deduplication.
- **Section key normalization**: `sectionFromSlug` uses keyword matching; custom sections from frontmatter use `normalizeSectionKey`. Consistent.

### Recommendations

- Add `.gitignore` in blogrip if it should exclude `node_modules`, `content/blog/*.md` (user content), or logs.
- Document that `public/` is for static assets (favicon, images referenced by relative path).
- Consider adding a simple `/blog/about` static page option in config for "About" link.

## Feature Analysis (Iteration 2)

### After First Pass

- Section label lookup from config: implemented.
- No other code changes needed from iteration 1.

### Additional Considerations

1. **Port conflict**: Default 3080 may conflict with other services. Config allows `PORT` env override.
2. **Hot reload**: No file watcher; adding/editing posts requires server restart. Acceptable for simple blog.
3. **Caching**: Posts are loaded on every request (no in-memory cache). For large blogs, consider caching with TTL or file mtime invalidation.
4. **Security**: `escapeHtml` and `escapeXml` used throughout; markdown output from `marked` may contain HTML. `marked` sanitizes by default in recent versions; verify for XSS.
5. **README**: Documents structure, config, frontmatter, routes. Sufficient for standalone use.

### Final Checklist

- [x] Config supports env overrides
- [x] Section labels from config when available
- [x] Sample welcome post included
- [x] README with quick start
- [x] No BrewLedger-specific dependencies or branding in core
- [x] analysis.md updated with blogrip documentation
