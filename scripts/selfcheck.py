#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clone-shield selfcheck: 扫你自己的客户端产物，找出高危暴露点并打分。
用法: python -I selfcheck.py <项目或产物路径>
只读。专查攻击者(REA/reverse-skill)最先捡漏的东西：明文密钥、sourcemap、调试符号、未声明等。
"""
import os, sys, re

SRC_EXT = ("js","mjs","ts","jsx","tsx","py","java","kt","cs","go","rs","c","cpp","h","swift","dart","json","env","map","config","xml","yml","yaml","properties")

# 高熵/密钥模式
SECRET_PATS = [
    (re.compile(r"-----BEGIN (RSA|EC|OPENSSH|PGP|PRIVATE) .*KEY-----"), "明文私钥"),
    (re.compile(r"(?i)(api[_-]?key|secret|passwd|password|token|access[_-]?key)\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}['\"]"), "硬编码密钥/口令"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS Access Key"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "疑似 API sk- 密钥"),
    (re.compile(r"(?i)mongodb(\+srv)?://[^\s'\"]+:[^\s'\"]+@"), "带口令的数据库连接串"),
]
SOURCEMAP_PAT = re.compile(r"sourceMappingURL=.+\.map")
CORE_HINT = re.compile(r"(auth|license|pricing|billing|payment|crypto|secret|algorithm|risk|rule|verify|validat)", re.I)

def walk_files(root):
    for dp, dns, fns in os.walk(root):
        if any(x in dp for x in (".git", "node_modules", "venv", "__pycache__")):
            continue
        for f in fns:
            if f.rsplit(".",1)[-1].lower() in SRC_EXT:
                yield os.path.join(dp, f)

def main():
    if len(sys.argv) < 2:
        print("用法: python -I selfcheck.py <路径>"); sys.exit(1)
    root = os.path.abspath(sys.argv[1])
    high, med, info = [], [], []

    has_license_decl = False
    has_integrity = False
    map_files = 0

    for path in walk_files(root):
        rel = os.path.relpath(path, root)
        try:
            txt = open(path, "r", encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        low = txt.lower()
        if any(k in low for k in ("禁止逆向", "no reverse eng", "reverse engineering is prohibited", "专有软件", "proprietary")):
            has_license_decl = True
        if any(k in low for k in ("integrity", "checksum", "完整性", "tamper", "signature verif")):
            has_integrity = True
        if path.endswith(".map"):
            map_files += 1
            high.append((rel, "sourcemap 文件(.map) — 直接泄露源码结构"))
        if SOURCEMAP_PAT.search(txt):
            high.append((rel, "引用了 sourceMappingURL — 生产包应删除"))
        for pat, desc in SECRET_PATS:
            if pat.search(txt):
                high.append((rel, "明文敏感信息: " + desc))
        # 核心逻辑直接出现在疑似客户端源码里
        if CORE_HINT.search(rel) and path.rsplit(".",1)[-1].lower() in ("js","ts","py","cs","java"):
            if any(w in low for w in ("if (user.vip", "ispremium", "price =", "def verify", "function verify", "checklicense")):
                med.append((rel, "核心判断(会员/价格/校验)疑似在客户端 — 应搬服务端"))

    if not has_license_decl:
        med.append(("(全局)", "未发现‘禁止逆向/专有软件’声明 — 建议嵌入(L0)"))
    if not has_integrity:
        med.append(("(全局)", "未发现完整性/防篡改校验迹象 — 建议加(L3)"))

    print("="*60); print("clone-shield selfcheck ·", root); print("="*60)
    def dump(title, items):
        print(f"\n[{title}] {len(items)} 项")
        for rel, d in items[:40]:
            print(f"  - {rel}: {d}")
    dump("高危 HIGH", high)
    dump("中危 MED", med)

    score = max(0, 100 - len(high)*15 - len(med)*5)
    print("\n" + "="*60)
    print(f"暴露面评分: {score}/100  (高危 x{len(high)}, 中危 x{len(med)})")
    if high:
        print("结论: 有高危暴露，必须先清零高危(删 sourcemap / 移除明文密钥)再谈其它层。")
    elif med:
        print("结论: 无高危，按中危项补齐 L0/L2/L3。")
    else:
        print("结论: 自动扫描无明显暴露。继续对 verification.md 做人工矩阵验证。")
    print("注意: 本脚本只查‘能自动查的’。虚拟化强度、服务端绑定、限流等仍需按 verification.md 人工验证。")

if __name__ == "__main__":
    main()
