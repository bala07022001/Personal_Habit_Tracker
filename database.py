"""
database.py - SQLite persistence layer for Habit & Reading Tracker
"""
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "tracker.db"


def get_conn():
    conn = sqlite3.connect(
        str(DB_PATH),
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS habits (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,
            category    TEXT DEFAULT 'General',
            is_active   INTEGER DEFAULT 1,
            created_at  DATE DEFAULT (date('now'))
        );
        CREATE TABLE IF NOT EXISTS habit_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id   INTEGER NOT NULL REFERENCES habits(id),
            log_date   DATE NOT NULL,
            done       INTEGER DEFAULT 0,
            note       TEXT,
            UNIQUE(habit_id, log_date)
        );
        CREATE TABLE IF NOT EXISTS journal (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date DATE NOT NULL UNIQUE,
            content    TEXT,
            mood       TEXT,
            gratitude  TEXT,
            wins       TEXT,
            created_at TIMESTAMP DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS books (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            title           TEXT NOT NULL,
            author          TEXT,
            discipline      TEXT,
            status          TEXT DEFAULT 'Yet To Start',
            start_date      DATE,
            completion_date DATE,
            year_read       TEXT,
            activity        TEXT,
            rating          INTEGER,
            review          TEXT,
            key_lessons     TEXT,
            favourite_quote TEXT,
            tags            TEXT,
            added_at        DATE DEFAULT (date('now'))
        );
        CREATE TABLE IF NOT EXISTS reading_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id     INTEGER NOT NULL REFERENCES books(id),
            log_date    DATE NOT NULL,
            pages_read  INTEGER DEFAULT 0,
            notes       TEXT,
            UNIQUE(book_id, log_date)
        );
        """)



# ── HABITS ────────────────────────────────────────────────────────────────────

def get_habits(active_only=True):
    with get_conn() as conn:
        q = "SELECT * FROM habits"
        if active_only:
            q += " WHERE is_active = 1"
        q += " ORDER BY id"
        return [dict(r) for r in conn.execute(q).fetchall()]


def add_habit(name: str, category: str = "General"):
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO habits(name, category) VALUES (?, ?)", (name, category))


def toggle_habit_active(habit_id: int, active: bool):
    with get_conn() as conn:
        conn.execute("UPDATE habits SET is_active=? WHERE id=?", (int(active), habit_id))


def log_habits(date_str: str, logs: dict):
    """logs: {habit_id: (done: bool, note: str)}"""
    with get_conn() as conn:
        for habit_id, (done, note) in logs.items():
            conn.execute("""
                INSERT INTO habit_log(habit_id, log_date, done, note)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(habit_id, log_date) DO UPDATE SET done=excluded.done, note=excluded.note
            """, (habit_id, date_str, int(done), note))


def get_habit_log_for_date(date_str: str):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT h.id, h.name, h.category,
                   COALESCE(hl.done, 0) as done, COALESCE(hl.note, '') as note
            FROM habits h
            LEFT JOIN habit_log hl ON hl.habit_id = h.id AND hl.log_date = ?
            WHERE h.is_active = 1
            ORDER BY h.id
        """, (date_str,)).fetchall()
        return [dict(r) for r in rows]


def get_habit_streak(habit_id: int):
    """Returns current streak (consecutive days done up to today)."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT log_date, done FROM habit_log
            WHERE habit_id = ? ORDER BY log_date DESC
        """, (habit_id,)).fetchall()
    streak = 0
    for r in rows:
        if r["done"] == 1:
            streak += 1
        else:
            break
    return streak


def get_habit_stats(days: int = 30):
    """Returns per-habit completion % for last N days."""
    with get_conn() as conn:
        rows = conn.execute(f"""
            SELECT h.name, h.id,
                   SUM(hl.done) as done_count,
                   COUNT(hl.id) as total_logged,
                   MAX(hl.log_date) as last_logged
            FROM habits h
            LEFT JOIN habit_log hl ON hl.habit_id = h.id
                AND hl.log_date >= date('now', '-{days} days')
            WHERE h.is_active = 1
            GROUP BY h.id
            ORDER BY h.id
        """).fetchall()
        return [dict(r) for r in rows]


def get_habit_heatmap(habit_id: int, year: int):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT log_date, done FROM habit_log
            WHERE habit_id = ? AND strftime('%Y', log_date) = ?
            ORDER BY log_date
        """, (habit_id, str(year))).fetchall()
        return {r["log_date"]: r["done"] for r in rows}


def get_daily_completion_trend(days: int = 60):
    """Returns [{log_date, pct}] for the last N days — used by Analytics page."""
    with get_conn() as conn:
        rows = conn.execute(f"""
            SELECT log_date,
                   ROUND(100.0 * SUM(done) / COUNT(*), 1) as pct
            FROM habit_log
            WHERE log_date >= date('now', '-{days} days')
            GROUP BY log_date ORDER BY log_date
        """).fetchall()
        return [dict(r) for r in rows]


def get_dow_completion():
    """Returns [{dow, pct}] grouped by day-of-week (0=Sun)."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT strftime('%w', log_date) as dow,
                   ROUND(100.0 * SUM(done) / COUNT(*), 1) as pct
            FROM habit_log GROUP BY dow ORDER BY dow
        """).fetchall()
        return [dict(r) for r in rows]


# ── JOURNAL ───────────────────────────────────────────────────────────────────

def save_journal(entry_date: str, content: str, mood: str, gratitude: str, wins: str):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO journal(entry_date, content, mood, gratitude, wins)
            VALUES(?,?,?,?,?)
            ON CONFLICT(entry_date) DO UPDATE SET
                content=excluded.content, mood=excluded.mood,
                gratitude=excluded.gratitude, wins=excluded.wins
        """, (entry_date, content, mood, gratitude, wins))


