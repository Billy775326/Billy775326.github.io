# CLAUDE.md

本仓库是 Hexo + Butterfly 构建产物的**纯静态博客**(GitHub Pages):仓库内没有 Hexo 源工程,禁止引入构建流程;一切改动直接编辑静态 HTML/CSS/JS,推 `main` 即上线,没有预览环境。

**开始任何改动前,先读 [docs/README.md](docs/README.md)**,按任务再读:

- 发新文章 / 首页分页(18 篇/页链式后移)→ `docs/publishing.md`
- 导航卡模板 / 图片缩略图 / IP 文档地址 / TDK / 页脚 / 代码块约定 → `docs/conventions.md`
- 目录结构 → `docs/structure.md`
- 分类标签 → `tools/README.md`

两条铁律:

1. **对话中用户提出的新要求/偏好/否决,执行完必须回写 `docs/changelog.md` 和(如是长期约定)`docs/conventions.md`**——docs 是约定的唯一事实来源。
2. 批量修改用 Python + 正则,脚本必须幂等,改完 `git diff` 校验;git 提交**不加** AI 署名(Co-Authored-By 等)。
