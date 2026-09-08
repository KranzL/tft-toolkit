import json
import re
import time
import urllib.request
from pathlib import Path

PAGE_URL = "https://tactics.tools/team-compositions"
API_URL = "https://api.tft.tools/team-compositions/{rank_group}/{patch_id}"
GENERAL_URL = "https://d3.tft.tools/stats2/general/1100/{patch_id}/{rank_group}"
BOARDS_PER_GAME = 8
RANK_GROUPS = {"master": 0, "diamond": 1, "emerald": 2, "platinum": 3, "gm": 4}
RANK_LABELS = {0: "Master+", 1: "Diamond+", 2: "Emerald+", 3: "Platinum+", 4: "Grandmaster+"}
HEADERS = {"User-Agent": "tft-toolkit/0.1 (personal meta tracker)", "Origin": "https://tactics.tools", "Referer": "https://tactics.tools/"}
CACHE_DIR = Path(__file__).resolve().parents[2] / "data" / "meta" / "cache"


def _fetch(url, ttl=1800, cache_key=None):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = cache_key or re.sub(r"[^A-Za-z0-9]+", "_", url)[-120:]
    path = CACHE_DIR / f"{key}.json"
    if path.exists() and time.time() - path.stat().st_mtime < ttl:
        return json.load(open(path))
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)
    json.dump(data, open(path, "w"))
    return data


