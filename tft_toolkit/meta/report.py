import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tft_toolkit.meta import tactics_tools, tencent
from tft_toolkit.meta.analyze import Names, player_stats, region_breakdown, summarize_boards, trait_stats, unit_stats
from tft_toolkit.meta.riot_api import PLATFORM_LABELS
from tft_toolkit.meta.store import Store

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = ROOT / "data" / "meta"


def build_snapshot(rank="master", include_riot=True, riot_days=7, log=print):
    names = Names()
    snap = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "set": names.data.set_number,
            "set_name": names.data.set_name, "region_labels": PLATFORM_LABELS, "unit_costs": names.unit_cost}

    log("fetching tactics.tools comps")
    rank_group = tactics_tools.RANK_GROUPS.get(rank, 0)
    raw, patch_id, patch_label = tactics_tools.fetch_comps(rank_group=rank_group)
    tt = tactics_tools.normalize(raw, names, rank_group=rank_group, patch_id=patch_id, patch_label=patch_label)
    try:
        general = tactics_tools.normalize_general(tactics_tools.fetch_general(rank_group=rank_group, patch_id=patch_id), names)
    except Exception as e:
        log(f"general stats unavailable: {e}")
        general = None
    tt["general"] = general
    snap["tactics"] = tt

    log("fetching Tencent China server data")
    try:
        ids = tencent.TencentIds(names)
        cn = tencent.fetch_comps(ids)
        cn["units"] = tencent.fetch_units(ids)
        cn["traits"] = tencent.fetch_traits(ids)
        cn["curated"] = tencent.fetch_curated(ids)
        snap["tencent"] = cn
    except Exception as e:
        log(f"Tencent data unavailable: {e}")
        snap["tencent"] = None

    snap["riot"] = None
    if include_riot:
        store = Store()
        counts = store.counts()
        if counts["matches"]:
            since = (datetime.now(timezone.utc) - timedelta(days=riot_days)).timestamp() * 1000
            boards = store.boards(since_ms=since, set_number=names.data.set_number, queue_id=1100)
            comps = summarize_boards(boards, names, min_count=max(5, len(boards) // 150))
            snap["riot"] = {
                "boards": len(boards), "matches": counts["matches"], "players_tracked": counts["players"], "days": riot_days,
                "comps": comps, "traits": trait_stats(boards, names), "units": unit_stats(boards, names),
                "players": player_stats(boards, store.players(), names), "regions": region_breakdown(comps, boards),
            }
    return snap


def trend_delta(trend):
    if not trend or len(trend) < 3:
        return 0.0
    head = trend[:2]
    tail = trend[-2:]
    a = sum(t["share"] for t in head) / len(head)
    b = sum(t["share"] for t in tail) / len(tail)
    return b - a


def write_outputs(snap, log=print):
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M")
    latest = SNAPSHOT_DIR / "latest.json"
    dated = SNAPSHOT_DIR / f"snapshot-{stamp}.json"
    for c in snap["tactics"]["comps"]:
        c["trend_delta"] = trend_delta(c["trend"])
    json.dump(snap, open(latest, "w"), ensure_ascii=False)
    json.dump(snap, open(dated, "w"), ensure_ascii=False)
    log(f"wrote {latest}")
    return latest


def print_summary(snap, region=None, limit=12):
    tt = snap["tactics"]
    print(f"Set {snap['set']} {snap['set_name']} | tactics.tools {tt['rank_group']} patch {tt.get('patch')} | {tt['games']:,} games | generated {snap['generated_at']}")
    comps = [c for c in tt["comps"] if c["share"] >= 0.004]
    if region:
        comps = [c for c in comps if region in c["regions"]]
        comps.sort(key=lambda c: -c["regions"][region]["share"])
        print(f"\nTop comps in {PLATFORM_LABELS.get(region, region)} (by play share in that region)")
    else:
        comps.sort(key=lambda c: -c["count"])
        print("\nMost played comps (all regions)")
    print(f"{'comp':40s} {'share':>6s} {'place':>6s} {'top4':>5s} {'win':>5s} {'trend':>6s}  units")
    for c in comps[:limit]:
        share = c["regions"][region]["share"] if region else c["share"]
        place = c["regions"][region]["avg_place"] if region else c["avg_place"]
        delta = c.get("trend_delta", 0) * 100
        arrow = "+" if delta > 0.15 else ("-" if delta < -0.15 else " ")
        print(f"{c['name'][:40]:40s} {share*100:5.1f}% {place:6.2f} {c['top4_rate']*100:4.0f}% {c['win_rate']*100:4.0f}% {arrow}{abs(delta):4.1f}  {', '.join(u['name'] for u in c['units'])}")
    strong = sorted([c for c in tt["comps"] if c["share"] >= 0.01], key=lambda c: c["avg_place"])[:6]
    print("\nBest average placement (at least 1% play share)")
    for c in strong:
        print(f"  {c['name'][:40]:40s} place {c['avg_place']:.2f} share {c['share']*100:.1f}%")
    rising = sorted([c for c in tt["comps"] if c["share"] >= 0.005], key=lambda c: -c.get("trend_delta", 0))[:5]
    falling = sorted([c for c in tt["comps"] if c["share"] >= 0.005], key=lambda c: c.get("trend_delta", 0))[:5]
    print("\nRising this week: " + "; ".join(f"{c['name']} (+{c['trend_delta']*100:.1f} pts)" for c in rising if c["trend_delta"] > 0))
    print("Falling this week: " + "; ".join(f"{c['name']} ({c['trend_delta']*100:.1f} pts)" for c in falling if c["trend_delta"] < 0))
    cn = snap.get("tencent")
    if cn:
        print(f"\nChina Master+ (Tencent, patch {cn.get('patch')}, {cn.get('date')})")
        for c in cn["comps"][:8]:
            print(f"  {c['name'][:40]:40s} place {c['avg_place']:.2f} top4 {c['top4_rate']*100:.0f}% win {c['win_rate']*100:.0f}% games {c['raw'].get('use_num')}  {', '.join(c['units'])}")
    riot = snap.get("riot")
    if riot:
        print(f"\nRiot API sample: {riot['boards']} boards from {riot['matches']} matches, last {riot['days']} days")
        for c in riot["comps"][:8]:
            print(f"  {c['name'][:40]:40s} n {c['count']:4d} place {c['avg_place']:.2f} top4 {c['top4_rate']*100:.0f}%")
    else:
        print("\nRiot API ladder sample: none yet (set RIOT_API_KEY and run: python -m tft_toolkit.meta collect)")
