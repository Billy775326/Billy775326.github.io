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

仍需作者维护：标题/摘要/正文、真实日期、分类标签、图片 URI、永久链接、需要主题关联时的 `related_nav`。访问量来自原不蒜子服务，不使用文章数代替；阅读时间是估计值。

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
5. 等待 GitHub Pages 成功，检查线上新文章、首页、搜索、图片和 sitemap。

## 校验与回滚

`npm --prefix hexo run verify` 检查现有构建：迁移文章的原链接/日期/正文、全部分页、搜索条数、分类标签、字数显示、内部导航、SEO。

`python hexo/bin/test_new_post.py` 在临时副本里新增 Markdown，验证 50 篇时 18/18/14，并检查重复构建结果一致。不发布测试文章。这个迁移回归用例的 50 篇基线需随真实文章数量调整；日常 verify 按实际文章数动态检查。

迁移前完整备份在本机 `E:/pycoding/backups/blog-before-hexo-20261004-205234/`：repository.bundle、working-tree.zip、SHA-256 manifest。迁移前提交为 `4a15c30`。后续每次 release 另有静态文件备份。

线上回滚首选对迁移发布提交正常 `git revert` 并推送；保留原文件和源工程的 Git 历史。不要 force push，也不要用未核实路径进行递归删除。
