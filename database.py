"""
Database setup and query helpers.
Uses PostgreSQL (via DATABASE_URL) in production, SQLite locally.
All database access goes through this module.
"""

import os
import sqlite3
from datetime import date

DATABASE_URL = os.environ.get("DATABASE_URL", "")
USE_POSTGRES = bool(DATABASE_URL)

# SQLite fallback path (local dev only)
DB_PATH = os.environ.get("DB_PATH", "music.db")
if not USE_POSTGRES:
    _db_dir = os.path.dirname(DB_PATH)
    if _db_dir:
        os.makedirs(_db_dir, exist_ok=True)


# ── Connection ────────────────────────────────────────────────────────────────

def get_conn():
    if USE_POSTGRES:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn


def _execute(conn, sql, params=None):
    cur = conn.cursor()
    cur.execute(sql, params or ())
    return cur


def _executescript(conn, statements):
    cur = conn.cursor()
    for stmt in statements:
        stmt = stmt.strip()
        if stmt:
            cur.execute(stmt)
    conn.commit()


def init_db():
    """Create all tables if they don't exist. Safe to run multiple times."""
    if USE_POSTGRES:
        statements = [
            """CREATE TABLE IF NOT EXISTS albums (
                id                  SERIAL PRIMARY KEY,
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
            )""",
            """CREATE TABLE IF NOT EXISTS feedback (
                id              SERIAL PRIMARY KEY,
                album_id        INTEGER REFERENCES albums(id),
                feedback_type   TEXT NOT NULL,
                date_submitted  DATE NOT NULL,
                requeue_date    DATE,
                acted_on        BOOLEAN DEFAULT FALSE
            )""",
            """CREATE TABLE IF NOT EXISTS digest_history (
                id          SERIAL PRIMARY KEY,
                date_sent   DATE NOT NULL,
                album_ids   TEXT NOT NULL,
                world_region TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS world_rotation (
                id                  SERIAL PRIMARY KEY,
                region_name         TEXT NOT NULL UNIQUE,
                last_recommended    DATE,
                follow_up_requested BOOLEAN DEFAULT FALSE
            )""",
            """CREATE TABLE IF NOT EXISTS pending_digest (
                id          SERIAL PRIMARY KEY,
                created_at  DATE NOT NULL,
                digest_json TEXT NOT NULL,
                sent        BOOLEAN DEFAULT FALSE
            )""",
            """INSERT INTO world_rotation (region_name) VALUES
                ('Middle East / North Africa / Persia'),
                ('Southeast Asia'),
                ('Latin America (Colombia / Peru / Bolivia / Uruguay)'),
                ('West Africa'),
                ('East Africa'),
                ('Central Asia')
            ON CONFLICT (region_name) DO NOTHING""",
        ]
    else:
        statements = [
            """CREATE TABLE IF NOT EXISTS albums (
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
            )""",
            """CREATE TABLE IF NOT EXISTS feedback (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                album_id        INTEGER REFERENCES albums(id),
                feedback_type   TEXT NOT NULL,
                date_submitted  DATE NOT NULL,
                requeue_date    DATE,
                acted_on        BOOLEAN DEFAULT FALSE
            )""",
            """CREATE TABLE IF NOT EXISTS digest_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date_sent   DATE NOT NULL,
                album_ids   TEXT NOT NULL,
                world_region TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS world_rotation (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                region_name         TEXT NOT NULL UNIQUE,
                last_recommended    DATE,
                follow_up_requested BOOLEAN DEFAULT FALSE
            )""",
            """CREATE TABLE IF NOT EXISTS pending_digest (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at  DATE NOT NULL,
                digest_json TEXT NOT NULL,
                sent        BOOLEAN DEFAULT FALSE
            )""",
            """INSERT OR IGNORE INTO world_rotation (region_name) VALUES
                ('Middle East / North Africa / Persia'),
                ('Southeast Asia'),
                ('Latin America (Colombia / Peru / Bolivia / Uruguay)'),
                ('West Africa'),
                ('East Africa'),
                ('Central Asia')""",
        ]

    conn = get_conn()
    try:
        _executescript(conn, statements)
    finally:
        conn.close()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _row_to_dict(row):
    if row is None:
        return None
    if isinstance(row, dict):
        return row
    return dict(row)


