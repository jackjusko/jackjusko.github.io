# Blog System - Feature Analysis

## Overview

The blog system provides a standalone, public blog within the BrewLedger console application. It is designed to help brewers with practical guides and tips on inventory, par levels, and workflows—positioned as helpful content rather than marketing. The blog has its own layout (no dashboard sidebar), right sidebar with popular posts and CTA, and full SEO support for Google indexing.

## Implementation Summary

### Architecture

- **Location**: `platforms/console/` only
- **Content**: Markdown files in `src/blog/posts/*.md` with YAML frontmatter
- **Loader**: `blogLoader.js` with `import.meta.glob` for build-time inclusion
- **Layout**: Dedicated blog layout in `App.vue` (route meta `isBlog: true`)
- **No backend**: All content is static, bundled at build time

### Key Components

| Component | Purpose |
|-----------|---------|
| `blogLoader.js` | Parses frontmatter, loads all posts, filters popular posts |
| `BlogList.vue` | Index page with article cards |
| `BlogPost.vue` | Single post view with MarkdownRenderer |
| `BlogSidebar.vue` | Popular posts list + About BrewLedger CTA |
| `MarkdownRenderer.vue` | Renders markdown to HTML |

### Routes

- `/blog` → BlogList (public)
- `/blog/:slug` → BlogPost (public)

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| title | Yes | Post title |
| slug | No | URL slug (defaults to filename) |
| date | Yes | Publication date (YYYY-MM-DD) |
| author | No | Author name |
| excerpt | No | Short summary for listings and meta |
| popular | No | `true` to show in sidebar popular list |

### SEO

- Canonical URLs per page via `@vueuse/head`
- Meta descriptions (excerpt for posts, static for index)
- `SITE_BASE_URL` in config.js for prerender/SSR fallback
- App.vue skips head for blog post routes; BlogPost sets its own

## Edge Cases & Considerations

### First Iteration

1. **Missing slug**: blogLoader derives from filename—handles omitted slug
2. **Popular filter**: `popular: true` (YAML) parsed as boolean; empty popular list renders nothing (sidebar section hidden)
3. **Post not found**: BlogPost shows "Post not found" with back link
4. **Loading states**: Both list and post show spinners during load
5. **Router guard**: Auth guard allows `/blog` for both authenticated and unauthenticated users
6. **Markdown XSS**: MarkdownRenderer uses escapeHtml; code blocks preserved safely

### Second Iteration

7. **Vite glob path**: `../blog/posts/*.md` is correct relative to blogLoader location
8. **Multiple useHead**: BlogPost and App.vue both set head; BlogPost overrides for post pages
9. **Sticky sidebar**: `lg:sticky lg:top-8` keeps sidebar visible on long posts
10. **Mobile layout**: Sidebar appears below main content on small screens (flex-col)
11. **Empty popular**: `v-if="popular.length"` hides Popular posts section when none marked
12. **SITE_BASE_URL**: BlogList and BlogPost import for canonical fallback when window undefined

## Constraints & Assumptions

- Blog is console-only; no mobile blog
- Content is static; no CMS or dynamic post creation
- Author manually sets `popular: true` for sidebar curation
- Markdown supports: headers, bold, italic, lists, code, links
- No server-side rendering; canonicals work via client-side @vueuse/head (Google executes JS)

## Documentation

- `src/blog/README.md`: Post format and frontmatter for authors
- `analysis.md`: Blog system section under Multi-Platform Architecture
