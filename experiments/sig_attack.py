import urllib.request, hmac, hashlib, time
SECRET = b"server-side-shared-secret"
base = "http://127.0.0.1:8783/api/data"
def call(ts, sig, label):
    r = urllib.request.Request(base, headers={"X-Ts": str(ts), "X-Sig": sig})
    try:
        resp = urllib.request.urlopen(r, timeout=5); print(f"{label:<28} -> {resp.getcode()} {resp.read().decode()}")
    except urllib.error.HTTPError as e: print(f"{label:<28} -> {e.code} {e.read().decode()}")
now = time.time()
good = hmac.new(SECRET, f"/api/data|{now}".encode(), hashlib.sha256).hexdigest()
call(now, good, "合法签名")                       # 期望 200
call(now, "deadbeef"*8, "伪造签名(攻击者无密钥)")  # 期望 401
call(now, "", "无签名")                            # 期望 401
call(now-120, good, "重放旧请求(过期时间戳)")       # 期望 401
