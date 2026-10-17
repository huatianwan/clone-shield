# L1 · 客户端加固（破坏 REA / reverse-skill 的反编译器输出）

目标：让攻击者拆得动文件，但拆出来的是一堆读不懂的东西。核心机制——**降低反编译器输出质量**，因为 REA 把伪代码喂给 AI，伪代码越烂还原率越低（Promon 2026 Q1：从汇编喂比从伪代码喂低 2–5 倍；三层混淆后 ARM 还原率仅 8.5%）。

**原则**：按资产分级差异化配置，别平均用力。核心函数上最重的（虚拟化），重要函数混淆，一般函数加密/压缩。重度保护有体积和性能代价（OBsmith：JS-Confuser High 档 +7509% 体积、+295% 运行时），只用在核心上。

> ⚠️ **本机实测教训（2026-10-16）**：对一段含秘密规则的 JS 做了控制流平坦化+字符串数组混淆，用 webcrack 反混淆 **1 秒内把秘密常量全部还原**（ACME/97/13/定价/折扣），函数结构还原到几乎等于原始。**结论：JS 混淆（L1）单独用挡不住真实反混淆器，只能拖时间。任何秘密规则必须靠 L2 搬到服务端——同一实验里，L2 加固后 webcrack 零还原。** L1 永远是外层拖延，不是最终防线。细节见 `verification.md` 的真实对抗实验。

## 按技术栈对照

| 栈 | REA 后端 | 加固手段 | 工具 |
|---|---|---|---|
| 网页前端 JS | 读源码/sourcemap | ①删 sourcemap ②核心逻辑编 WASM ③剩余 JS 混淆 | javascript-obfuscator、wasm-pack(Rust)、emscripten |
| Electron | 解包 asar 读模块 | ①asar 加密 ②核心编 V8 字节码 ③核心逻辑挪原生 .node | bytenode、asarmor、electron-vite |
| Android | JADX 反编译 | ①R8/ProGuard 压缩混淆 ②核心下沉 JNI/so ③so 用 OLLVM ④完整性校验 | R8、DexGuard、OLLVM、ndk |
| iOS | Hopper/IDA | ①符号剥离 ②字符串加密 ③核心混淆 | iXGuard、strip |
| .NET | 静态读 CIL（不运行） | ①混淆 ②核心虚拟化 ③运行时解密（静态看不到） | ConfuserEx、.NET Reactor |
| Python | 读 .py/.pyc | ①Nuitka 编原生 ②PyArmor 加密 | Nuitka、PyArmor |
| Go/Rust 原生 | 静态解析元数据 | ①strip 符号 ②去 cargo-auditable ③控制流混淆 | -ldflags "-s -w"、garble、OLLVM |
| C/C++ 原生 | Ghidra/IDA 反编译 | ①控制流平坦化 ②虚拟化 ③加壳 | OLLVM、Tigress、VMProtect、Themida |
| 智能合约/EVM | EVM 字节码反编译 | 链上放最小公开逻辑，专有部分放链下（见 L2.6） | 代理合约、预言机 |

## 针对 REA 具体后端的"定点打击"

- **针对 Ghidra/IDA（原生）**：控制流平坦化（FLA）+ 虚假控制流（BCF）+ 指令替换（SUB）三件套，这正是 Promon 测出"相乘式"提升复杂度的组合。核心再加虚拟化（VMP），让反编译器根本还原不出结构。
- **针对 JADX（APK）**：R8 full mode + 名称混淆 + 把"值钱"的逻辑（授权、算法）用 JNI 下沉到 so，JADX 只能看到一个 native 方法声明。
- **针对 WABT（WASM）**：WASM 本身就比 JS 难读，但别把完整逻辑都塞进去——配合 L2，让 WASM 里也只是"调服务端"。
- **针对静态 .NET 读取**：因为 REA **不运行** .NET，用"运行时解密"最有效——核心方法体加密，运行时才解，静态 CIL 里是一团密文。

## 验收（selfcheck 会查）
- [ ] 生产包里没有 sourcemap（.map 文件、`//# sourceMappingURL`）
- [ ] 生产二进制已 strip 符号
- [ ] 核心算法/授权逻辑不在可直接反编译的层（已 WASM/so/虚拟化/运行时解密）
- [ ] 混淆是针对核心差异化的，不是对全量平均处理
