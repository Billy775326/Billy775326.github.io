# 新文章发布与数据同步

适用于 2026-10-05 起的 Hexo 源工程；取代手工维护首页、分类和搜索的旧流程。

## 初次安装

在仓库根目录执行（已验证 Node.js 24；Python 3）：

```powershell
npm --prefix hexo ci
python -m pip install -r hexo/requirements.txt
```

本机 npm 默认缓存受限时，可加 `--cache E:/pycoding/.npm-cache`。不把本机缓存路径写死到项目。

## 写文章

```powershell
npm --prefix hexo run new -- "文章标题"
```

编辑 `hexo/source/_posts/` 下新建的 Markdown。至少补齐：

```yaml
---
title: 清楚描述主题的标题
date: "2026-10-05T12:00:00+08:00"
updated: "2026-10-05T12:00:00+08:00"
permalink: blog/2026/10/example-post/
description: 真实说明本文适用条件、解决的问题和覆盖范围。
categories:
  - 系统与运维
tags:
  - Docker
cover: https://img.iowill.com/实际封面地址
thumbnail: https://img.iowill.com/实际缩略图地址
---
```

示例时间和地址必须改为真实值。永久链接发布后不要随意更改；大类五选一，细化标签 2–6 个。未来日期和 draft 不会公开。新文章正文不要重复写 H1。

图片先备份 `upload/文章名/`，再上传图床，cover 使用原图、thumbnail 使用缩略图，正文使用图床 URI。上传工具继续在 `scripts/`，Token 只在本机读取，不入库。

### 配图完成后再发布（2026-10-08 补充）

已约定专属配图的文章，必须完成封面、正文插图和封面缩略图后再发布；不能自行改用默认封面或删除占位符来跳过步骤。只有用户明确要求先发无图版本时才例外。

1. 根据文章主题生成配图，查看最近 6–9 篇封面，避免重复主体、构图和配色组合。全站以淡彩描边、圆润造型、柔和阴影为基础；分类只调整结构感、空间感和场景气质，不绑定固定物件。
2. 原图及提示词备份到 `upload/文章名/`。核对技术图的文字、名称大小写、箭头与正文一致。生成最长边不超过 1000px、JPEG q80 的封面缩略图。
3. 上传到 `img.iowill.com`，保存 `image-urls.json`，替换 cover、thumbnail 以及正文占位，补充描述性 alt 和图注。
4. 检查生成文章确实含有预期数量的正文图片，图床响应可解码为图片；核对首页、侧栏、分享元数据使用专属封面，桌面和手机均可显示。

本次三图方案可使用以下上传工具（Python 需安装 `requests`）；读取仓库外的 `E:/tmp/bed_token.txt`，默认干跑，`--go` 才上传：

```powershell
python scripts/upload_article_images.py "upload/文章名" --folder "编程开发/文章名"
python scripts/upload_article_images.py "upload/文章名" --folder "编程开发/文章名" --go
```

该工具上传 `cover.png`、`body1.png`、`body2.png`、`thumbs/cover.jpg`，按已保存映射跳过已上传文件；复用 `BED_STATE` 与 `BED_PROXY` 配置，默认使用本机代理。替换已发布图片时应另行规划版本文件，不能把旧 URI 映射当作新图上传成功。

历史 `.html` 文章可直接编辑正文 HTML。`legacy_html: true` 表示仍与迁移基线保持原样；首次有意修改正文时设为 `false` 并更新 `updated`，校验仍检查原永久链接和发布时间。三篇原 Markdown 另存 `hexo/migration/original-markdown/` 供参考，不是第二份发布输入。不要直接将复杂历史 HTML 自动反转成 Markdown。

## 构建与预览

```powershell
npm --prefix hexo run build
npm --prefix hexo run preview
```

访问 http://127.0.0.1:4000/；Ctrl+C 停止。预览展示完成兼容处理的 `public/`，修改后重新构建；不要单独 `hexo generate` 后直接发布。

自动同步：文章页、首页 18 篇分页、总/年/月归档、分类标签及计数、最近 5 篇、search.xml、sitemap.xml、代码块、字数、预计阅读时间、网站总字数。兼容脚本维护缩略图、秒级日期、透明页脚、JSON-LD、历史标签 URL 和上下篇卡片。

仍需作者维护：标题/摘要/正文、真实日期、分类标签、图片 URI、永久链接。底部上下篇按发布时间自动生成，不再配置 `related_nav`。访问量来自原不蒜子服务，不使用文章数代替；阅读时间是估计值。

## 发布

1. 更新 `hexo/source/_data/site.json` 的 `updated_at`，使用带时区的真实维护时间。
2. 检查桌面/手机、深浅色、新文章、搜索、底部卡片与上一页/下一页。
3. 执行：

