# clone-shield · 防复刻护盾 Skill

让 Codex / Claude Code 把**你自己的软件**加固到"抄不动、抄走也没用"。针对 REA、reverse-skill、PentAGI 这类 AI 逆向/复刻/渗透工具定点防守。

> ⚠️ 防守工具，只对你拥有或有权加固的软件使用。客户端无法 100% 防护——目标是让复制**无价值、无法运行、代价高**。

## 结构
```
clone-shield/
  SKILL.md                      入口：边界、教义、工作流、六层总表、完成判定
  references/
    threat-model.md             REA/reverse-skill/PentAGI 真实逻辑 + 首步动作→反制
    layer1-client-hardening.md  按栈加固，破坏反编译器输出
    layer2-architecture.md      核心上云 + 服务端绑定 + 协议/合约防护
    layer3-rasp.md              反调试/反注入/静默降级/服务端吊销
    layer4-agent-brake.md       合规刹车(只筛守规矩者，不能单独用)
    layer5-server-defense.md    防 PentAGI：限流/鉴权/设备证明/自测
    layer6-forensics-legal.md   指纹水印/蜜标 + EULA/DMCA/软著
    verification.md             自测矩阵，反复验证到全绿
  scripts/
    recon.py                    扫项目：识别栈/暴露面/资产分级/加固计划(只读)
    selfcheck.py                扫产物：明文密钥/sourcemap/符号/缺声明，打分(只读)
```

## 安装（Claude Code / Codex 通用）
把整个 `clone-shield/` 目录放到你的 skills 目录：
- Claude Code: `~/.claude/skills/clone-shield/`
- Codex: 按其 skill/agents 约定放入技能目录

触发：对 AI 说"用 clone-shield 加固我的项目"或"防复刻 / 防逆向 / 防破解我的代码"。

## 快速开始
```bash
python -I scripts/recon.py <你的项目路径>       # 看暴露面和加固计划
python -I scripts/selfcheck.py <你的产物路径>   # 打分，先清高危
# 然后按 SKILL.md 六层加固，对 verification.md 逐格验证到全绿
```

Windows 控制台中文乱码时：先 `set PYTHONUTF8=1` 或 `chcp 65001`。