def get_journal(entry_date: str):
    with get_conn() as conn:
        r = conn.execute("SELECT * FROM journal WHERE entry_date=?", (entry_date,)).fetchone()
        return dict(r) if r else None


def get_journal_history(limit: int = 30):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT entry_date, mood, substr(content,1,120) as preview
            FROM journal ORDER BY entry_date DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]


# ── BOOKS ─────────────────────────────────────────────────────────────────────

def add_book(title, author="", discipline="", status="Yet To Start",
             year_read="", activity="", rating=None, review="",
             key_lessons="", favourite_quote="", tags="",
             completion_date=None, start_date=None):
    with get_conn() as conn:
        exists = conn.execute(
            "SELECT id FROM books WHERE lower(trim(title))=lower(trim(?))", (title,)
        ).fetchone()
        if exists:
            return
        conn.execute("""
            INSERT INTO books
            (title, author, discipline, status, year_read, activity, rating,
             review, key_lessons, favourite_quote, tags, completion_date, start_date)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (title, author, discipline, status, year_read, activity, rating,
              review, key_lessons, favourite_quote, tags, completion_date, start_date))


def update_book(book_id: int, **fields):
    if not fields:
        return
    sets = ", ".join(f"{k}=?" for k in fields)
    vals = list(fields.values()) + [book_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE books SET {sets} WHERE id=?", vals)


def get_books(status_filter=None):
    with get_conn() as conn:
        if status_filter:
            rows = conn.execute("SELECT * FROM books WHERE status=? ORDER BY id", (status_filter,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM books ORDER BY id").fetchall()
        return [dict(r) for r in rows]


def get_book(book_id: int):
    with get_conn() as conn:
        r = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
        return dict(r) if r else None


def search_books(query: str):
    q = f"%{query}%"
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR discipline LIKE ? OR tags LIKE ? ORDER BY id",
            (q, q, q, q),
        ).fetchall()
        return [dict(r) for r in rows]


def log_reading_session(book_id: int, log_date: str, pages_read: int, notes: str = ""):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO reading_log(book_id, log_date, pages_read, notes)
            VALUES(?,?,?,?)
            ON CONFLICT(book_id, log_date) DO UPDATE SET
                pages_read=excluded.pages_read, notes=excluded.notes
        """, (book_id, log_date, pages_read, notes))


def get_reading_sessions(book_id: int):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM reading_log WHERE book_id=? ORDER BY log_date DESC",
            (book_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_books_stats():
    with get_conn() as conn:
        row = conn.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status='Completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status='Inprogress' THEN 1 ELSE 0 END) as inprogress,
                SUM(CASE WHEN status='Yet To Start' THEN 1 ELSE 0 END) as yet_to_start,
                SUM(CASE WHEN status='On Hold' THEN 1 ELSE 0 END) as on_hold
            FROM books
        """).fetchone()
        return dict(row)


def delete_book(book_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM reading_log WHERE book_id=?", (book_id,))
        conn.execute("DELETE FROM books WHERE id=?", (book_id,))


def deduplicate_books():
    """Delete duplicate books keeping only the lowest id per title (case-insensitive)."""
    with get_conn() as conn:
        dupes = conn.execute("""
            SELECT lower(trim(title)) as ltitle, MIN(id) as keep_id, COUNT(*) as cnt
            FROM books
            GROUP BY lower(trim(title))
            HAVING cnt > 1
        """).fetchall()
        removed = 0
        for row in dupes:
            result = conn.execute(
                "DELETE FROM books WHERE lower(trim(title))=? AND id != ?",
                (row["ltitle"], row["keep_id"])
            )
            removed += result.rowcount
        return removed


# ── QUERY EDITOR ──────────────────────────────────────────────────────────────

def execute_query(sql: str):
    """Execute a raw SQL query (SELECT/INSERT/UPDATE/DELETE). Returns results or error message."""
    try:
        with get_conn() as conn:
            cursor = conn.execute(sql)
            # Fetch all results if it's a SELECT
            if sql.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                return {"success": True, "data": [dict(r) for r in rows], "count": len(rows)}
            else:
                # For INSERT/UPDATE/DELETE, return affected rows
                return {"success": True, "data": None, "count": cursor.rowcount}
    except Exception as e:
        return {"success": False, "error": str(e), "count": 0}


def get_table_schema():
    """Returns schema info for all tables."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT name FROM sqlite_master WHERE type='table' ORDER BY name
        """).fetchall()
        tables = [r[0] for r in rows]
        
        schema = {}
        for table in tables:
            columns = conn.execute(f"PRAGMA table_info({table})").fetchall()
            schema[table] = [
                {"name": col[1], "type": col[2], "notnull": col[3], "default": col[4], "pk": col[5]}
                for col in columns
            ]
        return schema

