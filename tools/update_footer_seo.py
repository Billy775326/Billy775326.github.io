"""Apply shared compact footer and factual structured data; generate sitemap."""
from pathlib import Path
if (Path(__file__).resolve().parents[1] / 'hexo/_config.yml').exists():
    raise SystemExit('Hexo source migration is active. Use npm --prefix hexo run build / release; see docs/publishing.md.')
from datetime import datetime,timezone,timedelta
from urllib.parse import quote
import json,re,xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as B
from rebuild_taxonomy import ROOT,region
from update_recent_posts import update_recent_posts

BASE='https://iowill.com'
FOOTER='''<footer id="footer" aria-label="网站页脚"><div class="footer-other"><div class="footer-credits"><span class="copyright">© 2023–2026 By <a href="/">Billy</a></span><span class="framework-info">由 <a href="https://hexo.io" rel="noopener" target="_blank">Hexo</a> 驱动<span class="footer-separator" aria-hidden="true">·</span><a href="https://github.com/jerryc127/hexo-theme-butterfly" rel="noopener" target="_blank">Butterfly</a> 主题</span></div><div class="footer_custom_text"><nav aria-label="页脚导航"><a href="/about/"><i class="fas fa-user" aria-hidden="true"></i>关于</a><a href="/archives/"><i class="fas fa-archive" aria-hidden="true"></i>归档</a><a href="/categories/"><i class="fas fa-folder-open" aria-hidden="true"></i>分类</a><a href="/tags/"><i class="fas fa-tags" aria-hidden="true"></i>标签</a><a href="/sitemap.xml"><i class="fas fa-sitemap" aria-hidden="true"></i>站点地图</a><a href="https://github.com/Billy775326" rel="me noopener" target="_blank"><i class="fab fa-github" aria-hidden="true"></i>GitHub</a></nav></div></div></footer>'''
AUTHOR={'@type':'Person','@id':BASE+'/#author','name':'Billy','url':BASE+'/','sameAs':['https://github.com/Billy775326']}

