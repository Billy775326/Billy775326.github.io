"""Small, testable metadata transforms used by the final publishing pass."""
from datetime import datetime, timedelta, timezone
import json
import re
from urllib.parse import unquote

from bs4 import BeautifulSoup


def archive_noindex(raw):
    """Change only the archive head; keep historical body bytes untouched."""
    head = re.search(r'(<head\b[^>]*>)(.*?)(</head\s*>)', raw, re.I | re.S)
    if not head:
        raise ValueError('Historical archive has no head for its robots directive')

    def keep_other_meta(match):
        tag = BeautifulSoup(match[0], 'html.parser').find('meta')
        if tag and str(tag.get('name', '')).lower() == 'robots':
            return ''
        return match[0]

    content = re.sub(r'<meta\b[^>]*>', keep_other_meta, head[2], flags=re.I)
    content += '<meta name="robots" content="noindex,follow">'
    return raw[:head.start(2)] + content + raw[head.end(2):]


def page_description(url, posts, per_page=18):
    """Describe the actual collection and page without guessing article topics."""
    url = unquote(url)
    page_match = re.search(r'/page/(\d+)/$', url)
    page = int(page_match[1]) if page_match else 1
    collection_url = url[:page_match.start()] + '/' if page_match else url
    page_note = f'当前为第 {page} 页。' if page > 1 else ''

    if collection_url == '/':
        if page > 1:
            first = (page - 1) * per_page + 1
            last = min(page * per_page, len(posts))
            return (f'Billy 的博客文章列表第 {page} 页，展示按发布时间排列的第 {first}–{last} 篇文章，'
                    f'共 {len(posts)} 篇。继续浏览编程开发、系统运维与工具实践记录。')
        return f'Billy 的博客，记录编程开发、系统运维与工具实践。目前收录 {len(posts)} 篇文章，可从最新文章、分类、标签或归档开始浏览。'

    for kind, label in [('categories', '分类'), ('tags', '标签')]:
        terms = {}
        for post in posts:
            for term in post[kind]:
                key = '/' + unquote(term['path']).strip('/') + '/'
                terms.setdefault(key, {'name': term['name'], 'count': 0})['count'] += 1
        if collection_url == f'/{kind}/':
            if kind == 'categories':
                return f'Billy 的博客分类目录，按主题整理 {len(posts)} 篇文章、{len(terms)} 个分类。选择分类，浏览对应的学习笔记、实践记录与问题排查。'
            return f'Billy 的博客标签目录，使用 {len(terms)} 个标签关联 {len(posts)} 篇文章。通过技术名称或具体主题，查找相关笔记与实践记录。'
        if collection_url in terms:
            term = terms[collection_url]
            return (f'Billy 的博客“{term["name"]}”{label}下的文章，共 {term["count"]} 篇。'
                    f'按发布时间浏览这一主题的笔记与实践记录，并通过文章标题查看具体内容。{page_note}')

    archive = re.fullmatch(r'/archives/(\d{4}/)?(\d{2}/)?', collection_url)
    if archive:
        year = int(archive[1][:-1]) if archive[1] else None
        month = int(archive[2][:-1]) if archive[2] else None
        dates = [datetime.fromisoformat(p['date'].replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=8))) for p in posts]
        count = sum((year is None or d.year == year) and (month is None or d.month == month) for d in dates)
        period = f'{year} 年 {month} 月' if month else f'{year} 年' if year else '全部'
        return f'Billy 的博客{period}文章归档，共 {count} 篇文章。按发布时间回顾文章，查看对应的标题与日期，或切换年份和月份继续浏览。{page_note}'
    return None


def valid_schema(script):
    """Return usable JSON-LD; empty or malformed blocks should not be emitted."""
    try:
        data = json.loads(script)
    except (TypeError, ValueError):
        return None
    if not isinstance(data, dict) or not data or not (data.get('@type') or data.get('@graph')):
        return None
    return data


def normalize_images(soup, dimensions):
    """Use measured intrinsic sizes for body images and native loading hints."""
    normalized = {unquote(url): size for url, size in dimensions.items()}
    # Existing theme CSS reserves cover boxes (home: 192px tall; archive:
    # 100x70/70x70; aside: 4em square; post navigation: 150px/120px tall).
    # These layout sizes are deliberately not claimed as image source sizes.
    for img in soup.select('img'):
        img['loading'] = 'lazy'
        img['decoding'] = 'async'
    for selector in ('#recent-posts .post_cover img', '.article-sort-item-img img'):
        for img in soup.select(selector)[:3]:
            img['loading'] = 'eager'
    first_cover = soup.select_one('#recent-posts .post_cover img')
    if first_cover:
        first_cover['fetchpriority'] = 'high'
    for img in soup.select('#nav img'):
        img['loading'] = 'eager'
    for index, img in enumerate(soup.select('#article-container img')):
        if index == 0:
            img['loading'] = 'eager'
        size = normalized.get(unquote(img.get('src', '')))
        if size is None:
            continue
        if (not isinstance(size, dict) or any(type(size.get(key)) is not int or size[key] <= 0 for key in ('width', 'height'))):
            raise ValueError(f'Invalid measured image dimensions: {img.get("src")}')
        img['width'] = str(size['width'])
        img['height'] = str(size['height'])
