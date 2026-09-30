# 前端与 SEO 约定

以下约定于 2026-09-29 全站统一生效。改样式/加文章时**必须遵守**,新要求出现时先改本文件再动手。

## 总原则:一切基于 Butterfly 原生(2026-09-29 用户明确要求)

- **整个博客的主题风格以 Butterfly 5.7.0 原生为准**,不引入与主题风格冲突的自制样式
- 自定义 CSS/JS 仅限下文明确记录的几处(紧凑页脚卡、移动端导航卡高度、meta 紧凑),均为用户点名要求过的
- 代码块、卡片、按钮等一律用主题原生渲染,先看主题 CSS/JS 已有能力再动手

## 上一篇/下一篇导航卡模板

```html
<nav class="pagination-post" id="pagination" aria-label="文章导航">
  <a class="pagination-related" href="/blog/…" title="标题" aria-label="上一篇：标题" rel="prev">
    <img class="cover" src="缩略图" alt="标题" loading="lazy"
         onerror="this.onerror=null;this.src='/img/404.jpg'">
    <div class="info"><div class="info-1">
      <div class="info-item-1"><i class="fas fa-angle-left fa-fw" aria-hidden="true"></i>上一篇</div>
      <div class="info-item-2">显示标题</div>
    </div><div class="info-2"><div class="info-item-1">阅读全文：标题</div></div></div>
  </a>
  <!-- 下一篇:<div class="info text-right">,图标 fa-angle-right 放文字后,rel="next" -->
</nav>
```

- 卡片显示标题去掉 `YYYYMMDD-` 日期前缀(title 属性保留全名)
- hover 摘要固定为「阅读全文：标题」,**不塞正文段落**
- 不使用 `full-width` 类(单卡由 flex 自动撑满)
- 封面统一相对路径;外链图床(img.billy12.xyz)直接用原 URI
- 上下篇按**主题相邻**优先,不强求时间序

## 顶栏毛玻璃

- 用户要求顶栏毛玻璃及透明遮罩：`#page-header > #nav` 使用半透明背景、14px backdrop blur、细底边；封面上为深色遮罩，浅色吸顶为白色透明层，深色模式使用深色透明层。
- 保留 Butterfly 导航显隐、搜索、手机菜单和文字配色逻辑；不支持 backdrop-filter 时使用更实的背景回退，不添加会拦截点击的遮罩元素。

## 首页卡片边缘

- 2026-09-30 用户反馈边缘过于清晰，改为柔和轻轮廓：在 `css/cards.css` 的既有首页卡片规则中使用内收 1px outline，浅色深色描边透明度为 0.06，深色白色描边透明度为 0.08。不改变卡片尺寸、列数与原有悬停效果。

## 图片

- 用户提供图床 URI 后，正文占位注释必须转换为实际 `<img>`（可使用 `<figure>` 与 `<figcaption>`）；仅替换注释中的 URI 不会显示图片。发布前检查 `#article-container img` 的数量及链接。

- **文章没有专属配图时,封面默认用** `https://img.billy12.xyz/file/1786437586692_千与千寻.jpg`(og:image / JSON-LD / 导航卡 / 侧栏直接引用该外链)
- `<img>`(导航卡/侧栏/相关推荐/首页卡)一律用 `upload/thumbs/` 缩略图
- og:image / twitter:image / JSON-LD image / 分享 data-image 用原图或文章专属封面
- 新增封面:现有图压缩,PIL `thumbnail ≤1000px`、JPEG q80,存 `upload/thumbs/<原名>.jpg`;若原图已 ≤100KB 且 ≤800px 宽可直接引用
- `upload/` 中文文件名,HTML 引用需百分号编码;外链图床 URI 原样使用

## IP 与敏感信息(写技术文必读)

- 文中 IP 一律用 **RFC 5737 文档保留地址**:公网 `203.0.113.x` / `198.51.100.x`,私网 `172.20.0.x`,通配 `0.0.0.0`;不用 `ETH0_IP` 这类代号(用户要求"用户友好方便看"),也**绝不写真实 IP**
- 网关、容器地址等照常配成一组连贯的示意地址,并在文中说明"均为文档保留地址,请替换为实际配置"

## TDK(SEO)

