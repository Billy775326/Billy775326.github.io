# 变更与要求记录(changelog)

> **维护规则(重要):对话中用户提出的任何新要求、偏好、否决,执行完成后必须当天记录到本文件**(日期 + 要点 + 涉及文件)。docs 是全站约定的唯一事实来源,不记录 = 下次会话丢失。

## 2026-09-29

### 全站批量优化(约 150 文件,脚本 e:\tmp\blog_batch.py 系列,临时)
- 上下篇导航卡全量重写:统一模板(aria-label / rel / loading=lazy / 规范 onerror)+ 方向箭头图标(fa-angle-left/right)+ hover 显示「阅读全文:标题」;卡片标题去 `YYYYMMDD-` 前缀;封面按主题映射缩略图;清退 `full-width` 遗留
- 封面压缩:新建 `upload/thumbs/`,千与千寻 673KB→43KB;全站 1166 处 `<img>` 换缩略图,og/JSON-LD/data-image 保留原图
- TDK:43 篇补齐 keywords(取标签)+ 真实 description(18 篇截首段、8 篇截图为主的文章手写);meta/og/JSON-LD 三处同步
- 首页分页修复:发现历史问题——发新文只插首页卡未链式后移,19/18/6 → 修正为 **18/18/7**,时间序连续无重复

### 页脚(两轮)
- 第一版加了"托管 GitHub Pages + 运行天数",仍保留主题纯蓝大留白 → **用户反馈:纯蓝、占位太多太空**
- 第二版改紧凑卡片式:白底(暗色模式自适应 `var(--card-bg)`)+ 顶部细线 + 单行版权/框架 + 小字第二行;`.footer-other` 内边距 80px→约 30px

### 时间
- 所有「发表于/更新于」title 提示精确到秒(北京时间);修复 95 处日期级提示

### MySQL 文章(Debian多网卡Docker-MySQL回程路由排查)
- IP 代号(ETH0_IP 等)→ RFC 5737 文档地址(203.0.113.10 / 198.51.100.20 / 172.20.0.2 / 0.0.0.0),**用户要求用户友好方便看**;`MARK` 为 iptables 动作名,保留
- 三张配图换 img.billy12.xyz 外链 URI(01-cover / 02-wrong-return-path / 03-mark-routing-fix),封面同步到 og/JSON-LD/首页卡/各页侧栏/相邻文章导航卡(共 96 文件)
- JSON-LD 日期修正:2025-04-17(模板残留)→ 2026-09-29T04:00:00.000Z

### 代码块
- 原为裸 `figure.highlight`(无语言标签/复制按钮/配色)→ **用户反馈太丑**;改暗色主题 + 工具栏(语言标签 + 复制按钮),CSS 在 index.css 补丁区,JS 在 main.js 末尾

### docs 建立
- 新建 `docs/`(README / structure / publishing / conventions / changelog),面向 AI 助手,类似记忆文件
- **用户要求:docs 要有自我维护提示,对话中的要求细节要常记录**(即本文件维护规则)
- 新建根 `README.md`(面向人)与 `CLAUDE.md`(Claude Code 入口指针)

### 2026-09-29 晚间追加
- **默认封面规则:无专属配图的文章,封面默认用外链 `https://img.billy12.xyz/file/1786437586692_千与千寻.jpg`**(用户指定),已写入 conventions.md
- MySQL 文章封面/插图确认换为 img.billy12.xyz 外链;清除已过时的"上传图床后替换 URI"注释(HTML+md)
- **老文章侧栏"最新文章"批量刷新**(用户要求):43 篇文章页 + tags/categories 等共 149 页统一为真实最新 5 篇——MySQL(09-29)→ ArchLinux KDE → MAAREADME → ReDroid MAA → TigerVNC(并列时间戳 2026-09-10 15:29:21 时按用户 MySQL 页侧栏原顺序);时间到秒、封面按约定
- 脚本:e:\tmp\blog_fix5b.py(幂等,当前判断比对前两篇 href)
- **品牌资产更换(用户指定)**:`Billy_blog_logo.png` 做网站 logo(生成 64×64 favicon.png + 多尺寸 favicon.ico,替换原 32×32 模糊图);`me.jpg` 做用户头像(替换原 60×58 的 img/avatar.jpg);只改 img/ 二进制,HTML 零改动;约定写入 conventions.md「品牌资产」
- **封面治理(用户指定"替换成封面,没有封面就使用默认图片")**:清查发现 `Linux系统根分区满了….jpg` 被当作 `云服务器Debian12根分区扩容记录` 的封面(正文并未使用,属构建期乱配)→ 换默认图;MySQL 文章 1 处残留 → 换专属封面;全站 og:image / twitter:image / JSON-LD image / data-image 中凡值为本地千与千寻或该 Linux 图(=无真实封面标记)的文章,统一换成默认外链 `…/1786437586692_千与千寻.jpg`(共 140 处,11 个文件清理残留);有真实封面的文章(redroid 系列外链图等)验证未动;导航卡/侧栏仍用本地缩略图不变
