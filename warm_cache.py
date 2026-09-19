"""Startup warmer: fills cache for all 6 chains (staggered by MIN_CALL_GAP) then exits.
Run alongside whale_live_server at boot so the ocean is always full."""
import sys, time
sys.path.insert(0, "C:/Users/aasun/nansen-bot")
import urllib.request, json

CHAINS = ["ethereum", "solana", "base", "arbitrum", "bnb", "polygon"]

for ch in CHAINS:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:8083/api/live?chain={ch}", timeout=90) as r:
            d = json.loads(r.read())
            print(f"{ch}: {d['count']} flows (age {d['cache_age_s']}s)", flush=True)
    except Exception as e:
        print(f"{ch}: {e}", flush=True)
    time.sleep(50)   # respect MIN_CALL_GAP
print("warm done", flush=True)