def main():
    update_recent_posts()
    entries={};changed=0
    article_count=len(json.loads((ROOT/"content/taxonomy.json").read_text(encoding="utf8"))["posts"])
    updated_at=json.loads((ROOT/"content/site-info.json").read_text(encoding="utf8"))["updated_at"]
    for p in ROOT.rglob('*.html'):
        rel=p.relative_to(ROOT)
        if rel.parts[0] in ['upload','docs']:continue
        raw=p.read_text(encoding='utf8');s=B(raw,'html.parser')
        if not s.select_one('footer#footer'):continue
        before=raw
        # Card timestamps use the machine-readable instant in China Standard Time.
        card_times=s.select('.recent-post-item time[datetime], .aside-list-item time[datetime], .article-sort-item time[datetime]')
        replacements={}
        for t in card_times:
            value=t['datetime']
            instant=datetime.fromisoformat(value.replace('Z','+00:00'))
            if instant.tzinfo is None:
                instant=instant.replace(tzinfo=timezone(timedelta(hours=8)))
            replacements[value]=instant.astimezone(timezone(timedelta(hours=8))).strftime('%Y/%m/%d %H:%M:%S')
        def card_time(match):
            attrs=match[1]
            value=re.search(r'datetime=["\']([^"\']+)',attrs)
            if value and value[1] in replacements:
                return '<time'+attrs+'>'+replacements[value[1]]+'</time>'
            return match[0]
        # Restrict updates to card regions; article metadata remains untouched.
        for tag,cls in [('div','recent-post-item'),('div','aside-list-item'),('div','article-sort-item')]:
            cursor=0
            while True:
                bounds=region(raw[cursor:],tag,'class',cls)
                if not bounds:break
                start,end=cursor+bounds[0],cursor+bounds[1]
                block=re.sub(r'<time(\b[^>]*)>.*?</time>',card_time,raw[start:end],flags=re.S)
                block=re.sub(r'<span\b[^>]*class=["\']article-meta-label["\'][^>]*>\s*发表于\s*</span>', '', block)
                raw=raw[:start]+block+raw[end:]
                cursor=start+len(block)

        bounds=region(raw,'div','class','card-webinfo')
        if bounds:
            start,end=bounds
            info=raw[start:end]
            info=re.sub(r'(<div class="item-name">文章数目\s*:</div>\s*<div class="item-count">)\d+',lambda m:m[1]+str(article_count),info)
            info=re.sub(r'data-lastpushdate="[^"]*"','data-lastpushdate="'+updated_at+'"',info,flags=re.I)
            raw=raw[:start]+info+raw[end:]
        if p.name=='index.html' and rel.parts[0]!='legacy-html' and not s.select_one('meta[http-equiv="refresh"]'):
            path=p.parent.relative_to(ROOT).as_posix()
            canonical=BASE+('/' if path=='.' else '/'+quote(path,safe='/')+'/')
            raw=re.sub(r'<link\b(?=[^>]*rel=["\']canonical["\'])[^>]*>',
                       '<link rel="canonical" href="'+canonical+'">',raw)
            raw=re.sub(r'<meta\b(?=[^>]*property=["\']og:url["\'])[^>]*>',
                       '<meta property="og:url" content="'+canonical+'">',raw)
        a,b=region(raw,'footer','id','footer');raw=raw[:a]+FOOTER+raw[b:]
        raw=re.sub(r'<script\b[^>]*>.*?</script>',lambda m:'' if 'querySelectorAll("#runday")' in m[0] else m[0],raw,flags=re.S)
        def schema(m):
            if not m[2].strip():return ''
            try:data=json.loads(m[2])
            except ValueError:return m[0]
            if not isinstance(data,dict):return m[0]
            if data.get('@type')=='WebSite' and rel.as_posix()=='index.html':
                data.update({'@id':BASE+'/#website','inLanguage':'zh-CN','description':'记录编程开发、系统运维与工具实践。','author':AUTHOR,'publisher':{'@id':BASE+'/#author'}})
            elif data.get('@type')=='BlogPosting':
                url=BASE+'/'+p.parent.relative_to(ROOT).as_posix()+'/'
                data.update({'@id':url+'#article','url':url,'inLanguage':'zh-CN','mainEntityOfPage':{'@type':'WebPage','@id':url},'isPartOf':{'@type':'WebSite','@id':BASE+'/#website','name':'Billy 的博客','url':BASE+'/'},'author':AUTHOR,'publisher':AUTHOR})
                category=s.select_one('a.post-meta-categories')
                if category:data['articleSection']=category.text
                data['keywords']=[t.text for t in s.select('.post-meta__tags')]
            else:return m[0]
            return m[1]+json.dumps(data,ensure_ascii=False,indent=2).replace('</','<\\/')+m[3]
        raw=re.sub(r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',schema,raw,flags=re.S)
        if raw!=before:p.write_text(raw,encoding='utf8',newline='\n');changed+=1
        if rel.parts[0]=='legacy-html':continue
        # All discoverable theme pages are canonical static directory indexes.
        if p.name!='index.html' or s.select_one('meta[http-equiv="refresh"]'):continue
        path=p.parent.relative_to(ROOT).as_posix()
        url=BASE+('/' if path=='.' else '/'+quote(path,safe='/')+'/')
        modified=s.select_one('meta[property="article:modified_time"]')
        entries[url]=modified['content'] if modified else None
    ns='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',ns)
    tree=ET.Element('{'+ns+'}urlset')
    for url,date in sorted(entries.items()):
        node=ET.SubElement(tree,'{'+ns+'}url');ET.SubElement(node,'{'+ns+'}loc').text=url
        if date:
            datetime.fromisoformat(date.replace('Z','+00:00'))
            ET.SubElement(node,'{'+ns+'}lastmod').text=date
    ET.indent(tree)
    (ROOT/'sitemap.xml').write_bytes(ET.tostring(tree,encoding='utf-8',xml_declaration=True)+b'\n')
    robots=ROOT/'robots.txt'
    raw=robots.read_text(encoding='utf8') if robots.exists() else 'User-agent: *\nAllow: /\n'
    raw=re.sub(r'^Sitemap:.*\n?','',raw,flags=re.M).rstrip()+'\n\nSitemap: '+BASE+'/sitemap.xml\n'
    robots.write_text(raw,encoding='utf8')
    print('Updated pages:',changed,'Sitemap URLs:',len(entries))

if __name__=='__main__':main()
