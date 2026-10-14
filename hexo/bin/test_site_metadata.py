"""Regression checks for collection descriptions, archive policy and image hints."""
import unittest

from bs4 import BeautifulSoup

from site_metadata import archive_noindex, normalize_images, page_description, valid_schema


class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.posts = [{
            'date': '2026-09-30T20:00:00Z',
            'categories': [{'name': '编程开发', 'path': 'categories/programming/'}],
            'tags': [{'name': 'C++', 'path': 'tags/cpp/'}],
        }]

    def test_archive_policy_is_idempotent_and_preserves_body(self):
        body = '<body><pre>  old\n text &amp; code  </pre><time datetime="2020-01-01">旧时间</time></body>'
        raw = '<html><head><meta name="ROBOTS" content="index"><title>存档</title></head>' + body + '</html>'
        result = archive_noindex(raw)
        self.assertEqual(result.split('</head>', 1)[1], raw.split('</head>', 1)[1])
        self.assertEqual(result, archive_noindex(result))
        tags = BeautifulSoup(result, 'html.parser').select('meta[name="robots"]')
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0]['content'], 'noindex,follow')

    def test_collection_counts_and_beijing_archive_month(self):
        self.assertIn('“C++”标签', page_description('/tags/cpp/', self.posts))
        self.assertIn('1 个分类', page_description('/categories/', self.posts))
        self.assertIn('共 1 篇', page_description('/archives/2026/10/', self.posts))
        self.assertIn('共 0 篇', page_description('/archives/2026/09/', self.posts))
        self.assertIn('第 2 页', page_description('/archives/2026/page/2/', self.posts))
        self.assertIn('第 19–20 篇', page_description('/page/2/', self.posts * 20))
        self.assertIsNone(page_description('/about/', self.posts))

    def test_empty_and_nonobject_schema_blocks_are_rejected(self):
        for value in ['', 'undefined', 'null', '{}', '[]', '{"@graph": []}', '"text"']:
            with self.subTest(value=value):
                self.assertIsNone(valid_schema(value))
        self.assertEqual(valid_schema('{"@type":"BlogPosting"}')['@type'], 'BlogPosting')

    def test_image_hints_do_not_claim_layout_sizes_as_source_sizes(self):
        covers = ''.join(f'<div class="post_cover"><img src="cover{i}.jpg"></div>' for i in range(5))
        html = (f'<div id="recent-posts">{covers}</div><aside><img src="side.jpg"></aside>'
                '<article id="article-container"><img src="https://example.com/%E5%9B%BE.png" alt="图">'
                '<img src="unknown.jpg"></article>')
        soup = BeautifulSoup(html, 'html.parser')
        normalize_images(soup, {'https://example.com/图.png': {'width': 1280, 'height': 720}})
        self.assertEqual([i['loading'] for i in soup.select('.post_cover img')], ['eager'] * 3 + ['lazy'] * 2)
        self.assertEqual(soup.select_one('aside img')['loading'], 'lazy')
        known, unknown = soup.select('#article-container img')
        self.assertEqual((known['width'], known['height']), ('1280', '720'))
        self.assertEqual(known['src'], 'https://example.com/%E5%9B%BE.png')
        self.assertEqual(known['alt'], '图')
        self.assertNotIn('width', unknown.attrs)
        self.assertTrue(all('width' not in i.attrs for i in soup.select('.post_cover img')))
        self.assertTrue(all(i['decoding'] == 'async' for i in soup.select('img')))

    def test_dimensions_must_be_measured_positive_integers(self):
        for size in [{'width': 0, 'height': 200}, {'width': '100', 'height': 200}, {'width': True, 'height': 200}]:
            with self.subTest(size=size):
                soup = BeautifulSoup('<div id="article-container"><img src="x"></div>', 'html.parser')
                with self.assertRaises(ValueError):
                    normalize_images(soup, {'x': size})


if __name__ == '__main__':
    unittest.main()
