# 目录结构

| 路径 | 说明 |
|---|---|
| `blog/YYYY/MM/<slug>/index.html` | 43 篇文章正文页(目录年月与发文时间对应) |
| `index.html` + `page/2/`、`page/3/` | 首页与分页,每页 18 张文章卡,都在 `<div class="recent-post-items">` 容器内 |
| `archives/` | 按年/月归档页(`archives/index.html` 总档 + 年/月子目录) |
| `categories/<slug>/` | 5 个分类页:编程开发 programming、算法与数据结构 algorithms、系统与运维 systems-operations、软件与工具 software-tools、游戏与实践 gaming |
| `tags/<slug>/` | 标签页(83 个;文章页侧栏只显示频次前 20,全部在 `/tags/`) |
| `search.xml` | 本地搜索索引,**发文必须登记**,否则搜不到 |
| `css/index.css` | Butterfly 主题样式;自定义补丁只追加在文件末尾 `2026-09-29 pagination & footer tweaks` 区块 |
| `js/main.js`、`js/utils.js` | 主题 JS(每页加载) |
| `img/` | 站点固定图:avatar.jpg、404.jpg、favicon、friend_404.gif(onerror 兜底图) |
| `upload/` | 图床,中文文件名,HTML 引用时百分号编码 |
| `upload/thumbs/` | 压缩缩略图(2026-09-29 建);`<img>` 一律用它,SEO 元数据用原图,见 conventions.md |
| `content/posts/<slug>.md` | 文章 Markdown 源稿,front matter 含 title/date/categories/tags |
| `content/taxonomy.json` | 分类→slug、标签→slug 的唯一登记处 |
| `content/分类与标签清单.md` | 逐篇分类标签清单(人读) |
| `tools/` | 分类标签维护脚本 `rebuild_taxonomy.py` / `verify_taxonomy.py`,说明见 `tools/README.md` |
| `legacy-html/` | 历史独立页面,不计入文章数,仅同步全局元素 |

## 文章页内部结构(Butterfly)

单行压缩 HTML,关键锚点:

- `<head>`:title → meta description/keywords → og:* → JSON-LD(BlogPosting)→ canonical
- 正文容器:`id="article-container"`
- 正文后依次:版权盒 `post-copyright` → 标签 `tag_share` → **上下篇导航 `<nav class="pagination-post" id="pagination">`** → (部分文章有"相关推荐" `relatedPosts`)
- 侧栏 `aside-content`:作者卡(文章/标签/分类计数)→ 公告 → 目录 → 最新文章 5 篇
- 页脚 `footer#footer`（全站统一，2023 起版权、简介与导航；运行天数已移除）

## 首页卡片

`<div class="recent-post-items">` 内每篇一张 `<div class="recent-post-item">` 大卡(封面+标题+摘要+日期+分类),按时间倒序,页与页之间时间序必须连续。
