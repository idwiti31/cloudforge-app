from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/health", "/ready"):
            response = {
                "application": "CloudForge",
                "status": "healthy",
                "path": self.path
            }
            self.send_response(200)
        else:
            response = {"error": "Not found"}
            self.send_response(404)

        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        print(f"{self.client_address[0]} - {format % args}")

if __name__ == "__main__":
    print("CloudForge API starting on port 8080")
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
