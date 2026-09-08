import json
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DEFAULT_SET_FILE = DATA_DIR / "set18.json"

STYLE_POINTS = {"bronze": 1, "silver": 2, "gold": 3, "prismatic": 4, "unique": 2}


@dataclass
class Breakpoint:
    min: int
    max: int | None
    style: str


@dataclass
class Trait:
    id: str
    name: str
    kind: str
    desc: str
    breakpoints: list[Breakpoint]
    emblem: dict | None

    def style_for(self, count):
        best = None
        for bp in self.breakpoints:
            if count >= bp.min:
                best = bp.style
        return best

    def next_breakpoint(self, count):
        for bp in self.breakpoints:
            if bp.min > count:
                return bp
        return None

    @property
    def first_min(self):
        return self.breakpoints[0].min if self.breakpoints else 1

    @property
    def has_emblem(self):
        return self.emblem is not None


@dataclass
class Unit:
    id: str
    name: str
    cost: int
    traits: list[str]
    slots: int = 1
    ability: dict = field(default_factory=dict)
    stats: dict = field(default_factory=dict)
    trait_bonus: dict = field(default_factory=dict)
    optional_traits: list[str] = field(default_factory=list)
    flex_origins: list[str] = field(default_factory=list)
    flex_counts_double: bool = False


@dataclass
class SetData:
    set_number: int
    set_name: str
    traits: list[Trait]
    units: list[Unit]
    eclipse: dict
    built_at: str
    lux_forms: dict = field(default_factory=dict)
    items: dict = field(default_factory=dict)

    def __post_init__(self):
        self.trait_by_name = {t.name: t for t in self.traits}
        self.trait_by_id = {t.id: t for t in self.traits}
        self.unit_by_name = {u.name: u for u in self.units}
        self.unit_by_id = {u.id: u for u in self.units}

    def emblem_traits(self):
        return [t for t in self.traits if t.has_emblem]

    def units_with_trait(self, trait_name):
        return [u for u in self.units if trait_name in u.traits]


def load_set(path=None):
    path = Path(path) if path else DEFAULT_SET_FILE
    raw = json.load(open(path))
    traits = [
        Trait(
            id=t["id"], name=t["name"], kind=t["kind"], desc=t.get("desc", ""),
            breakpoints=[Breakpoint(b["min"], b["max"], b["style"]) for b in t["breakpoints"]],
            emblem=t.get("emblem"),
        )
        for t in raw["traits"]
    ]
    units = [
        Unit(
            id=u["id"], name=u["name"], cost=u["cost"], traits=list(u["traits"]),
            slots=u.get("slots", 1), ability=u.get("ability", {}), stats=u.get("stats", {}),
            trait_bonus=u.get("trait_bonus", {}), optional_traits=u.get("optional_traits", []),
            flex_origins=u.get("flex_origins", []), flex_counts_double=u.get("flex_counts_double", False),
        )
        for u in raw["units"]
    ]
    return SetData(
        set_number=raw["set"], set_name=raw["set_name"], traits=traits, units=units,
        eclipse=raw.get("eclipse", {}), built_at=raw.get("built_at", ""),
        lux_forms=raw.get("lux_forms", {}), items=raw.get("items", {}),
    )
