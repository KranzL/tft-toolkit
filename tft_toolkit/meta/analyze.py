import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone

from tft_toolkit.setdata import load_set

STYLE_NAMES = {0: None, 1: "bronze", 2: "silver", 3: "gold", 4: "prismatic", 5: "prismatic"}
STYLE_RANK = {None: 0, "bronze": 1, "silver": 2, "gold": 3, "unique": 2, "prismatic": 4}


class Names:
    def __init__(self, data=None):
        data = data or load_set()
        self.unit_names = {u.id: u.name for u in data.units}
        self.unit_cost = {u.name: u.cost for u in data.units}
        self.trait_names = {t.id: t.name for t in data.traits}
        self.trait_kind = {t.name: t.kind for t in data.traits}
        self.data = data

    def unit(self, character_id):
        if character_id in self.unit_names:
            return self.unit_names[character_id]
        if character_id in self.data.lux_forms:
            origin = self.data.lux_forms[character_id]
            return f"Lux ({origin})" if origin else "Lux"
        if "Lux" in character_id:
            return "Lux"
        tail = character_id.split("_")[-1]
        for uid, name in self.unit_names.items():
            if uid.split("_")[-1] == tail:
                return name
        return character_id

    def trait(self, trait_id):
        return self.trait_names.get(trait_id, trait_id)

    def trait_from_emblem(self, item_id):
        m = re.match(r"DA_18_Emblem(\w+)", item_id or "")
        if not m:
            return item_id
        raw = m.group(1)
        for t in self.data.traits:
            if t.emblem and t.emblem["id"] == item_id:
                return t.name
        return raw

    def item(self, item_id):
        if not item_id:
            return item_id
        if item_id in self.data.items:
            return self.data.items[item_id]
        emblem = self.trait_from_emblem(item_id)
        if emblem != item_id:
            return f"{emblem} Emblem"
        name = re.sub(r"^(DA_18_|DA_|TFT\d*_Item_|TFT_Item_)", "", item_id)
        name = re.sub(r"(Artifact_|Item_)", "", name)
        name = name.replace("_Radiant", " (Radiant)").replace("18", "")
        name = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)
        return name


def trait_style(t):
    style = t.get("style")
    if style is None:
        return None
    return STYLE_NAMES.get(style)


def archetype_of(board, names: Names):
    scored = []
    for t in board["traits"]:
        style = trait_style(t)
        if not style:
            continue
        name = names.trait(t["name"])
        kind = names.trait_kind.get(name, "unique")
        rank = STYLE_RANK.get(style, 0)
        if kind == "unique":
            rank = min(rank, 1.5)
        scored.append((rank, t.get("num_units", 0), name, t.get("tier_current", 0)))
    scored.sort(reverse=True)
    top = scored[:2]
    if not top:
        return "No traits", []
    label = " + ".join(f"{name} {num}" for rank, num, name, tier in top)
    return label, [name for rank, num, name, tier in top]


def carry_of(board, names: Names):
    best = None
    for u in board["units"]:
        items = u.get("itemNames") or []
        n_items = len([i for i in items if i])
        key = (n_items, u.get("tier", 1), names.unit_cost.get(names.unit(u["character_id"]), 0))
        if best is None or key > best[0]:
            best = (key, u)
    if best is None or best[0][0] == 0:
        return None
    return names.unit(best[1]["character_id"])


