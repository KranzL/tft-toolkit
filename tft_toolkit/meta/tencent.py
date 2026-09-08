import json
import re
import time
import urllib.request
from pathlib import Path

VERSION_CONFIG = "https://game.gtimg.cn/images/lol/tfth5lib/v1/versionconfig.json"
PROXY = "https://mlol.qt.qq.com/go/exploit/proxy"
CURATED = "https://game.gtimg.cn/images/lol/act/tftzlkauto/json/lineupJson/{season}/62/lineup_detail_total.json"
HEADERS = {"User-Agent": "Mozilla/5.0 tft-toolkit/0.1", "Referer": "https://lol.qq.com/tft/", "Origin": "https://lol.qq.com"}
TIER_PARTS = {"all": "255", "master": "0", "diamond": "1", "gold_emerald": "2", "below_gold": "3"}
TIER_LABELS = {"255": "All ranks", "0": "Master+", "1": "Diamond+", "2": "Gold to Emerald", "3": "Below Gold"}
CACHE_DIR = Path(__file__).resolve().parents[2] / "data" / "meta" / "cache"


def _get_json(url, ttl=3600, cache_key=None):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = cache_key or re.sub(r"[^A-Za-z0-9]+", "_", url)[-120:]
    path = CACHE_DIR / f"{key}.json"
    if path.exists() and time.time() - path.stat().st_mtime < ttl:
        return json.load(open(path))
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        starts = [i for i in (raw.find("{"), raw.find("[")) if i >= 0]
        data = json.loads(raw[min(starts):]) if starts else None
    json.dump(data, open(path, "w"), ensure_ascii=False)
    return data


