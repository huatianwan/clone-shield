# 脆弱服务端（PentAGI 会秒破）：/api/user/<id> 无鉴权、可枚举、无限流
import http.server, json, re
USERS = {str(i): {"id": i, "name": f"user{i}", "email": f"u{i}@corp.com",
                  "phone": f"138-0000-{i:04d}", "plan": "pro"} for i in range(1, 201)}
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        m = re.match(r"/api/user/(\d+)", self.path)
        if m:
            u = USERS.get(m.group(1))
            if u:
                self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers()
                self.wfile.write(json.dumps(u).encode()); return
        self.send_response(404); self.end_headers()
if __name__ == "__main__":
    http.server.HTTPServer(("127.0.0.1", 8781), H).serve_forever()
