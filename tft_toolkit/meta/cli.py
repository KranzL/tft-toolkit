import argparse
import json
import os
import sys

from tft_toolkit.meta import report


def cmd_refresh(args):
    snap = report.build_snapshot(rank=args.rank, include_riot=not args.no_riot, riot_days=args.days)
    out = report.write_outputs(snap)
    report.print_summary(snap, region=args.region)
    print(f"\nDashboard: file://{out}")


def cmd_show(args):
    path = report.SNAPSHOT_DIR / "latest.json"
    if not path.exists():
        sys.exit("no snapshot yet, run: python -m tft_toolkit.meta refresh")
    snap = json.load(open(path))
    report.print_summary(snap, region=args.region, limit=args.limit)


def cmd_collect(args):
    from tft_toolkit.meta.collect import collect
    from tft_toolkit.meta.riot_api import RiotClient
    from tft_toolkit.meta.store import Store
    if not os.environ.get("RIOT_API_KEY"):
        sys.exit("RIOT_API_KEY is not set. Create a key at https://developer.riotgames.com (development keys expire after 24 hours) and export it.")
    client = RiotClient(log=print)
    store = Store()
    stats = collect(client, store, platforms=args.platforms, players_per_platform=args.players, matches_per_player=args.matches,
                    max_requests=args.max_requests, resolve_names=not args.no_names)
    print(json.dumps(stats, indent=1))
    print("store:", store.counts())


def cmd_ladder(args):
    from tft_toolkit.meta.store import Store
    store = Store()
    rows = store.players(platform=args.platform, limit=args.limit)
    if not rows:
        sys.exit("no ladder data yet, run: python -m tft_toolkit.meta collect")
    for r in rows:
        name = f"{r['game_name']}#{r['tag_line']}" if r.get("game_name") else r["puuid"][:12]
        print(f"{r['platform']:5s} {r['tier']:12s} {r['lp']:5d} LP  {r['wins']:3d}W {r['losses']:3d}L  {name}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tft-meta", description="Track what is climbing in TFT ranked across regions.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("refresh", help="pull fresh data from all sources and rebuild the dashboard")
    r.add_argument("--rank", choices=["master", "diamond", "emerald", "platinum", "gm"], default="master", help="rank floor for the tactics.tools sample")
    r.add_argument("--region", default=None, help="platform id to highlight in the terminal summary, e.g. kr, na1, euw1")
    r.add_argument("--days", type=int, default=7, help="days of Riot API matches to analyze")
    r.add_argument("--no-riot", action="store_true")
    r.set_defaults(func=cmd_refresh)

    s = sub.add_parser("show", help="print the latest snapshot summary")
    s.add_argument("--region", default=None)
    s.add_argument("--limit", type=int, default=12)
    s.set_defaults(func=cmd_show)

    c = sub.add_parser("collect", help="pull Master+ ladder players and their recent matches from the Riot API")
    c.add_argument("--platforms", nargs="+", default=["na1", "euw1", "kr"], help="platform ids: na1 euw1 eun1 kr jp1 br1 la1 la2 oc1 tr1 ru sg2 tw2 vn2 me1")
    c.add_argument("--players", type=int, default=60, help="top players per platform to sample")
    c.add_argument("--matches", type=int, default=10, help="recent matches per player")
    c.add_argument("--max-requests", type=int, default=None)
    c.add_argument("--no-names", action="store_true", help="skip resolving player names (saves one request per player)")
    c.set_defaults(func=cmd_collect)

    l = sub.add_parser("ladder", help="print collected ladder players")
    l.add_argument("--platform", default=None)
    l.add_argument("--limit", type=int, default=30)
    l.set_defaults(func=cmd_ladder)

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
