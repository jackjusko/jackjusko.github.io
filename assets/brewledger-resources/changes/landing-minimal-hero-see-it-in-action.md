# Landing: Minimal Hero + See it in Action First

**Date**: 2026-02-13

## Summary
Landing page structure and script were updated to use a minimal hero (no device mockups) and to place the "See it in action" section immediately after the hero as the first content below the fold, with large mobile and desktop mockups and carousels.

## Changes

### Structure
- **Hero**: Single centered column; headline, subline, CTAs (Book a demo, See the platform → `#screenshots`), and pill line (mobile app, desktop console, real-time sync, works offline). No phone or desktop mockups in hero.
- **Section order**: Hero → **See it in action** (#screenshots) → Platform → Benefits → Workflows → Offline → Features → Built for → Pricing → FAQ → Footer.
- **See it in action**: One section containing (1) large mobile phone mockup with 7-slide carousel (prev/next + dots), (2) large desktop browser mockup with 4-slide carousel (dots). Removed the duplicate lower section that had "Scroll up for mobile screenshots" and desktop-only block.

### Navigation
- Nav link **Screens** added as first item, linking to `#screenshots`.

### Script
- Removed hero desktop carousel state and logic: `heroDesktopTrackRef`, `currentHeroDesktopSlide`, `failedHeroDesktopSlides`, `goToHeroDesktopSlide`, `updateHeroDesktopTrack`, and `updateHeroDesktopTrack()` in `onMounted`. Single desktop carousel remains in "See it in action" (`desktopTrackRef`, `currentDesktopSlide`, etc.).

### Documentation
- `analysis.md`: Promotional Landing Page section updated for content order, nav (Screens first), minimal hero description, and screenshot section placement (both mobile and desktop in "See it in action" only).

## Files
- `platforms/console/src/views/Landing.vue` (template + script)
- `analysis.md` (Promotional Landing Page subsection)
