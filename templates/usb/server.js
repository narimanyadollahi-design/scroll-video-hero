// Tiny static server with HTTP Range support (needed for scrubbing the hero video). No dependencies.
const http = require("http");
const fs = require("fs");
const path = require("path");
const { exec } = require("child_process");

const ROOT = path.join(__dirname, "site");
const MIME = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".json": "application/json", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
  ".svg": "image/svg+xml", ".woff2": "font/woff2", ".woff": "font/woff", ".mp4": "video/mp4", ".txt": "text/plain",
  ".ico": "image/x-icon", ".map": "application/json",
};

function send(res, code, body, headers = {}) { res.writeHead(code, headers); res.end(body); }

const server = http.createServer((req, res) => {
  let urlPath = decodeURIComponent(req.url.split("?")[0]);
  if (urlPath.endsWith("/")) urlPath += "index.html";
  let file = path.normalize(path.join(ROOT, urlPath));
  if (!file.startsWith(ROOT)) return send(res, 403, "Forbidden");
  fs.stat(file, (err, st) => {
    if (err || !st.isFile()) {
      const nf = path.join(ROOT, "404.html");
      return fs.readFile(nf, (e2, data) => send(res, 404, e2 ? "Not found" : data, { "Content-Type": "text/html; charset=utf-8" }));
    }
    const type = MIME[path.extname(file).toLowerCase()] || "application/octet-stream";
    const base = { "Content-Type": type, "Accept-Ranges": "bytes", "Cache-Control": "no-cache" };
    const range = req.headers.range;
    if (range) {
      const m = /bytes=(\d*)-(\d*)/.exec(range);
      let start = m && m[1] ? parseInt(m[1], 10) : 0;
      let end = m && m[2] ? parseInt(m[2], 10) : st.size - 1;
      if (isNaN(start) || isNaN(end) || start > end || start >= st.size) {
        return send(res, 416, "", { ...base, "Content-Range": `bytes */${st.size}` });
      }
      end = Math.min(end, st.size - 1);
      res.writeHead(206, { ...base, "Content-Range": `bytes ${start}-${end}/${st.size}`, "Content-Length": end - start + 1 });
      if (req.method === "HEAD") return res.end();
      return fs.createReadStream(file, { start, end }).pipe(res);
    }
    res.writeHead(200, { ...base, "Content-Length": st.size });
    if (req.method === "HEAD") return res.end();
    fs.createReadStream(file).pipe(res);
  });
});

function listen(port, tries) {
  server.once("error", (e) => {
    if (e.code === "EADDRINUSE" && tries > 0) listen(port + 1, tries - 1);
    else { console.error("Could not start the server:", e.message); process.exit(1); }
  });
  server.listen(port, "127.0.0.1", () => {
    const url = `http://localhost:${port}/`;
    console.log("\n  Site is running at " + url + "\n  Close this window to stop.\n");
    if (!process.env.NO_OPEN) {
      const cmd = process.platform === "win32" ? `start "" "${url}"` : process.platform === "darwin" ? `open "${url}"` : `xdg-open "${url}"`;
      exec(cmd);
    }
  });
}
listen(parseInt(process.env.PORT || "4173", 10), 20);
