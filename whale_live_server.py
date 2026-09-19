"""Whale Hunter LIVE server — makes the ocean genuinely alive.
Serves fresh smart-money netflows from the Nansen key pool with per-chain caching,
CORS open for the game page, rate-limited to protect credits.
GET /api/live            → next chain round-robin (cache 2 min)
GET /api/live?chain=solana → specific chain
GET /api/health          → uptime + cache stats (no API call)
Binds 127.0.0.1 only.
"""
import json, sys, time, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, "C:/Users/aasun/nansen-bot")
from key_pool import api

CHAINS = ["ethereum", "solana", "base", "arbitrum", "bnb", "polygon"]
CACHE_TTL = 120          # seconds per chain
MIN_CALL_GAP = 45        # global min seconds between key-pool calls

cache = {}               # chain → {ts, flows}
rr = {"i": 0}
last_call = {"t": 0.0}
lock = threading.Lock()
stats = {"calls": 0, "served": 0, "new_tokens": 0, "start": time.time()}


def fetch_chain(chain):
    """Pull netflow for chain; returns flows list (may be empty on error)."""
    now = time.time()
    with lock:
        c = cache.get(chain)
        if c and now - c["ts"] < CACHE_TTL:
            return c["flows"], True
        if now - last_call["t"] < MIN_CALL_GAP:
            # rate-gated: return stale cache for this chain if any,
            # else the freshest cached chain (never empty if any cache exists)
            if c:
                return c["flows"], True
            best = None
            for ch2, v in cache.items():
                if best is None or v["ts"] > cache[best]["ts"]:
                    best = ch2
            return (cache[best]["flows"] if best else []), (best is not None)
        last_call["t"] = now
    flows = []
    page = 1
    while True:
        try:
            body, _rem = api("smart-money/netflow",
                             {"chains": [chain], "pagination": {"page": page, "per_page": 100}})
        except Exception as e:
            print(f"[live] {chain} p{page} error: {e}", flush=True)
            break
        rows = body.get("data", []) if isinstance(body, dict) else []
        if not rows:
            break
        for f in rows:
            flows.append({
                "token": (f.get("token_symbol") or "?").strip(),
                "token_address": f.get("token_address") or "",
                "chain": f.get("chain") or chain,
                "net_1h": f.get("net_flow_1h_usd") or 0,
                "net_24h": f.get("net_flow_24h_usd") or 0,
                "net_7d": f.get("net_flow_7d_usd") or 0,
                "net_30d": f.get("net_flow_30d_usd") or 0,
                "traders": f.get("trader_count") or 0,
                "sector": (f.get("token_sectors") or ["?"])[0],
                "mcap": f.get("market_cap_usd") or 0,
            })
        pg = body.get("pagination", {}) if isinstance(body, dict) else {}
        if pg.get("is_last_page", True) or page >= 2:
            break
        page += 1
    with lock:
        old = {f["token"] for f in (cache.get(chain) or {}).get("flows", [])}
        stats["calls"] += 1
        stats["new_tokens"] += sum(1 for f in flows if f["token"] not in old)
        cache[chain] = {"ts": time.time(), "flows": flows}
    return flows, False


class H(BaseHTTPRequestHandler):
    def _send(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        stats["served"] += 1
        if u.path == "/api/health":
            with lock:
                cached = {c: round(time.time() - v["ts"]) for c, v in cache.items()}
            return self._send({"ok": True, "uptime_s": round(time.time() - stats["start"]),
                               "api_calls": stats["calls"], "served": stats["served"],
                               "new_tokens_seen": stats["new_tokens"], "cache_age_s": cached})
        if u.path == "/api/live":
            q = parse_qs(u.query)
            chain = (q.get("chain") or [""])[0].lower()
            if chain not in CHAINS:
                with lock:
                    chain = CHAINS[rr["i"] % len(CHAINS)]
                    rr["i"] += 1
            flows, cached_hit = fetch_chain(chain)
            with lock:
                cc = cache.get(chain)
                age = round(time.time() - cc["ts"]) if cc else -1
                real_chain = cc["flows"][0]["chain"] if cc and cc["flows"] else chain
            return self._send({"chain": real_chain, "ts": int(time.time()), "cache_age_s": age,
                               "count": len(flows), "flows": flows[:150]})
        self._send({"error": "not found"}, 404)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", 8083), H)
    print("[live] whale-live-server on http://127.0.0.1:8083", flush=True)
    srv.serve_forever()
