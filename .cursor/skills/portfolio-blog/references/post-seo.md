# Post SEO checklist

Use for every published post on `https://jackjusko.github.io`.

## Title and slug

- **Browser title:** `{Post title} | Jack Jusko` (pipe, not dash before name)
- **H1:** Post title only — one H1 per page
- **Slug:** kebab-case, lowercase, no stop words unless needed for clarity (`homelab-wazuh-buffer-tuning` not `homelab-wazuh-buffer-tuning-notes-from-july`)
- **URL:** `https://jackjusko.github.io/blog/{slug}/` (trailing slash)

## Meta description

- 140–160 characters
- First person or direct statement of what the reader gets
- Include a concrete noun (tool, project, problem) when possible
- Do not duplicate the title verbatim

## Open Graph and Twitter

- `og:type` = `article`
- `og:url` and canonical must match
- Default `og:image`: `https://jackjusko.github.io/assets/images/JackJusko.jpg`
- Use a project logo only when the post is primarily about that project and the image exists under `assets/projects/`

## Article JSON-LD

Required fields in `application/ld+json`:

| Field | Source |
|-------|--------|
| `headline` | Post title |
| `description` | Meta description |
| `datePublished` | ISO 8601 date (`YYYY-MM-DD`) |
| `author` | Person: Jack Jusko, url `https://jackjusko.github.io/` |
| `publisher` | Person: Jack Jusko |
| `mainEntityOfPage.@id` | Canonical URL |
| `keywords` | Comma-separated tags |

## Headings and body

- Logical H2 sections; H3 only when a section needs sub-parts
- Short paragraphs; lists when enumerating steps or tools
- Link to related portfolio pages (`/projects/…`, `/labs/…`) when naturally relevant — do not force links

## Files to update on publish

1. Create `blog/{slug}/index.html` from `templates/post.html` (homelab dark theme — see [theme.md](theme.md))
2. Append entry to `blog/posts.json`:
   ```json
   {
     "slug": "example-slug",
     "title": "Post Title",
     "date": "2026-07-11",
     "description": "Meta description text.",
     "tags": ["security", "homelab"]
   }
   ```
3. Add to `sitemap.xml` before `</urlset>`:
   ```xml
   <url>
     <loc>https://jackjusko.github.io/blog/{slug}/</loc>
     <lastmod>YYYY-MM-DD</lastmod>
   </url>
   ```
4. `blog/index.html` loads from `posts.json` automatically — no manual edit unless layout changes
5. Home page `#latest-writing` loads from `posts.json` automatically — no manual edit

## Tags

- 2–5 tags per post, lowercase preferred
- Tags are browse filters, not categories — no tag index pages
- Reuse existing tags when they fit (`security`, `homelab`, `brewing`, `ai`, `career`)
