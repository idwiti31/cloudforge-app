import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

APP_VERSION = os.getenv("APP_VERSION", "v1")

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CloudForge | Deployment Dashboard</title>
  <style>
    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: Arial, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
    }

    main {
      max-width: 900px;
      margin: 55px auto;
      padding: 24px;
    }

    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 30px;
    }

    h1 { margin: 0 0 8px; }
    p { color: #94a3b8; line-height: 1.6; }

    .badge {
      background: #064e3b;
      color: #6ee7b7;
      padding: 9px 14px;
      border-radius: 24px;
      font-size: 14px;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 16px;
    }

    .card {
      background: #1e293b;
      border: 1px solid #334155;
      padding: 24px;
      border-radius: 14px;
    }

    .label {
      color: #94a3b8;
      font-size: 14px;
    }

    .value {
      font-size: 24px;
      font-weight: bold;
      margin-top: 12px;
    }

    .highlight { color: #60a5fa; }

    button {
      margin-top: 24px;
      padding: 12px 18px;
      border: 0;
      border-radius: 8px;
      background: #2563eb;
      color: white;
      cursor: pointer;
      font-size: 15px;
    }

    button:hover { background: #1d4ed8; }
    footer { margin-top: 35px; color: #64748b; font-size: 13px; }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>☁️ CloudForge</h1>
        <p>Deployment Dashboard · DevOps playground</p>
      </div>
      <span class="badge" id="status">Checking status...</span>
    </header>

    <section class="grid">
      <div class="card">
        <div class="label">API Status</div>
        <div class="value" id="api">Checking...</div>
      </div>

      <div class="card">
        <div class="label">App Version</div>
        <div class="value highlight" id="version">Loading...</div>
      </div>

      <div class="card">
        <div class="label">Container Platform</div>
        <div class="value">Docker</div>
      </div>

      <div class="card">
        <div class="label">Orchestration</div>
        <div class="value">Kubernetes</div>
      </div>
    </section>

    <div class="card" style="margin-top: 20px">
      <h3>Deployment message</h3>
      <p id="message">Connecting to the CloudForge API...</p>
      <button onclick="loadStatus()">Refresh status</button>
    </div>

    <footer>
      CloudForge · Built with Python, Docker, Kubernetes and GitHub Actions
    </footer>
  </main>

  <script>
    async function loadStatus() {
      const status = document.getElementById("status");
      const api = document.getElementById("api");
      const version = document.getElementById("version");
      const message = document.getElementById("message");

      try {
        const response = await fetch("/api/status");
        if (!response.ok) throw new Error("API unavailable");

        const data = await response.json();

        status.textContent = "● Healthy";
        api.textContent = data.status;
        version.textContent = data.version;
        message.textContent =
          "CloudForge is running version " + data.version +
          ". Your deployment dashboard is connected to the API.";
      } catch (error) {
        status.textContent = "Unavailable";
        api.textContent = "Offline";
        message.textContent = "Could not connect to the API. Please try again.";
      }
    }

    loadStatus();
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/":
            body = HTML.encode("utf-8")
            content_type = "text/html; charset=utf-8"
            status_code = 200

        elif path in ("/health", "/ready", "/api/status"):
            data = {
                "status": "healthy",
                "path": path,
            }

            if path == "/api/status":
                data["version"] = os.getenv("APP_VERSION", APP_VERSION)
                data["service"] = "cloudforge-api"

            body = json.dumps(data).encode("utf-8")
            content_type = "application/json; charset=utf-8"
            status_code = 200

        else:
            body = json.dumps({"error": "Not found"}).encode("utf-8")
            content_type = "application/json; charset=utf-8"
            status_code = 404

        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print(f"CloudForge listening on port 8080 (version {APP_VERSION})")
    server.serve_forever()
