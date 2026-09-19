# 🐋 Whale Hunter

**Hunt real whales. Live Nansen smart-money flows become the ocean.**

Built for the **Nansen Meridian Buildathon** (Sep 14–27, 2026). A arcade game where every whale you catch is a **real, live smart-money flow** — token symbol, chain, and USD size come straight from the Nansen API.

## 🎮 How it works

1. **Real flows feed the game.** `harvest.py` pulls smart-money netflows for 6 chains (Ethereum, Solana, Base, Arbitrum, BNB, Polygon) from the Nansen API and stores them as daily snapshots (`data/flows_YYYYMMDD.json`).
2. **Flows become whales.** Every whale swimming across your screen is a live flow: the bigger the net flow (USD), the bigger the whale. A $300K inflow is a monster; a $2K flow is a minnow. Each whale wears its **chain's color** as a stripe.
3. **Catch whales, score points.** Click a whale before it dives (they blink when about to dive!). Points = flow size ÷ 100. Chain catches fast for **combo multipliers** up to ×3.5.
4. **⭐ GOLDEN whales** are mega inflows over $100K — rare, fast, +250 bonus, fanfare jingle.
5. **🦈 SHARKS are outflows** — smart money LEAVING a token. Catching one costs you points (and pride). Read the market, not just the whales.
6. **◉ SONAR PULSE** (SPACE, costs 200 pts, 8s cooldown): 3 seconds of x-ray vision — whales ringed in gold, labels enlarged.
7. **Two modes**: ⏱ TIMED HUNT (60s high-score chase) and 🌊 ENDLESS (relaxed). Waves every 25s — whales swim faster and spawn denser each wave.
8. **Sound effects** synthesized live with WebAudio (no files) — rising catch pitch, golden fanfare, shark growl, sonar ping.
9. **End screen**: score, biggest catch, best combo, accuracy, golden count, per-mode high score (localStorage) + one-click **share-your-score** tweet.

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
