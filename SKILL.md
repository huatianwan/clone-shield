---
name: clone-shield
description: 让 Codex / Claude Code 把你自己的软件加固到"抄不动、抄走也没用"。针对 REA、reverse-skill、PentAGI 这类 AI 逆向/复刻/渗透工具做定点防守。只对你自己拥有或有权加固的项目使用。触发词：防复刻 / 防逆向 / 防破解 / 加固 / anti-clone / clone-shield / 保护我的代码不被 AI 抄。
---

# clone-shield · 防复刻护盾

一套给**防守方**的技能包。你把 Codex / Claude Code 指向**你自己的项目**，它按这套方法把项目加固到：

> **抄不动（成本高到不值）· 抄走也跑不起来（离开你服务端就是死壳）· 抄到的不是真东西（核心根本不在客户端）。**

本 skill 是 reverse-skill 的镜像反面：reverse-skill 教 AI 怎么拆你，clone-shield 教 AI 怎么守你。

> **验证状态**：本 skill 已用真实工具对抗验证（见 `VALIDATION.md`，9 个实验，JS/原生/.NET/APK/Frida/服务端全栈"加固前泄露→L2 后挖不到"）。**三个目标工具本体全部实测通过**：REA 0.2.1+Hopper（macOS 云机，加固前规则完整还原、L2 后零还原）、PentAGI 多 agent（云机，脆弱接口 200/200 全泄、加固后 0/200 任务 failed）、reverse-skill 全套工具链（webcrack/radare2/JADX/Frida 本机实打）。

## ⛔ 使用边界（每次必读）

- **只对你拥有、或拿到书面授权加固的软件使用。** 这是防守工具，不是攻击工具。
- **MUST NOT**：不生成攻击分析者机器的代码、不生成 hack-back / 投毒 payload、不伪造"你已违法/已报警"的恐吓、不帮别人绕过第三方的保护。让对方停下来的上限是"在自己代码里立一块看得懂的‘此地有主’牌子"，到此为止。
- **诚实前提（必须让用户知道）**：纯客户端的东西，给足时间和动机，**没有 100% 防得住的**。能跑在用户机器上，就必然能被 dump。本 skill 的目标不是"不可能被复制"，而是让复制**无价值、无法运行、代价高**。谁声称"客户端 100% 防破解"都是卖安慰剂。

## 核心教义（Doctrine，贯穿全程）

1. **客户端 = 公开区。** 发出去的 JS / APK / exe / 二进制，都当成攻击者已经完整拿到。
2. **价值搬到服务端。** 真正值钱的（算法、定价、风控、权限、数据）不放客户端；客户端只做展示和转发。这是对**黑盒复刻**和 **REA 证据链**唯一真正有效的一招。
3. **让复制品是死的。** 关键步骤服务端实时下发/校验，离线即废。抄到的是空壳。
4. **混淆只买时间，不买安全（已实测）。** 本机真实实验：JS 混淆被 webcrack 1 秒还原出全部秘密常量；同一秘密搬到服务端（L2）后，再强的反混淆也零还原。→ **任何秘密规则，L2 服务端化是必需项，L1 只是拖延外层。** 见 `references/verification.md`。
5. **合规刹车只筛守规矩的人。** 立"禁止逆向"的声明能挡掉一键梭哈的人，但 reverse-skill 自带"解除安全审查"垫片，铁了心的人直接跳过。所以刹车只是第 0 层，真正的拦截靠第 1–3 层。

## 工作流（路由契约，读完立即执行，不要停在"已理解"）

1. `NOW` 读 `references/threat-model.md` —— 搞清 REA / reverse-skill / PentAGI 每一步具体怎么打你。
2. `NOW` 跑 `scripts/recon.py <项目路径>` —— 识别技术栈、列出客户端暴露面、给资产分级、产出加固计划。
3. `THEN` 按资产分级，逐层加固（下表）。核心资产优先，别平均用力。
4. `THEN` 跑 `scripts/selfcheck.py <项目路径>` —— 打分，列出还漏的防护点。
5. `LOOP` 对照 `references/verification.md` 的自测矩阵，逐个工具验证"首步动作是否被反制"。没过的回到第 3 步补，**反复直到矩阵全绿**。
6. `LAST` 全绿后才动笔写文章 / 交付报告。

## 六层防护（按资产重要性差异化配置）

| 层 | 目标 | 防谁 | 参考 |
|---|---|---|---|
| L0 合规刹车 | 立"此地有主"声明，筛掉守规矩的顺手党 | reverse-skill 正常模式、REA 合规 agent | `references/layer4-agent-brake.md` |
| L1 客户端加固 | 混淆/虚拟化/WASM/字节码，破坏 REA 用的反编译器输出 | REA(Ghidra/IDA/JADX/WABT)、reverse-skill | `references/layer1-client-hardening.md` |
| L2 架构上云 | 核心逻辑服务端化 + 服务端绑定执行 | 黑盒复刻、REA 证据链 | `references/layer2-architecture.md` |
| L3 运行时自保护 | 反调试/反注入/完整性校验/静默降级 | REA 运行时 PTY 捕获、Frida 动态分析 | `references/layer3-rasp.md` |
| L4 服务端防渗透 | 限流/WAF/鉴权/设备证明 + 先自测 | PentAGI 多 agent 渗透 | `references/layer5-server-defense.md` |
| L5 取证与法律 | 指纹水印/蜜标 + EULA/DMCA/软著 | 事后维权 | `references/layer6-forensics-legal.md` |

## 完成判定（声称做完前 MUST 全部通过）

- [ ] recon 产出的"客户端暴露的核心资产"清单，已全部搬到服务端或加固到位
- [ ] selfcheck 无高危项（客户端无明文密钥、无 sourcemap、无调试符号、有完整性校验）
- [ ] verification 自测矩阵里 REA / reverse-skill / PentAGI 三列全部有对应反制且验证通过
- [ ] 已向用户说明"客户端无法 100% 防护"的现实与本次加固的实际边界
- [ ] 复制品离线无法运行（服务端绑定）已验证
