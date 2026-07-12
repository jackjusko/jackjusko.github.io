---
name: portfolio-blog
description: >-
  Turn Jack Jusko's brain dumps into first-person, SEO-optimized blog posts on
  jackjusko.github.io. Creates blog/{slug}/index.html, updates posts.json and
  sitemap.xml, applies home-funnel CTAs back to the portfolio, and fixes
  structure when suitable. Use when asked to write a blog post, publish writing,
  or turn notes into a post for this portfolio site.
---

# Portfolio blog publisher

Publish first-person posts to this static site’s `/blog/` section. Primary goal: useful articles that send readers back to the portfolio home.

## When to use

- User dumps thoughts and wants a blog post
- User says “publish this to my blog” or “write a post from what I said”
- User wants SEO-optimized writing added to `blog/`

## Before writing

Read these references in order:

1. [references/voice.md](references/voice.md) — first-person editing rules
2. [references/theme.md](references/theme.md) — homelab dark theme (required; match blog/index.html)
3. [references/post-seo.md](references/post-seo.md) — title, meta, JSON-LD, file updates
4. [references/home-funnel.md](references/home-funnel.md) — required CTAs to portfolio home

If available, also read `~/.cursor/skills/first-person-enthusiast-writer/ai-patterns.md` and run an anti-AI pass before shipping.

## Publish workflow

### Step 1 — Intake

- Capture the user’s raw text as source material
- Note tone (casual vs formal) and preserve it

### Step 2 — Shape the post

- Choose a clear title and kebab-case slug (check `blog/posts.json` for collisions)
- Write lede + H2 sections from the dump
- Assign 2–5 tags
- Fix structure and grammar; correct facts only per voice.md
- Split body for mid-article CTA: content before / after the funnel block

### Step 3 — SEO and theme

- Meta description 140–160 chars
- Use [templates/post.html](templates/post.html) as-is for layout and theme — **do not switch to stone/light styling**
- Fill all placeholders:
  - `{{TITLE}}`, `{{SLUG}}`, `{{DESCRIPTION}}`
  - `{{DATE_ISO}}` (YYYY-MM-DD), `{{DATE_DISPLAY}}` (e.g. July 11, 2026)
  - `{{KEYWORDS}}` (comma-separated tags)
  - `{{TAG_CHIPS}}` — `<a href="../?tag=…" class="rounded border border-zinc-700 px-2 py-0.5 text-xs text-zinc-500 hover:border-emerald-800 hover:text-emerald-400">tag</a>` per tag
  - `{{BODY_HTML}}` and `{{BODY_CONTINUATION_HTML}}`

### Step 4 — Ship files

1. Write `blog/{slug}/index.html`
2. Append to `blog/posts.json` (keep valid JSON array, newest entries can be appended; index sorts by date)
3. Add `<url>` block to root `sitemap.xml` with today’s `lastmod`
4. Do not edit the plan file or unrelated pages

`blog/index.html` and home `#latest-writing` load from `posts.json` automatically.

### Step 5 — Confirm to user

Report:

- Published URL: `https://jackjusko.github.io/blog/{slug}/`
- Title, date, tags
- One-line summary of structural/factual edits made
- Any flagged corrections or removed unsupported claims

## Site constants

- **Base URL:** `https://jackjusko.github.io`
- **Author:** Jack Jusko — Software, AI & Cybersecurity Engineer
- **Default OG image:** `/assets/images/JackJusko.jpg`
- **Portfolio home:** `/` (use `../../` from post pages)

## Template body HTML

Use semantic HTML in body placeholders:

```html
<p>…</p>
<h2>Section title</h2>
<ul><li>…</li></ul>
```

Match the homelab theme per [references/theme.md](references/theme.md): zinc background, emerald/cyan accents, `.prose-blog` body classes. Do not add extra CSS unless the template is updated site-wide.

## Do not

- Add categories or category URLs
- Skip home funnel blocks
- Use stone/light theme on blog pages
- Invent experience not in the user’s dump
- Use `index.html` in public URLs (directory form only)
- Commit unless the user asks
