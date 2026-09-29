"""Validate taxonomy coverage, counts, URLs and optional baseline body preservation."""
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote
from bs4 import BeautifulSoup as BS
import json, subprocess, sys, xml.etree.ElementTree as ET
from rebuild_taxonomy import ROOT, region

config=json.loads((ROOT/'content/taxonomy.json').read_text(encoding='utf8'))
posts=config['posts'];groups={'categories':defaultdict(set),'tags':defaultdict(set)}
paths=list((ROOT/'blog').rglob('index.html'))
assert len(paths)==len(posts)
for path in paths:
    raw=path.read_text(encoding='utf8');s=BS(raw,'html.parser');m=posts[path.parent.name]
    url='/'+path.parent.relative_to(ROOT).as_posix()+'/'
    assert [a.text for a in s.select('a.post-meta-categories')]==[m['category']],path
    assert [a.text for a in s.select('.post-meta__tags')]==m['tags'],path
    assert [n['content'] for n in s.select('meta[property="article:tag"]')]==m['tags']
    assert s.select_one('meta[property="article:section"]')['content']==m['category']
    groups['categories'][m['category']].add(url)
    for t in m['tags']:groups['tags'][t].add(url)
    if len(sys.argv)>1:
        old=subprocess.check_output(['git','show',sys.argv[1]+':'+path.relative_to(ROOT).as_posix()],cwd=ROOT).decode('utf8')
        a,b=region(raw,'article','id','article-container');x,y=region(old,'article','id','article-container')
        assert raw[a:b]==old[x:y],('Article body changed',path)
        before=BS(old,'html.parser')
        assert str(s.select_one('.post-title'))==str(before.select_one('.post-title'))
        assert str(s.select_one('#post-info .post-meta-date'))==str(before.select_one('#post-info .post-meta-date'))
for kind,items in groups.items():
    for name,urls in items.items():
        slug=config['categories'][name] if kind=='categories' else config['tag_slugs'].get(name,name)
        path=ROOT/kind/slug/'index.html';s=BS(path.read_text(encoding='utf8'),'html.parser')
        listed=[a['href'] for a in s.select('.article-sort-item-title')]
        assert len(listed)==len(set(listed)) and set(listed)==urls,(name,listed,urls)
        assert str(len(urls))+' 篇' in s.select_one('.article-sort-title').text
for p in ROOT.rglob('*.html'):
    if 'upload' in p.relative_to(ROOT).parts:continue
    s=BS(p.read_text(encoding='utf8'),'html.parser')
    for a in s.select('a[href]'):
        href=unquote(a['href'])
        if href.startswith(('/categories/','/tags/')):
            assert (ROOT/href.strip('/')/'index.html').exists(),(p,href)
    for box in s.select('.site-data'):
        for kind,n in [('archives',len(posts)),('categories',len(groups['categories'])),('tags',len(groups['tags']))]:
            node=box.select_one('a[href="/'+kind+'/"] .length-num')
            assert node and int(node.text)==n,(p,kind)
    for n in s.select('meta[http-equiv="refresh"]'):
        dest=unquote(n['content'].split('url=',1)[1]);target=ROOT/dest.strip('/')/'index.html'
        assert target.exists(),(p,dest)
        assert not BS(target.read_text(encoding='utf8'),'html.parser').select_one('meta[http-equiv="refresh"]'),('Redirect chain',p)
entries=ET.parse(ROOT/'search.xml').findall('entry');assert len(entries)==len(posts)
for e in entries:
    slug=e.findtext('url').rstrip('/').split('/')[-1];m=posts[slug]
    assert [x.text for x in e.findall('categories/category')]==[m['category']]
    assert [x.text for x in e.findall('tags/tag')]==m['tags']
print('PASS: all article bodies/titles/dates preserved (when baseline provided); taxonomy coverage, unique membership, counts, links, redirects and search metadata.')
