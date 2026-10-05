# 目录结构

| 路径 | 用途 |
|---|---|
| `hexo/_config.yml` | 站点、永久链接、18 篇分页、分类标签 slug、插件配置 |
| `hexo/_config.butterfly.yml` | Butterfly 导航、搜索、字数、阅读时间等 |
| `hexo/source/_posts/` | 文章唯一编辑入口；历史 HTML，新文 Markdown |
| `hexo/source/about/` | 关于页源文件 |
| `hexo/source/css/site-preserved.css` | 迁移保留的原 CSS 与现有自定义补丁 |
| `hexo/source/css/cards.css` | 首页卡片定制样式 |
| `hexo/source/_data/site.json` | 网站维护时间 |
| `hexo/themes/butterfly/` | 本地可维护主题，5.7.0，保留许可证 |
| `hexo/scripts/site-data.js` | 保留标签 slug，导出构建模型供校验 |
| `hexo/bin/finalize.py` | 现站格式、缩略图、页脚、导航、SEO 兼容处理 |
| `hexo/bin/verify.py` | 发布前数据与链接校验 |
| `hexo/bin/release.py` | 备份及同步已校验产物；不提交/推送 |
| `hexo/migration/` | 迁移正文基线、旧跳转与原 Markdown 参考 |
| `hexo/package-lock.json` | 锁定插件与依赖版本，用 npm ci 安装 |
| `hexo/public/` | 本地预览产物，忽略入库 |
| 根 `blog/`、`index.html`、`page/`、`archives/` 等 | 自动生成的 Pages 发布内容，不手改 |
| `upload/` | 用户授权的图片备份；前端用图床 |
| `scripts/` | 现有图床工具，凭据不得入库 |
| `tools/`、`content/` | 迁移前维护方式的历史参考，不再驱动构建 |

当前 45 篇文章、5 分类、92 标签；总数以后以 Hexo 构建模型为准。
