import random
from dataclasses import dataclass, field

from tft_toolkit.setdata import STYLE_POINTS, SetData

MAX_ITEMS_PER_UNIT = 3
ECLIPSE_NAME = "Eclipse"


@dataclass
class Candidate:
    key: str
    unit_id: str
    name: str
    cost: int
    slots: int
    traits: tuple
    counts: dict
    label: str
    lux_origin: str | None = None
    khazix_evo: str | None = None


@dataclass
class Options:
    level: int = 8
    objective: str = "tiers"
    max_cost: int = 5
    min_cost: int = 1
    include: list = field(default_factory=list)
    exclude: list = field(default_factory=list)
    khazix_evolved: bool = False
    restarts: int = 40
    top_n: int = 10
    seed: int | None = None


@dataclass
class TraitLine:
    name: str
    count: int
    style: str | None
    next_min: int | None
    next_style: str | None
    from_emblems: int


@dataclass
class Result:
    units: list
    lux_origin: str | None
    khazix_evo: str | None
    emblem_holders: dict
    traits: list
    active_count: int
    style_points: int
    total_cost: int
    score: float
    feasible: bool
    path: list = field(default_factory=list)


def build_candidates(data: SetData, opts: Options):
    cands = []
    for u in data.units:
        if u.cost > opts.max_cost or u.cost < opts.min_cost:
            if u.name not in opts.include:
                continue
        if u.name in opts.exclude:
            continue
        base_counts = {}
        for t in u.traits:
            base_counts[t] = base_counts.get(t, 0) + 1
        for t, b in u.trait_bonus.items():
            base_counts[t] = base_counts.get(t, 0) + b
        if u.flex_origins:
            for origin in u.flex_origins:
                counts = dict(base_counts)
                counts[origin] = counts.get(origin, 0) + (2 if u.flex_counts_double else 1)
                cands.append(Candidate(
                    key=u.name, unit_id=u.id, name=u.name, cost=u.cost, slots=u.slots,
                    traits=tuple(list(u.traits) + [origin]), counts=counts,
                    label=f"{u.name} ({origin})", lux_origin=origin,
                ))
            continue
        cands.append(Candidate(
            key=u.name, unit_id=u.id, name=u.name, cost=u.cost, slots=u.slots,
            traits=tuple(u.traits), counts=base_counts, label=u.name,
        ))
        if u.optional_traits and opts.khazix_evolved:
            for evo in u.optional_traits:
                counts = dict(base_counts)
                counts[evo] = counts.get(evo, 0) + 1
                cands.append(Candidate(
                    key=u.name, unit_id=u.id, name=u.name, cost=u.cost, slots=u.slots,
                    traits=tuple(list(u.traits) + [evo]), counts=counts,
                    label=f"{u.name} ({evo})", khazix_evo=evo,
                ))
    return cands


def assign_emblems(board, emblems):
    holders = {c.key: [] for c in board}
    order = sorted(emblems.items(), key=lambda kv: sum(1 for c in board if kv[0] not in c.traits))
    slots = []
    for trait, n in order:
        slots.extend([trait] * n)
    assignment = {}

    def try_assign(i):
        if i == len(slots):
            return True
        trait = slots[i]
        for c in board:
            if trait in c.traits or trait in holders[c.key]:
                continue
            if len(holders[c.key]) >= MAX_ITEMS_PER_UNIT:
                continue
            holders[c.key].append(trait)
            if try_assign(i + 1):
                return True
            holders[c.key].pop()
        return False

    ok = try_assign(0)
    if ok:
        assignment = {k: v for k, v in holders.items() if v}
    return ok, assignment


TIER_WEIGHT = {"bronze": 1.0, "silver": 2.0, "gold": 3.0, "prismatic": 4.5, "unique": 1.0}
EMBLEM_TRAIT_MULTIPLIER = 2.0
EMBLEM_WASTED_PENALTY = 3.0
COST_PENALTY = 0.05


