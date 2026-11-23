"""Build static pages from BibTeX and JSON. No browser-side data loading."""
import argparse
from datetime import datetime, timezone, timedelta
import html
import json
from pathlib import Path
import shutil

from publications import publication_html

ROOT = Path(__file__).resolve().parents[1]


def esc(value):
    return html.escape(str(value), quote=True)


def image(src, alt):
    return f'<img src="{esc(src)}" alt="{esc(alt)}" loading="lazy" decoding="async">'


def student_role(person, today=None):
    role = person['role']
    if 'enrollment_year' not in person:
        return role
    today = today or datetime.now(timezone(timedelta(hours=8))).date()
    academic_year = today.year - (today.month < 9)
    year = academic_year - int(person['enrollment_year']) + 1
    return role + (f', Year {year}' if year > 0 else '')


def people_html(data):
    pi = data['pi']
    lines = ''.join('<p>' + (f'<a class="mentor-link" href="{esc(line["url"])}">{esc(line["text"])} <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3h7v7M21 3 10 14"/><path d="M10 5H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5"/></svg></a>' if isinstance(line, dict) else esc(line)) + '</p>' for line in pi['lines'])
    history = ''.join(f'<p><strong>{esc(item["period"])}</strong><span>{esc(item["description"])}</span></p>' for item in pi['history'])
    pi_html = f'''<article class="mentor-profile">
        <div class="mentor-copy"><p class="eyebrow">Principal investigator</p><h1>{esc(pi['name'])}</h1>
          <div class="mentor-lines">{lines}</div>
          <div class="mentor-history" aria-label="Education and experience">{history}</div>
          <p class="mentor-email">Email: <a href="mailto:{esc(pi['email'])}">{esc(pi['email'])}</a></p>
        </div><figure class="mentor-photo">{image(pi['image'], pi['name'] + ' portrait')}</figure>
      </article>'''
    groups = []
    for group in data['groups']:
        members = []
        for person in group['members']:
            details = ''.join(f'<p>{esc(detail)}</p>' for detail in person.get('details', []))
            if 'enrollment_year' in person:
                today = datetime.now(timezone(timedelta(hours=8))).date()
                incoming = today.year - (today.month < 9) < person['enrollment_year']
                if incoming:
                    details += f'<p>Expected {person["enrollment_year"]}</p>'
            email = person.get('email')
            if email:
                details += f'<p class="member-email"><a href="mailto:{esc(email)}">{esc(email)}</a></p>'
            members.append(f'''<article class="member-card">{image(person['image'], person['name'] + ' portrait')}
              <div class="member-copy"><p class="eyebrow">{esc(student_role(person))}</p><h2>{esc(person['name'])}</h2>{details}</div></article>''')
        groups.append(f'<div class="people-group"><div class="people-group-heading"><h3>{esc(group["name"])}</h3></div><div class="people-grid compact-grid">'+ '\n'.join(members) + '</div></div>')
    return pi_html, '\n'.join(groups)


def gallery_html(events):
    return '\n'.join('<figure>' + ''.join(image(photo['src'], photo['alt']) for photo in event['images']) + f'<figcaption>{esc(event["caption"])}</figcaption></figure>' for event in events)


def software_html(tools):
    cards = []
    for tool in tools:
        logo = image(tool['logo'], '') if tool.get('logo') else '<span class="software-mark" aria-hidden="true">S</span>'
        rows = []
        for key, label in [('features', 'Key features'), ('publication', 'Publication'), ('github', 'GitHub'), ('documentation', 'Documentation'), ('version', 'Version / status'), ('citation', 'Citation')]:
            value = tool.get(key)
            if value:
                content = f'<a href="{esc(value["url"])}">{esc(value["text"])}</a>' if isinstance(value, dict) else esc(value)
                rows.append(f'<div><dt>{label}</dt><dd>{content}</dd></div>')
        card = f'<article class="card software-card"><div class="software-heading">{logo}<div><span class="tag">{esc(tool["status"])}</span><h2>{esc(tool["name"])}</h2></div></div><p>{esc(tool["description"])}</p><dl class="software-details">'+''.join(rows)+'</dl></article>'
        if not tool.get('published', False):
            card = '<!-- Unpublished software\n' + card.replace('--', '—') + '\n-->'
        cards.append(card)
    return '\n'.join(cards)


