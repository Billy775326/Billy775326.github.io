# -*- coding: utf-8 -*-
"""分析每张 upload/thumbs/ 缩略图归属的文章/分类/角色(封面或插图/全站默认),
生成上传计划 <STATE>/thumb_bed_plan.json,供 bed_upload_thumbs.py 消费。纯本地扫描,不联网。

目录规则(用户 2026-09-30 指定):
  封面   -> <文章分类>/<文章标题>/cover.<ext>
  正文图 -> <文章分类>/<文章标题>/body.<ext>
  缩略图 -> <文章分类>/<文章标题>/thumbs/cover.<ext> 或 thumbs/body.<ext>

判定逻辑:
  body   = <img> 落在本文 <div id="article-container"> ... </article> 之间
  cover  = 包在 <a href="/blog/..."> 里,取被引用最多的目标文章
  default= 被 >=20 篇不同文章引用 => 全站默认封面缩略图,单独归档(见 bed_upload_thumbs.py 的 DEFAULT_THUMB_FOLDER)
"""
import os, re, json, glob, urllib.parse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.environ.get("BED_STATE", "e:/tmp")   # 计划/映射/token 等产物目录,勿入仓库
OUT = os.path.join(STATE, "thumb_bed_plan.json")

THUMBS = os.listdir(os.path.join(REPO, "upload", "thumbs")) if os.path.isdir(os.path.join(REPO, "upload", "thumbs")) else []
PAT = re.compile(r'/upload/thumbs/[^"\'\s<>)]+')

def decode(ref):
    return os.path.basename(urllib.parse.unquote(ref))

# 1) 每篇文章的分类与标题
art_info = {}
for f in glob.glob(os.path.join(REPO, "blog", "**", "index.html"), recursive=True):
    rel = "/" + os.path.relpath(f, REPO).replace(os.sep, "/").replace("index.html", "")
    h = open(f, encoding="utf-8").read()
    t = re.search(r"<title>(.*?)\s*\|\s*Billy 的博客</title>", h, re.S)
    sec = re.search(r'<meta property="article:section" content="([^"]+)"', h)
    art_info[rel] = dict(title=t.group(1).strip() if t else "?",
                         cat=sec.group(1) if sec else "?")

def folder_of(href):
    ai = art_info.get(href)
    if not ai:
        return None
    return f"{ai['cat']}/{ai['title']}/thumbs", ai

# 2) 扫描引用上下文
usage = {d: dict(covers=[], bodys=[]) for d in THUMBS}
files = []
for x in glob.glob(os.path.join(REPO, "**", "*.html"), recursive=True):
    first = os.path.relpath(x, REPO).replace(os.sep, "/").split("/")[0]
    if first.startswith(("legacy-html", "tools", ".git", "docs", "scripts")):
        continue   # 注意:必须用相对路径首段判断,绝对路径首段是盘符
    files.append(x)
for f in files:
    h = open(f, encoding="utf-8").read()
    if "upload/thumbs" not in h:
        continue
    a = h.find('id="article-container"')
    body_zone = ""
    if a >= 0:
        e = h.find("</article>", a)
        if e >= 0:
            body_zone = h[a:e]
    for r in PAT.findall(body_zone):
        d = decode(r)
        if d in usage:
            usage[d]["bodys"].append(r)
    for m in re.finditer(r'<a[^>]*?href="(/blog/[^"]+/)"[^>]*>((?:(?!</a>).)*?)</a>', h, re.S):
        for r in PAT.findall(m.group(2)):
            d = decode(r)
            if d in usage:
                usage[d]["covers"].append(m.group(1))

# 3) 归属
plan = []
for d in THUMBS:
    u = usage[d]
    stem = os.path.splitext(d)[1]
    total = len(u["covers"]) + len(u["bodys"])
    if u["bodys"]:
        href = u["bodys"][0]
        fo = folder_of(href) or ("?/?/thumbs", {})
        plan.append(dict(local="upload/thumbs/" + d, role="body", owner=href,
                         cat=fo[1].get("cat", "?"), title=fo[1].get("title", "?"),
                         folder=fo[0], name="body" + stem, refs=total))
        continue
    if u["covers"]:
        cnt = {}
        for href in u["covers"]:
            cnt[href] = cnt.get(href, 0) + 1
        if len(cnt) >= 20:
            plan.append(dict(local="upload/thumbs/" + d, role="default",
                             owner="(全站默认封面)", cat="-", title="默认封面",
                             folder="(默认封面目录)", name="cover" + stem,
                             refs=total, targets=len(cnt)))
            continue
        owner = max(cnt, key=cnt.get)
        fo = folder_of(owner) or ("?/?/thumbs", {})
        plan.append(dict(local="upload/thumbs/" + d, role="cover", owner=owner,
                         cat=fo[1].get("cat", "?"), title=fo[1].get("title", "?"),
                         folder=fo[0], name="cover" + stem, refs=total,
                         owner_refs=cnt[owner]))
        continue
    plan.append(dict(local="upload/thumbs/" + d, role="none", owner="(无引用)",
                     cat="?", title="?", folder="", name="", refs=0))

os.makedirs(STATE, exist_ok=True)
json.dump(plan, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for p in plan:
    dest = (p["folder"] + "/" + p["name"]) if p["folder"] else "(未归类)"
    print(f"{p['role']:7} | {dest} | refs={p['refs']}")
print("\nplan ->", OUT)
