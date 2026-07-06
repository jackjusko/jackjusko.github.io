# Feature Analysis: Promotional Landing as Console Default View

## Summary
Integrated `index_migrate.html` (the promotional BrewLedger marketing page) into the console app as the default view at `/`. Unauthenticated visitors see the marketing landing page; authenticated users are redirected to the dashboard.

## Implementation Overview

### 1. Landing.vue Component
- **Location**: `platforms/console/src/views/Landing.vue`
- **Content**: Full conversion of index_migrate.html into a Vue SPA component
- **Features preserved**:
  - Hero section with value proposition
  - ROI/Savings section
  - Feature grid (Digital Brew Logs, Inventory Trust, Par Levels, etc.)
  - Batch intelligence spotlight
  - Workflows section
  - Competitor comparison table
  - Pricing cards (Essentials $39, Standard $59, Growth $79)
  - FAQ section
  - CTA/Footer with Book Demo and Get Started
- **Carousel**: 7-slide screenshot carousel with Vue refs, auto-advance (4s), manual prev/next
- **Image fallback**: Placeholder text when screenshots (sc1.png–sc7.png) fail to load
- **Navigation**: Login and Book Demo links in nav; Get Started links to /register

### 2. Router Changes
- **`/`** → Landing (public, `meta.isLanding: true`)
- **`/dashboard`** → Dashboard (requires auth) — moved from `/`
- **Auth guard behavior**:
  - Authenticated users visiting `/` → redirect to `/dashboard`
  - Authenticated users visiting `/login` or `/register` → redirect to `/dashboard`
  - Unauthenticated users accessing protected routes → redirect to `/login`
- Login and Register success redirects updated to `/dashboard`

### 3. App.vue Layout
- **Conditional rendering**: When `$route.meta.isLanding` is true, render only `<router-view>` (no sidebar, no app chrome)
- **Dashboard path** in nav items updated from `/` to `/dashboard`
- **Logout** redirects to `/` (landing page)

### 4. Static Assets
- **`public/screenshots/`**: Created for sc1.png through sc7.png; carousel images served from `/screenshots/scN.png`
- **Note**: Screenshots must be added manually; `.gitkeep` documents the expected files

### 5. index.html
- Title: "BrewLedger — Inventory you can trust. Built for brew day."
- Inter font via Google Fonts
- Schema.org JSON-LD (SoftwareApplication, Organization, FAQPage)
- Canonical URL, scroll-smooth on html

## Feature Analysis – First Iteration

### Potential Issues

1. **Missing screenshots**: Carousel shows placeholder text if sc1–sc7.png are absent. User must copy from promotional site or provide new assets.

2. **Route meta consistency**: `isLanding` must be set correctly; any new public routes need appropriate meta to avoid layout confusion.

3. **SEO**: Schema and meta are in index.html and apply to all routes. For routes like /dashboard, this is redundant but harmless. Dynamic head per route would require @unhead/vue or similar.

4. **Deep links**: Authenticated users bookmarking `/` will always be redirected to `/dashboard`. Expected.

5. **Mobile responsiveness**: Landing uses responsive classes from original HTML; Tailwind v3 in console should support them. Verify on small viewports.

6. **External links**: Book Demo uses mailto:; CTA links to #cta. All work as expected.

7. **Carousel timer cleanup**: `onUnmounted` clears interval; no memory leaks when navigating away.

### Recommendations
- Add screenshots to `public/screenshots/` before production deploy
- Consider adding a "Back to app" or Dashboard link in landing nav for authenticated users who land on / (currently they're redirected, so low priority)

## Feature Analysis – Second Iteration

### Additional Considerations

8. **Blog integration**: Router includes BlogList/BlogPost. Landing nav does not link to blog. If blog is part of the promotional flow, add a "Blog" or "Resources" nav item.

9. **Dark mode**: Landing uses fixed amber/slate palette. App shell supports dark mode. Landing intentionally uses marketing light theme; no conflict.

10. **Performance**: Landing is a large single component. Lazy-loading Landing.vue would help initial load for users going directly to /login. Trade-off: landing is default, so it loads first regardless.

11. **Broken image handling**: `failedSlides` uses reactive object; Vue tracks new keys correctly with spread in @error handler.

12. **Accessibility**: Anchor links (#roi, #features, etc.) and smooth scroll work. Consider adding skip-to-content for screen readers.

13. **Tailwind purge**: Landing.vue is in `src/` so Tailwind content paths include it. Custom utilities (shadow-[6px_6px_0px_0px_...]) use arbitrary values and are preserved.

### Final Recommendations
- Document screenshot requirements in README or deployment guide
- Optional: Add blog link to landing nav if blog is part of marketing strategy
- No blocking issues identified for merge
