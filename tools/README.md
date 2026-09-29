# 分类标签维护

当前仓库保存的是静态站点，不包含原 Hexo 工程。分类标签的维护入口为 `content/taxonomy.json`，逐篇清单见 `content/分类与标签清单.md`。

每篇文章使用一个主题分类，标签描述技术、工具和知识点；故障排查作为跨分类标签。空正文文章仅依据标题设置保守标签。历史独立页面 `legacy-html` 不计入 43 篇文章，仅同步导航。

运行环境：Python 3、beautifulsoup4。

```bash
python tools/rebuild_taxonomy.py
python tools/verify_taxonomy.py
```

发布前还可以传入调整前的 Git 提交，检查文章正文、标题和日期未被改动：

```bash
python tools/verify_taxonomy.py <baseline-commit>
```

脚本重建文章分类标签元数据、分类标签列表、全站侧栏计数、首页卡片分类及搜索元数据，并同步已有 Markdown 源稿。它不会重新生成正文。重复执行不应产生额外变化。

旧分类标签地址保留静态跳转；C++ 使用独立的 `cpp` 路径，Linux 统一名称并继续使用 `linux` 路径。侧栏仅显示使用频次最高的 20 个标签，全部标签在 `/tags/` 展示。

若以后恢复 Hexo 源工程，应将本清单同步到原文 front matter，以免重新构建覆盖本次分类结果。
