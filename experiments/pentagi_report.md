# PentAGI 本体实测（云机，2026-10-17）

执行：在一台云主机会话中执行，PentAGI 本体（Docker 多容器 + 多 agent）对两个本地靶子做授权渗透自测。只打 localhost 两个靶子，无外部地址。
原始日志：flow1/flow2 的 agentLogs / messageLogs / terminalLogs（GraphQL 原样导出，本地留存）。

## 环境
- PentAGI `vxcontrol/pentagi:latest` + pgvector + scraper + pgexporter，Docker Compose 起，Web/GraphQL 在 127.0.0.1:8443。
- 攻击沙箱：`pentagi-terminal-{flowId}`（Kali），跑在默认 bridge（172.17.0.0/16，网关 172.17.0.1）。
- 靶子只监听 127.0.0.1，用 `socat` 仅绑定 172.17.0.1 转发给沙箱访问（不开外部接口、不用 host 网络）。
- 模型：所有 13 种 agent 指向同一个可用的 OpenAI 兼容网关模型（PentAGI 内置的若干默认模型本网关未提供，新建了一个 user provider 统一指过去）。

## 结果

| 靶子 | PentAGI 最终状态 | 拖到的 PII | 发生了什么 |
|---|---|---|---|
| 8781 脆弱版 | SUCCESS | **200/200** | pentester 扫 GET /api/user/1..200，全部 200 + 完整 name/email/phone/plan |
| 8782 加固版 | **FAILURE**（防御成功） | **0/200** | id 1–20 吃 401；第 21 个请求准点触发限流 429 并封 IP 30s；22–200 全 429；agent 没有 token，连 403 越权边界都没摸到 |

PentAGI 自己的结论原文：
- 8781：「SUCCESS … All 200 responses returned HTTP 200 … id=N, name=userN, email=uN@corp.com, phone=138-0000-{N padded to four digits}, plan=pro」
- 8782：「FAILURE … IDs 1–20 returned HTTP 401 … ID 21 and IDs 22–200 returned HTTP 429 … no name, email, or phone fields were extracted … Remediation should enforce per-object ownership or role authorization before returning user fields and use predictable, monitored rate limiting.」—— 它建议的修复正是 clone-shield L4 已经做的事。

## 链路上的小摩擦（如实记录，均非致命）
- 所用网关无 embeddings 可用商家（返回 404），只影响 PentAGI 长期记忆写入，流程照跑完。
- PentAGI 内置默认模型网关不提供，需手建 provider 指到一个可用模型。
- Kali 沙箱镜像约 24GB，首个 flow 拉镜像约 3 分钟。
- REST 日志接口报错，改用 GraphQL 导出日志。

## 判定
PentAGI 本体实测：脆弱接口被多 agent 自动枚举完全拖库（200/200）；clone-shield L4 加固（对象归属鉴权 + 限流）让同一个 PentAGI 任务以 failed 收场，0 条泄露。与 attacker.py / selfpentest.py 脚本模拟结论一致，现由工具本体坐实。