- 每篇必须有:`<title>` | `meta description`(80–120 字真实摘要,截首段或手写) | `meta keywords`(文章标签逗号连接)
- 三处同步一致:meta description / og:description / JSON-LD `description`
- JSON-LD 的 datePublished / dateModified 必须与 og 时间一致(勿照抄模板旧值)

## 时间显示

- 文章头部「发表于 / 更新于」**可见文字本身**就要精确到秒:`YYYY-MM-DD HH:MM:SS`(北京时间,由 `datetime` 属性 UTC+8 换算),title 提示同样到秒(2026-09-29 用户要求升级:此前只要求 title 到秒)
- meta 行排版紧凑:`#post-meta` 分隔符/图标间距已在 CSS 补丁区收紧
- 侧栏、归档等列表可见文字保持日期简写,完整时间放 title 提示

## 页脚(全站统一)

- 2026-09-29 最新要求：页脚契合 Butterfly 原生主题，采用 `footer-other / copyright / framework-info / footer_custom_text` 居中堆叠结构；不使用左右分栏品牌区或双层分隔卡。版权起始年份为 **2023**。2026-09-30 调整为版权与框架合并一行、图标导航一行，删除重复介绍；小屏允许自然换行。移除基于首篇文章日期计算的「本站已运行」天数。
- 页脚导航提供归档、分类、标签、站点地图、作者 GitHub；语义化 `footer/nav`、键盘焦点、移动端换行，保留 Butterfly 深浅色变量。
- SEO/GEO 基础维护：`python tools/update_footer_seo.py` 更新页脚、真实作者/文章 JSON-LD、sitemap.xml 和 robots.txt。站点地图不收录跳转页、历史独立页或维护文档；不伪造 lastmod，不添加隐藏关键词或承诺 AI 引用。

- 紧凑卡片式:`var(--card-bg)` 底 + 顶部分隔线,自动适配暗色模式(用户否决过纯蓝大留白样式,勿回退)
- 旧运行天数已移除；版权年份与文章发布日期分别维护。
- 改页脚 = 更新 `tools/update_footer_seo.py` 模板并全站同步，以配平的 `footer#footer` 为替换边界。

## 代码块(2026-09-29 用户否决自定义版,已回退)

- **一律使用 Butterfly 原生代码块风格**,不要自制配色/工具栏(自定义暗色 `#282c34` + `.hl-tools` 工具栏已被用户否决并删除)
- 原生工具栏由主题 `js/main.js` 的 `addHighlightTool` 按 `GLOBAL_CONFIG.highlight` 自动生成(`highlightCopy: true`、`highlightLang: true`),页面无需任何额外标记
- 现有 `figure.highlight` HTML 结构保持原样即可

## CSS / JS 补丁位置

- 自定义 CSS 只追加在 `css/index.css` 末尾 `2026-09-29 pagination & footer tweaks` / `post-meta compact` 区块,不改主题原有规则
- **`js/main.js` 目前没有任何自定义补丁**(主题 JS 保持原样),新增 JS 需求先确认主题没有内建能力

## 品牌资产(logo / 头像)

- 网站 logo 源文件:`upload/Billy_blog_logo.png`(335×335),由它生成 `img/favicon.png`(64×64)与 `img/favicon.ico`(16/32/48 多尺寸)
- 用户头像源文件:`upload/me.jpg`,直接作为 `img/avatar.jpg` 使用
- 换 logo/头像 = 重新生成上述 img/ 目标文件即可,**不需要改任何 HTML**(全站引用 /img/ 固定路径)

## 移动端

## 关于页面

- `/about/` 使用 Butterfly 原生普通页面结构，介绍作者、内容方向、文章导航和 GitHub 入口；不编造身份、联系方式或经历。
- 桌面导航、手机侧栏导航及页脚提供“关于”入口，页面加入站点地图并使用 AboutPage 结构化数据，不计入文章数。
- `python tools/add_about_page.py` 维护关于页与顶部/手机导航，随后运行 `python tools/update_footer_seo.py` 同步页脚与站点地图。

- <768px:导航卡高 120px(桌面 150px)、双卡竖排;页脚两行居中

## 2026-09-30 首页视觉细化

- 用户确认六项建议：标题最多两行并预留两行高度；浅色淡蓝紫渐变背景；卡片 16px 圆角；封面统一 16:9、摘要两行；保持日期与分类等精简信息；保留紧凑页脚。
- 深色模式保持深色背景，首页分页共享卡片样式，原有轻描边和响应式列数保留。