def _proxy(alias, params, ttl=900):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = "qq_" + alias + "_" + re.sub(r"[^A-Za-z0-9]+", "_", json.dumps(params, sort_keys=True))
    path = CACHE_DIR / f"{key}.json"
    if path.exists() and time.time() - path.stat().st_mtime < ttl:
        return json.load(open(path))
    body = json.dumps({"req_alias": alias, "is_return_source": 0, "version_id": "v1", "req_params": params}).encode()
    req = urllib.request.Request(PROXY, data=body, headers={**HEADERS, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("result") != 0:
        raise RuntimeError(f"tencent proxy {alias} failed: {data.get('msg')} {data.get('err_msg')}")
    json.dump(data, open(path, "w"), ensure_ascii=False)
    return data


class TencentIds:
    def __init__(self, names):
        cfg = _get_json(VERSION_CONFIG, ttl=86400, cache_key="qq_versionconfig")
        current = next((c for c in cfg if c.get("idSeason", "").startswith("s18") and "m" not in c.get("idSeason", "")), cfg[0])
        self.season = current["idSeason"]
        self.version = (current.get("arrVersionLimit") or [None])[0]
        chess = _get_json(current["urlChessData"], ttl=86400, cache_key="qq_chess")
        race = _get_json(current["urlRaceData"], ttl=86400, cache_key="qq_race")
        job = _get_json(current["urlJobData"], ttl=86400, cache_key="qq_job")
        self.chess = {}
        self.chess_cn = {}
        for c in chess.get("data", []):
            api = c.get("hero_EN_name") or ""
            self.chess[c["chessId"]] = names.unit(api) if api else c.get("displayName")
            self.chess_cn[c["chessId"]] = c.get("displayName")
        self.traits = {}
        for t in race.get("data", []) + job.get("data", []):
            api = t.get("characterid") or ""
            self.traits[t["traitId"]] = names.trait(api) if api else t.get("name")
        self.names = names

    def unit(self, chess_id):
        return self.chess.get(str(chess_id), str(chess_id))

    def trait(self, trait_id):
        return self.traits.get(str(trait_id), str(trait_id))


def fetch_comps(ids: TencentIds, tier="master", time_type="v", queue="1100"):
    data = _proxy("tft_lineup_group_list", {"queue_id": queue, "tier_part": TIER_PARTS[tier], "time_type": time_type})["data"]
    comps = []
    for entry in data.get("main_traits_data", []):
        main_traits = [(ids.trait(t["trait_id"]), int(t["chess_num"])) for t in entry.get("main_trait_list", [])]
        info = entry.get("info") or {}
        for row in info.get("list", []):
            units = [ids.unit(c) for c in row.get("lineup", [])]
            core = [ids.unit(c) for c in row.get("core_chess", [])]
            sub = [(ids.trait(t["trait_id"]), int(t["chess_num"])) for t in row.get("sub_trait_list", [])]
            carry = ids.unit(row["main_c_chess"]) if row.get("main_c_chess") else (ids.unit(info["main_c_chess_id"]) if info.get("main_c_chess_id") else None)
            comps.append({
                "source": "tencent",
                "name": " + ".join(f"{t} {n}" for t, n in main_traits[:2]) + (f" ({carry})" if carry else ""),
                "main_traits": main_traits,
                "sub_traits": sub,
                "units": units,
                "core_units": core,
                "flex_units": [ids.unit(c) for c in row.get("free_chess", [])],
                "carry": carry,
                "carry_items": [ids.names.item(i) for i in row.get("main_c_chess_equip", [])],
                "assist": [ids.unit(c) for c in row.get("assist_chess", [])],
                "assist_items": [ids.names.item(i) for i in row.get("assist_chess_equip", [])],
                "avg_place": float(row.get("avg_rank") or 0),
                "avg_place_delta": float(row.get("avg_rank_diff") or 0),
                "use_rate": float(row.get("use_rate") or 0) if row.get("use_rate") is not None else None,
                "top4_rate": float(row.get("top_4_rate") or 0) if row.get("top_4_rate") is not None else None,
                "win_rate": float(row.get("top_1_rate") or 0) if row.get("top_1_rate") is not None else None,
                "raw": {k: v for k, v in row.items() if k not in ("lineup", "core_chess", "free_chess", "sub_trait_list", "assist_chess", "assist_chess_equip", "main_c_chess_equip")},
            })
    comps.sort(key=lambda c: c["avg_place"] or 9)
    return {"source": "tencent", "region": "CN", "tier": TIER_LABELS[TIER_PARTS[tier]], "patch": data.get("period"), "date": data.get("dtstatdate"), "comps": comps}


def fetch_units(ids: TencentIds, tier="master", time_type="v", queue="1100"):
    out = []
    for cost in range(1, 6):
        data = _proxy("tft_hero_ranking", {"tier_part": TIER_PARTS[tier], "base_price": str(cost), "iqueue_id": queue, "time_type": time_type})["data"]
        for row in data.get("details", []):
            stats = (row.get("list") or [{}])[0]
            hid = row.get("hero_id") or ""
            if not (hid.startswith("DA_") or hid in ids.names.unit_names):
                continue
            out.append({
                "id": row.get("hero_id"), "name": ids.names.unit(row.get("hero_id")), "cost": cost,
                "avg_place": float(stats.get("avg_rank") or 0), "top4_rate": float(stats.get("top_4_rate") or 0),
                "win_rate": float(stats.get("top_1_rate") or 0), "play_rate": float(stats.get("use_rate") or 0),
            })
    out.sort(key=lambda u: u["avg_place"] or 9)
    return out


def fetch_traits(ids: TencentIds, tier="master", queue="1100"):
    data = _proxy("tft_trait_strength_trend", {"tier_part": TIER_PARTS[tier], "battletype": queue})["data"]
    out = []
    for row in data.get("main_buff_data", []):
        traits = [(ids.trait(t["trait_id"]), int(t.get("cycle") or 0)) for t in row.get("trait_list", [])]
        levels = []
        for lvl in range(1, 6):
            use = float(row.get(f"{lvl}_use_rate") or 0)
            if use <= 0:
                continue
            levels.append({"level": lvl, "avg_place": float(row.get(f"{lvl}_avg_rank") or 0), "top4_rate": float(row.get(f"{lvl}_top_4_rate") or 0),
                           "win_rate": float(row.get(f"{lvl}_top_1_rate") or 0), "play_rate": use})
        out.append({"traits": traits, "name": " + ".join(f"{t} {n}" for t, n in traits), "levels": levels})
    return {"date": data.get("dtstatdate"), "rows": out}


def _heroes(rows, names):
    out = []
    for h in rows or []:
        if not isinstance(h, dict) or h.get("chess_type", "hero") != "hero":
            continue
        hid = h.get("hero_id") or ""
        items = [names.item(i) for i in (h.get("equipment_id") or "").split(",") if i]
        out.append({"name": names.unit(hid), "stars": h.get("numStar") or 1, "items": items, "carry": bool(h.get("is_carry_hero"))})
    return out


def fetch_curated(ids: TencentIds):
    data = _get_json(CURATED.format(season=ids.season), ttl=3600, cache_key="qq_curated")
    out = []
    for l in data.get("lineup_list", []):
        try:
            detail = json.loads(l.get("detail") or "{}")
        except json.JSONDecodeError:
            detail = {}
        author = (l.get("lineupauthor_data") or {}).get("name")
        traits = [{"name": ids.names.trait(c.get("id", "")), "count": c.get("num")} for c in detail.get("contact") or [] if isinstance(c, dict)]
        out.append({
            "name": detail.get("line_name") or l.get("id"),
            "author": author,
            "quality": l.get("quality"),
            "patch": l.get("simulator_edition"),
            "updated": l.get("update_time"),
            "level": detail.get("needLevel"),
            "final": _heroes(detail.get("hero_location"), ids.names),
            "early": _heroes(detail.get("y21_early_heros"), ids.names),
            "mid": _heroes(detail.get("y21_metaphase_heros"), ids.names),
            "three_star": [ids.names.unit(h) for h in (detail.get("level_3_heros") or "").split(",") if h],
            "traits": traits,
            "notes": {"early": detail.get("early_info"), "items": detail.get("equipment_info")},
        })
    return out
