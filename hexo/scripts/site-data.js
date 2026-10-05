'use strict';
const fs = require('node:fs');
const path = require('node:path');

// Existing tag URLs include spaces (e.g. Docker Compose). Hexo's default slugize
// would silently change those URLs. Preserve names and explicitly mapped slugs.
hexo.model('Tag').schema.virtual('slug').get(function () {
  return hexo.config.tag_map[this.name] || this.name;
});
const postTagGetter = hexo.model('Post').schema.path('tags').getter;
hexo.model('Post').schema.path('tags').get(function () {
  return postTagGetter.call(this).sort('name', 1);
});

// Database insertion order is asynchronous. Break date/size ties consistently
// so a clean rebuild cannot shuffle navigation, recent posts, tags or search.
for (const [name, sort] of Object.entries({
  posts: {date: -1, migration_order: 1, slug: 1},
  pages: {path: 1}, tags: {name: 1}, categories: {name: 1}
})) {
  const original = hexo.locals.getters[name];
  hexo.locals.set(name, () => original().sort(sort));
}

// Feed the post-build verifier from Hexo's actual models, not a second hand-maintained list.
hexo.extend.filter.register('after_generate', function () {
  const posts = hexo.locals.get('posts').sort('date', -1).toArray().map(p => ({
    title: p.title, path: p.path.replace(/^\/+/, "").replace(/\/$/, "/index.html"), slug: p.slug, date: p.date.toISOString(),
    updated: p.updated.toISOString(), description: p.description || '',
    cover: p.cover, thumbnail: p.thumbnail || p.cover,
    categories: p.categories.toArray().map(c => ({name: c.name, path: c.path})),
    tags: p.tags.toArray().map(t => ({name: t.name, path: t.path})),
    related_nav: p.related_nav || [], legacy_html: !!p.legacy_html
  }));
  const dir = path.join(hexo.base_dir, '.cache');
  fs.mkdirSync(dir, {recursive: true});
  fs.writeFileSync(path.join(dir, 'posts.json'), JSON.stringify(posts, null, 2));
});
