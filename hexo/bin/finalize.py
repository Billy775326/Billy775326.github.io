"""Preserve site conventions after Hexo renders; never edits source or article bodies."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from html import escape
from urllib.parse import quote, unquote
import json, re, xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as B

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
BASE = 'https://iowill.com'
posts = json.loads((ROOT / '.cache/posts.json').read_text(encoding='utf8'))
lookup = {'/' + p['path'].removesuffix('index.html'): p for p in posts}
updated = json.loads((ROOT / 'source/_data/site.json').read_text(encoding='utf8'))['updated_at']
footer = (ROOT / 'migration/footer.html').read_text(encoding='utf8')
footer = re.sub(r'2023[–-]\d{4}', '2023–' + updated[:4], footer)
author = {'@type': 'Person', '@id': BASE + '/#author', 'name': 'Billy', 'url': BASE + '/', 'sameAs': ['https://github.com/Billy775326']}

def meta(s, key, value, prop=False):
    attr = 'property' if prop else 'name'
    node = s.find('meta', attrs={attr: key})
    if node is None:
        node = s.new_tag('meta', attrs={attr: key}); s.head.append(node)
    node['content'] = value

def navlink(p, rel):
    label = '上一篇' if rel == 'prev' else '下一篇'
    url = '/' + p['path'].removesuffix('index.html')
    return f'<a class="pagination-related" href="{escape(url)}" rel="{rel}" title="{escape(p["title"])}" aria-label="{label}：{escape(p["title"])}"><img class="cover" loading="lazy" src="{escape(p["thumbnail"])}" alt="{escape(p["title"])}"><div class="info"><div class="info-1"><div class="info-item-1">{label}</div><div class="info-item-2">{escape(p["title"])}</div></div><div class="info-2">阅读全文：{escape(p["title"])}</div></div></a>'

for file in PUBLIC.rglob('*.html'):
    if file.relative_to(PUBLIC).parts[0] == 'legacy-html': continue
    raw = file.read_text(encoding='utf8'); s = B(raw, 'html.parser')
    if not s.head: continue
    # Upstream inject helpers emit spaces on empty JavaScript lines. Normalize
    # only head scripts; historical article/code whitespace stays untouched.
    for script in s.head.select('script'):
        if script.string:
            script.string = '\n'.join(line.rstrip() for line in script.string.split('\n'))
    rel = file.relative_to(PUBLIC).as_posix()
    url = '/' + rel.removesuffix('index.html')
    canonical = BASE + quote(url, safe='/')
    c = s.select_one('link[rel=canonical]')
    if c: c['href'] = canonical
    meta(s, 'og:url', canonical, True)
    f = s.select_one('#footer')
    if f: f.replace_with(B(footer, 'html.parser'))
    for t in s.select('time[datetime]'):
        if t.find_parent(id='article-container'): continue
        d = datetime.fromisoformat(t['datetime'].replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=8)))
        t.string = d.strftime('%Y-%m-%d %H:%M:%S' if t.find_parent(id='post-info') else '%Y/%m/%d %H:%M:%S')
        t['title'] = t.string
    for c in s.select('.recent-post-item'):
        for n in c.select('.article-meta-label'): n.decompose()
        category = c.select_one('a.article-meta__categories')
        if category:
            category.parent['class'] = ['article-meta__categories']
            category.attrs.pop('class', None)
    # Use thumbnails only in list/navigation regions, never replace content images or OG covers.
    for a in s.select('.post_cover a, .aside-list-item a.thumbnail, a.article-sort-item-img'):
        p = lookup.get(unquote(a.get('href', '')))
        if p and a.img: a.img['src'] = p['thumbnail']
    last = s.select_one('[data-lastpushdate]')
    if last: last['data-lastpushdate'] = updated
    for schema in s.select('script[type="application/ld+json"]'):
        try: data = json.loads(schema.string or '')
        except ValueError: continue
        if data.get('@type') == 'BlogPosting' and url in lookup:
            p = lookup[url]
            data.update({'@id': canonical + '#article', 'url': canonical, 'description': p['description'], 'author': author, 'publisher': author, 'inLanguage': 'zh-CN', 'mainEntityOfPage': {'@type': 'WebPage', '@id': canonical}, 'isPartOf': {'@type': 'WebSite', '@id': BASE + '/#website'}, 'articleSection': p['categories'][0]['name'], 'keywords': [t['name'] for t in p['tags']]})
        elif data.get('@type') == 'WebSite': data.update({'@id': BASE + '/#website', 'author': author, 'url': BASE + '/', 'inLanguage': 'zh-CN'})
        schema.string = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    if url in lookup:
        p = lookup[url]
        meta(s, 'description', p['description']); meta(s, 'og:description', p['description'], True)
        meta(s, 'keywords', ','.join(t['name'] for t in p['tags']))
        meta(s, 'twitter:card', 'summary_large_image')
        nav = s.select_one('#pagination')
        targets = [(lookup[n['url']], n['rel']) for n in p['related_nav'] if n['url'] in lookup and n['rel'] in ['prev', 'next']]
        if not targets:
            i = posts.index(p)
            if i + 1 < len(posts): targets.append((posts[i + 1], 'prev'))
            if i > 0: targets.append((posts[i - 1], 'next'))
        if nav:
            nav.clear(); nav['aria-label'] = '文章导航'
            for target, direction in targets: nav.append(B(navlink(target, direction), 'html.parser'))
    if rel == 'about/index.html':
        for old in s.select('script[type="application/ld+json"]'):
            if '"AboutPage"' in (old.string or ''): old.decompose()
        sc = s.new_tag('script', attrs={'type': 'application/ld+json'})
        sc.string = json.dumps({'@context': 'https://schema.org', '@type': 'AboutPage', 'url': canonical, 'name': '关于 Billy', 'inLanguage': 'zh-CN', 'mainEntity': author}, ensure_ascii=False)
        s.head.append(sc)
    file.write_text(str(s), encoding='utf8', newline='\n')

for name, text in json.loads((ROOT / 'migration/redirects.json').read_text(encoding='utf8')).items():
    p = PUBLIC / name
    if not p.exists(): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding='utf8')

# The installed sitemap plugin supplies post/taxonomy entries; supplement archive/pagination URLs.
# Strip build-time lastmod on non-articles: a rebuild is not an editorial change.
ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'; ET.register_namespace('', ns)
tree = ET.parse(PUBLIC / 'sitemap.xml'); root = tree.getroot(); entries = {}
for node in list(root):
    loc = node.find('{' + ns + '}loc')
    if loc is not None: entries[loc.text.rstrip('/') + '/'] = node
for p in PUBLIC.rglob('index.html'):
    if p.relative_to(PUBLIC).parts[0] == 'legacy-html': continue
    raw = p.read_text(encoding='utf8')
    if 'http-equiv="refresh"' in raw: continue
    suffix = p.parent.relative_to(PUBLIC).as_posix()
    loc = BASE + ('/' if suffix == '.' else '/' + quote(suffix, safe='/') + '/')
    if loc not in entries:
        node = ET.SubElement(root, '{' + ns + '}url'); ET.SubElement(node, '{' + ns + '}loc').text = loc; entries[loc] = node
for loc, node in entries.items():
    p = lookup.get(unquote(loc.removeprefix(BASE)))
    for lm in list(node.findall('{' + ns + '}lastmod')): node.remove(lm)
    if p: ET.SubElement(node, '{' + ns + '}lastmod').text = p['updated']
    node.find('{' + ns + '}loc').text = loc
ET.indent(tree); tree.write(PUBLIC / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
(PUBLIC / '.nojekyll').write_text('', encoding='utf8')
# searchdb concatenates root + explicit permalink paths; collapse duplicate slashes
# in entry URLs only, leaving article HTML/CDATA and external image URLs untouched.
search = PUBLIC / 'search.xml'
text = search.read_text(encoding='utf8')
text = re.sub(r'<url>/+([^<]*)</url>', lambda m: '<url>/' + m[1] + '</url>', text)
search.write_text(text, encoding='utf8', newline='\n')
print(f'Finalized {len(posts)} posts and {len(entries)} sitemap URLs')
