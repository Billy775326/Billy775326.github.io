# 前端与 SEO 约定

以下约定于 2026-09-29 全站统一生效。改样式/加文章时**必须遵守**,新要求出现时先改本文件再动手。

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

## 图片

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

- 所有「发表于 / 更新于」的 title 提示精确到秒:`YYYY-MM-DD HH:MM:SS`(北京时间,由 `datetime` 属性 UTC+8 换算)
- 侧栏、归档等列表可见文字保持日期简写,完整时间放 title 提示

## 页脚(全站统一)

- 紧凑卡片式:`var(--card-bg)` 底 + 顶部分隔线,自动适配暗色模式(用户否决过纯蓝大留白样式,勿回退)
- 第二行「本站已运行 N 天」由内联 JS 计算,起算日 **2024-07-24**(首篇文章)
- 改页脚 = 全站批量替换,幂等标记 `class="footer-main"`

## 代码块

- 全站暗色主题(`#282c34` 底、圆角 8px、等宽字体栈),样式在 `css/index.css` 末尾补丁区块
- `js/main.js` 末尾补丁为每个 `figure.highlight` 注入工具栏(语言标签 + 复制按钮),幂等(已有 `.hl-tools` 跳过)

## CSS / JS 补丁位置

- 自定义 CSS 只追加在 `css/index.css` 末尾 `2026-09-29 pagination & footer tweaks` 区块,不改主题原有规则
- 自定义 JS 只追加在 `js/main.js` 末尾 `2026-09-29 自定义补丁` 注释之后,不改主题代码

## 品牌资产(logo / 头像)

- 网站 logo 源文件:`upload/Billy_blog_logo.png`(335×335),由它生成 `img/favicon.png`(64×64)与 `img/favicon.ico`(16/32/48 多尺寸)
- 用户头像源文件:`upload/me.jpg`,直接作为 `img/avatar.jpg` 使用
- 换 logo/头像 = 重新生成上述 img/ 目标文件即可,**不需要改任何 HTML**(全站引用 /img/ 固定路径)

## 移动端

- <768px:导航卡高 120px(桌面 150px)、双卡竖排;页脚两行居中
