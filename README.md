# Billy 的博客

[https://iowill.com](https://iowill.com) — 记录编程、系统运维与工具实践。

已恢复 Hexo 8.1.2 + Butterfly 5.7.0 源工程，45 篇文章、5 分类、92 标签。源文件在 `hexo/`，根目录为 GitHub Pages 发布产物。

```powershell
npm --prefix hexo ci
python -m pip install -r hexo/requirements.txt
npm --prefix hexo run preview
npm --prefix hexo run release
```

release 自带备份及校验，不自动提交/推送。文章、首页、归档、搜索、字数和阅读时间由构建同步。

- [源工程与插件](hexo/README.md)
- [发布与回滚](docs/publishing.md)
- [站点维护约定](docs/README.md)

不要直接修改生成后的 HTML。AI 助手先阅读 docs/README.md。
