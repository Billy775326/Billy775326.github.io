"""Rebuild curated taxonomy for the existing static Butterfly site.

Run from any directory with Python 3 and beautifulsoup4 installed.
Article bodies are kept byte-for-byte; taxonomy.json is the editable source.
"""
from pathlib import Path
from collections import defaultdict
from urllib.parse import quote, unquote
from html import escape
import json, re
from bs4 import BeautifulSoup as BS

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://billy775326.github.io'
E = lambda x: escape(str(x), quote=True)

def parse(raw): return BS(raw, 'html.parser')
def load(p): return (ROOT/p).read_text(encoding='utf8')
def save(p, raw):
    path=ROOT/p;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(raw,encoding='utf8',newline='\n')

def region(raw, tag, attr, value):
    for m in re.finditer(r'<'+tag+r'\b[^>]*>',raw):
        a=re.search(r'\b'+attr+r'=[\"\']([^\"\']*)[\"\']',m[0])
        if not a or (value not in a[1].split() if attr=='class' else value!=a[1]):continue
        depth=1
        for end in re.finditer(r'</?'+tag+r'\b[^>]*>',raw[m.end():]):
            depth += -1 if end[0].startswith('</') else 1
            if depth==0:return m.start(),m.end()+end.end()
        raise ValueError('Unclosed '+value)
    return None

def replace(raw,tag,attr,value,new):
    bounds=region(raw,tag,attr,value)
    if not bounds:return raw
    a,b=bounds;return raw[:a]+new+raw[b:]

