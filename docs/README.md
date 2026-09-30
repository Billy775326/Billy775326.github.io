# docs — 面向 AI 助手的站点说明

> 本目录性质类似"记忆文件":供任何 AI 助手(Claude Code / Cursor / 其他 agent)在改动本仓库前快速理解约束与流程。人类读者看仓库根 `README.md` 即可。

## 硬约束(先读这个)

1. 本仓库是 Hexo 8.1.2 + Butterfly 5.7.0 **构建产物的静态站**,仓库内**没有 Hexo 源工程**。不要尝试 `hexo generate`、不要引入构建流程——一切改动直接编辑静态 HTML/CSS/JS。
2. 推送到 GitHub `main` 分支后由 GitHub Pages 部署，必须等待部署完成并核对线上；仓库没有本地 Hexo 构建流程。
3. 全站 UTF-8、LF 行尾。批量修改使用配平节点边界，避免用正则跨越嵌套 div；脚本必须**幂等**(重复执行不产生二次变化),改完用 `git diff` 校验结构与数量。
4. `legacy-html/` 是历史独立页面,不计入 44 篇文章,仅同步页脚/导航等全局元素;`tools/__pycache__/` 忽略不提交。
5. 本目录(`docs/`)会随 Pages 公开可访问,不要在里面写任何敏感信息(IP、密钥、服务器细节)。

## 文档索引

- [structure.md](structure.md) — 目录结构与关键文件
- [publishing.md](publishing.md) — 发布新文章的完整流程、手动/自动数据同步矩阵、18 篇分页及测试基线注意事项
- [conventions.md](conventions.md) — 导航卡模板、图片/缩略图、IP 约定、SEO(TDK)、页脚、代码块的既定约定
- [changelog.md](changelog.md) — 变更与要求记录(逐日累积)

## 本目录自身的维护规则(必读)

**对话中用户提出的任何新要求、偏好或否决,执行完成后必须当天回写:**

1. 新约定/模板/规则 → 写入 [conventions.md](conventions.md) 对应小节
2. 当天做了什么、用户说了什么 → 追加到 [changelog.md](changelog.md)(日期 + 要点 + 涉及文件)
3. docs 改动随站点代码一起提交,不单独拖延

不记录 = 下次会话/下一个 AI 丢失上下文。这是 docs 存在的全部意义。

## 站点概况

- 44 篇文章(2024-07 起)、5 个分类、88 个标签;首页每页 18 篇,当前 3 页(18/18/8)
- 分类标签唯一登记处:`content/taxonomy.json`,维护脚本见 `tools/README.md`
- 上下篇导航按**主题相邻**优先安排,不严格等于时间序
