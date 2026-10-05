# Billy 博客 Hexo 源工程

Hexo 8.1.2 / Butterfly 5.7.0。原文章永久链接、内容、图片与时间均迁移保留。

```powershell
npm ci
python -m pip install -r requirements.txt
npm run build
npm run preview
# 验证后生成根目录发布产物（自带备份，不自动 push）
npm run release
```

详细流程：[发布文档](../docs/publishing.md)。源工程不是生成产物副本：文章模型、首页、分页、归档、标签、搜索、统计由 Hexo 与插件重新生成，源文章更新可驱动整个站点。

## 已安装插件

| 插件 | 用途 |
|---|---|
| hexo-generator-searchdb 1.5.0 | 本地搜索索引，Butterfly 搜索界面 |
| hexo-generator-sitemap 3.0.1 | sitemap，后处理补全归档/分页，保留真实文章修改时间 |
| hexo-wordcount 6.0.1 | 字数、预计阅读时间和全站总字数 |
| hexo-generator-index/archive/category/tag | 自动首页、18 篇分页、归档、分类与标签 |
| hexo-renderer-marked/pug/stylus | Markdown、主题模板和样式渲染 |
| hexo-server | 备用 Hexo 开发服务器；日常 preview 使用最终产物避免漏过后处理 |

不蒜子继续显示真实 PV/UV。没有虚构今日访客、热门排行或新增未配置账号的分析平台。字数按插件的中英文计数规则统计，阅读时间仅为估计。

## 保真迁移

迁移前仅有 3 篇 Markdown，故 45 篇统一导入带 front matter 的 `.html`，不做有损反向转换。它们是 Hexo 可编辑的文章源文件，不是整页静态快照；头部、侧栏、统计、列表均重新生成。`disableNunjucks: true` 防止代码正文被当作模板执行。新文用 Markdown。

`source/css/site-preserved.css` 保留既有主题 CSS/定制，不直接修改根 CSS。`themes/butterfly` 为可审阅的本地主题副本，禁止修改 node_modules。图床图片引用保持原 URI。

## 环境与依赖

已在 Node.js 24 + Python 3 下验证，提交 package-lock.json，使用 npm ci 保持版本一致。Python 需 beautifulsoup4。

2026-10-05 安装审计发现上游 braces <=3.0.3 的深层模式栈耗尽问题（GHSA-vfj7-8cjw-p6xm），导致 Hexo/搜索/站点地图依赖链共 9 个 high 报告；注册表当前最新版仍为 3.0.3。未使用会降级 Hexo 的 audit fix --force。依赖仅在本机构建时执行，不随静态网页发送给访客；仅对可信仓库内容构建，后续有兼容修复版本时升级锁文件并重跑测试。不要把预览服务器暴露公网。

官方参考：[Hexo front matter](https://hexo.io/docs/front-matter)、[Hexo 配置](https://hexo.io/docs/configuration)、[Butterfly](https://butterfly.js.org/)。
