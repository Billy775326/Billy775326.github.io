"""Ensure the deploy artifact contains only site output, never repository backups."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
ALLOWED = {'index.html', 'blog', 'archives', 'page', 'tags', 'categories', 'about',
           'css', 'js', 'img', 'legacy-html', 'upload', 'CNAME', 'robots.txt',
           'sitemap.xml', 'search.xml', '.nojekyll', '404.html'}
TYPES = {name: {'.html'} for name in ('blog', 'archives', 'page', 'tags', 'categories', 'about', 'legacy-html')}
TYPES.update({'css': {'.css'}, 'js': {'.js'},
              'img': {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.ico', '.svg'},
              'upload': {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.svg'}})


def check_tree(public=PUBLIC):
    compatibility = json.loads((ROOT / 'source/_data/published-assets.json').read_text(encoding='utf8'))
    allowed_uploads = set(compatibility)
    assert (public / 'index.html').is_file(), 'Missing home page'
    actual_uploads = set()
    for path in public.rglob('*'):
        assert not path.is_symlink(), ('Symlink in deployment', path)
        if not path.is_file():
            continue
        rel = path.relative_to(public).as_posix()
        parts = path.relative_to(public).parts
        assert parts[0] in ALLOWED, ('Unexpected deployment file', rel)
        if parts[0] in TYPES:
            assert path.suffix.lower() in TYPES[parts[0]], ('Unexpected published file type', rel)
        else:
            assert len(parts) == 1, ('Unexpected nested output', rel)
        if rel.startswith('upload/'):
            actual_uploads.add(rel)
            assert rel in allowed_uploads, ('Backup asset leaked', rel)
    assert actual_uploads == allowed_uploads, ('Missing compatibility assets', allowed_uploads - actual_uploads)
    print(f'PASS: deployment boundary; {len(actual_uploads)} explicitly preserved image assets')


if __name__ == '__main__':
    check_tree()
