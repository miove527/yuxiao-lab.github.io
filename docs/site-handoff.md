# Website design and implementation handoff

## Purpose and scope

This is the public website of Xiao Lab, Department of Chemistry, Fudan University.
It presents research, publications, software, people, teaching and lab activities.
The design prioritizes readable scientific information, consistent page geometry
and simple maintenance through source data. The site remains static and can be
opened locally without a backend or a JavaScript build tool.

For routine content changes, use [agent-updates.md](agent-updates.md). This document
explains how the website is assembled and how to extend or modify its behavior.
Read the actual implementation before changing it; this document is a map, not
a substitute for the current source.

## Source ownership and output

```text
data/                 Editorial information: BibTeX and JSON
templates/            Seven HTML page sources
scripts/build_site.py Render data and assemble the publishable site
scripts/publications.py
                      BibTeX parsing and publication markup
scripts/check_site.py Generated-page and local-reference checks
assets/               Maintained images, styles and JavaScript
assets/styles.css     Shared appearance and responsive behavior
assets/site.js        Mobile navigation and publication controls
site/                 Generated HTML and copied assets for local preview
docs/                 Content guide and this implementation handoff
.github/workflows/    PR validation and Pages deployment
```

All seven HTML files in `site/` are generated. Edit their templates or source data,
then rebuild. Maintain original images, styles and JavaScript under `assets/`;
the copies in `site/assets/` are generated and ignored by Git. Research is authored directly in `templates/research.html`; the other
templates contain tokens replaced by rendered data.

Running the build without arguments updates `site/*.html`. With `--output _site`,
it generates pages there and copies source assets plus `.nojekyll` and an optional `CNAME` from `site/`. Data, templates, scripts and docs are not published. Links such as
`assets/people/photo.jpg` are relative to the published site root, although the
file is stored under `assets/people/` in the repository. This preserves
navigation when hosted at a fork's project Pages URL.

## Page responsibilities

| Page | Content and behavior |
| --- | --- |
| Home | Campus hero, research overview, dated News & Updates and recruitment/contact information. News is newest first with a configurable limit. |
| Research | Three research directions with illustrations and explanatory text. Images are shown completely rather than cropped. |
| Publications | One citation list supports simple and card views, sorting, status/year filters, and highlighted entries. Patent records follow the list. |
| Software | Prepared tool records can be kept unpublished. Publishable cards contain tool information and resource links. |
| People | PI profile, two-column desktop member groups and build-time academic-year labels. |
| Teaching | Course cards, optional English descriptions and semester-specific syllabus, materials and assignment links. |
| Gallery | Date-sorted activity records with gathering/outing filtering, two-column desktop layout, one-column mobile layout and an accessible activity photo dialog. |

Navigation order is Home, Research, Publications, Software, People, Teaching,
Gallery. Navigation markup is repeated across templates; update all seven when
adding a page. The active page uses `aria-current="page"`. Shared JavaScript
expects every page to include the navigation button and navigation container.

## Visual system

Use existing CSS variables rather than introducing slightly different colors:

| Token | Value | Role |
| --- | --- | --- |
| `--ink` | `#1a1a2e` | Main text |
| `--muted` | `#6e7491` | Secondary text |
| `--accent` | `#6A5ACD` | Eyebrows, primary controls and emphasis |
| `--accent-dark` | `#584BAA` | Links and publication summaries |
| `--background` | `#f7f9fa` | Shared page background |
| `--surface` | `#ffffff` | Cards |
| `--line` | `#d8d8e8` | Borders and separators |
| `--max` | `1120px` | Content container width |

The body uses an Inter/system sans-serif stack. The PI name deliberately uses
Georgia/Times and a heavier weight. Page titles omit terminal periods; ordinary
sentences retain punctuation. Cards use the existing borders, radii and spacing.
Keep long text and scientific notation readable; publication authors include
underlined Yu Xiao, journal names are bold italic and modification notation uses
superscript characters.

All interior-page eyebrows share the same accent color, left edge and distance
below the navigation bar. `--page-top` is 62px on desktop and 42px at widths up to
900px. Ordinary hero paragraphs must not override eyebrow colors. The default
page background is solid; do not reintroduce page-specific gradient panels.
`scrollbar-gutter: stable` avoids horizontal shifts between short and long pages.

Research, Teaching and Publications use the shared compact intro spacing, with
36px from the last intro line to the first content/control row. Gallery reserves
subtitle space through `.gallery-intro` so its first card row aligns on desktop
without adding dummy text. On small screens, titles wrap naturally; do not force
desktop alignment through fixed heights that clip content.

