# 站点维护说明

## 当前架构（2026-10-05 起）

用户已授权恢复 Hexo 源工程并迁移发布流程。本条取代此前“禁止引入构建、直接维护 HTML”的旧限制。

- `hexo/` 是唯一可编辑源工程：Hexo 8.1.2 + Butterfly 5.7.0。
- 根目录 HTML/CSS/JS 是 GitHub Pages 发布产物，不直接修改。`main` 推送后仍由 Pages 发布，不改变现有域名 iowill.com。
- `hexo/source/_posts/` 为文章源文件。45 篇历史文章保留为带 front matter 的 HTML，保留正文、代码、图片、锚点与永久链接；新文章使用 Markdown。
- 分类标签以文章 front matter 为准，slug 映射在 `hexo/_config.yml`。根 `content/` 仅保留迁移前记录，不再作为生成输入。
- `npm --prefix hexo run build`：生成、兼容处理、校验。`npm --prefix hexo run release`：再次构建校验、备份后更新根发布目录，不自动提交或推送。
- 每页固定 18 篇，当前 45 篇 / 5 分类 / 92 标签、18/18/9。数字由构建产生，不手工维护文章列表。
- 不运行旧 `tools/` 静态批处理：它们不适用于含源工程的目录，已加防误用提示。
- 文章正文的修改时间只在内容实际修改时更新；网站维护时间修改 `hexo/source/_data/site.json`。
- 图片备份仍放 `upload/文章名/`，前端引用图床。令牌、密码、服务器真实 IP 不入库。

## 文档索引

- [publishing.md](publishing.md)：新文章、预览、发布和回滚。
- [structure.md](structure.md)：源工程及构建产物。
- [conventions.md](conventions.md)：外观、图片和 SEO 约定，按最新日期优先。
- [changelog.md](changelog.md)：历史变更。
- [../hexo/README.md](../hexo/README.md)：环境、插件及迁移说明。

用户新要求完成后，继续当天更新约定和变更记录。全站 UTF-8 / LF；不得提交 node_modules、public、临时文件和凭据。
