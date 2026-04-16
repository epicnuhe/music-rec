"""
Database setup and query helpers.
All database access goes through this module.
"""

import os
import sqlite3
from datetime import date

DB_PATH = os.environ.get("DB_PATH", "music.db")

# Create the database directory if it doesn't exist (needed for Railway volumes)
_db_dir = os.path.dirname(DB_PATH)
if _db_dir:
    os.makedirs(_db_dir, exist_ok=True)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist. Safe to run multiple times."""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS albums (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                artist              TEXT NOT NULL,
                album_title         TEXT NOT NULL,
                year                INTEGER,
                country             TEXT,
                genre_tags          TEXT,
                source_name         TEXT,
                source_url          TEXT,
                source_author       TEXT,
                curatorial_context  TEXT,
                date_scraped        DATE,
                times_seen          INTEGER DEFAULT 1,
                recommended         BOOLEAN DEFAULT FALSE,
                date_recommended    DATE,
                slot_assigned       TEXT
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                album_id        INTEGER REFERENCES albums(id),
                feedback_type   TEXT NOT NULL,
                date_submitted  DATE NOT NULL,
                requeue_date    DATE,
                acted_on        BOOLEAN DEFAULT FALSE
            );

            CREATE TABLE IF NOT EXISTS digest_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date_sent   DATE NOT NULL,
                album_ids   TEXT NOT NULL,
                world_region TEXT
            );

            CREATE TABLE IF NOT EXISTS world_rotation (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                region_name         TEXT NOT NULL UNIQUE,
                last_recommended    DATE,
                follow_up_requested BOOLEAN DEFAULT FALSE
            );

            CREATE TABLE IF NOT EXISTS pending_digest (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at  DATE NOT NULL,
                digest_json TEXT NOT NULL,
                sent        BOOLEAN DEFAULT FALSE
            );

            INSERT OR IGNORE INTO world_rotation (region_name) VALUES
                ('Middle East / North Africa / Persia'),
                ('Southeast Asia'),
                ('Latin America (Colombia / Peru / Bolivia / Uruguay)'),
                ('West Africa'),
                ('East Africa'),
                ('Central Asia');
        """)


# ── Album helpers ─────────────────────────────────────────────────────────────

def album_exists(artist: str, album_title: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM albums WHERE LOWER(artist)=LOWER(?) AND LOWER(album_title)=LOWER(?)",
            (artist, album_title)
        ).fetchone()
        return row is not None


def increment_times_seen(artist: str, album_title: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE albums SET times_seen = times_seen + 1 WHERE LOWER(artist)=LOWER(?) AND LOWER(album_title)=LOWER(?)",
            (artist, album_title)
        )


def insert_album(data: dict) -> int:
    """Insert a new album record. Returns the new row id."""
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO albums
                (artist, album_title, year, country, genre_tags, source_name, source_url,
                 source_author, curatorial_context, date_scraped)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            data.get("artist"),
            data.get("album_title"),
            data.get("year"),
            data.get("country"),
            ", ".join(data.get("genre_tags") or []),
            data.get("source_name"),
            data.get("source_url"),
            data.get("source_author"),
            data.get("curatorial_context"),
            date.today().isoformat(),
        ))
        return cur.lastrowid


def get_candidate_pool(limit: int = 200) -> list:
    """Return albums not yet recommended, ordered by times_seen desc."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM albums
            WHERE recommended = FALSE
            ORDER BY times_seen DESC, date_scraped DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]


def get_recommended_album_ids() -> list:
    with get_conn() as conn:
        rows = conn.execute("SELECT id FROM albums WHERE recommended = TRUE").fetchall()
        return [r["id"] for r in rows]


def mark_recommended(album_ids: list, slot_map: dict):
    """Mark albums as recommended and record which slot they occupied."""
    today = date.today().isoformat()
    with get_conn() as conn:
        for album_id in album_ids:
            conn.execute("""
                UPDATE albums SET recommended=TRUE, date_recommended=?, slot_assigned=?
                WHERE id=?
            """, (today, slot_map.get(str(album_id)), album_id))


def get_album_by_id(album_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM albums WHERE id=?", (album_id,)).fetchone()
        return dict(row) if row else None


# ── Feedback helpers ──────────────────────────────────────────────────────────

def record_feedback(album_id: int, feedback_type: str, requeue_date: str | None = None):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO feedback (album_id, feedback_type, date_submitted, requeue_date)
            VALUES (?,?,?,?)
        """, (album_id, feedback_type, date.today().isoformat(), requeue_date))


