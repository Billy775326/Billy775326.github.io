# 发布维护脚本使用说明

这些脚本已随仓库提交在 `tools/`，配合 [新文章发布与数据同步](../docs/publishing.md) 使用。它们维护静态 HTML，不是 Hexo 构建器，也不会自动把 Markdown 发布成文章。

## 获取完整脚本与安装依赖

在 GitHub 仓库页面使用 Code → Download ZIP 并解压，或克隆整个仓库：

```powershell
git clone https://github.com/Billy775326/Billy775326.github.io.git
cd Billy775326.github.io
python --version
python -m pip install -r tools/requirements.txt
```

已有仓库请直接进入其根目录，不必重复克隆。建议 Python 3.10 或更新版本；唯一第三方依赖是 Beautiful Soup，其他模块来自标准库。Windows 若只提供 `py`，可将下面的 `python` 换成 `py -3`；macOS/Linux 可使用 `python3`。

需要隔离依赖时先运行 `python -m venv .venv`，再用 `.venv/Scripts/python.exe`（Windows）或 `.venv/bin/python`（macOS/Linux）执行安装和后续命令。不要提交虚拟环境。

**不要只下载一个脚本运行：** 脚本之间存在导入关系，且依赖仓库中的 content、blog、分类标签、搜索索引等数据；保持仓库目录结构。

## 脚本入口与作用

| 脚本 | 调用方式 | 是否修改站点 |
|---|---|---|
| [rebuild_taxonomy.py](rebuild_taxonomy.py) | `python tools/rebuild_taxonomy.py` | 是：重建分类/标签页面、分类标签元数据、作者卡统计、已有搜索条目分类标签、已有源稿分类标签和清单 |
| [update_footer_seo.py](update_footer_seo.py) | `python tools/update_footer_seo.py` | 是：同步页脚、网站资讯、卡片完整时间、canonical/og:url、结构化关联、sitemap/robots |
| [verify_taxonomy.py](verify_taxonomy.py) | `python tools/verify_taxonomy.py` | 否：检查文章/分类/标签/搜索覆盖、计数、链接和跳转 |
| [test_maintenance.py](test_maintenance.py) | `python tools/test_maintenance.py` | 不改工作站点：在临时副本运行维护及幂等性回归，完成后清理副本 |
| [add_about_page.py](add_about_page.py) | `python tools/add_about_page.py` | 是：维护关于页和相关导航；普通发文不需要运行，运行前审查是否会覆盖手工修改 |
| [requirements.txt](requirements.txt) | `python -m pip install -r tools/requirements.txt` | 安装当前 Python 环境依赖，不改文章 |

除 verify 的可选提交参数外，上述脚本不提供命令行参数，也没有统一的 `--dry-run` 模式。不要把未知参数当作预览功能。

## 一次发布的运行示例

先手动创建文章 HTML/源稿、登记 taxonomy、新增搜索 entry、调整首页和归档分页，详见发布文档。更新 `content/site-info.json` 的 `updated_at` 为真实维护时间，例如带时区的 `2026-09-30T10:30:00+08:00`（仅格式示例，不要重复使用这个固定时间）。

```powershell
python tools/rebuild_taxonomy.py
python tools/update_footer_seo.py
python tools/verify_taxonomy.py
python tools/test_maintenance.py
git diff --check
git status --short
```

每条命令检查退出码和输出，失败后先修复，不继续发布。顺序不可颠倒：日期规范化必须在分类重建之后执行。

正常输出包括分类重建的 JSON 计数、SEO 同步的 `Updated pages` / `Sitemap URLs`、校验的 `PASS`。重复维护应保持结果稳定；网站更新时间不会自动每次变成当前时间，需要发布者显式更新。

脚本不会创建新文章、增加搜索 entry、排列首页/归档分页或自动刷新最新文章侧栏。脚本完成后仍需浏览器检查、审查 diff、提交、推送并确认 Pages 部署。

## 校验参数和测试基线

已有文章的纯维护可额外执行：

```powershell
python tools/verify_taxonomy.py HEAD
```

`HEAD` 可替换为修改前的真实提交哈希；需要 Git 可用及该提交存在。此模式还检查正文、标题和文章日期不变。新增文章在旧提交中不存在，不能直接使用此模式，改用不带参数的验证并单独审查旧文章 diff。

当前 `test_maintenance.py` 有 43 篇与 18/18/7 的固定预期。新增第 44 篇需更新为 44 和 18/18/8；如果新增分页，还需纳入该页。它会检查分类图标、网站资讯、日期、缩略图、内容保留、canonical/sitemap 与幂等性，但不能代替视觉验证或完整归档检查。

## 常见问题

- `No module named bs4`：用执行脚本的同一个 Python 运行 `python -m pip install -r tools/requirements.txt`。
- 文件不存在：确认获取完整仓库并从根目录执行示例；不要移动 tools 或删除依赖数据文件。
- taxonomy 出现 KeyError/断言失败：检查新文章目录 slug 与 posts 键、分类名称和标签登记是否一致。
- 搜索条目数量失败：手动补齐 search.xml，检查重复 URL、XML 转义；重建脚本不会补写新 entry。
- 分页断言失败：先核实真实文章数与各页链接，再调整测试基线；不能仅删除断言。
- 幂等性失败或旧内容变化：检查脚本输出和 diff，定位原因后再发布，不把错误结果直接推到 main。

脚本和文档一起通过 Git 提交发布；GitHub Pages 不会在服务器端执行 Python。源文件链接用于查看/下载，实际维护在本地进行。
