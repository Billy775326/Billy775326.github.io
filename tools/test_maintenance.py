"""Run the maintenance pipeline in an isolated copy, preserving the live files."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,tempfile
from urllib.parse import unquote
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as B

ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='blog-maintenance-') as temp:
    root=Path(temp)
    for name in ['blog','tags','categories','page','archives','legacy-html','content','tools','about']:
        shutil.copytree(ROOT/name,root/name,ignore=shutil.ignore_patterns('__pycache__'))
    for name in ['index.html','search.xml','sitemap.xml','robots.txt']:
        shutil.copy2(ROOT/name,root/name)
    before={p.relative_to(root):B(p.read_text(encoding='utf8'),'html.parser') for p in root.rglob('*.html')}
    def run(script):subprocess.run([sys.executable,str(root/'tools'/script)],cwd=root,check=True,stdout=subprocess.PIPE)
    run('rebuild_taxonomy.py');run('update_footer_seo.py');run('verify_taxonomy.py')
    for rel,old in before.items():
        new=B((root/rel).read_text(encoding='utf8'),'html.parser')
        info=new.select_one('.card-webinfo')
        if info:
            assert info.select_one('.item-count').text.strip()==str(len(json.loads((root/'content/taxonomy.json').read_text(encoding='utf8'))['posts']))
            assert info.select_one('[data-lastpushdate]')['data-lastpushdate']==json.loads((root/'content/site-info.json').read_text(encoding='utf8'))['updated_at']
        for selector in ['#article-container','.post-title','#post-info .post-meta-date','.card-recent-post','#footer']:
            assert str(old.select_one(selector))==str(new.select_one(selector)),(rel,selector)
        if rel.parts[0] in ['tags','categories'] and old.select_one('.article-sort'):
            old_images={a['href']:a.img['src'] for a in old.select('a.article-sort-item-img')}
            new_images={a['href']:a.img['src'] for a in new.select('a.article-sort-item-img')}
            assert old_images==new_images,(rel,'thumbnails')
            assert all(re.fullmatch(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}',t.text) for t in new.select('.article-sort time'))
    urls=[]
    for name,expected in [('index.html',18),('page/2/index.html',18),('page/3/index.html',8)]:
        s=B((root/name).read_text(encoding='utf8'),'html.parser');cards=s.select('.recent-post-item a.article-title')
        assert len(cards)==expected;urls.extend(a['href'] for a in cards)
        for meta in s.select('.recent-post-item .article-meta-wrap'):
            assert len(meta.select('.fa-inbox'))==1,(name,'duplicate category icon')
            assert len(meta.select('.article-meta__categories a'))==1,(name,'category link')
    assert len(set(urls))==44
    ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    for node in ET.parse(root/'sitemap.xml').findall('s:url/s:loc',ns):
        suffix=node.text.removeprefix('https://iowill.com/');p=root/unquote(suffix)/'index.html'
        s=B(p.read_text(encoding='utf8'),'html.parser');assert s.select_one('link[rel=canonical]')['href']==node.text
    hashes={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    run('rebuild_taxonomy.py');run('update_footer_seo.py')
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==v for p,v in hashes.items()),'Pipeline is not idempotent'
print('PASS: isolated pipeline; article/sidebar/footer preservation; thumbnails, date precision, 18/18/8 pagination, canonical/sitemap consistency, idempotence.')
