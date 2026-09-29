"""Create the theme-native About page and add desktop/mobile navigation."""
import json,re
from rebuild_taxonomy import ROOT,BASE,region,replace

CONTENT='''<div id="page"><article id="article-container" class="post-content"><h2 id="about-billy">你好，我是 Billy</h2><p>欢迎来到 Billy 的博客。这里记录学习与折腾，把编程笔记、系统配置和问题排查过程整理下来，方便回顾，也希望能给遇到类似问题的人一些参考。</p><h2 id="topics">这里写什么</h2><ul><li><a href="/categories/programming/">编程开发</a>：Rust、C++ 与项目实践。</li><li><a href="/categories/algorithms/">算法与数据结构</a>：题目分析和解题记录。</li><li><a href="/categories/systems-operations/">系统与运维</a>：Linux、容器、网络及故障排查。</li><li><a href="/categories/software-tools/">软件与工具</a>：工具配置、使用经验与博客搭建。</li><li><a href="/categories/gaming/">游戏与实践</a>：游戏相关工具和实践记录。</li></ul><h2 id="reading">如何阅读</h2><p>可以从<a href="/archives/">文章归档</a>按时间浏览，也可以通过<a href="/categories/">分类</a>和<a href="/tags/">标签</a>寻找主题。技术文章中的示例需要结合自己的系统版本和环境使用。</p><h2 id="contact">找到我</h2><p><a href="https://github.com/Billy775326" rel="me noopener" target="_blank">GitHub · Billy775326</a></p><p>如果发现文章有疏漏，欢迎通过<a href="https://github.com/Billy775326/Billy775326.github.io" rel="noopener" target="_blank">博客仓库</a>交流或提交修正。</p><h2 id="site">关于本站</h2><p>本站使用 Hexo 与 Butterfly 主题，托管于 GitHub Pages。文章的转载与使用方式，请查看各篇文章末尾的版权说明。</p></article></div>'''

def main():
    path=ROOT/'about/index.html'
    raw=path.read_text(encoding='utf8') if path.exists() else (ROOT/'categories/index.html').read_text(encoding='utf8')
    raw=replace(raw,'div','id','page',CONTENT)
    raw=re.sub(r'<title>.*?</title>','<title>关于 | Billy 的博客</title>',raw,count=1)
    raw=re.sub(r'(<h1\b[^>]*>).*?(</h1>)',r'\g<1>关于\2',raw,count=1,flags=re.S)
    raw=replace(raw,'script','id','config-diff','<script id="config-diff">var GLOBAL_CONFIG_SITE = {"title":"关于","isHighlightShrink":false,"isToc":false,"pageType":"page"};</script>')
    description='关于 Billy 的博客：记录编程开发、算法、系统运维、软件工具与游戏实践，提供文章导航和作者 GitHub 入口。'
    raw=re.sub(r'<meta\b(?=[^>]*(?:property=["\']og:(?:title|url|description)["\']|name=["\'](?:description|keywords)["\']))[^>]*>','',raw)
    raw=re.sub(r'<link\b(?=[^>]*rel=["\']canonical["\'])[^>]*>','',raw)
    raw=re.sub(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>','',raw,flags=re.S)
    data={'@context':'https://schema.org','@type':'AboutPage','@id':BASE+'/about/#page','url':BASE+'/about/','name':'关于 Billy 的博客','description':description,'inLanguage':'zh-CN','mainEntity':{'@type':'Person','@id':BASE+'/#author','name':'Billy','url':BASE+'/about/','sameAs':['https://github.com/Billy775326']},'isPartOf':{'@id':BASE+'/#website'}}
    raw=raw.replace('</head>','<meta name="description" content="'+description+'"><meta property="og:title" content="关于 | Billy 的博客"><meta property="og:description" content="'+description+'"><meta property="og:url" content="'+BASE+'/about/"><link rel="canonical" href="'+BASE+'/about/"><script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script></head>',1)
    path.parent.mkdir(exist_ok=True);path.write_text(raw,encoding='utf8')
    link='<div class="menus_item"><a class="site-page" href="/about/"><i class="fa-fw fas fa-user"></i><span> 关于</span></a></div>'
    for p in ROOT.rglob('*.html'):
        if 'upload' in p.relative_to(ROOT).parts:continue
        raw=p.read_text(encoding='utf8');cursor=0
        while True:
            bounds=region(raw[cursor:],'div','class','menus_items')
            if not bounds:break
            a,b=cursor+bounds[0],cursor+bounds[1]
            if 'href="/about/"' not in raw[a:b]:raw=raw[:b-6]+link+raw[b-6:];b+=len(link)
            cursor=b
        if raw!=p.read_text(encoding='utf8'):p.write_text(raw,encoding='utf8')

if __name__=='__main__':main()
