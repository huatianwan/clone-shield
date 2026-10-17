import frida, sys, time
# 真实 Frida 注入：spawn 目标 exe，注入 frida-agent，捕获子进程输出
exe, key = sys.argv[1], sys.argv[2]
dev = frida.get_local_device()
out = []
def on_output(pid, fd, data):
    if data: out.append(bytes(data))
dev.on("output", on_output)
pid = dev.spawn([exe, key], stdio="pipe")   # 注入发生在 spawn+attach
sess = dev.attach(pid)                        # frida-agent 加载进目标
dev.resume(pid)
time.sleep(1.2)
try: sess.detach()
except Exception: pass
print("Frida 注入下，程序判定:", b"".join(out).decode(errors="ignore").strip())
