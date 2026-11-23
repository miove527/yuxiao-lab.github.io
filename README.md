# Xiao Lab Website

Website for Xiao Lab, Department of Chemistry, Fudan University.

[Lab website](https://yuxiaolab.com/) · [Fudan faculty profile](https://chemistry.fudan.edu.cn/0c/af/c45141a724143/page.htm)

The site has seven pages: Home, Research, Publications, Software, People, Teaching
and Gallery. It uses static HTML, shared CSS and a small JavaScript file. News,
publications, patents, people, software, courses and gallery entries are maintained
as data and rendered into HTML by a Python build script.

## Design and implementation handoff

See [docs/site-handoff.md](docs/site-handoff.md) for architecture, page design,
responsive behavior, build/deployment decisions and extension guidance.

## For AI Agents

Read [AGENTS.md](AGENTS.md) and [docs/agent-updates.md](docs/agent-updates.md) before
updating information. The latter covers News, Publications, Patents, People,
Software, Teaching and Gallery.

1. Read the user's requested changes and the relevant source data. Update those
   files rather than manually changing generated HTML.
2. Verify new publication metadata and links against the publisher, DOI, PubMed or
   preprint source. Keep full author lists and distinguish preprints, accepted
   manuscripts and published articles. Update an existing record rather than
   duplicating the same work.
3. Use supplied member, course and activity information. Use enrollment_year for automatic September-based student years; do not
   invent missing contact details or publish prepared software
   records without instruction. Put new files in the matching asset directory.
4. Run `python scripts/build_site.py`, `python scripts/check_site.py` and
   `git diff --check`. If JavaScript changes, also run `node --check site/assets/site.js`.
   Inspect the source and generated-page diffs for unintended information changes.
5. Report what changed, what was checked and any missing information. Commit,
   push, PR creation and deployment follow the user's authorization for the task.

Useful publication fields include `date` for publication-date sorting,
`highlight = {true}`, `status`, `keywords`, `summary`, `code` and `data`. Teaching
records support separate semester offerings and resource lists; News uses a
configurable display limit. Detailed schemas belong in the update guide, so this
README remains the entry point rather than a second copy of those instructions.

## Update information

| Content        | Source                    | Routine update                                                                        |
| -------------- | ------------------------- | ------------------------------------------------------------------------------------- |
| News & Updates | `data/news.json`        | Add a dated item; set `limit` to the number of recent items to display.             |
| Publications   | `data/publications.bib` | Append a BibTeX entry, or update the existing entry when a preprint is published.     |
| Patents        | `data/patents.json`     | Update inventors, application/publication numbers and source links.                   |
| PI and members | `data/people.json`      | Update the PI profile, member groups, roles, contact details and photos.              |
| Software       | `data/software.json`    | Add tool information.                                                                 |
| Teaching       | `data/teaching.json`    | Add courses, semester offerings, syllabus links, materials and assignment guidelines. |
| Gallery        | `data/gallery.json`     | Add an activity caption and its images.                                               |

See [the information-update guide](docs/agent-updates.md) for field definitions and
examples. Edit the data source, then regenerate the corresponding HTML. Research
content is maintained directly in `templates/research.html`.

## Build and preview

Use Python 3.12, matching the GitHub Actions environment. From the repository root:

```sh
python -m pip install -r requirements.txt
python scripts/build_site.py
python scripts/check_site.py
python -m http.server 8000 --directory site
```

Open [localhost:8000](http://localhost:8000). The generated HTML files in `site/` can also be
opened directly in a browser. Python and bibtexparser are needed only to regenerate
pages; the published website has no package or server runtime requirements.

For a local update, include the changed data, any new assets and the regenerated
HTML in the same commit. To build the deployment directory instead:

```sh
python scripts/build_site.py --output _site
python scripts/check_site.py _site
```

## Repository structure

```text
data/                     BibTeX and JSON content
templates/                Seven page sources
scripts/                  Build, publication rendering and reference checks
docs/agent-updates.md      Information-update guide for AI agents
AGENTS.md                 Agent entry point
site/
  *.html                  Seven generated pages
  assets/                 backgrounds, icons, research, people, gallery,
                          software, teaching, shared styles and JavaScript
  .nojekyll
.github/workflows/        Build, validation and Pages deployment
```

Local `test/`, `tests/`, `_site/`, Python caches and `.venv/` are ignored by Git.

## GitHub Actions

- Pull requests build and validate the website without deploying it.
- Pushes to `main`, and manual workflow runs on `main`, build and deploy to GitHub Pages.
- GitHub Pages must be configured to use **GitHub Actions** as its deployment source.

The workflow installs the build dependency, generates `_site/`, checks local
references and JavaScript syntax, then uploads the Pages artifact. Only website
HTML, assets, `.nojekyll` and an optional `CNAME` are published. Source data,
templates, scripts, documentation and local tests are excluded from the artifact.

Actions rebuilds from source data and does not commit generated HTML back to the
repository. A data-only edit made on GitHub therefore updates the deployed site;
run the build locally after pulling such edits to refresh local HTML snapshots.

Student records can use `enrollment_year`; Year X advances every September 1
in Asia/Shanghai. Before enrollment, Expected YEAR is displayed automatically.
Student years and Expected YEAR are calculated only during the Python build.
The September Actions schedule rebuilds and deploys static HTML; visitors perform
no student-year calculations. Local previews reflect the last local build date.
