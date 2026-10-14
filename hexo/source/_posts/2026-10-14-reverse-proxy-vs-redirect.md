---
title: 反向代理和重定向有什么区别？网站迁移时怎样减少排名波动
date: "2026-10-14T17:07:00+08:00"
updated: "2026-10-14T17:53:11+08:00"
permalink: blog/2026/10/reverse-proxy-vs-redirect/
description: 反向代理与重定向都能把访问引向另一台服务器，但浏览器地址、请求过程和搜索引擎收到的信号并不相同。结合 Nginx 配置，说明 301、302、307、308 的区别，以及换域名时如何处理旧链接、规范网址和抓取验证。
categories:
  - 系统与运维
tags:
  - 反向代理
  - 重定向
  - Nginx
  - SEO
  - 网站迁移
cover: https://img.iowill.com/file/系统与运维/反向代理和重定向的区别/cover.png
thumbnail: https://img.iowill.com/file/系统与运维/反向代理和重定向的区别/thumbs/cover.jpg
---

博客换了域名，旧站怎么处理？一种做法是让旧域名反向代理新站，另一种是直接跳转过去。看起来都能打开文章，搜索引擎收到的信息却不一样。

用反向代理，旧网址仍在提供内容；用永久重定向，旧网址会告诉浏览器和爬虫：“这篇文章搬到这里了。”所以，换服务器但不换网址，与正式更换文章地址，需要分开处理。

## 内容是服务器取回来，还是浏览器重新去取

先看反向代理。对外地址是 `www.example.com`，应用运行在同一台机器的 `127.0.0.1:8080`：

```text
浏览器 → www.example.com 上的 Nginx → 本机应用
浏览器 ← Nginx 返回内容             ← 应用响应
```

浏览器只访问了公开域名，取上游内容的工作由 Nginx 完成。用户不需要知道应用端口，地址栏也通常保持原样。[NGINX 反向代理说明](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)

换成重定向，过程就变了：

```text
浏览器请求 old.example.com/article/
    ← 301，Location: https://new.example.com/article/
浏览器请求 new.example.com/article/
    ← 200，文章内容
```

旧站返回新地址，浏览器再发起一次请求，文章是从新地址拿到的。爬虫跟随 HTTP 重定向时也要请求目标网址。

| | 反向代理 | 重定向 |
| --- | --- | --- |
| 谁去请求另一端 | 代理服务器 | 浏览器或爬虫 |
| 地址栏 | 通常保留原地址 | 导航到目标地址 |
| 常见用途 | 把内部应用接到公开入口 | 换域名、改文章路径、统一网址 |
| 是否表示文章搬家 | 不表示 | 永久重定向可以表达迁移意图 |

代理后面的应用也可能返回 301 或 302，浏览器收到后仍会跳转。因此，“用了反向代理”不等于“绝对不会跳转”，两者可以出现在同一次访问中。

