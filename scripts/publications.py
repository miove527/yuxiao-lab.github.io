"""Generate the static publication list from data/publications.bib."""
from pathlib import Path
import datetime
import html
import re

import bibtexparser
from bibtexparser.customization import author, convert_to_unicode

ROOT = Path(__file__).resolve().parents[1]


def text(value):
    return html.escape(value)


def date_key(entry):
    value = entry.get('date', entry['year'])
    parts = value.split('-')
    if len(parts) == 1 and entry.get('month'):
        month = entry['month'].strip().lower()[:3]
        month = str(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'].index(month) + 1) if not month.isdigit() else month
        parts.append(month)
    year, month, day = map(int, (parts + ['1', '1'])[:3])
    return datetime.date(year, month, day).isoformat()


def author_html(value, entry):
    names = author({'author': value})['author']
    result = []
    for name in names:
        parts = name.split(', ')
        display = ' '.join(parts[1:] + parts[:1]) if len(parts) > 1 else name
        marker = ('#' if display in entry.get('equal', '').split('; ') else '') + ('*' if display in entry.get('corresponding', '').split('; ') else '')
        result.append(('<u>Yu Xiao</u>' if display == 'Yu Xiao' else text(display)) + (f'<sup>{marker}</sup>' if marker else ''))
    return ', '.join(result)


def render(entry):
    for field in ['title', 'author', 'year']:
        if not entry.get(field):
            raise ValueError(f"{entry['ID']}: missing {field}")
    title = text(entry['title'])
    status = entry.get('status', 'Preprint' if entry['ENTRYTYPE'] == 'unpublished' else 'Published')
    journal = entry.get('journal', entry.get('booktitle', entry.get('publisher', '')))
    citation = entry['year']
    if entry.get('volume'):
        citation += ', ' + entry['volume']
        if entry.get('number'):
            citation += '(' + entry['number'] + ')'
    pages = entry.get('pages', entry.get('eid', ''))
    if pages:
        citation += ': ' + pages.replace('--', '–').replace('-', '–')
    doi = entry.get('doi', '').removeprefix('https://doi.org/').removeprefix('http://dx.doi.org/')
    paper = 'https://doi.org/' + doi if doi else entry.get('url', '')
    links = [(status if status == 'Preprint' else 'Paper', paper), ('Code', entry.get('code', '')), ('Data', entry.get('data', ''))]
    links_html = ''.join(f'<a href="{text(url)}">{label}</a>' for label, url in links if url)
    doi_html = f'<span class="citation-doi"> <a href="{text(paper)}">doi:{text(doi)}</a>.</span>' if doi else ''
    tags = [entry['year'], status] + [s.strip() for s in entry.get('keywords', '').split(',') if s.strip()]
    tags_html = ''.join(f'<span class="tag">{text(tag)}</span>' for tag in tags)
    summary = entry.get('summary', '')
    summary_html = f'<p class="publication-summary">{text(summary)}</p>' if summary else ''
    featured = ' class="featured-publication"' if entry.get('highlight', '').lower() == 'true' else ''
    return f'''        <li{featured} data-published="{date_key(entry)}" data-status="{text(status.lower())}" data-year="{text(entry['year'])}">
          <div class="publication-tags">{tags_html}</div>
          <h2 class="publication-title">{title}</h2>
          <p class="citation">{author_html(entry['author'], entry)}. <span class="citation-title">{title}. </span><strong><em>{text(journal)}</em></strong>, {text(citation)}.{doi_html}</p>
          {summary_html}
          <div class="publication-links">{links_html}</div>
        </li>'''


def default_order(entries):
    highlights = [entry for entry in entries if entry.get('highlight', '').lower() == 'true']
    highlights.sort(key=date_key, reverse=True)
    others = [entry for entry in entries if entry.get('highlight', '').lower() != 'true']
    preprints = [entry for entry in others if entry.get('status', 'Preprint' if entry['ENTRYTYPE'] == 'unpublished' else 'Published').lower() == 'preprint']
    return highlights + preprints + [entry for entry in others if entry not in preprints]


def publication_html(root=ROOT):
    parser = bibtexparser.bparser.BibTexParser(common_strings=True)
    parser.customization = convert_to_unicode
    database = bibtexparser.loads((root / 'data/publications.bib').read_text(encoding='utf-8'), parser=parser)
    ids = [entry['ID'] for entry in database.entries]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate BibTeX citation keys')
    if not ids:
        raise ValueError('No BibTeX entries found')
    body = '<!-- publications:start -->\n      <ol class="publication-list">\n'
    body += '\n'.join(render(entry) for entry in default_order(database.entries))
    body += '\n      </ol>\n      <!-- publications:end -->'
    years = sorted({int(entry['year']) for entry in database.entries}, reverse=True)
    return body, years
