"""Upload one article's backed-up images; keep credentials outside the repository."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

import requests

from bed_upload_thumbs import BASE, PROXY, token


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--folder', required=True, help='Image-bed category/article directory')
    parser.add_argument('--go', action='store_true', help='Actually upload; default is dry-run')
    args = parser.parse_args()
    root = args.directory.resolve()
    names = ['cover.png', 'body1.png', 'body2.png', 'thumbs/cover.jpg']
    for name in names:
        if not (root / name).is_file():
            parser.error(f'Missing image: {name}')
    manifest = root / 'image-urls.json'
    mapping = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else {}
    if not args.go:
        for name in names:
            print('Existing' if name in mapping else 'Upload', name, '->', args.folder)
        return
    session = requests.Session()
    session.trust_env = False
    session.proxies = {'https': PROXY}
    session.headers['Authorization'] = 'Bearer ' + token()
    for name in names:
        if name in mapping:
            continue
        folder = args.folder + ('/thumbs' if name.startswith('thumbs/') else '')
        mime = 'image/jpeg' if name.endswith('.jpg') else 'image/png'
        try:
            with (root / name).open('rb') as stream:
                response = session.post(
                    BASE + '/upload',
                    params={'uploadFolder': folder, 'uploadNameType': 'origin', 'returnFormat': 'full'},
                    files={'file': (Path(name).name, stream, mime)}, timeout=(15, 120),
                )
            response.raise_for_status()
            item = response.json()[0]
            url = item.get('publicUrl') or item.get('src', '')
            if url.startswith('/'):
                url = BASE + url
            parsed = urlsplit(url)
            if parsed.scheme != 'https' or parsed.netloc != urlsplit(BASE).netloc:
                raise ValueError('Unexpected image host')
        except Exception as exc:
            # Do not print request objects, headers or credentials.
            raise SystemExit(f'Upload failed for {name}: {type(exc).__name__}') from None
        mapping[name] = url
        manifest.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('Uploaded', name, flush=True)


if __name__ == '__main__':
    main()