def news_html(data):
    if not isinstance(data['limit'], int) or data['limit'] < 1:
        raise ValueError('news.limit must be a positive integer')
    articles = []
    for item in sorted(data['items'], key=lambda item: item['date'], reverse=True)[:data['limit']]:
        link = f'<a class="news-link" href="{esc(item["url"])}" aria-label="Read: {esc(item["title"])}"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3h7v7M21 3 10 14"/><path d="M10 5H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5"/></svg></a>'
        description = item.get('description')
        title = f'<h3>{esc(item["title"])}{(" " + link) if not description else ""}</h3>'
        body = f'<p>{esc(description)} {link}</p>' if description else ''
        articles.append(f'<article><time datetime="{esc(item["date"])}">{esc(item["date"])}</time>{title}{body}</article>')
    return '\n'.join(articles)


def teaching_html(courses):
    cards = []
    icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3h7v7M21 3 10 14"/><path d="M10 5H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5"/></svg>'
    for course in courses:
        if not course.get('published', False):
            continue
        meta = [course.get('code'), course.get('level')]
        if course.get('credits'):
            meta.append(str(course['credits']) + ' credits')
        if course.get('language'):
            meta.append(course['language'])
        description = []
        for key, label, language in [('description_en', 'Course description', 'en')]:
            if course.get(key):
                description.append(f'<details class="course-description"><summary>{label}</summary><p lang="{language}">{esc(course[key])}</p></details>')
        offerings = []
        for offering in course.get('offerings', []):
            links = ''.join(f'<li><a class="course-link" href="{esc(link["url"])}">{esc(link["label"])} {icon}</a></li>' for link in offering.get('links', []))
            materials = ''.join(f'<li><a class="course-link" href="{esc(item["url"])}">{esc(item["label"])} {icon}</a></li>' for item in offering.get('materials', []))
            if materials:
                links += '<li>Course materials<ul>' + materials + '</ul></li>'
            for item in offering.get('assignments', []):
                assignment = f'<a class="course-link" href="{esc(item["url"])}">{esc(item["label"])} {icon}</a>' if isinstance(item, dict) else esc(item)
                links += '<li>' + assignment + '</li>'
            role = f' · {esc(offering["role"])}' if offering.get('role') else ''
            offerings.append(f'<section class="course-offering"><h3>{esc(offering["term"])} {esc(offering["year"])}{role}</h3><ul class="course-resources">{links}</ul></section>')
        cards.append(f'<article class="card course-card" id="{esc(course["id"])}"><h2>{esc(course["title_en"])}</h2><p class="course-meta">'+ ' · '.join(esc(item) for item in meta if item) + '</p>' + ''.join(description) + ''.join(offerings) + '</article>')
    return '\n'.join(cards)


def build(root=ROOT, output=None):
    output = output or root / 'site'
    output.mkdir(parents=True, exist_ok=True)
    def load(name):
        return json.loads((root / 'data' / (name + '.json')).read_text(encoding='utf-8'))
    pi, groups = people_html(load('people'))
    patents = []
    for item in load('patents'):
        authors = ', '.join('<u>Yu Xiao</u>' if name == 'Yu Xiao' else esc(name) for name in item['authors'])
        patents.append(f'<li>{authors} ({item["year"]}). {esc(item["title"])}. PCT application {esc(item["application"])}. <a href="{esc(item["url"])}">Publication {esc(item["publication"])}</a>.</li>')
    publications, years = publication_html(root)
    replacements = {'TEACHING': teaching_html(load('teaching')), 'NEWS': news_html(load('news')), 'PATENTS': '\n'.join(patents), 'PI': pi, 'PEOPLE': groups, 'GALLERY': gallery_html(load('gallery')), 'SOFTWARE': software_html(load('software')), 'PUBLICATIONS': publications, 'YEARS': ''.join(f'<option value="{year}">{year}</option>' for year in years)}
    for name in ['index', 'people', 'gallery', 'software', 'publications', 'teaching', 'research']:
        page = (root / 'templates' / (name + '.html')).read_text(encoding='utf-8')
        for key, value in replacements.items():
            page = page.replace('{{' + key + '}}', value)
        if '{{' in page:
            raise ValueError(f'Unresolved template field in {name}.html')
        (output / (name + '.html')).write_text(page, encoding='utf-8', newline='\n')
    source = root / 'site'
    if output.resolve() != source.resolve():
        for name in ['.nojekyll', 'CNAME']:
            if (source / name).exists():
                shutil.copyfile(source / name, output / name)
        shutil.copytree(source / 'assets', output / 'assets', dirs_exist_ok=True)
    print(f'Built seven pages in {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Publish only website files to this directory')
    args = parser.parse_args()
    build(output=args.output)
