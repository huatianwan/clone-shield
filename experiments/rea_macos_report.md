# REA 本体实测（macOS 云机，2026-10-17）

执行：在一台 macOS 云主机会话中按 `rea_task.md` 执行。
环境：macOS 26.6.2 / Apple M4 (Virtual) / 8 核 / 16 GB；@morluto/rea 0.2.1（`rea --version` 显示 0.1.0）；Hopper Disassembler 6.6.0 demo（brew cask）。

## rea doctor
```
healthy: true
hopperPath: /Applications/Hopper Disassembler.app/Contents/MacOS/hopper
checks: node 24.21.0 ok / macos 26.6.2 ok / hopper ok
```
首次运行前 `rea analyze` 两次 HopperTimeoutError(120s)，需要手动通过：Gatekeeper 确认 → Hopper 选 Try the Demo → TCC 自动化授权（允许控制 Hopper，主要卡点）→ Mach-O loader 选项确认。

## 工具缺陷（如实记录）
`rea analyze` 在两个靶子上都报 `HopperRemoteError: Hopper request failed (-32000): Unknown bridge method`。
原因（执行方查了源码）：CLI 把增强工具 `binary_overview` 原样发给 Hopper bridge，bridge 只认底层方法；增强工具只在 MCP 路径（`rea --mcp`）里接好了。
因此改用：`rea decompile`（正常）+ MCP 路径的 binary_overview / search_strings / list_strings（正常）。

## baseline（规则在客户端）
`rea decompile ./baseline _license_valid` 关键片段：
```
r0 = strncmp(arg0, "ACME-", 0x5);
...  r10 = r10 - 0x30; if ((r10 & 0xff) >= 0xa) r10 = 0x0;  r8 = r8 + ...
r9 = 0x151d07eb; asm { smull x9, w8, w9 };
if (r8 - (...) * 0x61 == 0xd) r0 = 0x1;
```
- search_strings ACME → `"0x1000005c8": "ACME-"`
- 结论：前缀 ACME- **挖出**；`sum % 97 == 13` **挖出**（0x61=97、0xd=13，除法编译成魔数乘法，但含义完整）。

## l2（规则搬到服务端）
- `_license_valid` → `read_server_response(); return;`
- `_read_server_response`（weak 桩）→ `getchar() == 0x31`
- `_main` → 只有 usage / VALID / INVALID 分支
- search_strings ACME → `{}`；list_strings 只有 `VALID\n`、`INVALID\n`、`usage: lic <key>`
- 结论：前缀和规则**都挖不到**，只剩一个转发调用。
- 小瑕疵：binary_overview 的 document 字段显示的是仍开着的 baseline.hop，但实际查询命中的是 l2。

## 判定
REA 本体 + Hopper 实测：baseline 秘密规则完整还原 → ❌；L2 后零还原 → ✅。和 radare2 / JADX / webcrack 的结论一致。
