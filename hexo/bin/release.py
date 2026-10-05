"""Back up and copy verified public output into the existing GitHub Pages root.

No network calls, commits, pushes, or recursive directory removal occur here.
"""
from pathlib import Path
from datetime import datetime
import hashlib, json, shutil, subprocess, sys, zipfile

SOURCE = Path(__file__).resolve().parents[1]
REPO = SOURCE.parent.resolve()
PUBLIC = (SOURCE / 'public').resolve()
subprocess.run([sys.executable, str(SOURCE / 'bin/verify.py')], check=True)
allowed = {'index.html', 'blog', 'archives', 'page', 'tags', 'categories', 'about', 'css', 'js', 'img', 'legacy-html', 'CNAME', 'robots.txt', 'sitemap.xml', 'search.xml', '.nojekyll', '404.html'}
files = {p.relative_to(PUBLIC).as_posix(): p for p in PUBLIC.rglob('*') if p.is_file()}
assert files and 'index.html' in files
for rel in files:
    assert Path(rel).parts[0] in allowed, ('Unexpected output', rel)
    assert (REPO / rel).resolve().is_relative_to(REPO), rel
manifest = SOURCE / 'release-manifest.json'
old = json.loads(manifest.read_text(encoding='utf8')) if manifest.exists() else {}
stale = set(old) - set(files)
for rel in stale:
    assert Path(rel).parts[0] in allowed and (REPO / rel).resolve().is_relative_to(REPO)
backup = REPO.parent / 'backups' / ('hexo-release-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
backup.mkdir(parents=True)
with zipfile.ZipFile(backup / 'previous-static-files.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for rel in sorted(set(files) | stale):
        p = REPO / rel
        if p.is_file(): z.write(p, rel)
with zipfile.ZipFile(backup / 'previous-static-files.zip') as z: assert z.testzip() is None
for rel, p in files.items():
    dest = REPO / rel; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, dest)
for rel in stale:
    p = REPO / rel
    if p.is_file(): p.unlink()  # only previously managed files, with resolved path checks above
hashes = {rel: hashlib.sha256(p.read_bytes()).hexdigest() for rel, p in sorted(files.items())}
manifest.write_text(json.dumps(hashes, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(f'Released {len(files)} generated files. Backup: {backup}')
