#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clone-shield recon: 扫描你自己的项目，识别技术栈、列出客户端暴露面、给资产分级、产出加固计划。
用法: python -I recon.py <项目路径>
只读，不修改任何文件。
"""
import os, sys, json, re

STACK_SIGNS = {
    "web-js":      ["package.json", "webpack.config.js", "vite.config.js", "index.html"],
    "electron":    ["electron", "app.asar", "electron-builder"],
    "android":     ["AndroidManifest.xml", "build.gradle", "proguard-rules.pro"],
    "ios":         ["Info.plist", "Podfile", ".xcodeproj"],
    "dotnet":      [".csproj", ".sln", "packages.config"],
    "python":      ["requirements.txt", "setup.py", "pyproject.toml"],
    "go":          ["go.mod"],
    "rust":        ["Cargo.toml"],
    "native-c":    ["CMakeLists.txt", "Makefile", ".vcxproj"],
}
# 名字里带这些词的文件/目录 = 可能的核心资产
CORE_HINTS = re.compile(r"(auth|license|licen[cs]e|pricing|price|billing|payment|crypto|secret|"
                        r"algorithm|algo|core|engine|model|risk|rule|verify|validat|token|key)", re.I)
# 客户端产物目录
CLIENT_DIRS = re.compile(r"(dist|build|out|public|www|assets|release|bin|obj|apk|ipa|renderer|static)", re.I)

def detect_stacks(root):
    found = {}
    for dp, dns, fns in os.walk(root):
        if any(x in dp for x in (".git", "node_modules", "venv", "__pycache__")):
            continue
        names = fns + dns
        for stack, signs in STACK_SIGNS.items():
            for s in signs:
                if any(s in n for n in names):
                    found.setdefault(stack, 0)
                    found[stack] += 1
    return sorted(found, key=found.get, reverse=True)

def find_core_assets(root, limit=60):
    hits = []
    for dp, dns, fns in os.walk(root):
        if any(x in dp for x in (".git", "node_modules", "venv", "__pycache__", "dist", "build")):
            continue
        for f in fns:
            if CORE_HINTS.search(f) and f.rsplit(".",1)[-1] in (
                "js","ts","jsx","tsx","py","java","kt","cs","go","rs","c","cpp","h","swift","dart"):
                rel = os.path.relpath(os.path.join(dp, f), root)
                hits.append(rel)
                if len(hits) >= limit:
                    return hits
    return hits

def find_client_artifacts(root):
    arts = []
    for dp, dns, fns in os.walk(root):
        base = os.path.basename(dp)
        if CLIENT_DIRS.fullmatch(base) or CLIENT_DIRS.search(base):
            if "node_modules" in dp or ".git" in dp:
                continue
            arts.append(os.path.relpath(dp, root))
    return arts[:30]

def main():
    if len(sys.argv) < 2:
        print("用法: python -I recon.py <项目路径>"); sys.exit(1)
    root = os.path.abspath(sys.argv[1])
    if not os.path.isdir(root):
        print("不是目录:", root); sys.exit(1)

    stacks = detect_stacks(root)
    core = find_core_assets(root)
    arts = find_client_artifacts(root)

    print("="*60)
    print("clone-shield recon ·", root)
    print("="*60)
    print("\n[技术栈] (按置信度)")
    for s in stacks: print("  -", s)
    if not stacks: print("  (未识别，手动确认)")

    print("\n[疑似核心资产] (名字命中 auth/pricing/algorithm/crypto... — 优先搬服务端或重度加固)")
    for c in core: print("  !", c)
    if not core: print("  (未自动命中，手动梳理)")

    print("\n[客户端产物目录] (攻击者 = 已完整拿到，当成公开区)")
    for a in arts: print("  *", a)

    print("\n[加固计划草案]")
    plan = []
    if core:
        plan.append("L2: 把上面的核心资产逐条评估，能上服务端的全上服务端")
    for s in stacks:
        tip = {
            "web-js":   "L1: 删 sourcemap + 核心编 WASM + 剩余混淆",
            "electron": "L1: asar 加密 + 核心编 V8 字节码/原生 .node",
            "android":  "L1: R8 混淆 + 核心下沉 so(OLLVM) + 完整性校验",
            "ios":      "L1: 符号剥离 + 字符串加密 + App Attest",
            "dotnet":   "L1: 混淆 + 核心虚拟化 + 运行时解密",
            "python":   "L1: Nuitka 编原生 / PyArmor",
            "go":       "L1: -ldflags '-s -w' + garble",
            "rust":     "L1: strip + 去 cargo-auditable + 控制流混淆",
            "native-c": "L1: OLLVM 控制流平坦化 + 核心 VMProtect",
        }.get(s)
        if tip: plan.append(tip)
    plan += [
        "L3: 加反调试/反 Frida + 异常环境静默降级 + 完整性校验",
        "L4: 服务端限流/鉴权/设备证明；先自己渗透测一遍",
        "L0/L5: 嵌入版权+禁止逆向声明；埋指纹/蜜标；办软著",
    ]
    for i, p in enumerate(plan, 1): print(f"  {i}. {p}")

    print("\n下一步: 按计划加固后，跑 selfcheck.py 打分，再对 verification.md 逐格验证。")

if __name__ == "__main__":
    main()
