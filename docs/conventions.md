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
- 封面统一相对路径;外链图床(img.iowill.com)直接用原 URI
- 上下篇按**主题相邻**优先,不强求时间序

## 顶栏毛玻璃

- 用户要求顶栏毛玻璃及透明遮罩：`#page-header > #nav` 使用半透明背景、14px backdrop blur、细底边；封面上为深色遮罩，浅色吸顶为白色透明层，深色模式使用深色透明层。
- 保留 Butterfly 导航显隐、搜索、手机菜单和文字配色逻辑；不支持 backdrop-filter 时使用更实的背景回退，不添加会拦截点击的遮罩元素。

## 首页卡片边缘

- 2026-09-30 用户反馈边缘过于清晰，改为柔和轻轮廓：在 `css/cards.css` 的既有首页卡片规则中使用内收 1px outline，浅色深色描边透明度为 0.06，深色白色描边透明度为 0.08。不改变卡片尺寸、列数与原有悬停效果。

## 图片

- 用户提供图床 URI 后，正文占位注释必须转换为实际 `<img>`（可使用 `<figure>` 与 `<figcaption>`）；仅替换注释中的 URI 不会显示图片。发布前检查 `#article-container img` 的数量及链接。

- **文章没有专属配图时,封面默认用** `https://img.iowill.com/file/1786437586692_千与千寻.jpg`(og:image / JSON-LD / 导航卡 / 侧栏直接引用该外链)
- **图片一律存图床 img.iowill.com(CloudFlare ImgBed,即 cfbed),仓库不放图片文件**(2026-09-30 用户指示"使用图床";本地 `upload/thumbs/` 已删除):
  - 封面/正文图:`<分类>/<文章标题>/cover.<ext>`、`<分类>/<文章标题>/body<N>.<ext>`(多张插图 body1/body2 递增)
  - 缩略图:`<分类>/<文章标题>/thumbs/cover.<ext>` 或 `thumbs/body<N>.<ext>`(先 PIL 压缩 ≤1000px、JPEG q80 再传)
  - 全站默认封面缩略图(不属于单篇文章):`默认封面/thumbs/cover.jpg`
  - 图床会把目录名中的空格转为下划线;中文目录可用,HTML 引用原样写中文 URL(浏览器自动百分号编码)
- `<img>`(导航卡/侧栏/相关推荐/首页卡)用 thumbs 缩略图;og:image / twitter:image / JSON-LD image / data-image 用原图或文章专属封面
- 上传/替换用仓库 `scripts/`(图床专用,与 tools/ 站点维护脚本分开):`thumb_bed_plan.py`(归属分析)→ `bed_upload_thumbs.py --go`(上传;API token 放 `e:/tmp/bed_token.txt`,**严禁提交入库**)→ `bed_replace_refs.py --go`(全站替换引用并验证残留=0);均默认 dry-run
- cfbed API 文档:https://cfbed.sanyue.de/api/ (上传 POST /upload,Bearer 认证,uploadFolder/uploadNameType=origin/returnFormat=full)

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

- 2026-09-30：用户撤回两行标题、淡彩背景等六项视觉调整；保持此前布局。首页卡片分类重建须清理仅含图标/分隔线的旧 `span.article-meta`，保证每张卡片一个分类图标。

## 2026-09-30 参考站卡片样式

- 用户明确采用 billy12.xyz 的淡彩横向渐变、低透明度阴影、接近的卡片大小与圆角。首页宽度上限 1250px，卡片 320px 高、封面 192px、圆角 60px，桌面三列，中屏两列，手机一列。
- 卡片与参考站一致隐藏摘要，保留单行标题、日期分类；阴影透明度默认 0.05、悬停 0.09。保留深色背景和分类图标修复，每页仍为 18 篇。

## 2026-09-30 分页与侧栏最新要求

- 用户取消底部对齐：恢复侧栏自然排列与原生吸顶；每页固定 18 篇，末页不足允许。保留修复后的三列外边距。
- 网站资讯文章数由 taxonomy 自动维护，最后更新时间来自 content/site-info.json，由发布时显式更新；不改写访客和浏览统计。

## 文章卡片日期（2026-09-30 最新要求）

- 所有文章卡片（首页/分页、归档/分类/标签、侧栏文章）的日期统一为 `YYYY/MM/DD HH:mm:ss`，按原 datetime 转为北京时间，不编造时分秒。由 update_footer_seo.py 在分类重建后统一维护。

## 侧栏毛玻璃（2026-09-30）

- 侧栏所有 `.card-widget` 使用半透明遮罩背景、14px 毛玻璃及轻微内收轮廓，深浅色分别配色。不支持模糊时使用更实背景回退，包含 Safari 前缀。
- 不使用整体 opacity，不添加拦截点击的遮罩节点，保留文字清晰度、原布局与吸顶行为。

- 侧栏尺寸与圆角（2026-09-30）：卡片桌面 32px 圆角、18px/22px 内边距、16px 间距，作者卡保留适当上下留白；手机 24px 圆角。高度随内容，不裁切目录/标签，保留侧栏宽度与吸顶。阴影采用与文章卡片一致的低透明度参数。

## 2026-09-30 卡片日期与页脚背景最新要求

- 文章卡片不显示“发表于”前缀，保留日历图标和完整时间；正文文章元信息不变。共享维护脚本移除卡片标签，避免重建恢复。
- 页脚背景透明，去掉顶部边线和渐变短线，融入全页淡彩背景；保留紧凑导航及深浅色文字。

- 2026-09-30 最新文章已获用户授权统一刷新：update_recent_posts.py 使用配平边界同步最近 5 篇，由 update_footer_seo.py 自动调用，替代此前冻结内容的规则。

- 2026-09-30 卡片时间与分类采用 11px 紧凑单行布局，缩减图标及分隔线间距；完整时间不截断，极窄空间的分类允许省略但保留链接。中屏收紧信息区左右内边距。

- 2026-09-30 用户最新要求：文章图片可备份到 upload/文章名，线上正文、封面及缩略图统一使用图床 URI；备份目录允许入库，Token 不得入库。

- 2026-10-04 WebDAV 内容要求：仅 Docker，不引入 1Panel；内容按操作步骤与验证组织，标题不直接标注“教程”。SEO/GEO 采用明确适用范围、概念说明、可验证命令、故障表和官方出处，不承诺收录或生成式搜索引用。

## 2026-10-05 源工程迁移（优先于此前静态维护规则）

- 用户已授权完整迁移、备份与插件安装。`hexo/source`、`hexo/themes`、`hexo/_config*` 为维护入口；根 HTML/CSS/JS 为构建产物，不手工修改。
- 保留现有 Butterfly 外观、首页每页 18 篇、秒级日期、半透明侧栏/顶栏、透明紧凑页脚及 2023 起始版权年。
- 安装并启用 searchdb、sitemap、wordcount；页面新增文章字数/预计阅读时间，侧栏增加全站总字数；访问量仍来自不蒜子。
- 发布前必须 build + verify，release 自动备份再同步；完整流程与回滚见 publishing.md。

- 2026-10-05 访问统计异常时最多等待 8 秒，之后显示“暂不可用”，不可用不等于 0。继续使用不蒜子官方接口；禁止为显示数字填造假值或静默切换会重置历史数据的其他服务。实现位于 hexo/themes/butterfly/source/js/visit-counter.js。

## 2026-10-08 图床域名统一

用户确认新域名可用并授权全站替换。图床统一使用 `https://img.iowill.com`，图片路径不变；正文、封面、缩略图、元数据、上传工具及 URI 清单一致。
