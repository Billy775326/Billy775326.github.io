"""Check generated pages before they may replace the deployed static tree."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
from datetime import datetime
import json, math, re, xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as B

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
posts = json.loads((ROOT / '.cache/posts.json').read_text(encoding='utf8'))
assert posts
expected = {'/' + p['path'].removesuffix('index.html') for p in posts}
baseline = json.loads((ROOT / 'migration/posts.json').read_text(encoding='utf8'))
lookup = {p['slug']: p for p in posts}
removed_file = ROOT / 'migration/removed-posts.json'
removed = json.loads(removed_file.read_text(encoding='utf8')) if removed_file.exists() else []
removed_slugs = {p['slug'] for p in removed}
assert removed_slugs <= {p['slug'] for p in baseline}, 'Unknown removal record'
for retired in removed:
    assert retired['slug'] not in lookup, ('Deleted article restored', retired['slug'])
    assert not (PUBLIC / retired['url'].lstrip('/') / 'index.html').exists(), retired['url']
for old in baseline:
    if old['slug'] in removed_slugs:
        continue
    assert old['slug'] in lookup, ('Lost article', old['slug'])
    current = lookup[old['slug']]
    assert '/' + current['path'].removesuffix('index.html') == old['url']
    assert datetime.fromisoformat(current['date'].replace('Z', '+00:00')) == datetime.fromisoformat(old['date'].replace('Z', '+00:00'))
    # Imported HTML is kept structurally identical; future edits may remove legacy_html.
    if current['legacy_html']:
        s = B((PUBLIC / current['path']).read_text(encoding='utf8'), 'html.parser')
        assert str(B(s.select_one('#article-container').decode_contents(), 'html.parser')) == str(B(old['body'], 'html.parser')), ('Body changed', current['slug'])
urls = []
for page in range(1, math.ceil(len(posts) / 18) + 1):
    file = PUBLIC / ('index.html' if page == 1 else f'page/{page}/index.html')
    s = B(file.read_text(encoding='utf8'), 'html.parser')
    cards = s.select('.recent-post-item')
    assert len(cards) == min(18, len(posts) - (page - 1) * 18)
    urls += [c.select_one('.article-title')['href'] for c in cards]
    for c in cards:
        assert len(c.select('.fa-inbox')) == 1
        assert re.fullmatch(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}', c.time.text)
assert len(set(urls)) == len(posts) and set(urls) == expected
search = ET.parse(PUBLIC / 'search.xml')
entries = search.findall('entry')
assert len(entries) == len(posts), ('search count', len(entries))
search_urls = {urlsplit(e.findtext('url')).path for e in entries}
assert search_urls == expected
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
sitemap_urls = {unquote(n.text) for n in ET.parse(PUBLIC / 'sitemap.xml').findall('s:url/s:loc', ns)}
for p in posts:
    s = B((PUBLIC / p['path']).read_text(encoding='utf8'), 'html.parser')
    assert s.select_one('.post-meta-wordcount') is not None
    assert s.select_one('meta[name=keywords]')['content'] == ','.join(t['name'] for t in p['tags'])
    url = 'https://iowill.com/' + p['path'].removesuffix('index.html')
    assert unquote(s.select_one('link[rel=canonical]')['href']) == url
    assert url in sitemap_urls
    for group in [p['categories'], p['tags']]:
        for item in group: assert (PUBLIC / unquote(item['path']) / 'index.html').exists(), item
for file in PUBLIC.rglob('index.html'):
    if file.relative_to(PUBLIC).parts[0] == 'legacy-html': continue
    s = B(file.read_text(encoding='utf8'), 'html.parser')
    for a in s.select('a[href]'):
        parsed = urlsplit(a['href'])
        if parsed.netloc and parsed.netloc != 'iowill.com': continue
        href = unquote(parsed.path)
        if not href.startswith('/') or a.find_parent(id='article-container'): continue
        target = PUBLIC / href.lstrip('/')
        assert target.exists() or target.with_suffix('.html').exists(), (file, href)
print(f'PASS: {len(posts)} articles; original bodies/URLs/dates; 18-per-page; search, taxonomy, metadata, internal navigation')
