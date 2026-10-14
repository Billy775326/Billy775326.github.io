"""Regression checks for indexable pages, author metadata and image loading."""
from pathlib import Path
from urllib.parse import unquote
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as B

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
BASE = 'https://iowill.com'


def verify_seo():
    dimensions = json.loads((ROOT / 'source/_data/image-dimensions.json').read_text(encoding='utf8'))
    sitemap = ET.parse(PUBLIC / 'sitemap.xml')
    urls = {unquote(n.text) for n in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
    for file in PUBLIC.rglob('*.html'):
        rel = file.relative_to(PUBLIC).as_posix()
        soup = B(file.read_text(encoding='utf8'), 'html.parser')
        schema_types = []
        for script in soup.select('script[type="application/ld+json"]'):
            data = json.loads(script.string or '')  # Empty/invalid JSON is a build failure.
            assert isinstance(data, dict) and data.get('@type'), ('Invalid schema', rel)
            schema_types.append(data['@type'])
            if data['@type'] in ('BlogPosting', 'WebSite'):
                assert data['author']['url'] == BASE + '/about/', ('Author link', rel)
        if rel == 'index.html':
            assert schema_types.count('WebSite') == 1, ('Missing/duplicate website schema', rel)
        if rel == 'about/index.html':
            assert schema_types.count('AboutPage') == 1, ('Missing/duplicate about schema', rel)
        if rel.startswith('legacy-html/'):
            robots = soup.select_one('meta[name=robots]')
            assert robots and 'noindex' in robots.get('content', '').lower(), ('Archive indexable', rel)
            assert BASE + '/' + rel not in urls, ('Archive in sitemap', rel)
            continue
        if rel.startswith('blog/'):
            assert schema_types.count('BlogPosting') == 1, ('Missing/duplicate article schema', rel)
            assert len(soup.select('h1')) == 1, ('Article heading hierarchy', rel)
            body = soup.select_one('#article-container')
            for image in body.select('img[src]'):
                size = dimensions.get(image['src'])
                if size:
                    assert (image.get('width'), image.get('height')) == (str(size['width']), str(size['height'])), ('Image dimensions', rel, image['src'])
        for index, image in enumerate(soup.select('#recent-posts .post_cover img')):
            assert image.get('loading') == ('eager' if index < 3 else 'lazy'), ('Card loading', rel, index)
    print('PASS: valid JSON-LD, author links, archive noindex, headings and image hints')


if __name__ == '__main__':
    verify_seo()
