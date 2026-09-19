# 🐋 Whale Hunter

**Hunt real whales. Live Nansen smart-money flows become the ocean.**

Built for the **Nansen Meridian Buildathon** (Sep 14–27, 2026). A arcade game where every whale you catch is a **real, live smart-money flow** — token symbol, chain, and USD size come straight from the Nansen API.

## 🎮 How it works

1. **Real flows feed the game.** `harvest.py` pulls smart-money netflows for 6 chains (Ethereum, Solana, Base, Arbitrum, BNB, Polygon) from the Nansen API and stores them as daily snapshots (`data/flows_YYYYMMDD.json`).
2. **Flows become whales.** Every whale swimming across your screen is a live flow: the bigger the net flow (USD), the bigger the whale. A $300K inflow is a monster; a $2K flow is a minnow.
3. **Catch whales, score points.** Click a whale before it dives. Points = flow size ÷ 100. Catch fast for **combo multipliers** up to ×3.5.
4. **⭐ GOLDEN whales** are mega flows over $100K — rare, fast, +250 bonus.

## 🔁 Sustainable by design

The game **stays alive after the buildathon**: `harvest.py` runs daily (cron) so the ocean refreshes with the real market every day. Each day of harvest = ~18 API calls that power every gameplay session. Credits aren't burned — they're the ocean's breath.

## 🛠 Tech

- Pure HTML5 Canvas + vanilla JS — no dependencies, no build step
- Python harvester using the Nansen Smart Money Netflow API
- Data: 1,200+ flows/day across 6 chains

## ▶️ Run

```bash
python harvest.py        # fetch today's real flows (needs NANSEN_API_KEY in nansen-bot/keys.json pool)
python -m http.server    # serve
# open http://localhost:8000
```

Built with 🦀 by [@aasunbul](https://github.com/aasunbul) · data by [Nansen](https://nansen.ai) · #MeridianBuildathon
