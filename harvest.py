"""Whale Hunter — daily flows harvester (sustainable engine)
Pulls smart-money netflows (1h/24h/7d/30d) for 6 chains via key pool → data/flows_YYYYMMDD.json
"""
import json, os, sys, time
sys.path.insert(0, "C:/Users/aasun/nansen-bot")
from key_pool import api

OUT = "C:/Users/aasun/nansen-whale-hunter/data"
os.makedirs(OUT, exist_ok=True)

CHAINS = ["ethereum", "solana", "base", "arbitrum", "bnb", "polygon"]
all_flows = []
for ch in CHAINS:
    page = 1
    while True:
        try:
            body, rem = api("smart-money/netflow", {"chains": [ch], "pagination": {"page": page, "per_page": 100}})
            rows = body.get("data", []) if isinstance(body, dict) else body
        except Exception as e:
            print(f"{ch} p{page}: {e}")
            break
        if not rows:
            break
        for f in rows:
            all_flows.append({
                "token": (f.get("token_symbol") or "?").strip(),
                "token_address": f.get("token_address") or "",
                "chain": f.get("chain") or ch,
                "net_1h": f.get("net_flow_1h_usd") or 0,
                "net_24h": f.get("net_flow_24h_usd") or 0,
                "net_7d": f.get("net_flow_7d_usd") or 0,
                "net_30d": f.get("net_flow_30d_usd") or 0,
                "traders": f.get("trader_count") or 0,
                "sector": (f.get("token_sectors") or ["?"])[0],
                "mcap": f.get("market_cap_usd") or 0,
            })
        pg = body.get("pagination", {}) if isinstance(body, dict) else {}
        if pg.get("is_last_page", True) or page >= 3:
            break
        page += 1

day = time.strftime("%Y%m%d")
path = os.path.join(OUT, f"flows_{day}.json")
with open(path, "w", encoding="utf-8") as fh:
    json.dump({"date": day, "flows": all_flows}, fh)
print(f"saved {len(all_flows)} flows → {path}")