def _fetchone(conn, sql, params=None):
    cur = _execute(conn, sql, params)
    row = cur.fetchone()
    return _row_to_dict(row)


def _fetchall(conn, sql, params=None):
    cur = _execute(conn, sql, params)
    return [_row_to_dict(r) for r in cur.fetchall()]


# ── Album helpers ─────────────────────────────────────────────────────────────

def album_exists(artist: str, album_title: str) -> bool:
    conn = get_conn()
    try:
        row = _fetchone(conn,
            "SELECT id FROM albums WHERE LOWER(artist)=LOWER(%s) AND LOWER(album_title)=LOWER(%s)"
            if USE_POSTGRES else
            "SELECT id FROM albums WHERE LOWER(artist)=LOWER(?) AND LOWER(album_title)=LOWER(?)",
            (artist, album_title)
        )
        return row is not None
    finally:
        conn.close()


def increment_times_seen(artist: str, album_title: str):
    conn = get_conn()
    try:
        ph = "%s" if USE_POSTGRES else "?"
        _execute(conn,
            f"UPDATE albums SET times_seen = times_seen + 1 WHERE LOWER(artist)=LOWER({ph}) AND LOWER(album_title)=LOWER({ph})",
            (artist, album_title)
        )
        conn.commit()
    finally:
        conn.close()


