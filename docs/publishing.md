# 新文章发布与数据同步

本仓库是 Hexo + Butterfly 的静态构建产物，没有 Hexo 源工程。Markdown 是源稿记录，**新增 Markdown 不会生成页面**。以下命令均在仓库根目录执行；先阅读 [conventions.md](conventions.md)，再检查工作区，保留不属于本次发布的修改和未跟踪文件。

## 配套脚本与使用说明

脚本已随仓库上传，完整安装、命令示例、参数、输出及排错见 [维护脚本使用说明](../tools/README.md)。

- [分类标签重建脚本](../tools/rebuild_taxonomy.py)
- [页脚、网站资讯与 SEO 同步脚本](../tools/update_footer_seo.py)
- [分类与数据校验脚本](../tools/verify_taxonomy.py)
- [隔离回归检查脚本](../tools/test_maintenance.py)
- [Python 依赖清单](../tools/requirements.txt)

请克隆或下载完整仓库；脚本依赖仓库数据及彼此的模块，不能只下载单个 .py。安装依赖：

```powershell
python -m pip install -r tools/requirements.txt
```

完成以下手工准备后，再按第 5 节顺序运行。脚本在本地运行，上传到 GitHub Pages 不会自动执行。

## 1. 发布前准备

- 确定标题、稳定且唯一的 slug、摘要、封面、发布时间和修改时间。文章 URL 为 `/blog/YYYY/MM/<slug>/`，年月与发布时间对应。
- 新建 `content/posts/<slug>.md`，维护 title、date、updated、categories、tags 等 front matter；正文与 HTML 一致。复制旧稿时不能沿用旧日期或图片。
- 每篇一个主题大类，优先复用现有五类；标签建议 2–6 个具体主题，避免同义重复。唯一登记入口是 `content/taxonomy.json` 的 posts，以 slug 为键；新标签需要时补 tag_slugs。不要只编辑生成的分类清单。
- 发布正文不得包含真实敏感 IP、密钥或服务器凭据；需要脱敏时，正文、代码、截图、图片说明、搜索内容和源稿一起检查。
- 图片使用已确认可访问的图床 URI 或仓库图片；本地封面准备压缩缩略图，元数据使用合适原图。正文占位符要换成实际 img，补 alt；不要把不相关未跟踪图片一起提交。

## 2. 创建文章 HTML（手动）

以现有完整文章页为模板创建 `blog/YYYY/MM/<slug>/index.html`，逐项替换：

- head：title、description、keywords、canonical、og:url/title/description/image、文章发布时间/修改时间、Twitter 字段（模板存在时）。canonical 与 og:url 使用正式域名的目录 URL。
- BlogPosting JSON-LD：headline、description、image、datePublished、dateModified 等真实信息。脚本会补充关联信息，但不会替你写好标题、摘要和日期。
- 正文标题、`#article-container`、封面、可见发布时间/修改时间、目录锚点、代码块、正文图片与图注。
- 版权盒中的本文链接、作者及标题相关信息，标签与分享链接；清理复制模板遗留的旧文章相关推荐。
- 上下篇导航按主题相邻优先，手动检查被连接文章是否需要更新反向链接，不要求严格按日期。
- 沿用当前公共 CSS/JS 和主题结构；不要复制出第二个分类图标、旧页脚、过期侧栏统计或重复 id。

机器时间使用带时区的 ISO 8601，卡片显示按北京时间统一为 `YYYY/MM/DD HH:mm:ss`。不从日期简写猜测时分秒，也不为视觉调整改文章发布时间。

## 3. 手动登记首页、归档与搜索

### 首页和分页

每页固定 **18 篇**，末页允许不足。按发布时间倒序插入首页；第 19 篇移到下一页顶部，逐页后移，必要时建立新页。每个卡片链接、标题、封面、datetime、分类必须对应文章。

- 新增分页时同步所有首页分页的页码、当前页、上一页/下一页链接，以及模板内页面 URL 元数据。
- 当前基线是 43 篇、18/18/7；新增一篇后应是 **44 篇、18/18/8**，这是示例而非永久常量。
- 不通过拉伸卡片或侧栏、补空卡片来对齐底部；侧栏保留原生排列与吸顶。

### 归档

更新总归档及对应年、月归档：条目、标题中的计数、分页、侧栏归档月份及数量。跨年或跨月时创建所需目录；保持各归档原分页规则。维护脚本不会自动建立或重排这些归档。

### 搜索

手动向 `search.xml` 添加完整 entry，字段结构对照现有记录，至少正确提供标题、URL、正文内容；做好 XML 转义或 CDATA 边界处理。**分类脚本只更新已有 entry 的分类/标签，不会创建新 entry 或更新其正文。**

### 最新文章侧栏

历史上批量替换曾破坏嵌套 div，因此默认保留原结构和内容。若本次需要更新最新文章，必须作为单独明确的变更，用配平节点替换并检查文章数量、链接、缩略图、时间及 DOM 结构；不能用任意 `</div>` 作为正则终点。未更新时在发布说明中注明，不宣称自动刷新。

## 4. 数据同步清单

