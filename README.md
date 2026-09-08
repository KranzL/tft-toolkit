# tft-toolkit

Two tools for Teamfight Tactics Set 18, Enchanted Wilds.

1. Emblem planner. Give it the emblems you are holding and it finds the boards that turn them into the most trait breakpoints, with a level-by-level path.
2. Meta tracker. Pulls what Master+ players are climbing with across NA, EU, KR, JP, BR, LATAM, OCE, TR, SEA and China, and builds a dashboard.

There is also a full write-up of the set's units and traits in `docs/set18-analysis.md`.

## Setup

Python 3.11 or newer, no third-party packages needed at runtime.

```
cd tft-toolkit
python3 scripts/build_set_data.py
python3 scripts/build_planner_page.py
```

The first script pulls the live set data from Community Dragon into `data/set18.json`. Run it again after each patch. The second builds the planner web page.

## Emblem planner

Command line:

```
python3 -m tft_toolkit.planner Blossom Fae --level 8
python3 -m tft_toolkit.planner "Brawler x2" Lunar --level 9 --include "Master Yi" --exclude Taric
python3 -m tft_toolkit.planner --list-emblems
```

Options:

- `--level N` board size, default 8
- `--objective tiers|traits` push the strongest breakpoints (default) or the largest number of active traits
- `--max-cost 4` leave out 5-costs
- `--include UNIT` and `--exclude UNIT`, repeatable
- `--khazix-evolved` let Kha'Zix carry a second class trait
- `--json` machine-readable output

Web page: open `web/planner.html`. It runs entirely in the browser and works on a phone.

What the solver knows: Lux counts twice for her chosen origin, Elder Dragon takes two slots and adds two Riftbeast, Eclipse turns on at Solar 3 plus Lunar 3, a unit cannot hold an emblem for a trait it already has, and each unit holds at most three items.

## Meta tracker

```
python3 -m tft_toolkit.meta refresh
python3 -m tft_toolkit.meta show --region kr
```

`refresh` pulls the current patch from tactics.tools (all Riot regions, per-region and per-day breakdowns, top players per comp), the Master+ China server data from Tencent's official TFT site, and any Riot API matches you have collected. It writes `data/meta/latest.json` and the dashboard `web/meta.html`.

Rank floor for the global sample: `--rank master` (default), `--rank diamond`, `--rank emerald`, `--rank platinum`, `--rank gm`. Grandmaster and Challenger open a few weeks into a set, so early on `gm` returns the same games as `master`.

### Riot API ladder sampling

The Riot API gives per-player detail the aggregators do not: exactly which Master+ players are on which boards. Get a key at https://developer.riotgames.com (development keys last 24 hours, 100 requests per two minutes), then:

```
export RIOT_API_KEY=RGAPI-...
python3 -m tft_toolkit.meta collect --platforms na1 euw1 kr --players 60 --matches 10
python3 -m tft_toolkit.meta refresh
python3 -m tft_toolkit.meta ladder --platform kr
```

`collect` pulls the full Challenger, Grandmaster and Master lists for each platform, samples the top players by LP, stores their recent ranked games in `data/meta/matches.sqlite`, and skips games it already has. With a development key each platform takes roughly ten minutes for 60 players. Platforms: na1 euw1 eun1 kr jp1 br1 la1 la2 oc1 tr1 ru sg2 tw2 vn2 me1. China is not on the Riot API; the Tencent source covers it.

## Tests

```
pip install -r requirements-dev.txt
python3 -m pytest -q
```

## Layout

- `data/set18.json` units, traits, emblems, Lux forms and item names built from Community Dragon
- `tft_toolkit/planner` solver and CLI, `tft_toolkit/planner/templates/planner.html` the web page template
- `tft_toolkit/meta` Riot API client, sqlite store, collector, analysis, tactics.tools and Tencent sources, report and dashboard template
- `scripts` data builders
- `docs/set18-analysis.md` the set analysis
- `web` generated pages
