import hashlib
import sqlite3
from datetime import datetime

DB_PATH = "tournaments.db"


def _make_id(name: str, date: str) -> str:
    return hashlib.sha256(f"{name}|{date}".encode()).hexdigest()[:16]


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tournaments (
                id TEXT PRIMARY KEY,
                name TEXT,
                date TEXT,
                location TEXT,
                escaloes TEXT,
                category TEXT,
                url TEXT,
                first_seen TEXT
            )
        """)
        conn.commit()


def is_first_run() -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        count = conn.execute("SELECT COUNT(*) FROM tournaments").fetchone()[0]
    return count == 0


def get_seen_ids() -> set:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT id FROM tournaments").fetchall()
    return {row[0] for row in rows}


def filter_new(tournaments: list[dict]) -> list[dict]:
    seen = get_seen_ids()
    new = []
    for t in tournaments:
        t["id"] = _make_id(t["name"], t["date"])
        if t["id"] not in seen:
            new.append(t)
    return new


def add_tournaments(tournaments: list[dict]) -> None:
    now = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        for t in tournaments:
            tid = t.get("id") or _make_id(t["name"], t["date"])
            conn.execute(
                """
                INSERT OR IGNORE INTO tournaments (id, name, date, location, escaloes, category, url, first_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (tid, t["name"], t["date"], t["location"], t["escaloes"], t.get("category", ""), t.get("url", ""), now),
            )
        conn.commit()