def insert_album(data: dict) -> int:
    conn = get_conn()
    try:
        ph = "%s" if USE_POSTGRES else "?"
        suffix = "RETURNING id" if USE_POSTGRES else ""
        sql = f"""
            INSERT INTO albums
                (artist, album_title, year, country, genre_tags, source_name, source_url,
                 source_author, curatorial_context, date_scraped)
            VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph})
            {suffix}
        """
        cur = _execute(conn, sql, (
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
        conn.commit()
        if USE_POSTGRES:
            return cur.fetchone()["id"]
        return cur.lastrowid
    finally:
        conn.close()


def get_candidate_pool(limit: int = 200) -> list:
    conn = get_conn()
    try:
        ph = "%s" if USE_POSTGRES else "?"
        return _fetchall(conn, f"""
            SELECT * FROM albums
            WHERE recommended = FALSE
            ORDER BY times_seen DESC, date_scraped DESC
            LIMIT {ph}
        """, (limit,))
    finally:
        conn.close()


def get_album_by_id(album_id: int) -> dict | None:
    conn = get_conn()
    try:
        ph = "%s" if USE_POSTGRES else "?"
        return _fetchone(conn, f"SELECT * FROM albums WHERE id={ph}", (album_id,))
    finally:
        conn.close()


def mark_recommended(album_ids: list, slot_map: dict):
    today = date.today().isoformat()
    conn = get_conn()
    try:
        ph = "%s" if USE_POSTGRES else "?"
        for album_id in album_ids:
            _execute(conn,
                f"UPDATE albums SET recommended=TRUE, date_recommended={ph}, slot_assigned={ph} WHERE id={ph}",
                (today, slot_map.get(str(album_id)), album_id)
            )
        conn.commit()
    finally:
        conn.close()


# ── Feedback helpers ──────────────────────────────────────────────────────────

def record_feedback(album_id: int, feedback_type: str, requeue_date: str | None = None):
    conn = get_conn()
    try:
        ph = "%s" if USE_POSTGRES else "?"
        _execute(conn,
            f"INSERT INTO feedback (album_id, feedback_type, date_submitted, requeue_date) VALUES ({ph},{ph},{ph},{ph})",
            (album_id, feedback_type, date.today().isoformat(), requeue_date)
        )
        conn.commit()
    finally:
        conn.close()


def get_pending_scene_followup() -> str | None:
    conn = get_conn()
    try:
        row = _fetchone(conn, "SELECT region_name FROM world_rotation WHERE follow_up_requested = TRUE LIMIT 1")
        return row["region_name"] if row else None
    finally:
        conn.close()


def clear_scene_followup(region_name: str):
    conn = get_conn()
    try:
        ph = "%s" if USE_POSTGRES else "?"
        _execute(conn, f"UPDATE world_rotation SET follow_up_requested=FALSE WHERE region_name={ph}", (region_name,))
        conn.commit()
    finally:
        conn.close()


def request_scene_followup(region_name: str):
    conn = get_conn()
    try:
        ph = "%s" if USE_POSTGRES else "?"
        _execute(conn, f"UPDATE world_rotation SET follow_up_requested=TRUE WHERE region_name={ph}", (region_name,))
        conn.commit()
    finally:
        conn.close()


def get_older_decade_requested() -> bool:
    conn = get_conn()
    try:
        row = _fetchone(conn,
            "SELECT id FROM feedback WHERE feedback_type='older_decade' AND acted_on=FALSE ORDER BY date_submitted DESC LIMIT 1"
        )
        return row is not None
    finally:
        conn.close()


def mark_older_decade_acted():
    conn = get_conn()
    try:
        _execute(conn, "UPDATE feedback SET acted_on=TRUE WHERE feedback_type='older_decade' AND acted_on=FALSE")
        conn.commit()
    finally:
        conn.close()


# ── World rotation helpers ────────────────────────────────────────────────────

def get_next_world_region() -> str:
    conn = get_conn()
    try:
        row = _fetchone(conn,
            "SELECT region_name FROM world_rotation ORDER BY last_recommended ASC NULLS FIRST LIMIT 1"
        )
        return row["region_name"] if row else "Middle East / North Africa / Persia"
    finally:
        conn.close()


def update_world_region_date(region_name: str):
    conn = get_conn()
    try:
        ph = "%s" if USE_POSTGRES else "?"
        _execute(conn, f"UPDATE world_rotation SET last_recommended={ph} WHERE region_name={ph}",
                 (date.today().isoformat(), region_name))
        conn.commit()
    finally:
        conn.close()


# ── Digest helpers ────────────────────────────────────────────────────────────

def save_pending_digest(digest_json: str):
    conn = get_conn()
    try:
        _execute(conn, "UPDATE pending_digest SET sent=TRUE WHERE sent=FALSE")
        ph = "%s" if USE_POSTGRES else "?"
        _execute(conn, f"INSERT INTO pending_digest (created_at, digest_json) VALUES ({ph},{ph})",
                 (date.today().isoformat(), digest_json))
        conn.commit()
    finally:
        conn.close()


def get_pending_digest() -> str | None:
    conn = get_conn()
    try:
        row = _fetchone(conn,
            "SELECT digest_json FROM pending_digest WHERE sent=FALSE ORDER BY created_at DESC LIMIT 1"
        )
        return row["digest_json"] if row else None
    finally:
        conn.close()


def mark_digest_sent():
    conn = get_conn()
    try:
        _execute(conn, "UPDATE pending_digest SET sent=TRUE WHERE sent=FALSE")
        conn.commit()
    finally:
        conn.close()


def record_digest_history(album_ids: list, world_region: str):
    conn = get_conn()
    try:
        ph = "%s" if USE_POSTGRES else "?"
        _execute(conn,
            f"INSERT INTO digest_history (date_sent, album_ids, world_region) VALUES ({ph},{ph},{ph})",
            (date.today().isoformat(), ",".join(str(i) for i in album_ids), world_region)
        )
        conn.commit()
    finally:
        conn.close()


# ── Re-queue helpers ──────────────────────────────────────────────────────────

def get_due_requeued_albums() -> list:
    today = date.today().isoformat()
    conn = get_conn()
    try:
        ph = "%s" if USE_POSTGRES else "?"
        return _fetchall(conn, f"""
            SELECT f.id as feedback_id, a.*
            FROM feedback f
            JOIN albums a ON a.id = f.album_id
            WHERE f.feedback_type = 'requeue'
              AND f.acted_on = FALSE
              AND f.requeue_date <= {ph}
        """, (today,))
    finally:
        conn.close()


def mark_requeue_acted(feedback_id: int):
    conn = get_conn()
    try:
        ph = "%s" if USE_POSTGRES else "?"
        _execute(conn, f"UPDATE feedback SET acted_on=TRUE WHERE id={ph}", (feedback_id,))
        conn.commit()
    finally:
        conn.close()