| 数据/位置 | 来源及操作 | 自动化边界 |
|---|---|---|
| 文章 HTML、Markdown | 作者内容，手动创建并核对 | 脚本不生成文章或源稿 |
| 首页和分页 | 完整文章卡片，每页 18 篇 | 手动插入、后移、更新页码 |
| 总/年/月归档及侧栏月份数 | 真实文章日期 | 手动维护条目、计数和分页 |
| 分类、标签归属 | content/taxonomy.json | 先手动登记，再运行 rebuild_taxonomy.py |
| 分类/标签页面、文章分类标签元数据 | taxonomy 与文章 HTML | rebuild_taxonomy.py 重建 |
| 作者卡文章/分类/标签计数、分类列表、标签云 | taxonomy 与文章集合 | rebuild_taxonomy.py 同步 |
| content/分类与标签清单.md | taxonomy | 自动生成，不作为手工登记入口 |
| 已有 Markdown 分类标签 | taxonomy | 自动同步已有稿件，不创建新稿 |
| 搜索 entry 标题/URL/内容 | 新文章内容 | 手动新增；分类标签由脚本补充 |
| 网站资讯文章数 | taxonomy 中 posts 数量 | update_footer_seo.py 同步 |
| 网站最后更新时间 | content/site-info.json 的 updated_at | 手动设为本次真实维护时间，脚本分发 |
| 访客数、浏览量 | 原访问统计服务 | 不编造、不用文章数代替 |
| 卡片时间格式、公共页脚 | 原 datetime、共享模板 | update_footer_seo.py 同步 |
| canonical、og:url、结构化关联 | 页面路径和真实作者/文章信息 | update_footer_seo.py 规范化；文章标题等仍需手动正确填写 |
| sitemap.xml、robots.txt | 已存在的可收录页面 | update_footer_seo.py 生成/维护；不自动创建缺失页面 |
| 上下篇、相关推荐、最新文章 | 主题关系及已发布文章 | 手动核对，最新文章按上节限制处理 |
| 文档概况与测试基线 | 发布后的真实数量 | 更新 docs 概况和测试预期 |

网站更新时间与文章修改时间不同：`content/site-info.json` 使用带时区 ISO 8601，可记录 UTC；文章 dateModified 只反映该篇真实更新。sitemap 不伪造 lastmod，不收录历史独立页、跳转页或 docs。

## 5. 执行顺序

确认上面的手工登记完成，并更新 `content/site-info.json` 后，依次运行（Python 环境需要 beautifulsoup4）：

```powershell
python tools/rebuild_taxonomy.py
python tools/update_footer_seo.py
python tools/verify_taxonomy.py
python tools/test_maintenance.py
git diff --check
```

每一步成功再执行下一步。必须先重建分类，再统一日期、页脚与 SEO；只运行分类脚本可能让分类列表日期暂时回到简写。

**测试基线注意：** 当前 `tools/test_maintenance.py` 写死首页 18/18/7 和总数 43；新增文章时必须依据真实文章集合更新预期，新增分页还要纳入检查。不要删掉数量断言来让测试通过。当前基础分类检查不能代替首页顺序、所有归档和页面视觉检查。

`verify_taxonomy.py <commit>` 会逐篇读取旧提交并检查正文不变，适合已有文章的维护；新文章在旧提交不存在，发布新文章不能直接用该模式检查全部页面。此时运行不带参数版本，另外审查已有文章的 diff。

## 6. 发布前验证

- [ ] blog 文章数、taxonomy 记录数、搜索 entry 数、首页全部分页唯一链接数相等；legacy-html 不计入。
- [ ] 首页各页最多 18 篇，非末页恰好 18 篇，顺序连续、无遗漏重复；所有分页链接可达。
- [ ] 总/年/月归档覆盖新文章，计数及月份正确，分类标签页能找到新文章。
- [ ] 每张首页卡片只有一个分类图标和分类链接；日期完整到秒且时区正确。
- [ ] 作者卡与网站资讯文章数一致；更新时间正确，访问统计由原服务加载。
- [ ] 新文章标题、正文、源稿、摘要、图片、目录、上下篇、版权链接与元数据对应。
- [ ] sitemap 有新文章及新归档/分页，canonical、og:url、JSON-LD 指向正确正式 URL。
- [ ] 两次维护运行结果稳定，diff 未误改旧正文、侧栏结构或用户已有改动。

运行 `python -m http.server 8000`，浏览 `http://localhost:8000/`：检查首页、各分页、新文章、归档、分类标签和搜索；分别检查桌面/手机、浅色/深色，重点看长标题、完整日期、圆角封面及侧栏。静态验证通过不等于浏览器视觉已验证；无法验证时明确说明。

## 7. 提交与线上确认

- 更新 docs/README.md、docs/structure.md 中概况数字，记录 docs/changelog.md；新偏好更新 conventions.md。
- 用 `git status` 和 `git diff` 审核，只暂存本次发布文件；不要顺手提交原有 search.xml 改动或未跟踪图片，先确认其归属。
- 提交后正常 push main，等待 GitHub Pages 部署完成；推送成功不等于线上已更新。
- 在线核对新文章 URL、首页分页、搜索、图片和站点地图；有缓存时强制刷新。出现问题优先正常修复或 revert，不 force push。

## 最新文章同步（2026-09-30 更新）

用户已授权统一更新最新文章，取真实发布时间最新的 5 篇，同时间按首页顺序排列。`python tools/update_recent_posts.py` 可单独运行；`update_footer_seo.py` 已自动调用。优先使用首页缩略图，缺失时使用文章封面。脚本以配平节点只替换最新文章列表，不修改侧栏其他卡片。此规则取代此前默认冻结最新文章的约定。