The body is a minimum-viewport-height flex column and `main` expands, keeping the
footer at the bottom of short pages such as Software. Preserve that behavior when
changing content wrappers.

## Responsive layout and accessibility

The principal breakpoints are 900px and 620px. The desktop navigation becomes an
expandable menu at 900px. Its button updates `aria-expanded`; closed mobile links
are inert, and Escape closes the menu and restores focus. With JavaScript disabled,
the menu remains available through `.no-js` fallback rules.

Member and gallery grids use two columns on desktop and collapse on narrow screens.
PI history uses separate year and description columns so wrapped descriptions
align with their own text. The long institution name in the header may wrap while
leaving room for the menu button. Keep focus indicators, image alternative text,
native select labels and reduced-motion behavior intact.

Use external-link SVGs already present in the implementation for short resource
links. Icon-only news links have descriptive accessible labels. New icons should
not require an icon library. Keep public assets organized by use under
`backgrounds`, `icons`, `research`, `people`, `gallery`, `software` and `teaching`.

## Publication state

Both views operate on the same generated list. Card-only fields are hidden in
simple view through CSS; there is no second data fetch or duplicate citation list.
Default order places highlighted publications first, newest first, followed by all remaining entries in descending publication-date order. Publication-date order uses the generated
`data-published` key. Status and year filters combine rather than replacing each
other. An invalid URL selection falls back to its default option.

Selections are stored in the URL hash, for example
`#view=cards&sort=date&status=published&year=2026`. Changing a select uses
`history.replaceState`, avoiding an extra Back entry for each selection. On load,
`pageshow` and hash changes, controls are restored and applied. This works with
direct local HTML access and preserves selections when returning from a paper.
Retain stable parameter names when modifying the controls.

Highlighted papers use a pale gold border and a purple left edge. `highlight` is
editorial data, not an automatic inference from authorship or publication date. Journal highlights are separate optional linked metadata displayed in both views.
Patent publication links use the same un-underlined external-link icon style as course resources. Paper, Code and Data links are bold. Optional summaries share the Google Scholar
link color and have no colored background.

## Build-time student years

Only Python calculates student years. The browser must not calculate them.
`enrollment_year` is the September entry year; `role` contains the degree/position
without a manually appended year. The current academic start year is the current
Shanghai calendar year, minus one before September. The displayed year is:

```text
academic_start_year - enrollment_year + 1
```

Positive values produce Year 1, Year 2, and so on. Future entrants retain their
role and receive a separate Expected YEAR paragraph. The builder produces final
text, so this works with JavaScript disabled. Do not infer graduation from a high
year number; departure remains an editorial update.

The workflow rebuilds annually at `5 16 31 8 *` UTC, September 1 at 00:05 in
Shanghai. Keep scheduled workflows enabled on the publishing repository. Local
HTML reflects the last local build date; deployment reflects the last successful
Actions build. The schedule rebuilds deployment artifacts, not Git commits.

## Deployment and extending the site

PRs install the Python build dependency, generate `_site/`, check local references
and JavaScript syntax. They do not deploy. Main pushes, manual main runs and the
annual scheduled run build and deploy using the Pages artifact. Only the deploy
job has Pages write and OIDC permissions. Pages must use GitHub Actions as its
source; a repository's About link does not configure hosting.

When adding a page, add its template and, where applicable, its data/rendering
function; update the build list, all navigation blocks, the checker's page list,
README and relevant docs. Do not add a backend, framework or client-side data
fetch merely to expose another static information section.

For a content change, start with the data guide. For a layout change, locate the
shared CSS rule and check other pages that use it. For an interaction change,
update the shared script and test navigation/URL restoration. Avoid editing only
the generated file or compensating for a shared issue with page-specific offsets.

## Verification before handoff

```sh
python -m pip install -r requirements.txt
python scripts/build_site.py
python scripts/check_site.py
python scripts/build_site.py --output _site
python scripts/check_site.py _site
node --check assets/site.js
git diff --check
python -m http.server 8000 --directory site
```

Inspect changed source and generated pages. Check narrow mobile, tablet and desktop
widths; menu open/closed states; empty/unpublished software; expanded course
descriptions; publication filter combinations and Back/reload behavior. Test
student-year boundaries on August 31 and September 1, including future entrants.
Check images and resource links, plus a JavaScript-disabled People page.

The local-reference checker does not validate external services, authenticate
course platforms, assess visual layout or prove a GitHub deployment succeeded.
Record those limits when reporting validation. Local tests and caches are ignored
by Git; CI checks are the tracked scripts and workflow. No deployment success
should be claimed without an observed successful remote run.