def main():
    config=json.loads(load('content/taxonomy.json'))
    categories=config['categories'];mapping=config['posts']
    def link(kind,name):
        slug=categories[name] if kind=='categories' else config['tag_slugs'].get(name,name)
        return '/'+kind+'/'+quote(slug,safe='')+'/'
    paths=sorted((ROOT/'blog').rglob('index.html'))
    # Preserve each existing page shell and its already optimized card images.
    shells={p.relative_to(ROOT).as_posix():p.read_text(encoding='utf8')
            for kind in ['tags','categories'] for p in (ROOT/kind).rglob('index.html')}
    card_images={}
    for raw in shells.values():
        for a in parse(raw).select('a.article-sort-item-img'):
            img=a.select_one('img')
            if img and a.get('href'):card_images.setdefault(a['href'],img.get('src'))
    assert {p.parent.name for p in paths}==set(mapping),'Taxonomy must cover every post exactly once'
    posts=[];by_cat=defaultdict(list);by_tag=defaultdict(list)
    for p in paths:
        raw=p.read_text(encoding='utf8');s=parse(raw);m=mapping[p.parent.name]
        assert m['category'] in categories and 1<=len(m['tags'])<=6
        assert len(m['tags'])==len(set(m['tags']))
        t=s.select_one('.post-meta-date-created')
        im=s.select_one('meta[property="og:image"]')
        post=dict(m,path=p.relative_to(ROOT).as_posix(),url='/'+p.parent.relative_to(ROOT).as_posix()+'/',title=s.select_one('.post-title').text,date=t['datetime'],display_date=t.text[:10],full_date=t.text,cover=im['content'] if im else '/img/avatar.jpg')
        post['cover']=card_images.get(post['url']) or post['cover']
        posts.append(post);by_cat[m['category']].append(post)
        for tag in m['tags']:by_tag[tag].append(post)
    posts.sort(key=lambda p:(p['date'],p['url']),reverse=True)
    ordered_tags=sorted(by_tag,key=lambda t:(-len(by_tag[t]),t.casefold()))
    catlinks=''.join('<li class="category-list-item"><a class="category-list-link" href="'+link('categories',c)+'">'+E(c)+'</a><span class="category-list-count">'+str(len(by_cat[c]))+'</span></li>' for c in categories)
    asidecats='<ul class="card-category-list" id="aside-cat-list">'+''.join('<li class="card-category-list-item"><a class="card-category-list-link" href="'+link('categories',c)+'"><span class="card-category-list-name">'+E(c)+'</span><span class="card-category-list-count">'+str(len(by_cat[c]))+'</span></a></li>' for c in categories)+'</ul>'
    def cloud(side=False):
        ts=ordered_tags[:20] if side else ordered_tags
        return '<div class="'+('card-tag-cloud' if side else 'tag-cloud-list text-center')+'">'+''.join('<a href="'+link('tags',t)+'" title="'+E(t)+' · '+str(len(by_tag[t]))+' 篇" style="font-size: '+str(round(1+min(len(by_tag[t]),15)*.025,3))+'em;'+('color: #748a9c;' if side else ' background-color: #326e85;')+'">'+E(t)+'</a> ' for t in ts)+('<a href="/tags/">全部标签 →</a>' if side else '')+'</div>'
    def shared(raw):
        raw=replace(raw,'ul','id','aside-cat-list',asidecats)
        raw=replace(raw,'div','class','card-tag-cloud',cloud(True))
        counts={'archives':len(posts),'tags':len(by_tag),'categories':len(categories)}
        for kind,n in counts.items():
            pat=r'(<a\b[^>]*href="/'+kind+r'/"[^>]*>\s*<div class="headline">[^<]*</div>\s*<div class="length-num">)\d+'
            raw=re.sub(pat,lambda m:m[1]+str(n),raw)
        return raw
    # Article metadata only: no reserialization of article content or scripts.
    for post in posts:
        raw=load(post['path']);s=parse(raw)
        meta=s.select_one('#post-meta')
        for n in meta.select('span.post-meta-categories'):n.decompose()
        meta.select_one('.meta-firstline').append(parse('<span class="post-meta-categories"><span class="post-meta-separator">|</span><i class="fas fa-inbox fa-fw post-meta-icon"></i><a class="post-meta-categories" href="'+link('categories',post['category'])+'">'+E(post['category'])+'</a></span>').span)
        raw=replace(raw,'div','id','post-meta',str(meta))
        tagshtml='<div class="post-meta__tag-list">'+''.join('<a class="post-meta__tags" href="'+link('tags',t)+'">'+E(t)+'</a>' for t in post['tags'])+'</div>'
        if region(raw,'div','class','post-meta__tag-list'):
            raw=replace(raw,'div','class','post-meta__tag-list',tagshtml)
        else:
            raw=re.sub(r'(<div\b[^>]*class="tag_share"[^>]*>)',lambda m:m[1]+tagshtml,raw,count=1)
        raw=re.sub(r'<meta\b(?=[^>]*property=[\"\']article:(?:tag|section)[\"\'])[^>]*>\s*','',raw)
        metas='<meta property="article:section" content="'+E(post['category'])+'">'+''.join('<meta property="article:tag" content="'+E(t)+'">' for t in post['tags'])
        raw=raw.replace('</head>',metas+'</head>',1)
        save(post['path'],raw)
    # Templates are theme shells. Regenerate complete taxonomy lists without pagination.
    template=load('tags/Docker/index.html')
    def page_shell(title,url,main_id,main_html):
        existing=shells.get(unquote(url).strip('/')+'/index.html')
        raw=existing if existing and not parse(existing).select_one('meta[http-equiv="refresh"]') else template
        source_id=next((key for key in ['tag','category','page'] if region(raw,'div','id',key)),None)
        assert source_id,'Missing taxonomy content container'
        raw=re.sub(r'<title>.*?</title>','<title>'+E(title)+' | Billy 的博客</title>',raw,count=1)
        raw=re.sub(r'<meta\b(?=[^>]*(?:property=[\"\']og:(?:title|url|description)[\"\']|name=[\"\']description[\"\']))[^>]*>','',raw)
        raw=re.sub(r'<link\b(?=[^>]*rel=[\"\']canonical[\"\'])[^>]*>','',raw)
        raw=raw.replace('</head>','<meta property="og:title" content="'+E(title)+'"><meta property="og:url" content="'+BASE+url+'"><meta name="description" content="'+E(title)+'：按主题浏览 Billy 的博客文章。"><link rel="canonical" href="'+BASE+url+'"></head>',1)
        raw=replace(raw,'div','id',source_id,'<div id="'+main_id+'">'+main_html+'</div>')
        raw=re.sub(r'(<h1\b[^>]*>).*?(</h1>)',lambda m:m[1]+E(title)+m[2],raw,count=1,flags=re.S)
        raw=replace(raw,'script','id','config-diff','<script id="config-diff">var GLOBAL_CONFIG_SITE = '+json.dumps(dict(title=title,isHighlightShrink=False,isToc=False,pageType='category' if main_id=='category' else 'tag' if main_id=='tag' else 'page'),ensure_ascii=False)+';</script>')
        return shared(raw)
    def listing(items):
        result='<div class="article-sort">';year=None
        for p in sorted(items,key=lambda p:(p['date'],p['url']),reverse=True):
            y=p['display_date'][:4]
            if y!=year:result+='<div class="article-sort-item year">'+y+'</div>';year=y
            result+='<div class="article-sort-item"><a class="article-sort-item-img" href="'+p['url']+'" title="'+E(p['title'])+'"><img src="'+E(p['cover'])+'" alt="'+E(p['title'])+'" loading="lazy"></a><div class="article-sort-item-info"><div class="article-sort-item-time"><i class="far fa-calendar-alt"></i><time datetime="'+p['date']+'">'+p['display_date']+'</time></div><a class="article-sort-item-title" href="'+p['url']+'" title="'+E(p['title'])+'">'+E(p['title'])+'</a></div></div>'
        return result+'</div>'
    active=set()
    for kind,groups in [('categories',by_cat),('tags',by_tag)]:
        for name,items in groups.items():
            url=link(kind,name);path=unquote(url).strip('/')+'/index.html';active.add(path)
            label=('分类' if kind=='categories' else '标签')+' - '+name
            save(path,page_shell(label,url,'category' if kind=='categories' else 'tag','<div class="article-sort-title">'+E(label)+' · '+str(len(items))+' 篇</div>'+listing(items)))
    save('categories/index.html',page_shell('分类','/categories/','page','<div class="category-lists"><ul class="category-list">'+catlinks+'</ul></div>'))
    save('tags/index.html',page_shell('标签','/tags/','page',cloud()))
    # Keep old URLs usable; broad former categories lead to the new overview.
    alias=config['legacy_tag_redirects']
    for kind in ['categories','tags']:
        for p in (ROOT/kind).rglob('index.html'):
            rel=p.relative_to(ROOT).as_posix()
            if rel in active or rel==kind+'/index.html':continue
            name=p.relative_to(ROOT/kind).parts[0]
            dest=alias.get(name,'/tags/') if kind=='tags' else '/categories/'
            save(rel,'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0;url='+dest+'"><link rel="canonical" href="'+BASE+dest+'"><title>分类标签已调整</title></head><body><p>分类标签已调整，<a href="'+dest+'">点击前往新页面</a>。</p></body></html>\n')
    lookup={p['url']:p for p in posts}
    # All theme pages, including legacy standalone pages, share the same sidebar counts.
    for p in ROOT.rglob('*.html'):
        if 'upload' in p.relative_to(ROOT).parts:continue
        raw=p.read_text(encoding='utf8');updated=shared(raw)
        # Homepage cards carry the same category as their article.
        def card_meta(match):
            block=match[0];s=parse(block);a=s.select_one('a.article-title')
            post=lookup.get(a['href']) if a else None
            if not post:return block
            meta=s.select_one('.article-meta-wrap')
            if not meta:return block
            for n in meta.select('.article-meta__categories'):n.decompose()
            # Legacy category wrappers may retain only a separator and icon.
            for n in meta.select('span.article-meta'):
                if n.select_one('.fa-inbox') and not n.select_one('a, time') and not n.get_text(strip=True).strip('| '):
                    n.decompose()
            meta.append(parse('<span class="article-meta__categories"><span class="article-meta-separator"> | </span><i class="fas fa-inbox"></i> <a href="'+link('categories',post['category'])+'">'+E(post['category'])+'</a></span>').span)
            return replace(block,'div','class','article-meta-wrap',str(meta))
        # Match each card using balanced divs, preserving summaries and layout.
        cursor=0
        while True:
            bounds=region(updated[cursor:],'div','class','recent-post-item')
            if not bounds:break
            a,b=(cursor+bounds[0],cursor+bounds[1]);block=updated[a:b]
            class Match:
                def __getitem__(self,k):return block
            new=card_meta(Match());updated=updated[:a]+new+updated[b:];cursor=a+len(new)
        if updated!=raw:p.write_text(updated,encoding='utf8',newline='\n')
    # Keep search CDATA and article bodies intact; refresh metadata per entry.
    def search_entry(m):
        raw=m[0];u=re.search(r'<url>(.*?)</url>',raw)
        key='/'+u[1].lstrip('/') if u else ''
        p=lookup.get(key)
        if not p:return raw
        raw=re.sub(r'<(categories|tags)>.*?</\1>','',raw,flags=re.S)
        return raw.replace('</entry>','<categories><category>'+E(p['category'])+'</category></categories><tags>'+''.join('<tag>'+E(t)+'</tag>' for t in p['tags'])+'</tags></entry>')
    save('search.xml',re.sub(r'<entry>.*?</entry>',search_entry,load('search.xml'),flags=re.S))
    # Available Markdown source is kept in sync with the static page.
    for p in (ROOT/'content/posts').glob('*.md'):
        slug=p.stem
        if slug not in mapping:continue
        raw=p.read_text(encoding='utf8');m=mapping[slug]
        if raw.startswith('---\n'):
            _,head,body=raw.split('---',2)
            head=re.sub(r'\ncategories:.*?(?=\n\w|\Z)','',head,flags=re.S)
            head=re.sub(r'\ntags:.*?(?=\n\w|\Z)','',head,flags=re.S)
            head=head.rstrip()+'\ncategories:\n  - '+m['category']+'\ntags:\n'+''.join('  - '+t+'\n' for t in m['tags'])
            p.write_text('---'+head+'---'+body,encoding='utf8',newline='\n')
    report='# 文章分类与标签清单\n\n每篇文章归属一个主题大类，使用 2–6 个具体标签；故障排查作为跨分类标签。正文为空的旧文章仅根据标题赋予保守标签。\n\n'
    report+='| 大类 | 文章数 |\n|---|---:|\n'+''.join('| '+c+' | '+str(len(by_cat[c]))+' |\n' for c in categories)
    report+='\n共 '+str(len(posts))+' 篇文章、'+str(len(categories))+' 个分类、'+str(len(by_tag))+' 个标签。\n\n| 文章 | 分类 | 标签 |\n|---|---|---|\n'
    report+=''.join('| ['+p['title'].replace('|','\\|')+']('+p['url']+') | '+p['category']+' | '+ '、'.join(p['tags'])+' |\n' for p in posts)
    report+='\n维护入口：`content/taxonomy.json`。执行 `python tools/rebuild_taxonomy.py` 重建分类、标签与搜索元数据。旧分类标签 URL 保留跳转。`legacy-html` 为历史独立页面，本次仅同步其导航，不将其重新发布为文章。\n'
    save('content/分类与标签清单.md',report)
    print(json.dumps({'posts':len(posts),'categories':{c:len(by_cat[c]) for c in categories},'tags':len(by_tag)},ensure_ascii=False))

if __name__=='__main__':main()
