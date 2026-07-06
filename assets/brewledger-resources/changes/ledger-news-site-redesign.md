# The Ledger – News-Site Redesign

## Summary

The Ledger (blog at `/blog`) was redesigned from a blog-style publication into a **news-site experience**: dedicated sections, About and Subscribe pages, a news-style header and footer, and a front page that feels like a publication home rather than an "issue" list.

## Changes Implemented

### 1. Section support (blogLoader)

- **Frontmatter**: Optional `section` field (e.g. `section: Operations`). Normalized to URL-safe key: `operations`, `trends`, `industry`, `best-practices`.
- **Derivation**: When `section` is missing, section is inferred from slug via keyword mapping (e.g. slug containing "cellar", "ttb", "inventory" → operations; "lager", "trend", "sustainability" → trends; "industry", "consolidation" → industry; "getting-started", "welcome" → best-practices).
- **API**: `loadSections()` returns section keys that have at least one post; `loadPostsBySection(sectionKey)` returns posts for that section; `SECTION_LABELS` maps key → display label (Operations, Trends, Industry, Best Practices).

### 2. New routes and views

- **`/blog/about`** – `LedgerAbout.vue`: Static About page for The Ledger and BrewLedger, with "Featured in The Ledger" badge. SEO: title, description, canonical.
- **`/blog/subscribe`** – `LedgerSubscribe.vue`: Subscribe page with CTA and link to `LEDGER_NEWSLETTER_URL`. SEO: title, description, canonical.
- **`/blog/section/:sectionKey`** – `LedgerSection.vue`: Section index; lists posts for that section (from `loadPostsBySection`). Section key normalized; label from `SECTION_LABELS` or derived from key. SEO: dynamic title/description/canonical per section.

Routes are registered **before** `/blog/:slug` so `about`, `subscribe`, and `section/:sectionKey` are not matched as article slugs.

### 3. News-site header (App.vue blog layout)

- **Desktop**: Logo + "The Ledger" branding; nav: Home, Operations, Trends, Industry, Best Practices, About, Subscribe; theme toggle; "BrewLedger →" link.
- **Mobile**: Same nav as a wrap strip below the main header row (Home · Operations · … · About · Subscribe).
- **Footer**: Border-top strip with links (The Ledger, section links, About, Subscribe, Featured badge, BrewLedger, © year). Uses `ledgerSections` (same four sections) and `LedgerFeaturedBadge`.

### 4. Front page (BlogList.vue)

- **Section quick links**: Nav strip "Sections: [Operations] [Trends] [Industry] [Best Practices]" linking to `/blog/section/:key`.
- **Masthead**: Tagline updated to "· News, operations, trends".
- **Newsletter strip**: Full-width CTA block ("Weekly insights", "Subscribe →" to `/blog/subscribe`) between "In focus" and "Latest".
- **Latest**: "In this issue" renamed to "Latest"; same table-of-contents style list.

### 5. Sidebar (BlogSidebar.vue)

- **Sections** block added at top: links to `/blog/section/operations`, etc., using `SECTION_LABELS`.
- **Popular**: Unchanged; still from `popular: true`.
- **Subscribe**: "Subscribe →" now links to `/blog/subscribe` (router-link) instead of external URL.
- **About**: Copy updated to "The Ledger is BrewLedger's editorial arm…"; link "About The Ledger →" to `/blog/about`; "BrewLedger →" to `/` unchanged.

### 6. Article and tools

- **BlogPost.vue**: No structural changes; "Back to The Ledger" still goes to `/blog`.
- **CsvSearch**: Still under blog layout; route unchanged.

## Design decisions

- **Sections**: Fixed set (Operations, Trends, Industry, Best Practices) for nav/footer; section pages filter by key. Posts get section from frontmatter or slug-derived mapping so existing posts populate sections without frontmatter edits.
- **Subscribe**: Dedicated page for clarity and SEO; primary CTA in header and footer; sidebar and front-page strip point to `/blog/subscribe`, which then links out to `LEDGER_NEWSLETTER_URL`.
- **About**: Single About page for The Ledger + BrewLedger + Featured badge; positions The Ledger as a publication with an identity.
- **Footer**: Site-wide footer only in blog layout (not dashboard/landing); reinforces news-site feel and provides section/about/subscribe links.

## SEO and accessibility

- About, Subscribe, and Section pages set title, meta description, and canonical via `@vueuse/head`.
- Header nav uses `aria-label="Main"`; mobile nav is present so section links are available on small screens.
- No new sitemap entries in this change; sitemap can be updated to include `/blog/about`, `/blog/subscribe`, and `/blog/section/*` if desired.

## Possible follow-ups

- Add `/blog/section/*` and `/blog/about`, `/blog/subscribe` to `public/sitemap.xml`.
- Optional: "Latest" or "All" section that shows all posts (e.g. `/blog/section/latest` or keep home as the only unfiltered list).
- Optional: Section-specific RSS or meta tags per section page.
- Optional: Add `section` to more posts via frontmatter for finer control than slug-derived mapping.
