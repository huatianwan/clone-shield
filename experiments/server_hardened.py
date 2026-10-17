# clone-shield L4 加固服务端：鉴权(只能看自己) + 限流 + 异常检测
import http.server, json, re, time
from collections import defaultdict, deque
USERS = {str(i): {"id": i, "name": f"user{i}", "email": f"u{i}@corp.com",
                  "phone": f"138-0000-{i:04d}", "plan": "pro"} for i in range(1, 201)}
# 会话 token → 它所属的 user id（真实系统里由登录签发）
SESSIONS = {"valid-token-for-42": "42"}
RATE = defaultdict(deque)          # ip -> 请求时间戳
RATE_MAX, RATE_WIN = 20, 10.0      # 10 秒内最多 20 次
BLOCK = {}                         # ip -> 解封时间

class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _deny(self, code, msg):
        self.send_response(code); self.send_header("Content-Type","application/json"); self.end_headers()
        self.wfile.write(json.dumps({"error": msg}).encode())
    def do_GET(self):
        ip = self.client_address[0]; now = time.time()
        # 限流
        if ip in BLOCK and now < BLOCK[ip]:
            return self._deny(429, "rate limited")
        q = RATE[ip]; q.append(now)
        while q and now - q[0] > RATE_WIN: q.popleft()
        if len(q) > RATE_MAX:
            BLOCK[ip] = now + 30    # 异常高频 → 临时封
            return self._deny(429, "too many requests")
        m = re.match(r"/api/user/(\d+)", self.path)
        if not m: return self._deny(404, "not found")
        target = m.group(1)
        # 鉴权：必须带有效 token，且只能访问 token 绑定的 id（防 BOLA/IDOR）
        tok = self.headers.get("Authorization", "").replace("Bearer ", "")
        owner = SESSIONS.get(tok)
        if not owner: return self._deny(401, "unauthorized")
        if owner != target: return self._deny(403, "forbidden: not your object")
        u = USERS.get(target)
        if not u: return self._deny(404, "not found")
        self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers()
        self.wfile.write(json.dumps(u).encode())
if __name__ == "__main__":
    http.server.HTTPServer(("127.0.0.1", 8782), H).serve_forever()
