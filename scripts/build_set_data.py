import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CDRAGON_URL = "https://raw.communitydragon.org/latest/cdragon/tft/en_us.json"
SET_MUTATOR = "TFTSet18"
OUT = Path(__file__).resolve().parents[1] / "data" / "set18.json"

ORIGINS = {
    "Elderwood", "Blossom", "Riftbeast", "Coven", "Sprykin", "Blackthorn",
    "Inferno", "Solar", "Lunar", "Fae", "Primal", "Flora Fatalis", "Rival",
}
CLASSES = {
    "Ravager", "Adaptor", "Hunter", "Invoker", "Rapidfire", "Juggernaut",
    "Vanguard", "Brawler", "Executioner", "Defender", "Spellweaver", "Summoner",
}
STYLE_NAMES = {1: "bronze", 3: "silver", 4: "unique", 5: "gold", 6: "prismatic"}

KHAZIX_EVOLUTIONS = ["Executioner", "Rapidfire", "Ravager", "Spellweaver"]
ELDER_DRAGON_SLOTS = 2
ELDER_DRAGON_RIFTBEAST_BONUS = 2
ECLIPSE_REQUIREMENT = {"Solar": 3, "Lunar": 3}


def clean(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("%i:scaleAD%", "AD").replace("%i:scaleAP%", "AP")
    text = text.replace("%i:scaleAS%", "AS").replace("%i:scaleHealth%", "HP")
    text = text.replace("%i:scaleArmor%", "Armor").replace("%i:scaleMR%", "MR")
    text = text.replace("%i:scaleDR%", "Durability").replace("%i:scaleManaRegen%", "Mana Regen")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_cdragon(path):
    if path and Path(path).exists():
        return json.load(open(path))
    with urllib.request.urlopen(CDRAGON_URL, timeout=120) as resp:
        return json.load(resp)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None
    raw = load_cdragon(src)
    setdata = next(s for s in raw["setData"] if s["mutator"] == SET_MUTATOR)
    item_names = {i["apiName"]: i.get("name") for i in raw["items"] if i.get("apiName")}

    traits = []
    trait_by_name = {}
    for t in setdata["traits"]:
        name = t["name"]
        if name in ORIGINS:
            kind = "origin"
        elif name in CLASSES:
            kind = "class"
        else:
            kind = "unique"
        breakpoints = []
        for e in t["effects"]:
            if e.get("minUnits") is None:
                continue
            breakpoints.append({
                "min": e["minUnits"],
                "max": e["maxUnits"] if e["maxUnits"] < 25000 else None,
                "style": STYLE_NAMES.get(e["style"], str(e["style"])),
            })
        breakpoints.sort(key=lambda b: b["min"])
        rec = {
            "id": t["apiName"],
            "name": name,
            "kind": kind,
            "desc": clean(t.get("desc")),
            "breakpoints": breakpoints,
            "emblem": None,
        }
        traits.append(rec)
        trait_by_name[name] = rec

    for i in raw["items"]:
        api = i.get("apiName") or ""
        if not api.startswith("DA_18_Emblem") or api.endswith("Augment"):
            continue
        tname = (i.get("name") or "").replace(" Emblem", "").strip()
        if tname not in trait_by_name:
            continue
        comp = i.get("composition") or []
        trait_by_name[tname]["emblem"] = {
            "id": api,
            "craftable": bool(comp),
            "recipe": [item_names.get(c, c) for c in comp],
        }

    units = []
    lux_origins = []
    lux_forms = {}
    for c in setdata["champions"]:
        if not c.get("traits") or c["cost"] > 5:
            continue
        name = c["name"]
        if name.startswith("Lux (") and name.endswith(")"):
            lux_origins.append(name[5:-1])
            lux_forms[c["apiName"]] = name[5:-1]
            continue
        if name == "Lux":
            lux_forms[c["apiName"]] = None
        ability = c.get("ability") or {}
        rec = {
            "id": c["apiName"],
            "name": name,
            "cost": c["cost"],
            "traits": list(c["traits"]),
            "slots": 1,
            "ability": {"name": ability.get("name"), "desc": clean(ability.get("desc"))},
            "stats": {k: c["stats"].get(k) for k in ("hp", "damage", "attackSpeed", "armor", "magicResist", "mana", "initialMana", "range")},
        }
        if name == "Elder Dragon":
            rec["slots"] = ELDER_DRAGON_SLOTS
            rec["trait_bonus"] = {"Riftbeast": ELDER_DRAGON_RIFTBEAST_BONUS}
        if name == "Kha'Zix":
            rec["optional_traits"] = KHAZIX_EVOLUTIONS
        if name == "Lux":
            rec["flex_origins"] = []
            rec["flex_counts_double"] = True
        units.append(rec)

    lux = next(u for u in units if u["name"] == "Lux")
    lux["flex_origins"] = sorted(lux_origins)
    units.sort(key=lambda u: (u["cost"], u["name"]))

    items = {}
    for i in raw["items"]:
        api = i.get("apiName") or ""
        if i.get("isAugment") or not i.get("name") or not api.startswith("DA_"):
            continue
        items[api] = i["name"]

    out = {
        "set": setdata["number"],
        "set_name": "Enchanted Wilds",
        "mutator": SET_MUTATOR,
        "source": CDRAGON_URL,
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "eclipse": ECLIPSE_REQUIREMENT,
        "traits": traits,
        "units": units,
        "lux_forms": lux_forms,
        "items": items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
    n_emb = sum(1 for t in traits if t["emblem"])
    print(f"wrote {OUT}: {len(units)} units, {len(traits)} traits, {n_emb} emblems, lux origins {lux['flex_origins']}")


if __name__ == "__main__":
    main()
