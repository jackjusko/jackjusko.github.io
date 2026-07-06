# Ahrefs Analytics on Desktop Console and Blog

## Summary
Added Ahrefs Web Analytics script so traffic is tracked on every page of the desktop console and all server-rendered blog routes.

## Implementation

### Console SPA
- **File**: `platforms/console/index.html`
- **Change**: Inserted `<script src="https://analytics.ahrefs.com/analytics.js" data-key="sgzRwL9OZ84glKY+yJ5nhA" async></script>` in the `<head>` section, after the Schema.org JSON-LD block.
- **Scope**: Console is a Vue SPA; `index.html` is the single HTML entry point, so the script loads on all SPA routes (landing, dashboard, settings, `/blog/subscribe`, etc.).

### Server-rendered blog
- **File**: `server/templates/blog-layout.js`
- **Change**: Inserted the same Ahrefs script in the shared layout `<head>`, after the articleSchema block.
- **Scope**: All blog routes served by `server/routes/blog.js` use this layout: `/blog`, `/blog/about`, `/blog/section/:key`, `/blog/:slug`.

## Considerations
- Script loads asynchronously (`async`) so it does not block page rendering.
- No changes to mobile app (`platforms/brewledger-app/`); analytics applies to desktop console and blog only.
- `data-key` is the Ahrefs site key; rotate if compromised.
