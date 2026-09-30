"""Synchronize existing recent-post widgets from real publication dates."""
from datetime import datetime, timezone, timedelta
from html import escape
from bs4 import BeautifulSoup as B
from rebuild_taxonomy import ROOT, region


def update_recent_posts():
    cards={}
    for page in [ROOT/'index.html', *sorted((ROOT/'page').rglob('index.html'))]:
        soup=B(page.read_text(encoding='utf8'),'html.parser')
        for card in soup.select('.recent-post-item'):
            link=card.select_one('a.article-title'); image=card.select_one('.post_cover img')
            if link and image:
                cards.setdefault(link['href'], (len(cards), image.get('data-lazy-src') or image.get('src')))
    posts=[]
    for page in sorted((ROOT/'blog').rglob('index.html')):
        soup=B(page.read_text(encoding='utf8'),'html.parser')
        title=soup.select_one('.post-title').get_text()
        stamp=soup.select_one('meta[property="article:published_time"]')['content']
        date=datetime.fromisoformat(stamp.replace('Z','+00:00'))
        if date.tzinfo is None: raise ValueError('Publication date needs timezone: '+str(page))
        url='/'+page.parent.relative_to(ROOT).as_posix()+'/'
        cover=soup.select_one('meta[property="og:image"]')
        order,image=cards.get(url,(len(cards),cover['content'] if cover else '/img/avatar.jpg'))
        posts.append((date,order,url,title,stamp,image))
    posts.sort(key=lambda p:(-p[0].timestamp(),p[1],p[2]))
    rows=[]
    for date,order,url,title,stamp,image in posts[:5]:
        shown=date.astimezone(timezone(timedelta(hours=8))).strftime('%Y/%m/%d %H:%M:%S')
        url,title,stamp,image=map(escape,(url,title,stamp,image))
        rows.append(f'<div class="aside-list-item"><a class="thumbnail" href="{url}" title="{title}"><img src="{image}" alt="{title}" loading="lazy" onerror="this.onerror=null;this.src=\'/img/404.jpg\'"></a><div class="content"><a class="title" href="{url}" title="{title}">{title}</a><time datetime="{stamp}" title="{shown}">{shown}</time></div></div>')
    listing='<div class="aside-list">'+''.join(rows)+'</div>'
    changed=0
    for page in ROOT.rglob('*.html'):
        if page.relative_to(ROOT).parts[0] in ['upload','docs']:continue
        raw=page.read_text(encoding='utf8')
        bounds=region(raw,'div','class','card-recent-post')
        if not bounds:continue
        a,b=bounds;widget=raw[a:b]
        inner=region(widget,'div','class','aside-list')
        if not inner:raise ValueError('Missing recent-post list: '+str(page))
        x,y=inner;updated=raw[:a]+widget[:x]+listing+widget[y:]+raw[b:]
        if updated!=raw:
            page.write_text(updated,encoding='utf8',newline='\n');changed+=1
    return changed

if __name__=='__main__':
    print('Updated recent-post widgets:',update_recent_posts())
