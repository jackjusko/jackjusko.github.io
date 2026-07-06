# Tools Prerender Re-implementation

## Summary

Re-added Vite prerender for `/tools` routes to restore SEO (crawlers receive full HTML). The plugin was removed when the blog migrated to server-rendered HTML. Only tools routes are prerendered; blog posts are server-rendered and excluded.

## Changes Implemented

### 1. Prerender Plugin (vite.config.js)

- **Package**: `vite-plugin-prerender-esm-fix` (ESM-compatible fork of `vite-plugin-prerender`; original has `require is not defined` with Vite 7)
- **Routes**: `/tools`, `/tools/bbl-to-case`, `/tools/csv-search` (no blog, no landing)
- **Renderer**: Puppeteer with `renderAfterTime: 10000` (10 second wait; no event dispatch)
- **Launch args**: `--no-sandbox`, `--disable-setuid-sandbox`, `--disable-dev-shm-usage`, `--disable-gpu` (helps on some Windows/CI environments)

### 2. No App.vue Changes

Using time-based wait only; no `prerender-ready` event dispatch needed.

### 3. Output

Prerender writes:
- `dist/tools/index.html`
- `dist/tools/bbl-to-case/index.html`
- `dist/tools/csv-search/index.html`

Server already supports this via `STATIC_DIR/tools/index.html` lookup (server.js lines 2278–2290).

## Verification

1. `npm run build` in platforms/console
2. If prerender succeeds: `dist/tools/index.html` etc. exist
3. If Puppeteer fails (e.g. Chrome launch on Windows): build still completes; dist has SPA assets; server falls back to index.html for /tools

## Known Issues

- **Puppeteer/Chrome**: May fail to launch on some Windows setups (`g_initialized_from_accessor`). Try running build on Linux/CI, or ensure Chromium is installed. Build completes either way; only prerendered HTML is missing.
- **Build time**: Prerender adds ~30+ seconds (10s wait × 3 routes + Puppeteer startup).