class Evaluator:
    def __init__(self, data: SetData, emblems: dict, objective: str):
        self.data = data
        self.emblems = {k: v for k, v in emblems.items() if v > 0}
        self.objective = objective
        self.eclipse = data.eclipse

    def counts_for(self, board):
        counts = {}
        for c in board:
            for t, n in c.counts.items():
                counts[t] = counts.get(t, 0) + n
        n_units = len(board)
        for t, k in self.emblems.items():
            holders = n_units - sum(1 for c in board if t in c.traits)
            counts[t] = counts.get(t, 0) + min(k, max(holders, 0))
        return counts

    def active_lines(self, counts):
        lines = []
        active = 0
        points = 0
        weighted = 0.0
        for t in self.data.traits:
            n = counts.get(t.name, 0)
            if n <= 0:
                continue
            style = t.style_for(n)
            nb = t.next_breakpoint(n)
            lines.append(TraitLine(
                name=t.name, count=n, style=style,
                next_min=nb.min if nb else None, next_style=nb.style if nb else None,
                from_emblems=self.emblems.get(t.name, 0),
            ))
            if style:
                active += 1
                points += STYLE_POINTS.get(style, 1)
                w = TIER_WEIGHT.get(style, 1.0)
                if t.name in self.emblems:
                    w *= EMBLEM_TRAIT_MULTIPLIER
                weighted += w
            elif t.name in self.emblems:
                weighted -= EMBLEM_WASTED_PENALTY
        if self.eclipse and all(counts.get(k, 0) >= v for k, v in self.eclipse.items()):
            lines.append(TraitLine(name=ECLIPSE_NAME, count=1, style="gold", next_min=None, next_style=None, from_emblems=0))
            active += 1
            points += STYLE_POINTS["gold"]
            weighted += TIER_WEIGHT["gold"]
        lines.sort(key=lambda l: (l.style is None, -STYLE_POINTS.get(l.style or "", 0), -l.count, l.name))
        return lines, active, points, weighted

    def score_parts(self, board):
        counts = self.counts_for(board)
        lines, active, points, weighted = self.active_lines(counts)
        cost = sum(c.cost for c in board)
        emblem_active = sum(1 for l in lines if l.style and l.name in self.emblems)
        if self.objective == "traits":
            score = active * 100 + emblem_active * 50 + weighted - cost * COST_PENALTY
        else:
            score = weighted * 10 + active - cost * COST_PENALTY
        return score, lines, active, points, cost

    def score(self, board):
        return self.score_parts(board)[0]


def board_slots(board):
    return sum(c.slots for c in board)


def board_key(board):
    return tuple(sorted(c.label for c in board))


def valid_board(board):
    keys = [c.key for c in board]
    return len(keys) == len(set(keys))


def local_search(evaluator, cands, opts, rng, locked):
    by_key = {}
    for c in cands:
        by_key.setdefault(c.key, []).append(c)
    free = [c for c in cands if c.key not in locked]
    board = [c for c in cands if c.key in locked and (c.lux_origin is None or rng.random() < 0.2)]
    seen_keys = set()
    deduped = []
    for c in board:
        if c.key in seen_keys:
            continue
        seen_keys.add(c.key)
        deduped.append(c)
    board = deduped
    for k in locked:
        if k not in seen_keys:
            board.append(rng.choice(by_key[k]))
            seen_keys.add(k)
    pool = free[:]
    rng.shuffle(pool)
    for c in pool:
        if board_slots(board) + c.slots > opts.level:
            continue
        if c.key in seen_keys:
            continue
        board.append(c)
        seen_keys.add(c.key)
        if board_slots(board) >= opts.level:
            break

    best_score = evaluator.score(board)
    improved = True
    kicks = 0
    best_board = list(board)
    while improved or kicks < 3:
        improved = False
        current = best_score
        move = None
        present = {c.key for c in board}
        for i, out in enumerate(board):
            if out.key in locked:
                continue
            for inc in free:
                if inc.key in present and inc.key != out.key:
                    continue
                if board_slots(board) - out.slots + inc.slots > opts.level:
                    continue
                trial = board[:i] + board[i + 1:] + [inc]
                s = evaluator.score(trial)
                if s > current + 1e-9:
                    current = s
                    move = trial
        if move is None and board_slots(board) < opts.level:
            for inc in free:
                if inc.key in present or board_slots(board) + inc.slots > opts.level:
                    continue
                trial = board + [inc]
                s = evaluator.score(trial)
                if s > current + 1e-9:
                    current = s
                    move = trial
        if move is not None:
            board = move
            best_score = current
            best_board = list(board)
            improved = True
            continue
        kicks += 1
        if kicks >= 3:
            break
        swappable = [i for i, c in enumerate(board) if c.key not in locked]
        if len(swappable) < 2:
            break
        for i in rng.sample(swappable, 2):
            present = {c.key for c in board}
            choices = [c for c in free if c.key not in present and board_slots(board) - board[i].slots + c.slots <= opts.level]
            if choices:
                board[i] = rng.choice(choices)
        best_score = evaluator.score(board)
        improved = True
    return best_board


