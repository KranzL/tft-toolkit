import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.load(open(ROOT / "data" / "set18.json"))
units = data["units"]
traits = data["traits"]
by_trait = defaultdict(list)
for u in units:
    for t in u["traits"]:
        by_trait[t].append(u)
by_trait["Rival"] = [u for u in units if "Rival" in u["traits"]]
lux = next(u for u in units if u["name"] == "Lux")

def bp(t):
    return " / ".join(f"{b['min']} {b['style']}" for b in t["breakpoints"])

print("## Trait table\n")
print("| Trait | Kind | Breakpoints | Units | Emblem |")
print("|---|---|---|---|---|")
for kind in ("origin", "class", "unique"):
    for t in sorted([t for t in traits if t["kind"] == kind], key=lambda t: t["name"]):
        members = ", ".join(f"{u['name']} ({u['cost']})" for u in sorted(by_trait.get(t["name"], []), key=lambda u: (u["cost"], u["name"])))
        if t["name"] in lux["flex_origins"]:
            members += ", Lux (5, counts twice)"
        if t["name"] == "Riftbeast":
            members += "; Elder Dragon adds +2"
        emb = "none"
        if t["emblem"]:
            emb = " + ".join(t["emblem"]["recipe"]) if t["emblem"]["craftable"] else "not craftable"
        print(f"| {t['name']} | {kind} | {bp(t)} | {members} | {emb} |")

print("\n## Unit table\n")
print("| Cost | Unit | Traits | Range | Mana | Ability |")
print("|---|---|---|---|---|---|")
for u in sorted(units, key=lambda u: (u["cost"], u["name"])):
    st = u["stats"]
    mana = f"{int(st.get('initialMana') or 0)}/{int(st.get('mana') or 0)}"
    rng = int(st.get("range") or 0)
    desc = re.sub(r"@\w+(\*\d+)?@", "X", u["ability"]["desc"] or "")
    desc = desc.replace("\\n", " ").replace("|", "/")
    desc = re.sub(r"\s+", " ", desc)[:170]
    tr = ", ".join(u["traits"]) + (f" (choose: {', '.join(u['flex_origins'])})" if u.get("flex_origins") else "")
    print(f"| {u['cost']} | {u['name']} | {tr} | {rng} | {mana} | {u['ability']['name']}: {desc} |")

print("\n## Trait overlap\n")
print("Units carrying three traits: " + ", ".join(f"{u['name']} ({', '.join(u['traits'])})" for u in units if len(u["traits"]) >= 3))
print()
pairs = defaultdict(list)
for u in units:
    o = [t for t in u["traits"] if any(x["name"] == t and x["kind"] == "origin" for x in traits)]
    c = [t for t in u["traits"] if any(x["name"] == t and x["kind"] == "class" for x in traits)]
    for a in o:
        for b in c:
            pairs[(a, b)].append(u["name"])
print("Origin and class pairs that appear on more than one unit:")
for (a, b), names in sorted(pairs.items(), key=lambda kv: -len(kv[1])):
    if len(names) > 1:
        print(f"- {a} + {b}: {', '.join(names)}")

snap_path = ROOT / "data" / "meta" / "latest.json"
if snap_path.exists():
    snap = json.load(open(snap_path))
    tt = snap["tactics"]
    print(f"\n## Meta snapshot ({tt['rank_group']}, patch {tt.get('patch')}, {tt['games']:,} games, generated {snap['generated_at'][:16]} UTC)\n")
    print("| Comp | Share | Place | Top 4 | Win | 7-day change | Board |")
    print("|---|---|---|---|---|---|---|")
    comps = sorted([c for c in tt["comps"] if c["share"] >= 0.01], key=lambda c: -c["count"])
    for c in comps[:16]:
        d = c.get("trend_delta", 0) * 100
        print(f"| {c['name']} | {c['share']*100:.1f}% | {c['avg_place']:.2f} | {c['top4_rate']*100:.0f}% | {c['win_rate']*100:.0f}% | {d:+.1f} pts | {', '.join(u['name'] for u in c['units'])} |")
    print("\nRegion leaders (highest play share inside each region):\n")
    labels = snap.get("region_labels", {})
    regions = {}
    for c in tt["comps"]:
        for r, s in c["regions"].items():
            if s["share"] > regions.get(r, (0, None))[0]:
                regions[r] = (s["share"], c["name"], s["avg_place"])
    for r in ["na1", "euw1", "eun1", "kr", "jp1", "br1", "la1", "la2", "oc1", "tr1", "tw2", "vn2", "sg2"]:
        if r in regions:
            share, name, place = regions[r]
            print(f"- {labels.get(r, r)}: {name} ({share*100:.1f}% of boards, place {place:.2f})")
    cn = snap.get("tencent")
    if cn:
        print(f"\nChina Master+ (Tencent, patch {cn['patch']}, {cn['date']}):\n")
        print("| Comp | Games | Place | Top 4 | Win | Board |")
        print("|---|---|---|---|---|---|")
        for c in cn["comps"][:8]:
            print(f"| {c['name']} | {c['raw'].get('use_num')} | {c['avg_place']:.2f} | {c['top4_rate']*100:.0f}% | {c['win_rate']*100:.0f}% | {', '.join(c['units'])} |")
