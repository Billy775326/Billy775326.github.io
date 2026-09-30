# 发布新文章检查单

静态站没有构建流程,"发布" = 手工把新内容登记到全站各处。**漏一步就会版式错位**——2026-09-29 曾发生:只往首页头部插卡、没把第 18 篇后移,首页变成 19 篇。按下面顺序执行。

## 1. 文章页

新建 `blog/YYYY/MM/<slug>/index.html`。从最近一篇文章复制整页结构再替换:

- `<title>`、meta description / keywords、og:* 全套、JSON-LD(headline/description/image/dates/url)、canonical
- 正文写进 `id="article-container"`
- 上下篇导航卡(模板见 [conventions.md](conventions.md))
- 文内插图放 `upload/`,先压缩

## 2. 首页分页（每页 18 篇）

- 每页固定 18 篇，末页允许不足；新增文章插入首页顶部，溢出的最后一篇依次移至下一页顶部，必要时新增分页。
- 当前 43 篇分布为 18/18/7，必须校验顺序、总数、无重复遗漏及页码链接。
- 不强制文章列表与网站资讯底部对齐；侧栏使用主题原布局和吸顶行为。

## 3. 全站登记

- `archives/` 对应年/月页加条目(没有对应年/月目录就按现有结构新建)
- `tags/<标签>/`、`categories/<分类>/` 对应页加条目
- 更新全站文章/标签计数；侧栏“最新文章”保留原结构与内容，未经单独验证不得批量刷新（见侧栏回滚记录）。
- `search.xml` 增加新文章条目(格式对照现有条目)

## 4. 分类标签

- 在 `content/taxonomy.json` 和 `content/分类与标签清单.md` 登记,或直接跑:
  ```bash
  python tools/rebuild_taxonomy.py && python tools/verify_taxonomy.py
  ```
  脚本会重建分类标签页、侧栏计数、搜索元数据并同步 md 源稿,不改正文,重复执行无副作用
- 文章源稿存 `content/posts/<slug>.md`(front matter 与 taxonomy 一致)

## 5. 上下篇接链

导航按**主题相邻**优先(不强求时间序)。新文章插入后,手动调整相邻文章的 prev/next 卡指向,保持全站链条完整、不留断链/死链。

## 6. 发完自查

- `git diff` 逐文件确认没有误伤
- 本地 `python -m http.server` 过一遍:新文章页、三张首页、archives、tags/categories、搜索能否搜到
- 执行 `python tools/update_footer_seo.py`，同步页脚、结构化数据及站点地图；canonical、og:url 与 sitemap 统一使用目录 URL。
- 确认无误再 push main(推上去立即生效)

- 发布前将 `content/site-info.json` 的 `updated_at` 更新为本次实际更新时间（ISO 8601 含时区），再运行 `python tools/update_footer_seo.py`。网站资讯文章数从 taxonomy 自动读取，访问统计由原统计服务提供。
