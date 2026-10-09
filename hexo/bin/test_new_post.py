"""Exercise publication in an isolated source copy; never touches live source/output."""
from pathlib import Path
import json, shutil, subprocess, tempfile, sys, hashlib
from datetime import datetime, timezone
from bs4 import BeautifulSoup as B

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='billy-hexo-test-') as temp:
    test = Path(temp)
    for name in ['source', 'scripts', 'themes', 'migration', 'bin']:
        shutil.copytree(ROOT / name, test / name)
    for name in ['package.json', '_config.yml', '_config.butterfly.yml']:
        shutil.copy2(ROOT / name, test / name)
    # Copy dependencies as well: Windows symlinks require privileges, and a real
    # isolated directory makes cleanup safe. npm is not contacted during this test.
    shutil.copytree(ROOT / 'node_modules', test / 'node_modules')
    (test / 'source/_posts/migration-test.md').write_text('''---
title: Migration fixture
date: "2026-10-04T10:08:00+00:00"
updated: "2026-10-04T10:08:00+00:00"
description: Temporary publishing regression fixture
permalink: blog/2026/10/migration-test/
categories: [系统与运维]
tags: [Docker]
---

## Markdown rendering

Temporary **test** post.

```bash
echo hello
```
''', encoding='utf8')
    hexo = test / 'node_modules/hexo/bin/hexo'
    def build():
        subprocess.run(['node', str(hexo), 'clean'], cwd=test, check=True, stdout=subprocess.PIPE)
        subprocess.run(['node', str(hexo), 'generate'], cwd=test, check=True, stdout=subprocess.PIPE)
        for name in ['finalize.py', 'verify.py']:
            subprocess.run([sys.executable, str(test / 'bin' / name)], cwd=test, check=True, stdout=subprocess.PIPE)
    build()
    pages = ['index.html', 'page/2/index.html', 'page/3/index.html']
    counts = [len(B((test/'public'/p).read_text(encoding='utf8'),'html.parser').select('.recent-post-item')) for p in pages]
    assert counts == [18, 18, 8], counts
    page = B((test/'public/blog/2026/10/migration-test/index.html').read_text(encoding='utf8'), 'html.parser')
    assert page.select_one('#article-container strong').text == 'test'
    assert page.select_one('figure.highlight') is not None
    def hashes(): return {p.relative_to(test/'public').as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in (test/'public').rglob('*') if p.is_file()}
    before=hashes();build();after=hashes()
    assert before == after, [p for p in before if before[p] != after.get(p)]
print('PASS: new Markdown post, 44 posts, 18/18/8, automatic search/taxonomy/statistics, reproducible builds')
