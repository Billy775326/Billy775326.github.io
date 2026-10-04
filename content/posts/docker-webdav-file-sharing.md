---
title: Docker 部署 WebDAV：用 hacdias/webdav 搭建个人文件共享服务
slug: docker-webdav-file-sharing
draft: false
date: 2026-10-04T10:07:52+00:00
updated: 2026-10-04T10:07:52+00:00
description: 使用 Docker Compose 部署 hacdias/webdav，从目录挂载、账号权限和本机读写验证开始，再配置服务自带的 HTTPS。附上传下载、复制改名命令，以及连接失败、无法写入和证书错误的排查方法。
cover: https://img.billy12.xyz/file/系统与运维/Docker_部署_WebDAV：用_hacdias_webdav_搭建个人文件共享服务/cover.png
categories:
  - 系统与运维
tags:
  - WebDAV
  - Docker
  - Docker Compose
  - 自托管
  - 文件共享
---

# Docker 部署 WebDAV：用 hacdias/webdav 搭建个人文件共享服务

![Docker WebDAV 文件共享服务](https://img.billy12.xyz/file/系统与运维/Docker_部署_WebDAV：用_hacdias_webdav_搭建个人文件共享服务/cover.png)

如果只是想把服务器上的一个目录提供给电脑、手机和备份工具使用，可以先试试 WebDAV。它在 HTTP 上增加了目录、文件操作等能力；客户端是否支持挂载、锁定和大文件传输，要看具体实现。

这里使用 hacdias/webdav，配合 Docker Compose 管理配置和数据目录。先让服务只在宿主机上可访问，验证读写正常；需要给其他设备使用时，再开启服务自带的 TLS。整个方案只运行一个 WebDAV 容器，不需要管理面板或反向代理。

本文命令面向安装了 Docker Engine 和 Compose 插件的 Linux 主机，以普通 bridge 网络为例。域名 `dav.example.com` 是示例，公网访问时替换为自己的域名。以下响应码是验证预期，不是某台服务器的实测日志。

## 先分清三个路径和两个监听地址

![Docker 容器的端口入口、配置挂载和数据挂载](https://img.billy12.xyz/file/系统与运维/Docker_部署_WebDAV：用_hacdias_webdav_搭建个人文件共享服务/body1.png)

配置文件在宿主机上保存，容器读取它；上传文件则写到单独的数据目录。容器更新后，仍然挂载同一份目录。

| 宿主机位置 | 容器内位置 | 用途 |
|---|---|---|
| `/opt/webdav/config/` | `/config/` | 服务配置，只读挂载 |
| `/opt/webdav/data/` | `/data/` | 用户文件，可读写 |
| `/opt/webdav/certs/` | `/certs/` | 开启 HTTPS 时使用的证书，只读挂载 |

地址也有两层：配置中的 `0.0.0.0` 是应用在容器内的监听地址；Compose 中的 `127.0.0.1:6065:6065` 则把宿主机入口限制在回环地址。它们并不矛盾。Docker 的端口发布规则决定外部怎样进入容器，不能把容器自己的 `127.0.0.1` 当作宿主机地址。[Docker 端口发布说明](https://docs.docker.com/engine/network/port-publishing/)

建议使用受维护的 Docker 版本。Docker 官方特别说明，28.0.0 之前的版本存在同一二层网络设备可能访问回环发布端口的历史问题；不要只凭映射字符串就认定旧版本完全隔离。

## 准备配置与数据目录

以下命令需要有创建 `/opt/webdav` 目录和执行 Docker 的权限。先确认工具可用：

```bash
docker version
docker compose version
mkdir -p /opt/webdav/config /opt/webdav/data /opt/webdav/certs
cd /opt/webdav
```

创建 `/opt/webdav/config/config.yml`：

```yaml
address: 0.0.0.0
port: 6065
tls: false
directory: /data
permissions: R
behindProxy: false

users:
  - username: demo
    password: "REPLACE_WITH_A_UNIQUE_PASSWORD"
    permissions: CRUD
```

先把密码占位文字换成专用的长随机密码，再启动服务。配置文件里的 `R` 是默认只读，`demo` 用户单独获得创建、读取、更新、删除权限。不要删掉 `users` 后误以为仍然需要登录。

服务也支持 bcrypt 格式的密码和按用户设置目录；字段含义及密码生成方式可以对照 [hacdias/webdav 官方配置](https://github.com/hacdias/webdav#configuration)。使用哈希能减少明文密码落盘，但不能代替 HTTPS。

```bash
chmod 600 /opt/webdav/config/config.yml
```

如果后续给容器指定了非 root 用户，需要同时调整文件的属主和权限，让该用户能读取配置、写入数据目录。不要用 `chmod -R 777` 来跳过权限问题。

## 用 Docker Compose 启动

保存为 `/opt/webdav/compose.yml`：

```yaml
services:
  webdav:
    image: ghcr.io/hacdias/webdav:latest
    restart: unless-stopped
    command: ["-c", "/config/config.yml"]
    ports:
      - "127.0.0.1:6065:6065"
    volumes:
      - ./config:/config:ro
      - ./data:/data
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

这里用 `latest` 方便首次尝试。准备长期运行时，应先确认一个可用版本，再把镜像固定到该版本标签或摘要，避免以后拉取时悄悄更换版本。

```bash
cd /opt/webdav
docker compose config --quiet
docker compose pull
docker compose up -d
docker compose ps
docker compose logs --tail=50 webdav
```

`config --quiet` 只检查 Compose 文件，不验证 WebDAV 的 YAML 是否正确。容器反复重启时，先看日志里的配置解析、文件读取和端口错误。

## 用 curl 验证列目录、上传和下载

以下命令在 Docker 宿主机执行。`-u demo` 会让 curl 交互式询问密码；没有把密码直接放进命令行。[curl 参数说明](https://curl.se/docs/manpage.html)

先查看目录：

```bash
curl -i -u demo -X PROPFIND \
  -H "Depth: 1" \
  http://127.0.0.1:6065/
```

正常情况下应看到 `207 Multi-Status` 和 XML。`-i` 用于显示响应头；只把正文管道给 `head`，不能据此确认 HTTP 状态码。207 代表多状态响应，操作是否全部成功还要看 XML 中各项状态。

再创建独立测试目录，避免碰到已有文件：

```bash
probe="webdav-check-$(date +%Y%m%d%H%M%S)"
curl -i -u demo -X MKCOL "http://127.0.0.1:6065/$probe/"
printf 'hello webdav\n' > /tmp/webdav-probe.txt
curl -i -u demo -T /tmp/webdav-probe.txt \
  "http://127.0.0.1:6065/$probe/probe.txt"
curl --fail --silent --show-error -u demo \
  "http://127.0.0.1:6065/$probe/probe.txt"
```

新建目录和新文件通常返回 201；覆盖已有文件可能返回 204。下载内容应为 `hello webdav`。也可以在宿主机的数据目录里确认文件是否实际写入。

文件能上传，不代表客户端的复制和重命名就一定正常。继续在同一终端里验证这两个操作：

```bash
curl -i -u demo -X COPY \
  -H "Destination: http://127.0.0.1:6065/$probe/copy.txt" \
  -H "Overwrite: F" \
  "http://127.0.0.1:6065/$probe/probe.txt"

curl -i -u demo -X MOVE \
  -H "Destination: http://127.0.0.1:6065/$probe/renamed.txt" \
  -H "Overwrite: F" \
  "http://127.0.0.1:6065/$probe/copy.txt"
```

`Destination` 与请求使用相同的地址和端口；`Overwrite: F` 避免覆盖已有目标。本方案直接连接服务，不需要套用反代场景中的请求头重写配置。

## 让其他设备通过 HTTPS 连接

上面的端口只在服务器本机开放，手机连不上是预期行为。若要在公网使用，先准备指向服务器的域名，以及覆盖该域名、被客户端信任的证书。

将证书链和私钥分别放到：

```text
/opt/webdav/certs/fullchain.pem
/opt/webdav/certs/privkey.pem
```

这一步假设你已经取得有效证书；容器不会因为填了域名就自动签发或续期。复制证书时注意来源是否为符号链接，最终应确保挂载目录内能直接读取完整文件。

在 `config/config.yml` 中把 TLS 设置改为：

```yaml
tls: true
cert: /certs/fullchain.pem
key: /certs/privkey.pem
```

其他配置保持不变，容器内端口仍然是 6065。然后把 Compose 的 `ports` 和 `volumes` 分别替换为以下内容，注意是替换，不要保留两个同名 YAML 键：

```yaml
    ports:
      - "443:6065"
    volumes:
      - ./config:/config:ro
      - ./data:/data
      - ./certs:/certs:ro
```

先确认宿主机 443 没有被其他程序占用，配置好相应的入站访问规则，再应用修改：

```bash
cd /opt/webdav
docker compose config --quiet
docker compose up -d --force-recreate
docker compose logs --tail=50 webdav
curl -i -u demo -X PROPFIND -H "Depth: 0" https://dav.example.com/
```

TLS 由 WebDAV 服务自己处理。请用域名访问，直接换成 IP 可能导致证书名称校验失败；不要通过长期添加 `-k` 掩盖问题。若域名同时配置了 AAAA 记录，也要验证 IPv6 路径，避免部分设备连接到错误地址。

然后在另一台设备上，把前面的测试地址换成 `https://dav.example.com`，重新检查上传、下载、COPY 和 MOVE。服务端本机能连通，并不代表外部的 DNS、防火墙和证书都正确。

证书更新后执行 `docker compose restart webdav` 重新加载，并检查实际返回的证书。证书获取和续期属于独立维护事项。

## 客户端连接时填什么

| 项目 | 示例 |
|---|---|
| 协议 | WebDAV / HTTPS |
| 地址 | `https://dav.example.com/` |
| 用户名 | `demo` 或你自己的账号 |
| 密码 | 配置中对应账号的密码 |

macOS 可以在 Finder 的“连接服务器”中输入 HTTPS 地址；移动端需要使用支持 WebDAV 的文件管理应用。Windows 的资源管理器连接依赖 WebClient 等组件和系统策略，不能把所有版本都当成相同行为。遇到问题时，先用 curl 区分服务故障和客户端兼容性。

备份任务可以使用 rclone。运行 `rclone config`，创建名为 `webdav` 的远端，类型选 WebDAV，填写 URL、用户名和密码，通用服务商选项使用 `other`。配置好以后先执行只读检查：

```bash
rclone lsd webdav:
rclone copy ./photos webdav:photos --dry-run
```

确认目标无误后，再去掉 `--dry-run`。这里使用 `copy`，不使用会按源目录状态删除目标文件的 `sync`。客户端字段以 [rclone WebDAV 文档](https://rclone.org/webdav/) 为准。

## 连接失败或不能写入，从哪里查

| 表现 | 先检查什么 |
|---|---|
| 容器启动后立刻退出 | YAML 缩进、配置挂载路径、证书读取权限 |
| 本机连接被拒绝或重置 | 容器状态、日志、应用是否监听 `0.0.0.0:6065`、发布端口是否正确 |
| 本机能访问，其他设备不能 | 是否仍绑定宿主机回环、DNS、端口放行、IPv4/IPv6 路径 |
| 返回 401 | 用户名密码、客户端保存的旧凭据、是否读取了预期配置 |
| 能读取但不能上传 | 账号 C/U 权限、宿主机目录写权限、磁盘剩余空间 |
| COPY/MOVE 失败 | Destination 的主机和端口、目标父目录、账号权限、目标是否已存在 |
| HTTPS 校验失败 | 域名与证书匹配、有效期、完整证书链、客户端时间 |

容器内只监听 `127.0.0.1` 时，监听的是容器自己的回环；普通 bridge 模式下，发布端口流量进入容器网卡，不会因此到达该监听地址。修改为 `0.0.0.0` 后，仍然要通过宿主机端口绑定决定开放范围。

改了 WebDAV 配置后执行 `docker compose restart webdav`；改了端口或挂载等 Compose 设置，则执行 `docker compose up -d` 重新应用。若仍有疑问，可通过 `docker inspect` 核对实际挂载和端口，而不是只看文件中的预期设置。

## 更新容器之前，先确认数据在哪

上传目录通过 bind mount 保存到宿主机。删除并重建容器通常不会删除这份目录，但直接删除宿主机数据、错误覆盖文件或磁盘故障仍会造成损失。持久化不等于备份。[Docker bind mount 说明](https://docs.docker.com/engine/storage/bind-mounts/)

更新前记录当前镜像标签或摘要，并备份配置和数据；需要一致性备份时，暂停写入或停服务后再备份。确认新版本兼容后再执行：

```bash
cd /opt/webdav
docker compose pull
docker compose up -d
```

更新后重新跑一遍读写验证。只读账号可以设为 `R`；不授予删除权限能减少部分误操作，但有更新权限的账号仍可能覆盖文件，不能当作防勒索备份策略。

部署完成的标准很具体：客户端能验证证书、登录、列目录和读写文件；数据确实落在宿主机预期目录；重建容器后文件仍在。把这几项验证清楚，比只看到容器状态为 Running 更有用。

## 参考资料

- [hacdias/webdav 项目与配置](https://github.com/hacdias/webdav)
- [Docker 端口发布](https://docs.docker.com/engine/network/port-publishing/)
- [Docker bind mounts](https://docs.docker.com/engine/storage/bind-mounts/)
- [curl 参数说明](https://curl.se/docs/manpage.html)
- [rclone WebDAV](https://rclone.org/webdav/)
