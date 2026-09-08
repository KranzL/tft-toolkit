import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "tft_toolkit" / "planner" / "templates" / "planner.html"
OUT = ROOT / "planner.html"


def main():
    data = json.load(open(ROOT / "data" / "set18.json"))
    slim = {k: v for k, v in data.items() if k != "items"}
    for u in slim["units"]:
        u.pop("ability", None)
        u.pop("stats", None)
    for t in slim["traits"]:
        t.pop("desc", None)
    html = TEMPLATE.read_text().replace("__DATA__", json.dumps(slim, ensure_ascii=False).replace("</", "<\\/"))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
