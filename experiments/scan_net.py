import sys
# 模拟 REA 对 .NET 的静态读取：扫元数据/字符串堆里的明文(ASCII + UTF-16)
for f in sys.argv[1:]:
    data = open(f, "rb").read()
    print(f"\n=== {f} ({len(data)} bytes) ===")
    for needle in ["ACME-", "LicenseValid", "StartsWith", "RemoteVerify", "ReadLine"]:
        a = needle.encode("ascii")
        u = needle.encode("utf-16-le")
        hit = "命中" if (a in data or u in data) else "未找到"
        print(f"  {needle:<14} {hit}")
