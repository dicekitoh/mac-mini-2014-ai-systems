const http = require("http");
const fs = require("fs");
const path = require("path");
const { exec } = require("child_process");
const url = require("url");

const PORT = 3000;

// 簡単な認証トークン（本番環境では環境変数などを使用）
const AUTH_TOKEN = "***REMOVED***";

// 公開エンドポイント（認証不要）
const PUBLIC_ENDPOINTS = [
  "/api/public/health",
  "/api/public/info",
  "/api/public/time",
  "/api/public/echo"
];

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const query = parsedUrl.query;

  // CORS headers
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

  // OPTIONS request handling
  if (req.method === "OPTIONS") {
    res.writeHead(200);
    res.end();
    return;
  }

  // 公開エンドポイントは認証不要
  if (!PUBLIC_ENDPOINTS.includes(pathname)) {
    // 認証チェック
    const authHeader = req.headers.authorization;
    if (!authHeader || authHeader !== `Bearer ${AUTH_TOKEN}`) {
      res.writeHead(401, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Unauthorized" }));
      return;
    }
  }

  // APIエンドポイント
  switch (pathname) {
    // 公開エンドポイント（認証不要）
    case "/api/public/health":
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ 
        status: "ok", 
        timestamp: new Date().toISOString(),
        message: "MacMini2014 API Server is running"
      }));
      break;

    case "/api/public/info":
      exec("hostname && echo '---' && uname -r && echo '---' && uptime", (err, stdout, stderr) => {
        if (err) {
          res.writeHead(500, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: err.message }));
        } else {
          const lines = stdout.split('---').map(line => line.trim());
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ 
            hostname: lines[0],
            kernel: lines[1],
            uptime: lines[2]
          }));
        }
      });
      break;

    case "/api/public/time":
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ 
        server_time: new Date().toISOString(),
        timezone: process.env.TZ || "UTC"
      }));
      break;

    case "/api/public/echo":
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ 
        message: query.message || "Hello from MacMini2014!",
        query_params: query
      }));
      break;

    // 認証が必要なエンドポイント
    case "/api/read-file":
      if (query.path) {
        fs.readFile(query.path, "utf8", (err, data) => {
          if (err) {
            res.writeHead(500, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ error: err.message }));
          } else {
            res.writeHead(200, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ content: data }));
          }
        });
      } else {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Path parameter required" }));
      }
      break;

    case "/api/list-directory":
      if (query.path) {
        fs.readdir(query.path, { withFileTypes: true }, (err, files) => {
          if (err) {
            res.writeHead(500, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ error: err.message }));
          } else {
            const fileList = files.map(file => ({
              name: file.name,
              type: file.isDirectory() ? "directory" : "file"
            }));
            res.writeHead(200, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ files: fileList }));
          }
        });
      } else {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Path parameter required" }));
      }
      break;

    case "/api/system-info":
      exec("uname -a && echo '---' && df -h && echo '---' && free -h", (err, stdout, stderr) => {
        if (err) {
          res.writeHead(500, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: err.message }));
        } else {
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ info: stdout }));
        }
      });
      break;

    case "/api/health":
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ status: "ok", timestamp: new Date().toISOString() }));
      break;

    default:
      res.writeHead(404, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ 
        error: "Not found",
        available_public_endpoints: PUBLIC_ENDPOINTS,
        note: "Other endpoints require Authorization header"
      }));
  }
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`MacMini2014 API Server running on http://0.0.0.0:${PORT}`);
  console.log("Public endpoints (no auth required):");
  PUBLIC_ENDPOINTS.forEach(endpoint => console.log(`  GET ${endpoint}`));
  console.log("\nProtected endpoints (auth required):");
  console.log("  GET /api/health");
  console.log("  GET /api/read-file?path=/path/to/file");
  console.log("  GET /api/list-directory?path=/path/to/dir");
  console.log("  GET /api/system-info");
});