---
title: Debian多网卡Docker-MySQL回程路由排查
date: 2026-09-29 12:00:00
slug: debian-docker-mysql-multi-nic-routing
categories:
  - 教程
tags:
  - Debian
  - Docker
  - MySQL
  - 服务器运维
  - 策略路由
---

# Debian 多网卡部署 Docker MySQL，为什么只有 eth0 的 IP 能连接？

<!-- 封面：Debian-Docker-MySQL配图/01-cover.png；上传图床后，将下方 COVER_IMAGE_URI 替换为图片 URI。 -->
![Docker MySQL 多网卡连接排查封面](COVER_IMAGE_URI)

在一台 Debian 服务器上配置了多块网卡，每块网卡都有独立公网 IP。MySQL 通过 Docker 部署，发布端口为 `3306`。

实际使用时发现：

- 使用 eth0 的公网 IP，可以连接 MySQL。
- 使用其他网卡的公网 IP，连接超时。
- 已经配置了基于公网源 IP 的策略路由，但问题依然存在。

最终通过抓包确认：**请求从 eth1 进入，经过 Docker 转发到 MySQL；MySQL 的回复却从 eth0 发出。**

下面记录排查过程和经过验证的修复方法。文中的公网地址已替换为示例地址。

## 一、环境与现象

以 eth0、eth1 为例：

| 对象 | 地址或配置 |
|---|---|
| eth0 | `192.0.2.37/24` |
| eth0 网关 | `192.0.2.1` |
| eth1 | `198.51.100.252/25` |
| eth1 网关 | `198.51.100.254` |
| Docker 网桥 | `br-cb0d8db03272` |
| MySQL 容器 IP | `172.18.0.3` |
| Docker 端口映射 | `0.0.0.0:3306->3306/tcp` |

主路由表默认出口为 eth0：

```text
default via 192.0.2.1 dev eth0
```

同时，服务器已经配置了 eth1 的源地址策略路由：

```text
from 198.51.100.252 lookup 199
```

路由表 `199` 内容为：

```text
default via 198.51.100.254 dev eth1
```

在 Windows 客户端测试 eth1 的 MySQL 端口：

```powershell
Test-NetConnection 198.51.100.252 -Port 3306
```

结果为：

```text
TcpTestSucceeded : False
```

## 二、先排除监听地址和反向路径过滤

查看容器端口映射：

```bash
docker ps --format 'table {{.Names}}\t{{.Ports}}'
```

MySQL 显示：

```text
0.0.0.0:3306->3306/tcp
```

查看宿主机监听：

```bash
ss -lntp
```

对应输出：

```text
LISTEN 0 4096 0.0.0.0:3306 0.0.0.0:* users:(("docker-proxy",...))
```