def get_pending_scene_followup() -> str | None:
    """Return region name if a follow-up was requested last week."""
    with get_conn() as conn:
        row = conn.execute("""
            SELECT region_name FROM world_rotation
            WHERE follow_up_requested = TRUE LIMIT 1
        """).fetchone()
        return row["region_name"] if row else None


def clear_scene_followup(region_name: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE world_rotation SET follow_up_requested=FALSE WHERE region_name=?",
            (region_name,)
        )


def request_scene_followup(region_name: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE world_rotation SET follow_up_requested=TRUE WHERE region_name=?",
            (region_name,)
        )


def get_older_decade_requested() -> bool:
    """Return True if the user clicked 'Give me something older' last week."""
    with get_conn() as conn:
        row = conn.execute("""
            SELECT id FROM feedback
            WHERE feedback_type='older_decade' AND acted_on=FALSE
            ORDER BY date_submitted DESC LIMIT 1
        """).fetchone()
        return row is not None


def mark_older_decade_acted():
    with get_conn() as conn:
        conn.execute("""
            UPDATE feedback SET acted_on=TRUE
            WHERE feedback_type='older_decade' AND acted_on=FALSE
        """)


# ── World rotation helpers ────────────────────────────────────────────────────

def get_next_world_region() -> str:
    """Return the region that hasn't been recommended most recently."""
    with get_conn() as conn:
        row = conn.execute("""
            SELECT region_name FROM world_rotation
            ORDER BY last_recommended ASC NULLS FIRST
            LIMIT 1
        """).fetchone()
        return row["region_name"] if row else "Middle East / North Africa / Persia"


def update_world_region_date(region_name: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE world_rotation SET last_recommended=? WHERE region_name=?",
            (date.today().isoformat(), region_name)
        )


# ── Digest helpers ────────────────────────────────────────────────────────────

def save_pending_digest(digest_json: str):
    with get_conn() as conn:
        conn.execute("UPDATE pending_digest SET sent=TRUE WHERE sent=FALSE")
        conn.execute(
            "INSERT INTO pending_digest (created_at, digest_json) VALUES (?,?)",
            (date.today().isoformat(), digest_json)
        )


def get_pending_digest() -> str | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT digest_json FROM pending_digest WHERE sent=FALSE ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        return row["digest_json"] if row else None


def mark_digest_sent():
    with get_conn() as conn:
        conn.execute("UPDATE pending_digest SET sent=TRUE WHERE sent=FALSE")


def record_digest_history(album_ids: list, world_region: str):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO digest_history (date_sent, album_ids, world_region)
            VALUES (?,?,?)
        """, (date.today().isoformat(), ",".join(str(i) for i in album_ids), world_region))


# ── Re-queue helpers ──────────────────────────────────────────────────────────

def get_due_requeued_albums() -> list:
    """Return albums flagged for requeue where the requeue date has passed."""
    today = date.today().isoformat()
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT f.id as feedback_id, a.*
            FROM feedback f
            JOIN albums a ON a.id = f.album_id
            WHERE f.feedback_type = 'requeue'
              AND f.acted_on = FALSE
              AND f.requeue_date <= ?
        """, (today,)).fetchall()
        return [dict(r) for r in rows]


def mark_requeue_acted(feedback_id: int):
    with get_conn() as conn:
        conn.execute("UPDATE feedback SET acted_on=TRUE WHERE id=?", (feedback_id,))
