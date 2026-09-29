"""Apply shared compact footer and factual structured data; generate sitemap."""
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
import json,re,xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as B
from rebuild_taxonomy import ROOT,region

BASE='https://billy775326.github.io'
FOOTER='''<footer id="footer" aria-label="网站页脚"><div class="footer-other"><div class="copyright">© 2023–2026 By <a href="/">Billy</a></div><div class="framework-info"><span>框架 </span><a href="https://hexo.io" rel="noopener" target="_blank">Hexo</a><span class="footer-separator">|</span><span>主题 </span><a href="https://github.com/jerryc127/hexo-theme-butterfly" rel="noopener" target="_blank">Butterfly</a></div><div class="footer_custom_text"><span>记录编程开发、系统运维与工具实践。</span><nav aria-label="页脚导航"><a href="/about/">关于</a><span class="footer-separator" aria-hidden="true">·</span><a href="/archives/">归档</a><span class="footer-separator" aria-hidden="true">·</span><a href="/categories/">分类</a><span class="footer-separator" aria-hidden="true">·</span><a href="/tags/">标签</a><span class="footer-separator" aria-hidden="true">·</span><a href="/sitemap.xml">站点地图</a><span class="footer-separator" aria-hidden="true">·</span><a href="https://github.com/Billy775326" rel="me noopener" target="_blank">GitHub</a></nav></div></div></footer>'''
AUTHOR={'@type':'Person','@id':BASE+'/#author','name':'Billy','url':BASE+'/','sameAs':['https://github.com/Billy775326']}

def main():
    entries={};changed=0
    for p in ROOT.rglob('*.html'):
        rel=p.relative_to(ROOT)
        if rel.parts[0] in ['upload','docs']:continue
        raw=p.read_text(encoding='utf8');s=B(raw,'html.parser')
        if not s.select_one('footer#footer'):continue
        before=raw
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
