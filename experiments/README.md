# 可复现实验（clone-shield 真实对抗验证）

完整结果见 `../VALIDATION.md`。本目录是实验用的靶子与攻击脚本。

## JS 栈（reverse-skill 的 js-reverse 线 / REA 的 JS 静态读取路径）
```
# L1 仅混淆 → 被真实反混淆器秒破
npx javascript-obfuscator core.baseline.js --output core.l1.js --control-flow-flattening true --string-array true --string-array-encoding base64
npx webcrack core.l1.js -o cracked        # 结果：ACME/97/13/定价/0.87 全部还原

# L2 搬服务端 + 混淆 → 零还原
npx javascript-obfuscator core.l2.js --output core.l2.obf.js --control-flow-flattening true
npx webcrack core.l2.obf.js -o cracked2   # 结果：秘密规则一条都没还原，只剩 fetch
```

## 服务端栈（PentAGI 式 IDOR/BOLA 枚举）
```
python -I server_baseline.py        # 监听 :8781，无鉴权无限流
python -I server_hardened.py        # 监听 :8782，鉴权(对象归属)+限流
python -I attacker.py 8781                       # 结果：拖走 200/200 PII
python -I attacker.py 8782 valid-token-for-42    # 结果：403x20 + 429x180，泄露 0/200
```

## 原生栈（REA 原生路径 / reverse-skill 的 radare2·ida 线）
```
# 需便携工具：zig（编译）、radare2（攻击）
zig cc native_baseline.c -o lic_baseline.exe            # 基线(带符号)
zig cc native_baseline.c -O2 -s -o lic_l1.exe          # L1(strip)
rabin2 -z lic_baseline.exe        # 挖出 "ACME-" 秘密前缀
rabin2 -z lic_l1.exe              # strip 后 "ACME-" 仍在 → L1 不够
radare2 -q -c "aaa; s 0x401000; pd 60" lic_baseline.exe  # 反汇编出规则逻辑
zig cc native_l2.c -O2 -s -o lic_l2.exe                # L2(规则搬服务端)
rabin2 -z lic_l2.exe              # ACME 命中 0 → 秘密不在二进制里
```

## .NET 栈（REA 静态读 CIL / reverse-skill dotnet-reverse 线）
```
csc /optimize+ /out:Secret.exe License.cs           # 基线
csc /optimize+ /out:Secret_l2.exe License_l2.cs     # L2
python scan_net.py Secret.exe Secret_l2.exe         # 基线明文命中 ACME-/方法名；L2 消失
```

## APK/Java 栈（REA 的 APK 路径 / reverse-skill apk-reverse 线）
```
javac License.java LicenseL2.java
jadx -d jadx_base License.class       # 完整还原出 startsWith("ACME-")/%97==13
jadx -d jadx_l2 LicenseL2.class       # 只剩 remoteVerify，秘密规则全消失
```

## 文件
- `core.baseline.js`：含秘密规则的明文客户端
- `core.l2.js`：L2 加固后的客户端（算法已移服务端，只剩 fetch）
- `server_baseline.py` / `server_hardened.py`：脆弱 vs 加固服务端
- `attacker.py`：PentAGI 式自主枚举攻击脚本
