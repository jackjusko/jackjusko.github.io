# Blog visual theme

All blog pages must match the portfolio **homelab shell** on [index.html](../../index.html) — not the light stone style used on project/lab detail pages.

## Required on every blog page

Copy from [templates/post.html](../templates/post.html) or [blog/index.html](../../blog/index.html):

- **Background:** `bg-zinc-950 text-zinc-300`
- **Fonts:** Inter (body) + JetBrains Mono (`.font-mono`) via Google Fonts
- **Borders:** `.cmd-block { border-color: #1e3a2f; }`
- **Headings:** `text-zinc-100` (H1), `text-zinc-100` (H2 in prose)
- **Body copy:** `text-sm leading-relaxed text-zinc-400`
- **Links:** `text-cyan-400 hover:text-cyan-300` (or `hover:text-emerald-400` in nav)
- **Accents:** emerald for prompts/CTAs, cyan for paths and inline links
- **Cards/blocks:** `rounded-lg border cmd-block bg-zinc-900/50` or `bg-zinc-900/60`

## Header pattern

Homelab terminal prompt in header:

```html
<span class="text-zinc-500">jack@homelab</span>:<span class="text-cyan-400">~</span>$
```

Post pages: brand link + `← portfolio` back link to site root.

## Tag chips

```html
<a href="../?tag=TAG" class="rounded border border-zinc-700 px-2 py-0.5 text-xs text-zinc-500 hover:border-emerald-800 hover:text-emerald-400">TAG</a>
```

## Body HTML in posts

Use classes consistent with `.prose-blog` in the template:

- `<p class="…">` — inherits `text-zinc-400` from parent
- `<h2>Section</h2>` — styled by `.prose-blog h2` in template (do not use stone colors)
- Lists: standard `<ul><li>` inside `.prose-blog`

## Do not

- Use `bg-stone-50`, `text-stone-900`, or other stone palette on blog pages
- Omit Inter/JetBrains Mono font imports
- Invent a new layout — extend the existing template only

## Reference files

Before publishing, compare against:

- [blog/index.html](../../blog/index.html) — index layout
- [templates/post.html](../templates/post.html) — post shell
