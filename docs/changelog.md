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
- ~~**老文章侧栏"最新文章"批量刷新**(用户要求):43 篇文章页 + tags/categories 等共 149 页统一为真实最新 5 篇~~ → **已整体回滚**(见下)
- **品牌资产更换(用户指定)**:`Billy_blog_logo.png` 做网站 logo(生成 64×64 favicon.png + 多尺寸 favicon.ico,替换原 32×32 模糊图);`me.jpg` 做用户头像(替换原 60×58 的 img/avatar.jpg);只改 img/ 二进制,HTML 零改动;约定写入 conventions.md「品牌资产」
- **封面治理(用户指定"替换成封面,没有封面就使用默认图片")**:清查发现 `Linux系统根分区满了….jpg` 被当作 `云服务器Debian12根分区扩容记录` 的封面(正文并未使用,属构建期乱配)→ 换默认图;MySQL 文章 1 处残留 → 换专属封面;全站 og:image / twitter:image / JSON-LD image / data-image 中凡值为本地千与千寻或该 Linux 图(=无真实封面标记)的文章,统一换成默认外链 `…/1786437586692_千与千寻.jpg`(共 140 处,11 个文件清理残留);有真实封面的文章(redroid 系列外链图等)验证未动;导航卡/侧栏仍用本地缩略图不变

### 2026-09-29 侧栏回滚(用户反馈"回滚侧边栏的修改,它都被改错位了")
- 上述侧栏批量刷新(fix5b)**已全量回滚**:其收尾正则吞错 `</div>` 边界,149 页出现孤儿闭合标签导致卡片错位
- 回滚方式:`[card-recent-post 卡片开始, </main>)` 整段从基线 commit `a3601c2` 逐字节还原,区段外改动(导航卡/TDK/页脚/封面等)不受影响;149/149 页黄金校验通过
- 脚本:e:\tmp\blog_fix7_rollback.py(基线对比式,幂等)
- **教训(给后续 agent):批量替换嵌套 HTML 时禁止用"若干连续闭合标签"当正则右边界,必须用配平计数或整段基线还原;改完必须做 div 配平/逐字节校验**
- 侧栏"最新文章"维持各页原始状态,后续如需刷新需先解决主题生成的嵌套差异再单独方案
- **时间可见文本到秒 + 紧凑(2026-09-29 用户要求"时间部分都要显示到秒,时间格式排紧密点")**:43 篇文章头部「发表于/更新于」可见文字由纯日期升级为 `YYYY-MM-DD HH:MM:SS`(北京时间),42 篇修复;`#post-meta` 分隔符/图标间距收紧(CSS 补丁区 `post-meta compact`)
- **代码块回退 Butterfly 原生(2026-09-29 用户指示"代码块风格使用butterfly主题的代码块,整个博客主题都要基于butterfly主题")**:删除自定义暗色配色与 `.hl-tools` 工具栏(css/index.css 补丁区 + js/main.js 补丁);原生工具栏由主题 `addHighlightTool` 按 `GLOBAL_CONFIG.highlight`(highlightCopy/highlightLang=true)自动生成;总原则已写入 conventions.md 首节
