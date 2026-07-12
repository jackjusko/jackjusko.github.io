# Home funnel — required on every post

**Goal:** Readers finish the article and visit the portfolio home to learn about Jack — projects, labs, experience.

Every post must include all four placements. Do not remove or weaken these for “cleaner” layout.

## 1. Top nav (above the fold)

- Left: **Jack Jusko** → `../../` (site root)
- Right: **← Portfolio** → `../../`

Both links go to the portfolio home.

## 2. Author strip (under H1)

Linked card with photo + title:

- Image: `../../assets/images/JackJusko.jpg`
- Text: **Jack Jusko** — Software, AI & Cybersecurity Engineer
- Whole card links to `../../`

## 3. Mid-article CTA block

Place after the first major section or ~40% through the article — wherever a natural pause exists.

Template copy (adapt slightly per post, keep intent):

> I write about what I build and what I break in the lab. If this was useful, my portfolio has the longer-form project writeups, security labs, and work history.

Button: **See my portfolio →** → `../../`

In `templates/post.html`, split body at this block:
- `{{BODY_HTML}}` — content before CTA
- `{{BODY_CONTINUATION_HTML}}` — content after CTA

If the post is short (< 4 paragraphs), put the mid CTA after paragraph 2 and leave continuation empty or with closing paragraphs only.

## 4. End CTA (after article body)

Different wording from mid CTA — thank the reader, restate who Jack is, link home:

> Thanks for reading. I am Jack Jusko — I build software, work in security, and document both on this site.

Link text: **Back to jackjusko.github.io →** → `../../`

## Blog index

`blog/index.html` uses the homelab dark theme and links **← portfolio** to `../`. Match its header and card styles when updating the index layout.

## What not to do

- Single tiny footer link only
- Linking to GitHub/LinkedIn instead of portfolio as the primary CTA
- “Contact me” as the only conversion path
- Removing author strip to save space
- Stone/light theme on blog pages (see [theme.md](theme.md))
