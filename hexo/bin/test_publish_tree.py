"""Make sure an accidentally generated source/backup file cannot be deployed."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from check_publish_tree import ROOT, check_tree


class PublishBoundaryTests(unittest.TestCase):
    def test_rejects_source_and_unlisted_backups(self):
        with tempfile.TemporaryDirectory(prefix='blog-publish-check-') as temporary:
            public = Path(temporary).resolve()
            (public / 'index.html').write_text('<html></html>', encoding='utf8')
            for rel in json.loads((ROOT / 'source/_data/published-assets.json').read_text(encoding='utf8')):
                path = public / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'fixture')
            with contextlib.redirect_stdout(io.StringIO()):
                check_tree(public)
            for rel in ['hexo/source/_posts/private.md', 'docs/publishing.md', 'upload/backup.zip', 'upload/unlisted.jpg', 'blog/source.md', 'css/private.json', 'js/backup.tar.gz', 'img/README.MD']:
                path = public / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('must not deploy', encoding='utf8')
                with self.assertRaises(AssertionError, msg=rel):
                    check_tree(public)
                path.unlink()


if __name__ == '__main__':
    unittest.main()
