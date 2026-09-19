"""Whale Hunter PUBLIC proxy — serves /api/proxy for BYO Nansen keys (CORS *).
Combines game serving + proxy in one port for tunneling."""
import json, urllib.request, urllib.error, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent
BASE = "https://api.nansen.ai/api/v1"

last_call = {"t": 0.0}
lock = threading.Lock()

class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Cache-Control", "no-store")

    def _send(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(b)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            return self._send({"ok": True, "ts": int(time.time())})
        return self._send({"ok": True, "service": "whale-hunter-proxy"})

    def do_POST(self):
        if self.path != "/api/proxy":
            return self._send({"error": "not found"}, 404)
        try:
            n = int(self.headers.get("Content-Length") or 0)
            d = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._send({"error": "bad json"}, 400)
        path = d.get("path", "")
        payload = d.get("payload", {})
        api_key = d.get("apiKey", "")
        if not api_key or not path:
            return self._send({"error": "missing apiKey or path"}, 400)
        if not path.startswith(("smart-money/", "token/")):
            return self._send({"error": "path not allowed"}, 403)
        # global rate guard: 1 nansen call / 3s per proxy (BYO keys, still be polite)
        with lock:
            wait = 3 - (time.time() - last_call["t"])
        if wait > 0:
            time.sleep(wait)
        with lock:
            last_call["t"] = time.time()
        req = urllib.request.Request(
            f"{BASE}/{path}",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "apiKey": api_key},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = json.loads(r.read())
                return self._send({"data": body, "credits_remaining": r.headers.get("x-nansen-credits-remaining")})
        except urllib.error.HTTPError as e:
            try: detail = json.loads(e.read())
            except Exception: detail = None
            return self._send({"error": f"HTTP {e.code}", "detail": detail}, e.code)
        except Exception as e:
            return self._send({"error": str(e)[:200]}, 502)

    def log_message(self, *a): pass

if __name__ == "__main__":
    srv = ThreadingHTTPServer(("0.0.0.0", 8084), H)
    print("[proxy] whale-hunter public proxy on :8084", flush=True)
    srv.serve_forever()
