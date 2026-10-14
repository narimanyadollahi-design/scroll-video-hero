# Fallback server (Python 3) with HTTP Range support, for Mac/Linux without Node.
import http.server, os, re, socketserver, webbrowser
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def send_head(self):
        r = self.headers.get("Range"); path = self.translate_path(self.path)
        if os.path.isdir(path): path = os.path.join(path, "index.html")
        if not r or not os.path.isfile(path): return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)", r); size = os.path.getsize(path)
        s = int(m.group(1) or 0); e = int(m.group(2)) if m.group(2) else size - 1; e = min(e, size - 1)
        f = open(path, "rb"); f.seek(s)
        self.send_response(206); self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {s}-{e}/{size}"); self.send_header("Content-Length", str(e - s + 1))
        self.send_header("Accept-Ranges", "bytes"); self.end_headers()
        self._rng = (s, e); return f
    def copyfile(self, src, dst):
        if getattr(self, "_rng", None):
            s, e = self._rng; left = e - s + 1
            while left > 0:
                b = src.read(min(65536, left))
                if not b: break
                dst.write(b); left -= len(b)
            self._rng = None
        else: super().copyfile(src, dst)
    def log_message(self, *a): pass
port = 4173
while True:
    try: srv = socketserver.ThreadingTCPServer(("127.0.0.1", port), H); break
    except OSError: port += 1
print(f"\n  Site is running at http://localhost:{port}/\n  Press Ctrl+C to stop.\n")
webbrowser.open(f"http://localhost:{port}/"); srv.serve_forever()
