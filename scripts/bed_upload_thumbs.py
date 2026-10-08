# -*- coding: utf-8 -*-
"""按用户规则把缩略图上传到 img.iowill.com (CloudFlare ImgBed / cfbed)。

目录/命名规则(用户 2026-09-30 指定):
  封面   -> <文章分类>/<文章标题>/cover.<ext>
  正文图 -> <文章分类>/<文章标题>/body.<ext>
  缩略图 -> <文章分类>/<文章标题>/thumbs/cover.<ext> 或 thumbs/body.<ext>
  全站默认封面缩略图 -> DEFAULT_THUMB_FOLDER/cover.<ext>(不属于单篇文章)

用法:
  python scripts/bed_upload_thumbs.py            # 干跑:只显示计划,不联网
  python scripts/bed_upload_thumbs.py --go       # 真正上传
  python scripts/bed_upload_thumbs.py --check    # 列出图床上已有文件(需 list 权限)

前置:
  1) <STATE>/thumb_bed_plan.json  由 scripts/thumb_bed_plan.py 生成
  2) <STATE>/bed_token.txt        图床 API Token(单独一行;STATE 默认 e:/tmp,在仓库外,切勿提交)

产出:<STATE>/thumb_url_map.json  {本地相对路径: 图床URL},供 bed_replace_refs.py 使用
"""
import os, sys, json, shutil, subprocess, urllib.parse, tempfile

# ====== 配置 ======
BASE = "https://img.iowill.com"
DEFAULT_THUMB_FOLDER = "默认封面/thumbs"   # 全站默认封面缩略图的存放目录
UPLOAD_NAME_TYPE = "origin"               # 文件名已在暂存时改为 cover/body,原名直传
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.environ.get("BED_STATE", "e:/tmp")   # token/计划/映射目录,勿入仓库
TOKEN_FILE = os.path.join(STATE, "bed_token.txt")
PLAN_FILE = os.path.join(STATE, "thumb_bed_plan.json")
MAP_FILE = os.path.join(STATE, "thumb_url_map.json")
PROXY = os.environ.get("BED_PROXY", "http://127.0.0.1:10808")   # 直连失败自动改走
# =================

def token():
    if not os.path.exists(TOKEN_FILE):
        sys.exit(f"!! 缺 token 文件: {TOKEN_FILE}(把 token 单独一行存进去;该文件在仓库外,不要提交)")
    t = open(TOKEN_FILE, encoding="utf-8").read().strip()
    if not t:
        sys.exit("!! token 文件为空")
    return t

def upload_one(path, folder, name, tok):
    """暂存改名 -> POST /upload。folder/name 按用户规则。返回图床 URL。"""
    staged = os.path.join(tempfile.gettempdir(), name)
    shutil.copyfile(path, staged)
    url = (f"{BASE}/upload?uploadFolder={urllib.parse.quote(folder)}"
           f"&uploadNameType={UPLOAD_NAME_TYPE}&returnFormat=full")
    try:
        last = ""
        for extra in ([], ["-x", PROXY]):   # 先直连,失败走代理
            cmd = ["curl", "-sS", "--ssl-revoke-best-effort", "-X", "POST", url,
                   "-H", f"Authorization: Bearer {tok}",
                   "-F", f"file=@\"{staged}\""] + extra
            r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=120)
            last = (r.stdout or "") + (r.stderr or "")
            if r.returncode == 0 and r.stdout.strip().startswith("["):
                arr = json.loads(r.stdout)
                src = arr[0].get("src", "")
                if src.startswith("http"):          # returnFormat=full 时 src 即完整链接
                    return src
                return arr[0].get("publicUrl") or BASE + src
        raise RuntimeError(f"{os.path.basename(path)} :: {last[:200]}")
    finally:
        if os.path.exists(staged):
            os.remove(staged)

def check(tok):
    url = f"{BASE}/api/manage/list?count=-1&recursive=true"
    r = subprocess.run(["curl", "-sS", "--ssl-revoke-best-effort", url,
                        "-H", f"Authorization: Bearer {tok}"],
                       capture_output=True, text=True, encoding="utf-8", timeout=60)
    try:
        data = json.loads(r.stdout)
    except Exception:
        print("响应异常:", r.stdout[:300]); return
    for it in data.get("files", []):
        print(it.get("name"))

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "--check":
        check(token())
        return
    plan = json.load(open(PLAN_FILE, encoding="utf-8"))
    print("[plan]")
    for p in plan:
        dest = f"{p['folder']}/{p['name']}" if p["folder"] else "(跳过:无归属)"
        print(f"   {p['local']:60} -> {dest}")
    if mode != "--go":
        print("[dry-run] 未上传。确认计划无误后加 --go 执行。")
        return
    tok = token()
    mapping = json.load(open(MAP_FILE, encoding="utf-8")) if os.path.exists(MAP_FILE) else {}
    for p in plan:
        if not p["folder"]:
            continue
        if p["local"] in mapping:
            print("  skip(已有映射):", p["local"]); continue
        folder = DEFAULT_THUMB_FOLDER if p["role"] == "default" else p["folder"]
        url = upload_one(os.path.join(REPO, p["local"].replace("/", os.sep)),
                         folder, p["name"], tok)
        mapping[p["local"]] = url
        json.dump(mapping, open(MAP_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("  uploaded:", p["name"], "->", url)
    print(f"[done] map -> {MAP_FILE}")

if __name__ == "__main__":
    main()