这说明宿主机的 3306 发布在所有 IPv4 地址上，并没有只绑定 eth0。不过，监听所有地址不代表端到端网络一定可达。[Docker 端口发布文档](https://docs.docker.com/engine/network/port-publishing/)

接着查看反向路径过滤：

```bash
sysctl net.ipv4.conf.all.rp_filter \
       net.ipv4.conf.eth0.rp_filter \
       net.ipv4.conf.eth1.rp_filter
```

本次环境输出均为 `0`。

因此，可以排除 eth0、eth1 上的 `rp_filter` 检查导致丢包。其他环境如果使用严格模式 `1`，多网卡的非对称路由可能触发丢包，需要单独核查。[Linux 内核文档](https://www.kernel.org/doc/html/next/networking/ip-sysctl.html)

## 三、抓包发现：eth1 进，eth0 出

<!-- 插图一：Debian-Docker-MySQL配图/02-wrong-return-path.png；上传图床后，将下方 WRONG_RETURN_PATH_IMAGE_URI 替换为图片 URI。 -->
![故障路径示意：请求从 eth1 进入，MySQL 回包从 eth0 发出](WRONG_RETURN_PATH_IMAGE_URI)

*图 1：请求与回复使用了不同的网卡，TCP 握手未完成。箭头表示发送方向，不代表客户端已收到回复。*

在服务器执行：

```bash
tcpdump -ni any -nn \
  'tcp port 3306 and not (src net 172.18.0.0/16 and dst net 172.18.0.0/16)'
```

这里过滤掉了 Docker 子网内部的通信，避免把其他容器访问 MySQL 的正常流量误当成外部测试流量。

随后，在外部 Windows 客户端重新测试：

```powershell
Test-NetConnection 198.51.100.252 -Port 3306
```

抓包得到的关键过程如下：

```text
eth1 In:
客户端 → 198.51.100.252:3306    SYN

Docker 网桥 Out:
客户端 → 172.18.0.3:3306       SYN

Docker 网桥 In:
172.18.0.3:3306 → 客户端       SYN-ACK

eth0 Out:
198.51.100.252:3306 → 客户端    SYN-ACK
```

这段输出证明了三件事：

1. 外部请求已经到达 eth1。
2. Docker 已将请求转发给 MySQL，MySQL 也发出了回复。
3. 回复使用 eth1 的公网源地址，却从 eth0 发出。

之后可以看到重复的 SYN 和 SYN-ACK，但没有完成握手。

**回程出口错误已经确定。** 至于回复具体在哪里被丢弃，仅靠服务器侧抓包无法确定；上游网络可能对源地址与出口的对应关系有限制。

## 四、为什么已有源 IP 策略路由仍然无效？

已有规则匹配的是公网源地址：

```text
from 198.51.100.252 lookup 199
```

但 Docker 容器回复经过宿主机转发时，在选择路由的阶段，源地址仍然是：

```text
172.18.0.3
```

它无法匹配上面的公网源地址规则，于是使用主路由表，从 eth0 出口发送。

之后，连接跟踪对应的反向 NAT 才将源地址恢复成：

```text
198.51.100.252
```

因此，在物理网卡上抓到的最终数据包表现为：

```text
eth0 Out，源地址却是 eth1 的公网 IP
```

这也解释了为什么 eth0 能连接：主路由表的默认出口恰好就是 eth0，而其他网卡需要正确的回程选路。

## 五、修复：识别连接的回包，再按标记选路

<!-- 插图二：Debian-Docker-MySQL配图/03-mark-routing-fix.png；上传图床后，将下方 MARK_ROUTING_FIX_IMAGE_URI 替换为图片 URI。 -->
![修复原理：识别连接的回复方向，设置标记并通过路由表 199 选择 eth1](MARK_ROUTING_FIX_IMAGE_URI)

*图 2：利用连接跟踪识别回包，在路由选择前打标，使其匹配 eth1 对应的路由表。*

本次采用的办法是：

1. 利用连接跟踪，识别原本访问 `198.51.100.252:3306` 的连接。
2. 只给该连接的回复方向数据包添加标记。
3. 根据标记，使用已有的路由表 `199`，从 eth1 发出。

`--ctorigdst` 和 `--ctorigdstport` 匹配连接的原始目的地址及端口；`--ctdir REPLY` 限定回复方向。这样即使当前数据包的源地址还是容器 IP，也能识别它属于哪个公网入口的连接。[iptables 扩展手册](https://man7.org/linux/man-pages/man8/iptables-extensions.8.html)

以下命令中的 IP、网桥名、路由表编号需要替换为实际配置；规则优先级和标记也应避免与已有用途冲突。以下添加命令执行一次即可，重复执行会累积规则。

先添加按标记选路的规则：

```bash
ip rule add priority 10199 \
  fwmark 0x199/0xffffffff lookup 199
```

再对指定连接的回包打标：

```bash
iptables -t mangle -I PREROUTING 1 \
  -i br-cb0d8db03272 \
  -p tcp \
  -m conntrack --ctdir REPLY \
  --ctorigdst 198.51.100.252 \
  --ctorigdstport 3306 \
  -j MARK --set-xmark 0x199/0xffffffff
```

这里的 `0x199` 是自定义的数据包标记，不是路由表编号的自动转换；是 `ip rule` 将该标记关联到了路由表 `199`。[ip rule 手册](https://man7.org/linux/man-pages/man8/ip-rule.8.html)

规则只匹配回复方向，进入容器的原始请求不会被这条规则标记。

## 六、验证结果

客户端再次执行：

```powershell
Test-NetConnection 198.51.100.252 -Port 3306
```

结果变为：

```text
TcpTestSucceeded : True
```

**实际验证表明，新增规则后 eth1 的 MySQL 端口恢复了 TCP 连通。** 这也支持了此前关于 Docker 回程路由的判断。

如果需要进一步确认，可以重新抓包，检查 SYN-ACK 是否从 eth1 发出，并查看规则命中计数：

```bash
iptables -t mangle -nvL PREROUTING --line-numbers
```

最后再用 MySQL 客户端登录。TCP 连通和数据库认证是两个阶段；如果此时出现 `Access denied`，应继续检查 MySQL 用户授权和认证配置。

## 七、回滚与持久化说明

撤销本次规则：

```bash
iptables -t mangle -D PREROUTING \
  -i br-cb0d8db03272 \
  -p tcp \
  -m conntrack --ctdir REPLY \
  --ctorigdst 198.51.100.252 \
  --ctorigdstport 3306 \
  -j MARK --set-xmark 0x199/0xffffffff

ip rule del priority 10199 \
  fwmark 0x199/0xffffffff lookup 199
```

本次验证的是 **eth1 的 MySQL 3306 端口临时修复**，尚未验证其他网卡，也没有完成重启持久化。

扩展到其他公网 IP 时，需要为各入口配置对应的连接匹配、标记和路由表。持久化时则要同时恢复策略路由和防火墙规则，并确保执行顺序正确、重复执行不会累积规则。另外，Docker 网络重建后网桥名称可能变化，本文规则中的网桥名也需要同步检查。

这次排查最关键的证据，是抓包中的这一行：**eth1 的公网源地址出现在了 `eth0 Out` 上。** 端口确实开放、数据库也确实回复了，但回复没有沿着正确的出口返回。