![反向代理由服务器转发请求，重定向由浏览器接收 Location 后发起新请求](https://img.iowill.com/file/系统与运维/反向代理和重定向的区别/body1.png)

*上半部分是代理转发内容，下半部分是浏览器收到新地址后重新请求。*

## 换域名，不能只替换域名

假设旧文章地址是：

```text
https://old.example.com/archives/p42
```

新博客换了程序，也整理过链接，现在这篇文章在：

```text
https://new.example.com/blog/reverse-proxy-vs-redirect/
```

如果规则只是把旧域名替换成新域名，实际落点就成了：

```text
https://new.example.com/archives/p42
```

新站没有这个路径，结果是一次成功的 301，接着一次 404。只测试旧首页能否跳到新首页，很容易漏掉这种问题。

把所有旧文章都送到首页也不合适。点进一篇具体文章，却只看到首页列表，读者还得重新找；Google 也可能把这种不相关的跳转按 soft 404 处理。旧文章有对应内容，就跳到对应页面；几篇内容合并了，可以跳到合并后的文章；确实删除且没有替代内容，返回 404 或 410 即可。[Google 网站迁移文档](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes)

![路径改变时，旧文章应重定向到对应的新文章，单纯替换域名可能落到 404](https://img.iowill.com/file/系统与运维/反向代理和重定向的区别/body2.png)

*图中把新路径简写为 `/blog/article/`。下面的 404 来自新站不存在的旧路径，并非保留路径一定会出错。*

## Nginx 的三种配置

以下片段放在对应域名已有的 `server` 块内。域名需要替换，HTTPS 证书等配置沿用实际站点设置。

### 网址不变，后面接一个应用

Nginx 直接接收浏览器的 HTTPS 请求，应用监听本机 8080 端口：

```nginx
location / {
    proxy_pass http://127.0.0.1:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

这个例子里，`proxy_pass` 后面没有附加 URI，请求路径会传给应用。两个请求头分别传递外部主机名和协议；应用还需要正确设置公开访问地址，并按框架要求配置可信代理。[NGINX：proxy_pass](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass)

如果前面还有 CDN，且 CDN 到 Nginx 走 HTTP，`$scheme` 读到的是这一段的 HTTP，而不是浏览器访问 CDN 时的 HTTPS。出现跳转循环、链接变成 HTTP 等问题时，这一层也要检查，不能只看应用配置。

### 换域名，路径不变

在旧域名的 `server` 块里：

```nginx
location / {
    return 301 https://new.example.com$request_uri;
}
```

`$request_uri` 保留路径和查询参数。新旧站目录结构相同，才适合这样整体替换。[NGINX：return 指令](https://nginx.org/en/docs/http/ngx_http_rewrite_module.html#return)

### 路径也改了

给旧文章明确指定新地址：

```nginx
location = /archives/p42 {
    return 301 https://new.example.com/blog/reverse-proxy-vs-redirect/;
}
```

这里的目标是固定地址，不会自动带上原查询参数。如果旧站靠参数区分文章，例如同一路径下的不同文章 ID，就要把参数也纳入映射规则。

旧站的 HTTP 和 HTTPS 都要覆盖。HTTPS 必须先完成 TLS 连接，浏览器才能读到跳转响应，所以旧域名即使只用来跳转，也仍需要有效证书。

实际部署可以是“旧域名 301 到新域名，新域名反向代理应用”。没必要在两种技术之间二选一。

## 博客搬家用 301，其他几个状态码呢

| 状态码 | 含义 | 自动跟随时如何处理请求方法 |
| --- | --- | --- |
| 301 | 永久移动 | POST 可能改为 GET |
| 302 | 临时移动 | POST 可能改为 GET |
| 307 | 临时重定向 | 保持原请求方法 |
| 308 | 永久重定向 | 保持原请求方法 |

普通文章页面大多是 GET 请求，永久迁移使用 301 很常见。307、308 与前两个状态码的差别，在表单、API 等涉及 POST 的场景里更值得留意。[RFC 9110：重定向状态码](https://www.rfc-editor.org/rfc/rfc9110.html#name-redirection-3xx)

Google 将 301、308 作为目标网址成为规范网址的信号。302、307 表达临时跳转，本身没有同样的含义，但也不能据此说目标页面永远不会被收录。[Google：重定向与搜索](https://developers.google.com/search/docs/crawling-indexing/301-redirects)

如果还准备在百度搜索资源平台提交网站改版，按它的要求设置 301。百度改版工具明确写的是 301，不能直接把 Google 对 308 的处理方式套过去。[百度网站改版工具](https://ziyuan.baidu.com/rewrite)

## 对排名的影响，得看改了什么

只换服务器、接入代理，文章的公开网址没有变化，就没有必要为了 SEO 给文章加一次跳转。Google 将这种基础设施变化与网址迁移分开处理。[Google：不更改网址的网站迁移](https://developers.google.com/search/docs/crawling-indexing/site-move-no-url-changes)

代理本身没有什么“加权”效果。更实际的问题是：后端是否频繁返回 502、504，防护规则是否把爬虫拦在验证页外，应用生成的链接和 canonical 是否指向正确域名。代理接好了，页面却时常打不开，当然会影响访问和抓取。

如果用旧域名反向代理新站，两边都返回同一篇文章的 200 页面，搜索引擎看到的是两个可访问的网址。它没有因为内容来自新服务器，就自动知道你准备弃用旧域名。canonical 能声明首选网址，但不会带着读者跳转，也不能保证搜索引擎一定选择它。重复页面不等于必然受罚，不过可能留下你不想保留的那个地址。[Google：合并重复网址](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

真正换了文章网址，则需要给搜索引擎时间重新抓取和更新索引。Google 说明永久重定向不会因为跳转本身损失 PageRank，但 **PageRank 不等于某个关键词的排名**。内容、可访问性以及索引处理都可能影响结果，不能承诺迁移后位置不变，也没有通用的恢复天数。[Google：网站迁移常见问题](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes)

迁移时可以逐项核对这些地方：

- 旧文章直接跳到对应的新文章，避免绕过多个中间地址。
- 新文章的 canonical 指向自己的正式网址。
- 站内链接和 Sitemap 改用新网址。
- 旧网址允许爬虫访问，不用 robots.txt 把重定向挡住。

尤其别漏了新站模板：页面已经搬过来，canonical 却还指着旧站，会与重定向传达的信息冲突。[Google：规范网址的选择](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

旧域名也要继续维护。Google 一般建议至少保留重定向一年，百度改版工具要求持续保留到新站流量稳定。搜索之外，其他网站和读者收藏夹里的旧链接，也还需要这个入口。[Google 的保留建议](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes)、[百度改版要求](https://ziyuan.baidu.com/rewrite)

## 配完以后，拿旧文章链接测一遍

先看第一次响应，把示例地址换成实际的旧文章地址：

```bash
curl -sS -D - -o response.html "https://old.example.com/archives/p42"
```

终端里应能看到重定向状态码，以及指向新文章的 `Location`。这里发的是 GET，响应体保存到 `response.html`，避免只测 HEAD 时遇到与正常访问不同的处理结果。

再跟随跳转：

```bash
curl -sS -L --max-redirs 5 -D chain.headers -o final.html -w "%{http_code} %{url_effective}\n" "https://old.example.com/archives/p42"
```

`chain.headers` 里有整条跳转链的响应头，`final.html` 是最终拿到的内容。Windows PowerShell 可以写 `curl.exe`，避开旧版本里的命令别名。

除了最终地址和状态码，还要打开页面确认文章内容。有的网站连错误页都返回 200，看到 200 就算通过，会把问题留下来。

测试时挑几篇不同目录的旧文章，尤其是改过路径、带参数和有外部链接的页面。确认这些链接都能把人带到原本要看的内容，再通过搜索平台的索引报告和服务器日志观察后续抓取情况。跳转配置生效，与搜索引擎完成迁移，是两件需要分别确认的事。