LEVEL_COST_CAP = {2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 5, 9: 5, 10: 5, 11: 5, 12: 5}


def build_path(evaluator, board, locked, cands):
    from itertools import combinations
    steps = []
    final_size = board_slots(board)
    final_keys = {c.key for c in board}
    for size in range(3, final_size):
        cap = LEVEL_COST_CAP.get(size, 5)
        pool = [c for c in board if c.cost <= cap or c.key in locked]
        best = None
        best_val = None
        for k in range(min(size, len(pool)), 0, -1):
            for combo in combinations(pool, k):
                if board_slots(combo) > size:
                    continue
                sc, lines, active, points, cost = evaluator.score_parts(list(combo))
                val = (sc, -cost)
                if best_val is None or val > best_val:
                    best_val = val
                    best = list(combo)
            if best is not None:
                break
        if best is None:
            best = []
        fillers = []
        present = {c.key for c in best}
        while board_slots(best) < size:
            options = [c for c in cands if c.cost <= cap and c.key not in present and c.key not in final_keys and board_slots(best) + c.slots <= size and c.lux_origin is None]
            if not options:
                break
            scored = sorted(((evaluator.score(best + [c]), -c.cost, c.name), c) for c in options)
            pick = scored[-1][1]
            best.append(pick)
            fillers.append(pick.key)
            present.add(pick.key)
        sc, lines, active, points, cost = evaluator.score_parts(best)
        steps.append({
            "size": size,
            "units": [c.label + ("*" if c.key in fillers else "") for c in sorted(best, key=lambda c: (c.cost, c.name))],
            "active": active,
            "style_points": points,
        })
    sc, lines, active, points, cost = evaluator.score_parts(board)
    steps.append({
        "size": final_size,
        "units": [c.label for c in sorted(board, key=lambda c: (c.cost, c.name))],
        "active": active,
        "style_points": points,
    })
    return steps


def solve(data: SetData, emblems: dict, opts: Options):
    for name in emblems:
        if name not in data.trait_by_name:
            raise ValueError(f"unknown trait for emblem: {name}")
    cands = build_candidates(data, opts)
    known = {c.key for c in cands}
    for name in opts.include:
        if name not in known:
            raise ValueError(f"unknown or excluded unit: {name}")
    locked = set(opts.include)
    evaluator = Evaluator(data, emblems, opts.objective)
    rng = random.Random(opts.seed)
    found = {}
    for _ in range(opts.restarts):
        board = local_search(evaluator, cands, opts, rng, locked)
        key = board_key(board)
        if key in found:
            continue
        ok, holders = assign_emblems(board, evaluator.emblems)
        score, lines, active, points, cost = evaluator.score_parts(board)
        if not ok:
            score -= 5000
        found[key] = Result(
            units=sorted(board, key=lambda c: (c.cost, c.name)),
            lux_origin=next((c.lux_origin for c in board if c.lux_origin), None),
            khazix_evo=next((c.khazix_evo for c in board if c.khazix_evo), None),
            emblem_holders=holders,
            traits=lines,
            active_count=active,
            style_points=points,
            total_cost=cost,
            score=score,
            feasible=ok,
        )
    results = sorted(found.values(), key=lambda r: -r.score)[: opts.top_n]
    for r in results:
        r.path = build_path(evaluator, r.units, locked, cands)
    return results
