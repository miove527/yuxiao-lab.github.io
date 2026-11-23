# Information updates for AI agents

## Sources and build

Read the user's request and the relevant data before editing. Maintain information
in these files:

| Content | Source |
| --- | --- |
| News | `data/news.json` |
| Publications | `data/publications.bib` |
| Patents | `data/patents.json` |
| PI and members | `data/people.json` |
| Software | `data/software.json` |
| Teaching | `data/teaching.json` |
| Gallery | `data/gallery.json` |

Page sources live in `templates/`. Build results and publishable assets live in
`site/`. Do not edit generated HTML directly. Research content is maintained in
`templates/research.html`. Keep existing records unless removal is requested.

## News

`news.json` contains a positive integer `limit` and an `items` array. Each item
has `date` (YYYY-MM-DD), `title`, `url` and optional `description`. The newest
`limit` records are displayed. Keep older records in the data. Use actual event
or publication dates rather than guessed dates.

## Publications and patents

Append standard BibTeX entries with unique keys, `title`, `author` and `year`.
Use `and` between authors and retain complete author lists. Verify author identity,
title, journal, year, volume, issue, pages/article number and DOI against publisher,
PubMed or preprint records. Update an existing preprint when it is published.
Do not invent unassigned volume/issue/pages or duplicate versions of the same work.

Supported standard fields include `journal`, `volume`, `number`, `pages`, `eid`,
`doi`, `url`, `year` and `month`. Additional fields:

- `date`: first public/online publication date, preferably YYYY-MM-DD. Sorting
  falls back to year/month, using January/day 1 for unknown components.
- `status`: Published, Preprint or Accepted. Default: Published; `@unpublished`
  defaults to Preprint.
- `highlight`: true or false; default false. Change only when requested.
- `keywords`: comma-separated tags; `summary`: optional short, supported account.
- `code`, `data`: verified URLs; omit when unavailable.
- `equal`, `corresponding`: names separated by `; `, matching displayed authors.

Patents use `authors`, `year`, `title`, `application`, `publication` and `url`.
Distinguish application numbers, publication numbers and granted status.

## People

`pi` contains `name`, `lines`, `history`, `email` and `image`. Each `lines` item
is a string or an object with `text` and `url`. Each history item contains
`period` and `description`.

`groups` contains ordered groups with `name` and `members`. A member has `name`,
`role`, `image`, optional `email`, optional `details` (text array), and optional
integer `enrollment_year`. Keep role separate from the computed year:

```json
{
  "name": "New Member",
  "role": "Ph.D. student",
  "enrollment_year": 2026,
  "image": "assets/people/member-placeholder.svg",
  "details": []
}
```

Student years are calculated only at build time and advance on September 1 in
Asia/Shanghai. The scheduled Actions build deploys the updated static HTML; do
not add browser-side age/year calculations. Local HTML reflects its build date. September 2026 entrants
are Year 1 until August 31, 2027 and Year 2 from September 1, 2027. Before the
entry date, display Expected YEAR automatically. Do not manually add Year X to
role or Expected YEAR to details. Leave enrollment_year absent when unknown;
do not guess it. Keep graduation/departure changes under explicit user control.
Move members between groups instead of duplicating them. Photos belong in
`site/assets/people/`; data paths remain `assets/people/...`, relative to the site.

## Software

Each entry has `name`, boolean `published`, `status`, `description`, and optional
`logo`, `features`, `publication`, `github`, `documentation`, `version`, `citation`.
`published: false` keeps a prepared card out of the displayed page. Publish only
on instruction. Links can use objects with `text` and `url`; ordinary values can
be strings. Do not invent unpublished names, releases or repositories. Logos go
in `site/assets/software/`.

## Teaching

One record per course: unique `id`, boolean `published`, Chinese `title` (stored
for maintenance), displayed `title_en`, `code`, `credits`, `level`, optional
`language` and `description_en`. Keep all verified historical offerings.

Each `offerings` item has `year`, `term` (Spring, Fall or Summer), optional `role`,
`links`, `materials`, `assignments`. Link objects use `label` and `url`.
Materials are nested under Course materials. Assignment entries are at the same
level as Syllabus and can be text or link objects. Example:

```json
{"label": "Assignment Guidelines", "url": "https://elearning.fudan.edu.cn/"}
```

Public PPT/PPTX, PDF and handouts go in `site/assets/teaching/`; link them with
`assets/teaching/filename.pdf`. Leave empty arrays when resources are unavailable.
Do not create empty download links or copy restricted platform materials without
the user's authorization.

## Gallery

Each record has `caption` and an `images` array. Each image has `src` and `alt`.
Preserve record order. Files go in `site/assets/gallery/`; stored links use
`assets/gallery/...`. Use the supplied placeholder when photos are unavailable.
Do not substitute photos from another event.

## Verification and delivery

From the repository root:

```sh
python -m pip install -r requirements.txt
python scripts/build_site.py
python scripts/check_site.py
git diff --check
python -m http.server 8000 --directory site
```

If JavaScript changes, also run `node --check site/assets/site.js`. Inspect data
and generated-page diffs for lost or unintended information. Check links and
assets. CI builds PRs and deploys main, and regenerates student-year snapshots
each September. It does not commit generated HTML back to the repository.
Include data, assets and generated pages together for local updates. Local tests,
caches and `_site/` are ignored. Commit/push/PR actions require task authorization.
