"""Check generated pages and local references before deployment."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys
import re


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ['src', 'href'] and value:
                url = urlsplit(value)
                if not url.scheme and not url.netloc and url.path:
                    self.paths.append(unquote(url.path))


def check(root):
    for name in ['index', 'research', 'publications', 'software', 'people', 'teaching', 'gallery']:
        path = root / (name + '.html')
        page = path.read_text(encoding='utf-8')
        if '{{' in page:
            raise ValueError(f'{path}: unresolved template field')
        parser = References()
        parser.feed(page)
        for reference in parser.paths:
            if not (root / reference).is_file():
                raise ValueError(f'{path}: missing {reference}')
    css = root / 'assets/styles.css'
    for reference in re.findall(r'url\("([^"]+)"\)', css.read_text(encoding='utf-8')):
        if not (css.parent / reference).is_file():
            raise ValueError(f'{css}: missing {reference}')
    print('Checked seven pages: no unresolved template fields or missing local files.')


if __name__ == '__main__':
    check(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'site')
