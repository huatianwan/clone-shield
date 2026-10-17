# L4 请求签名 + 防重放：无有效 HMAC 签名 / 过期时间戳 → 拒绝
import http.server, hmac, hashlib, time, re
SECRET = b"server-side-shared-secret"   # 只在服务端；客户端用设备下发的会话密钥
WINDOW = 30
def sign(path, ts): return hmac.new(SECRET, f"{path}|{ts}".encode(), hashlib.sha256).hexdigest()
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_GET(self):
        ts = self.headers.get("X-Ts",""); sig = self.headers.get("X-Sig","")
        path = self.path
        # 时间戳窗口（防重放）
        try: age = abs(time.time() - float(ts))
        except Exception: age = 1e9
        if age > WINDOW:
            self.send_response(401); self.end_headers(); self.wfile.write(b"stale/missing ts"); return
        # 签名校验（防伪造）
        if not hmac.compare_digest(sig, sign(path, ts)):
            self.send_response(401); self.end_headers(); self.wfile.write(b"bad signature"); return
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK data")
if __name__ == "__main__":
    http.server.HTTPServer(("127.0.0.1", 8783), H).serve_forever()
