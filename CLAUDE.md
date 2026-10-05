# 维护入口

先读 docs/README.md。用户已于 2026-10-05 授权迁移为 Hexo 源工程，旧“禁止构建、直接编辑 HTML”规则废止。

只编辑 hexo/ 源文件，用 npm --prefix hexo run release 生成根目录发布内容，验证并备份后才能推送。不要运行迁移前 tools 静态批处理；不要提交 node_modules、public、缓存、令牌或未授权的其他文件。新约定当天回写 docs/conventions.md 和 docs/changelog.md。
