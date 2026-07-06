# Landing CTA Revision for Public Launch

## Summary

The desktop landing page was revised to support public launch. Primary CTAs now direct users to register, while "Book a demo" remains available as a secondary option.

## Changes Implemented

### 1. Nav
- **Login**: Replaced "Coming soon" popup with `router-link` to `/login`
- **Get started**: Added primary nav CTA linking to `/register`

### 2. Hero Section
- **Primary CTA**: "Get started for free" → `/register`
- **Secondary CTA**: "See the platform" → `#screenshots` (unchanged)
- **Tertiary**: "Book a demo" as underlined text link (opens contact form)

### 3. Pricing Section
- "Get started" button now links to `/register` instead of opening contact form
- Added "or Book a demo" text link below the button

### 4. Footer CTA
- Copy updated to: "Get started for free today, or book a demo for a guided walkthrough."
- **Get started for free** (primary) and **Book a demo** (secondary) buttons

### 5. Removed
- "Coming soon" popup (no longer needed; Login routes to `/login`)
- `showComingSoon` ref and associated Teleport block

## Files Modified

- `platforms/console/src/views/Landing.vue`
- `analysis.md` (Promotional Landing Page section)

## Feature Analysis (Iteration 1)

**Potential issues considered:**
- Authenticated users visiting `/` are redirected to `/dashboard` by the router guard—no change required
- All `router-link` components use client-side navigation; no full page reloads
- Contact form (Book a demo) still posts to Discord webhook—unchanged
- Responsive layout preserved with existing flex/gap classes

**Edge cases:**
- Users with expired trial or cancelled subscription hitting `/register`—router allows it; they can create new org or will hit billing flow after signup
- Deep links to `/` when authenticated—redirect to dashboard works as before

## Feature Analysis (Iteration 2)

**Additional considerations:**
- SEO: Register and login are now reachable from landing; no impact on crawlability (these are auth pages)
- Accessibility: `router-link` renders as `<a>` with proper href; screen readers get correct semantics
- Mobile nav: "Get started" may need to be visible in mobile hamburger if one exists—Landing uses fixed nav with `hidden md:flex` for main links; the CTA buttons use `flex items-center gap-3` and show on all breakpoints
