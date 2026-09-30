# -*- coding: utf-8 -*-
"""把全站 HTML 里的 /upload/thumbs/... 本地缩略图引用替换为图床 URL。

用法:
  python scripts/bed_replace_refs.py          # 干跑:只统计,不改文件
  python scripts/bed_replace_refs.py --go     # 执行替换
  python scripts/bed_replace_refs.py --go --remove-local   # 替换并验证为 0 后 git rm upload/thumbs

前置:<STATE>/thumb_url_map.json 由 scripts/bed_upload_thumbs.py --go 生成(STATE 默认 e:/tmp)

说明:残留验证会排除 docs/ 与 scripts/(那里的 "upload/thumbs" 是文档文字/脚本代码,不是图片引用)。
"""
import os, re, json, glob, sys, urllib.parse, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.environ.get("BED_STATE", "e:/tmp")
MAP_FILE = os.path.join(STATE, "thumb_url_map.json")

def main():
    go = "--go" in sys.argv
    remove_local = "--remove-local" in sys.argv
    mapping = json.load(open(MAP_FILE, encoding="utf-8"))
    lookup = {os.path.basename(k): url for k, url in mapping.items()}

    pat = re.compile(r'(?:https?://billy775326\.github\.io)?/upload/thumbs/[^"\'\s<>)]+')
    n_files = n_refs = 0
    miss = set()
    for f in glob.glob(os.path.join(REPO, "**", "*.html"), recursive=True):
        rel = os.path.relpath(f, REPO).replace(os.sep, "/")
        if rel.startswith((".git", "docs", "scripts")):
            continue   # legacy-html 也替换:它同样被 GitHub Pages 托管
        h = open(f, encoding="utf-8").read()
        if "upload/thumbs" not in h:
            continue
        def sub(m):
            nonlocal n_refs
            base = os.path.basename(urllib.parse.unquote(m.group(0)))
            url = lookup.get(base)
            if url is None:
                miss.add(base)
                return m.group(0)
            n_refs += 1
            return url
        h2 = pat.sub(sub, h)
        if go and h2 != h:
            open(f, "w", encoding="utf-8", newline="").write(h2)
            n_files += 1
    print(f"[{'applied' if go else 'dry-run'}] files updated: {n_files}, refs replaced: {n_refs}")
    if miss:
        print("!! 无映射的引用(先补上传):")
        for b in sorted(miss):
            print("   ", b)

    # 全仓残留验证(排除 docs/scripts 的文字提及)
    remaining = 0
    for ext in ("html", "xml", "md", "js", "css"):
        for f in glob.glob(os.path.join(REPO, "**", "*." + ext), recursive=True):
            rel = os.path.relpath(f, REPO).replace(os.sep, "/")
            if rel.startswith((".git", "legacy-html", "docs/", "scripts/")):
                continue
            c = open(f, encoding="utf-8", errors="ignore").read().count("upload/thumbs")
            if c:
                remaining += c
                print("   remaining:", rel, c)
    print("[verify] upload/thumbs 残留引用(不含 docs/scripts):", remaining)

    if remove_local:
        if remaining or miss:
            print("!! 仍有残留/缺映射,不执行本地删除")
            return
        if not go:
            print("!! dry-run 不删除本地文件")
            return
        subprocess.run(["git", "rm", "-r", "-q", "upload/thumbs"], cwd=REPO, check=True)
        print("[git] upload/thumbs 已从仓库移除")

if __name__ == "__main__":
    main()