```powershell
npm --prefix hexo run release
git diff --check
git status --short
```

release 会先校验并在仓库外 `../backups/hexo-release-时间/` 备份待覆盖文件，再复制到根目录。仅清理上次 release-manifest 中已不存在的受管文件，不删除源文件、docs、upload 或其他未跟踪内容。

4. 审核并提交本次源文件与生成产物，再正常 `git push origin main`。不要无差别加入与本次无关的图片。
5. 等待 `Build and deploy blog` 工作流成功，检查线上新文章、首页、搜索、图片和 sitemap。工作流从源工程重新构建，仅上传 `hexo/public`，不再发布仓库根目录。

### 发布目录与索引边界（2026-10-14）

- GitHub 仓库 Settings → Pages → Build and deployment 的 Source 使用 **GitHub Actions**；不要改回 Deploy from a branch，否则源稿和备份会重新暴露在博客域名下。
- 工作流 `.github/workflows/pages.yml` 使用 Node.js 24 / Python 3.12，执行 npm ci、安装 Python 依赖、build + verify，再上传 `hexo/public`。部署失败时保留上一次已成功的 Pages 版本。
- 本地仍执行 release，以保留发布前校验、生成产物审阅与自动备份。不要手改生成产物：CI 会从源文件重新构建。
- `hexo/bin/check_publish_tree.py` 限制发布目录，拒绝源码、文档、压缩备份和未列入白名单的 upload 文件。现有六张旧资源（两张在用封面/标识及四张已恢复的历史插图）通过 `hexo/source/upload/` 保留原路径，白名单为 `_data/published-assets.json`；新增文章仍使用图床。
- `legacy-html/` 的历史独立页保持可访问，但输出 `noindex, follow` 且不进入 Sitemap。不将 robots.txt 改为禁止抓取该目录，以便爬虫能读取 noindex。
- 网站域名不再提供 `/hexo/`、`/docs/`、`/scripts/` 和整库 `/upload/` 内容；公开 GitHub 仓库仍可查看源文件，这不是仓库私有化。
- 回滚内容优先正常 git revert + push，由工作流重建。若必须恢复旧的分支发布方式，应先确认根目录内容，并知晓整库源稿会重新对外可访问。

### 图片尺寸与模板校验

- 正文图片真实尺寸保存在 `hexo/source/_data/image-dimensions.json`，按原 src URL 记录 width/height。新增或替换图片时从实际文件读取尺寸后更新；不得猜测或拉伸图片。构建不依赖图床网络请求。
- finalizer 只补充正文图片的尺寸和加载提示；历史保真校验只忽略这些呈现属性，仍核对文本、图片地址、alt 和链接。
- 首页前三张卡片封面正常加载，其余原生懒加载；JSON-LD 不允许空块，作者链接使用 /about/。
- 修改这类模板后执行 `python hexo/bin/test_publish_tree.py`、`npm --prefix hexo run build`，涉及发布流程时再运行 `python hexo/bin/test_new_post.py` 检查临时新文与重复构建一致性。
- `scripts/site-data.js` 在处理文章前将 Node 进程时区统一为站点配置时区，避免 Hexo 8 对已有时区的 ISO 时间二次偏移。回归检查分别以 UTC、Asia/Shanghai 启动构建，输出必须一致；不得靠改写原文章 date 来绕过检查。

## 校验与回滚

`npm --prefix hexo run verify` 检查现有构建：迁移文章的原链接/日期/正文、全部分页、搜索条数、分类标签、字数显示、内部导航、SEO。

`python hexo/bin/test_new_post.py` 在临时副本里新增 Markdown，验证 40 篇时 18/18/4，并检查重复构建结果一致。不发布测试文章。这个迁移回归用例的 40 篇基线需随真实文章数量调整；日常 verify 按实际文章数动态检查。

迁移前完整备份在本机 `E:/pycoding/backups/blog-before-hexo-20261004-205234/`：repository.bundle、working-tree.zip、SHA-256 manifest。迁移前提交为 `4a15c30`。后续每次 release 另有静态文件备份。

线上回滚首选对迁移发布提交正常 `git revert` 并推送；保留原文件和源工程的 Git 历史。不要 force push，也不要用未核实路径进行递归删除。

## 删除已发布文章

先备份源文件，再删除 `_posts` 中对应文章。原迁移基线保留；用户明确删除的历史文章记录于 `hexo/migration/removed-posts.json`，校验要求它们不再生成。清理 related_nav 和历史独立页面的相关入口，更新网站维护时间后执行 release；受管的旧文章和空标签输出由发布脚本移除。检查搜索、sitemap、分页和线上旧链接 404，再确认发布完成。