def current_patch_id():
    req = urllib.request.Request(PAGE_URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
    if not m:
        raise RuntimeError("could not find page data on tactics.tools")
    j = json.loads(m.group(1))
    aperture = j["props"]["pageProps"]["aperture"]
    title = re.search(r"<title>(.*?)</title>", html)
    patch_label = None
    if title:
        pm = re.search(r"Patch ([0-9.]+[a-z]?)", title.group(1))
        patch_label = pm.group(1) if pm else None
    return aperture["patch"]["_0"], patch_label


def fetch_comps(rank_group=1, patch_id=None):
    patch_label = None
    if patch_id is None:
        patch_id, patch_label = current_patch_id()
    data = _fetch(API_URL.format(rank_group=rank_group, patch_id=patch_id), cache_key=f"tt_comps_{rank_group}_{patch_id}")
    return data, patch_id, patch_label


def fetch_general(rank_group=1, patch_id=None):
    if patch_id is None:
        patch_id, _ = current_patch_id()
    return _fetch(GENERAL_URL.format(rank_group=rank_group, patch_id=patch_id), cache_key=f"tt_general_{rank_group}_{patch_id}")


def comp_name(full, names):
    n = full.get("count", 0) or 1
    best = {}
    for tid, tier, count, place in full.get("traits", []):
        name = names.trait(tid)
        weight = (count / n) * (1 + 0.5 * tier)
        if name not in best or weight > best[name][0]:
            best[name] = (weight, tier, count)
    origins = [(w, nm) for nm, (w, tier, c) in best.items() if names.trait_kind.get(nm) == "origin"]
    classes = [(w, nm) for nm, (w, tier, c) in best.items() if names.trait_kind.get(nm) == "class"]
    origins.sort(reverse=True)
    classes.sort(reverse=True)
    prefix = origins[0][1] if origins and origins[0][0] >= 0.5 else (classes[0][1] if classes else "Flex")
    carries = [names.unit(u) for u, share in full.get("carryUnits", [])[:2]]
    if carries:
        return f"{prefix} {' & '.join(carries)}"
    return prefix


def normalize(data, names, rank_group=1, patch_id=None, patch_label=None):
    total = data.get("count", 0)
    comps = []
    for grp in data.get("groups", []):
        full = grp["full"]
        n = full.get("count", 0)
        if n == 0:
            continue
        best = full.get("comps", [{}])[0] if full.get("comps") else {}
        units = []
        seen_units = set()
        for uid in best.get("units", []):
            if uid in seen_units:
                continue
            seen_units.add(uid)
            units.append({"id": uid, "name": names.unit(uid)})
        core_units = []
        seen_core = set()
        for uid, tier, count, place in sorted(full.get("units", []), key=lambda r: -r[2]):
            if uid in seen_core:
                continue
            seen_core.add(uid)
            core_units.append({"id": uid, "name": names.unit(uid), "stars": tier, "rate": count / n if n else 0, "avg_place": place})
            if len(core_units) >= 12:
                break
        traits = []
        seen = set()
        for tid, tier, count, place in sorted(full.get("traits", []), key=lambda r: (-r[1], -r[2])):
            if tid in seen:
                continue
            seen.add(tid)
            traits.append({"id": tid, "name": names.trait(tid), "tier": tier, "rate": count / n if n else 0})
        regions = {}
        for region, per_game, place in full.get("regionDistribution", []):
            if per_game > 0:
                regions[region] = {"share": per_game / BOARDS_PER_GAME, "avg_place": place}
        trend = [{"date": d, "share": share, "avg_place": place} for d, share, place in sorted(full.get("dateStats", []))]
        region_trend = {}
        for region, d, share, place in full.get("regionDateStats", []):
            region_trend.setdefault(region, []).append({"date": d, "share": share, "avg_place": place})
        for r in region_trend.values():
            r.sort(key=lambda x: x["date"])
        players = [{"region": r, "name": nm, "avg_place_delta": v, "tag": tag} for r, nm, v, tag in full.get("topPlayers", [])[:10]]
        levels = {lvl: {"count": c, "place_sum": s} for lvl, c, s in full.get("levels", [])}
        emblems = {}
        for comp in full.get("spatComps", [])[:5]:
            for it in comp.get("spatItems", []):
                emblems[it] = emblems.get(it, 0) + comp.get("count", 0)
        comps.append({
            "source": "tactics.tools",
            "rank_group": RANK_LABELS.get(rank_group, str(rank_group)),
            "name": comp_name(full, names),
            "code": full.get("code"),
            "count": n,
            "share": n / total if total else 0,
            "avg_place": full.get("place"),
            "top4_rate": (full.get("top4", 0) / n) if n else 0,
            "win_rate": (full.get("win", 0) / n) if n else 0,
            "lp_delta": full.get("lpDelta"),
            "units": units,
            "core_units": core_units,
            "traits": traits[:8],
            "carries": [{"id": u, "name": names.unit(u), "weight": w} for u, w in full.get("carryUnits", [])[:3]],
            "win_conditions": [{"units": [names.unit(x.split("-")[0]) + (" 3-star" if x.endswith("-3") else "") for x in cond], "count": c, "avg_place": p} for cond, _, c, p in full.get("winCons", [])[:4]],
            "regions": regions,
            "trend": trend,
            "region_trend": region_trend,
            "top_players": players,
            "emblems": sorted(emblems.items(), key=lambda kv: -kv[1])[:4],
            "placement_distribution": full.get("placementDistribution"),
            "variants": [{"units": [names.unit(u) for u in dict.fromkeys(c.get("units", []))], "emblems": [names.trait_from_emblem(e) for e in c.get("spatItems", [])], "count": c.get("count"), "avg_place": c.get("place")} for c in full.get("comps", [])[:4]],
        })
    comps.sort(key=lambda c: (c["avg_place"] if c["avg_place"] is not None else 9, -c["count"]))
    return {"source": "tactics.tools", "rank_group": RANK_LABELS.get(rank_group), "patch_id": patch_id, "patch": patch_label, "games": total, "comps": comps}


def normalize_general(data, names):
    units = []
    for uid, s in data.get("units", {}).items():
        uname = names.unit(uid)
        units.append({"id": uid, "name": uname, "cost": names.unit_cost.get(uname.split(" (")[0]), "count": s.get("count"), "avg_place": s.get("place"), "top4": s.get("top4"), "win": s.get("won"),
                      "top_items": [names.item(i) for i in s.get("topItems", [])[:4]], "three_star_count": s.get("starCount"), "three_star_place": s.get("starPlace")})
    units.sort(key=lambda u: (u["avg_place"] if u["avg_place"] is not None else 9))
    traits = []
    for key, s in data.get("traits", {}).items():
        tid, _, tier = key.rpartition("__")
        traits.append({"id": tid, "name": names.trait(tid), "tier": int(tier) if tier.isdigit() else tier, "count": s.get("count"), "avg_place": s.get("place"), "top4": s.get("top4"), "win": s.get("won")})
    traits.sort(key=lambda t: (t["avg_place"] if t["avg_place"] is not None else 9))
    items = []
    for it in data.get("items", []):
        items.append({"id": it.get("itemId"), "name": names.item(it.get("itemId")), "count": it.get("count"), "avg_place": it.get("place"), "top4": it.get("top4"), "win": it.get("won")})
    items.sort(key=lambda i: (i["avg_place"] if i["avg_place"] is not None else 9))
    return {"total_entries": data.get("totalEntries"), "last_updated": data.get("lastUpdated"), "units": units, "traits": traits, "items": items}
