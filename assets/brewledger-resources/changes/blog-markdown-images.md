# Blog Markdown Image Support – Feature Analysis

## Summary
Added support for markdown images in the console blog post renderer so authors can use `![alt](url)` in post bodies. Links were already supported.

## Implementation

### MarkdownRenderer.vue
- **Image extraction**: Before HTML escaping, replace `![alt](url)` and `![alt](url "title")` with placeholders and store safe `<img>` HTML. Uses same placeholder pattern as code blocks so escaping does not alter image markup.
- **URL sanitization**: `safeImageUrl(url)` allows only `http://`, `https://`, `/`, `./`, `../` to prevent `javascript:` or `data:` XSS. Invalid URLs are dropped (image not rendered).
- **Output**: `<img src="..." alt="..." loading="lazy" class="markdown-image" />` with escaped `src` and `alt` for HTML safety.
- **Paragraph wrapping**: Standalone image lines are not wrapped in `<p>` (added `<img` to block-element check).
- **Styles**: `.markdown-image` gets `max-width: 100%`, `height: auto`, `border-radius`, `margin`, `display: block`.

### BlogPost.vue
- **Styles**: Blog-post scoped overrides for `img.markdown-image` (border-radius, margin, dark-mode opacity).

## Edge Cases Considered
- **Unsafe URLs**: Replaced with empty string; placeholder removed, so image is omitted.
- **Empty alt**: `![](url)` produces `alt=""` (valid).
- **Optional title**: `![alt](url "title")` parsed; title ignored in output (could add `title` attribute later if needed).
- **Order of operations**: Images processed before `escapeHtml` so raw markdown is matched; placeholders restored after escape so no double-escaping.

## Potential Gaps (First Pass)
- **Relative URLs**: Allowed (`/`, `./`, `../`). For posts built with Vite, `/image.png` resolves to app origin; authors must place assets in `public/` or use full URLs.
- **Broken images**: No fallback UI for 404 or load error; browser shows broken image. Could add `onerror` or wrapper later.
- **Captions**: No markdown syntax for image captions (e.g. figure/figcaption). Out of scope for this change.
- **data: URLs**: Intentionally disallowed by `safeImageUrl` to avoid XSS and large inline payloads.

## Integration
- No router or blogLoader changes; posts are markdown and images are inline syntax.
- Existing posts without images unchanged. New or edited posts can add `![description](https://example.com/image.png)` or relative paths.
- **Documentation**: `platforms/console/src/blog/README.md` updated with an "Images" section (syntax, URL rules, where to put local assets).

## Second pass
- **Broken images**: Still no onerror fallback; v-html prevents binding Vue handlers to rendered `<img>`. Acceptable for v1; could add a dedicated image component later if needed.
- **README**: Authors are directed to use `public/` for local images and full URLs for external; relative paths documented.
- **analysis.md**: Blog System section now documents markdown rendering including image support and URL sanitization.