def summarize_boards(boards, names: Names, min_count=8, days=7):
    now_ms = datetime.now(timezone.utc).timestamp() * 1000
    groups = defaultdict(list)
    for b in boards:
        label, traits = archetype_of(b, names)
        b["_archetype"] = label
        b["_archetype_traits"] = traits
        b["_carry"] = carry_of(b, names)
        b["_day"] = datetime.fromtimestamp(b["game_datetime"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        groups[label].append(b)

    total = len(boards)
    comps = []
    for label, items in groups.items():
        if len(items) < min_count:
            continue
        places = [i["placement"] for i in items]
        unit_counter = Counter()
        star_counter = defaultdict(Counter)
        item_counter = defaultdict(Counter)
        carry_counter = Counter()
        aug_counter = Counter()
        region_counter = Counter()
        day_counter = Counter()
        day_place = defaultdict(list)
        level_counter = Counter()
        for i in items:
            seen = set()
            for u in i["units"]:
                name = names.unit(u["character_id"])
                if name in seen:
                    continue
                seen.add(name)
                unit_counter[name] += 1
                star_counter[name][u.get("tier", 1)] += 1
                for it in u.get("itemNames") or []:
                    if it:
                        item_counter[name][it] += 1
            if i["_carry"]:
                carry_counter[i["_carry"]] += 1
            for a in i.get("augments") or []:
                aug_counter[a] += 1
            region_counter[i["platform"]] += 1
            day_counter[i["_day"]] += 1
            day_place[i["_day"]].append(i["placement"])
            level_counter[i.get("level")] += 1
        n = len(items)
        core = [(u, c / n) for u, c in unit_counter.most_common(12)]
        trend = []
        for day in sorted(day_counter):
            day_total = sum(1 for b in boards if b["_day"] == day)
            trend.append({
                "date": day, "count": day_counter[day],
                "share": day_counter[day] / day_total if day_total else 0,
                "avg_place": statistics.mean(day_place[day]),
            })
        comps.append({
            "name": label,
            "traits": groups[label][0]["_archetype_traits"],
            "count": n,
            "share": n / total if total else 0,
            "avg_place": statistics.mean(places),
            "top4_rate": sum(1 for p in places if p <= 4) / n,
            "win_rate": sum(1 for p in places if p == 1) / n,
            "units": [{"name": u, "rate": r, "stars": dict(star_counter[u].most_common(3)),
                       "items": [k for k, _ in item_counter[u].most_common(3)]} for u, r in core],
            "carries": carry_counter.most_common(3),
            "augments": aug_counter.most_common(5),
            "regions": dict(region_counter),
            "levels": dict(level_counter),
            "trend": trend,
        })
    comps.sort(key=lambda c: (c["avg_place"], -c["count"]))
    return comps


def trait_stats(boards, names: Names, min_count=8):
    rows = defaultdict(list)
    for b in boards:
        for t in b["traits"]:
            style = trait_style(t)
            if not style:
                continue
            rows[(names.trait(t["name"]), t.get("num_units", 0), style)].append(b["placement"])
    out = []
    for (name, num, style), places in rows.items():
        if len(places) < min_count:
            continue
        out.append({"trait": name, "count": num, "style": style, "boards": len(places),
                    "avg_place": statistics.mean(places), "top4_rate": sum(1 for p in places if p <= 4) / len(places)})
    out.sort(key=lambda r: r["avg_place"])
    return out


def unit_stats(boards, names: Names, min_count=8):
    rows = defaultdict(list)
    for b in boards:
        seen = set()
        for u in b["units"]:
            name = names.unit(u["character_id"])
            key = (name, u.get("tier", 1))
            if key in seen:
                continue
            seen.add(key)
            rows[key].append(b["placement"])
    out = []
    n_boards = len(boards) or 1
    for (name, tier), places in rows.items():
        if len(places) < min_count:
            continue
        out.append({"unit": name, "stars": tier, "cost": names.unit_cost.get(name), "boards": len(places),
                    "play_rate": len(places) / n_boards, "avg_place": statistics.mean(places),
                    "top4_rate": sum(1 for p in places if p <= 4) / len(places)})
    out.sort(key=lambda r: r["avg_place"])
    return out


def player_stats(boards, players, names: Names, recent=10):
    by_puuid = defaultdict(list)
    for b in boards:
        by_puuid[b["puuid"]].append(b)
    out = []
    for p in players:
        games = sorted(by_puuid.get(p["puuid"], []), key=lambda b: -b["game_datetime"])[:recent]
        if not games:
            continue
        comps = Counter(g["_archetype"] for g in games if "_archetype" in g)
        out.append({
            "puuid": p["puuid"], "platform": p["platform"], "name": f"{p.get('game_name') or 'unknown'}#{p.get('tag_line') or ''}",
            "tier": p["tier"], "lp": p["lp"], "wins": p["wins"], "losses": p["losses"],
            "games": len(games), "avg_place": statistics.mean(g["placement"] for g in games),
            "comps": comps.most_common(3),
        })
    out.sort(key=lambda r: (r["platform"], -r["lp"]))
    return out


def region_breakdown(comps, boards):
    per_region = defaultdict(int)
    for b in boards:
        per_region[b["platform"]] += 1
    out = {}
    for region, n in per_region.items():
        ranked = []
        for c in comps:
            k = c["regions"].get(region, 0)
            if k >= 3:
                ranked.append({"name": c["name"], "count": k, "share": k / n})
        ranked.sort(key=lambda r: -r["count"])
        out[region] = {"boards": n, "top": ranked[:8]}
    return out
