# TFT Toolkit

Two tools for Teamfight Tactics Set 18, Enchanted Wilds. Live at [lkranz.com/tft](https://lkranz.com/tft).

1. Emblem planner. Pick the emblems you are holding and get the boards that turn them into the most trait breakpoints, who holds which emblem, and a level-by-level path.
2. Meta Watch. What Master+ players are climbing with across NA, EU, KR, JP, BR, LATAM, OCE, TR, SEA and China, with rising and falling trends, region splits, units, traits and emblems. Add your own Riot API key to sample ladder players directly.

Everything runs in the browser. There is no backend and nothing to pay for. Vercel serves the static files and proxies two things the browser cannot reach directly: the tactics.tools page that carries the current patch id, and the Riot API hosts.

The set analysis, with every unit and trait, is in `docs/set18-analysis.md`.

## Running it locally

```
python3 -m http.server 8000
```

Then open http://localhost:8000. Without the Vercel proxies the meta page falls back to `latest` for the tactics.tools patch and the Riot ladder sampler will not work.

## Python versions

Same tools on the command line, no third-party packages needed.

```
python3 scripts/build_set_data.py
python3 scripts/build_planner_page.py
python3 -m tft_toolkit.planner Blossom Fae --level 8
python3 -m tft_toolkit.planner --list-emblems
python3 -m tft_toolkit.meta refresh --region kr
python3 -m tft_toolkit.meta show
```

Planner options: `--level N`, `--objective tiers|traits`, `--max-cost 4`, `--include UNIT`, `--exclude UNIT`, `--khazix-evolved`, `--json`.

`meta refresh` writes `data/meta/latest.json`, which the web page uses as a fallback when a live source is down. Commit it now and then so the fallback stays fresh.

### Riot API on the command line

```
export RIOT_API_KEY=RGAPI-...
python3 -m tft_toolkit.meta collect --platforms na1 euw1 kr --players 60 --matches 10
python3 -m tft_toolkit.meta refresh
python3 -m tft_toolkit.meta ladder --platform kr
```

This pulls the full Challenger, Grandmaster and Master lists, samples the top players by LP, and stores their recent ranked games in `data/meta/matches.sqlite`. The browser version in Meta Watch does the same thing on a smaller scale with the key stored in your browser.

## After each patch

```
python3 scripts/build_set_data.py
python3 scripts/build_planner_page.py
python3 scripts/build_analysis_tables.py
```

## Tests

```
pip install -r requirements-dev.txt
python3 -m pytest -q
node --check js/*.js
```
