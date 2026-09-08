import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "meta" / "matches.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
  puuid TEXT PRIMARY KEY,
  platform TEXT NOT NULL,
  tier TEXT,
  lp INTEGER,
  wins INTEGER,
  losses INTEGER,
  game_name TEXT,
  tag_line TEXT,
  fetched_at TEXT
);
CREATE TABLE IF NOT EXISTS matches (
  match_id TEXT PRIMARY KEY,
  platform TEXT NOT NULL,
  game_datetime INTEGER,
  game_version TEXT,
  patch TEXT,
  set_number INTEGER,
  queue_id INTEGER,
  fetched_at TEXT
);
CREATE TABLE IF NOT EXISTS participants (
  match_id TEXT NOT NULL,
  puuid TEXT NOT NULL,
  placement INTEGER,
  level INTEGER,
  last_round INTEGER,
  gold_left INTEGER,
  units TEXT,
  traits TEXT,
  augments TEXT,
  PRIMARY KEY (match_id, puuid)
);
CREATE TABLE IF NOT EXISTS seen_ids (
  match_id TEXT PRIMARY KEY
);
CREATE INDEX IF NOT EXISTS idx_matches_time ON matches(game_datetime);
CREATE INDEX IF NOT EXISTS idx_players_platform ON players(platform, lp);
"""


def patch_from_version(game_version):
    if not game_version:
        return None
    parts = game_version.split(" ")
    for p in parts:
        if p.count(".") >= 1 and p[0].isdigit():
            bits = p.split(".")
            return ".".join(bits[:2])
    return None


class Store:
    def __init__(self, path=None):
        self.path = Path(path) if path else DEFAULT_DB
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.executescript(SCHEMA)

    def upsert_players(self, entries):
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.conn.executemany(
            """INSERT INTO players (puuid, platform, tier, lp, wins, losses, fetched_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(puuid) DO UPDATE SET platform=excluded.platform, tier=excluded.tier, lp=excluded.lp,
               wins=excluded.wins, losses=excluded.losses, fetched_at=excluded.fetched_at""",
            [(e["puuid"], e["platform"], e["tier"], e["lp"], e["wins"], e["losses"], now) for e in entries],
        )
        self.conn.commit()

    def set_player_name(self, puuid, game_name, tag_line):
        self.conn.execute("UPDATE players SET game_name=?, tag_line=? WHERE puuid=?", (game_name, tag_line, puuid))
        self.conn.commit()

    def has_match(self, match_id):
        row = self.conn.execute("SELECT 1 FROM seen_ids WHERE match_id=?", (match_id,)).fetchone()
        return row is not None

    def mark_seen(self, match_id):
        self.conn.execute("INSERT OR IGNORE INTO seen_ids (match_id) VALUES (?)", (match_id,))

    def add_match(self, platform, match):
        info = match["info"]
        meta = match["metadata"]
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        version = info.get("game_version", "")
        self.conn.execute(
            """INSERT OR REPLACE INTO matches (match_id, platform, game_datetime, game_version, patch, set_number, queue_id, fetched_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (meta["match_id"], platform, int(info.get("game_datetime", 0)), version, patch_from_version(version),
             info.get("tft_set_number"), info.get("queue_id"), now),
        )
        rows = []
        for p in info.get("participants", []):
            rows.append((
                meta["match_id"], p.get("puuid"), p.get("placement"), p.get("level"), p.get("last_round"), p.get("gold_left"),
                json.dumps(p.get("units", [])), json.dumps(p.get("traits", [])), json.dumps(p.get("augments", [])),
            ))
        self.conn.executemany(
            "INSERT OR REPLACE INTO participants (match_id, puuid, placement, level, last_round, gold_left, units, traits, augments) VALUES (?,?,?,?,?,?,?,?,?)",
            rows,
        )
        self.mark_seen(meta["match_id"])
        self.conn.commit()

    def players(self, platform=None, limit=None):
        q = "SELECT puuid, platform, tier, lp, wins, losses, game_name, tag_line FROM players"
        args = []
        if platform:
            q += " WHERE platform=?"
            args.append(platform)
        q += " ORDER BY lp DESC"
        if limit:
            q += f" LIMIT {int(limit)}"
        cols = ["puuid", "platform", "tier", "lp", "wins", "losses", "game_name", "tag_line"]
        return [dict(zip(cols, r)) for r in self.conn.execute(q, args)]

    def boards(self, since_ms=None, set_number=None, queue_id=None):
        q = """SELECT m.match_id, m.platform, m.game_datetime, m.patch, p.puuid, p.placement, p.level, p.last_round,
                      p.units, p.traits, p.augments
               FROM participants p JOIN matches m ON m.match_id = p.match_id WHERE 1=1"""
        args = []
        if since_ms:
            q += " AND m.game_datetime >= ?"
            args.append(int(since_ms))
        if set_number:
            q += " AND m.set_number = ?"
            args.append(set_number)
        if queue_id:
            q += " AND m.queue_id = ?"
            args.append(queue_id)
        out = []
        for r in self.conn.execute(q, args):
            out.append({
                "match_id": r[0], "platform": r[1], "game_datetime": r[2], "patch": r[3], "puuid": r[4],
                "placement": r[5], "level": r[6], "last_round": r[7],
                "units": json.loads(r[8]), "traits": json.loads(r[9]), "augments": json.loads(r[10]),
            })
        return out

    def counts(self):
        m = self.conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
        p = self.conn.execute("SELECT COUNT(*) FROM participants").fetchone()[0]
        pl = self.conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
        return {"matches": m, "boards": p, "players": pl}
