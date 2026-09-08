import argparse
import json
import time

from tft_toolkit.planner.solver import Options, solve
from tft_toolkit.setdata import load_set


def parse_emblems(items, data, any_trait=False):
    emblems = {}
    allowed = data.traits if any_trait else data.emblem_traits()
    for raw in items:
        name, _, count = raw.rpartition(" x") if " x" in raw else (raw, "", "")
        name = name.strip()
        match = next((t.name for t in allowed if t.name.lower() == name.lower()), None)
        if match is None:
            raise SystemExit(f"no emblem for '{name}'. Emblems in this set: {', '.join(t.name for t in data.emblem_traits())} (use --any-trait to allow others)")
        emblems[match] = emblems.get(match, 0) + (int(count) if count else 1)
    return emblems


def format_result(i, r):
    lines = []
    status = "" if r.feasible else "  [emblems cannot all be placed]"
    lines.append(f"#{i}  {r.active_count} active traits, {r.style_points} tier points, {r.total_cost} gold{status}")
    unit_bits = []
    for c in r.units:
        bit = f"{c.label} ({c.cost})"
        held = r.emblem_holders.get(c.key)
        if held:
            bit += " +" + "+".join(held)
        unit_bits.append(bit)
    lines.append("   units: " + ", ".join(unit_bits))
    trait_bits = []
    for t in r.traits:
        if t.style:
            nxt = f" -> {t.next_min}" if t.next_min else ""
            trait_bits.append(f"{t.name} {t.count} {t.style}{nxt}")
    lines.append("   active: " + ", ".join(trait_bits))
    inactive = [f"{t.name} {t.count}/{t.next_min}" for t in r.traits if not t.style and t.next_min]
    if inactive:
        lines.append("   not yet: " + ", ".join(inactive))
    lines.append("   path:")
    for step in r.path:
        lines.append(f"     lvl {step['size']}: {', '.join(step['units'])}  [{step['active']} traits]")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tft-planner", description="Find boards that activate the most traits for a given set of emblems.")
    ap.add_argument("emblems", nargs="*", help="emblem traits, e.g. Blossom Fae 'Brawler x2'")
    ap.add_argument("--level", type=int, default=8, help="board size (default 8)")
    ap.add_argument("--objective", choices=["tiers", "traits"], default="tiers", help="maximize active trait count or tier points")
    ap.add_argument("--max-cost", type=int, default=5)
    ap.add_argument("--min-cost", type=int, default=1)
    ap.add_argument("--include", action="append", default=[], help="unit that must be on the board (repeatable)")
    ap.add_argument("--exclude", action="append", default=[], help="unit to leave out (repeatable)")
    ap.add_argument("--khazix-evolved", action="store_true", help="allow Kha'Zix to carry an evolved class trait")
    ap.add_argument("--restarts", type=int, default=40)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--list-emblems", action="store_true")
    ap.add_argument("--any-trait", action="store_true", help="allow traits without an emblem (for Tome of Traits or augment cases)")
    args = ap.parse_args(argv)

    data = load_set()
    if args.list_emblems:
        for t in data.emblem_traits():
            recipe = " + ".join(t.emblem["recipe"]) if t.emblem["craftable"] else "not craftable"
            print(f"{t.name:15s} {recipe}")
        return
    emblems = parse_emblems(args.emblems, data, args.any_trait)
    opts = Options(
        level=args.level, objective=args.objective, max_cost=args.max_cost, min_cost=args.min_cost,
        include=args.include, exclude=args.exclude, khazix_evolved=args.khazix_evolved,
        restarts=args.restarts, top_n=args.top, seed=args.seed,
    )
    t0 = time.time()
    results = solve(data, emblems, opts)
    dt = time.time() - t0
    if args.json:
        out = []
        for r in results:
            out.append({
                "units": [c.label for c in r.units], "lux_origin": r.lux_origin, "khazix_evo": r.khazix_evo,
                "emblem_holders": r.emblem_holders,
                "traits": [{"name": t.name, "count": t.count, "style": t.style, "next_min": t.next_min} for t in r.traits],
                "active_count": r.active_count, "style_points": r.style_points, "total_cost": r.total_cost,
                "feasible": r.feasible, "path": r.path,
            })
        print(json.dumps(out, indent=1))
        return
    emb = ", ".join(f"{k} x{v}" for k, v in emblems.items()) or "none"
    print(f"Emblems: {emb} | level {args.level} | objective {args.objective} | {dt:.1f}s")
    for i, r in enumerate(results, 1):
        print(format_result(i, r))
        print()


if __name__ == "__main__":
    main()
