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
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            description     TEXT,
            category        TEXT DEFAULT 'General',
            action_type     TEXT DEFAULT 'checkbox',
            unit            TEXT,
            target_value    REAL,
            status          TEXT DEFAULT 'active',
            created_at      DATE DEFAULT (date('now')),
            completed_at    DATE,
            archived_at     DATE
        );
        CREATE TABLE IF NOT EXISTS habit_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id        INTEGER NOT NULL REFERENCES habits(id),
            log_date        DATE NOT NULL,
            value           REAL,
            note            TEXT,
            UNIQUE(habit_id, log_date)
        );
        CREATE TABLE IF NOT EXISTS habit_versions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            original_habit_id INTEGER NOT NULL REFERENCES habits(id),
            new_habit_id    INTEGER REFERENCES habits(id),
            transition_date DATE DEFAULT (date('now')),
            reason          TEXT
        );
        CREATE TABLE IF NOT EXISTS journal (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date      DATE NOT NULL UNIQUE,
            content         TEXT,
            mood            TEXT,
            gratitude       TEXT,
            wins            TEXT,
            created_at      TIMESTAMP DEFAULT (datetime('now'))
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
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id         INTEGER NOT NULL REFERENCES books(id),
            log_date        DATE NOT NULL,
            pages_read      INTEGER DEFAULT 0,
            notes           TEXT,
            UNIQUE(book_id, log_date)
        );
        CREATE TABLE IF NOT EXISTS ideas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id         INTEGER REFERENCES books(id),
            habit_id        INTEGER REFERENCES habits(id),
            title           TEXT NOT NULL,
            description     TEXT,
            chapter_section TEXT,
            status          TEXT DEFAULT 'captured',
            captured_date   DATE DEFAULT (date('now')),
            applied_date    DATE
        );
        CREATE TABLE IF NOT EXISTS applications (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id         INTEGER NOT NULL REFERENCES ideas(id),
            project_name    TEXT NOT NULL,
            description     TEXT,
            application_date DATE DEFAULT (date('now')),
            impact          TEXT
        );
        """)




# ── HABITS ────────────────────────────────────────────────────────────────────

def create_habit(name: str, category: str = "General", description: str = "", 
                 action_type: str = "checkbox", unit: str = None, target_value: float = None):
    """Create a new habit with action-based tracking."""
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO habits(name, category, description, action_type, unit, target_value, status)
            VALUES(?, ?, ?, ?, ?, ?, 'active')
        """, (name, category, description, action_type, unit, target_value))


def get_habits(status: str = "active"):
    """Get habits by status: 'active', 'completed', 'archived', or 'all'."""
    with get_conn() as conn:
        if status == "all":
            q = "SELECT * FROM habits ORDER BY status, created_at DESC"
            rows = conn.execute(q).fetchall()
        else:
            q = "SELECT * FROM habits WHERE status = ? ORDER BY created_at DESC"
            rows = conn.execute(q, (status,)).fetchall()
        return [dict(r) for r in rows]


def get_habit(habit_id: int):
    """Get a single habit."""
    with get_conn() as conn:
        r = conn.execute("SELECT * FROM habits WHERE id=?", (habit_id,)).fetchone()
        return dict(r) if r else None


def update_habit(habit_id: int, **fields):
    """Update habit fields (e.g., name, description, target_value)."""
    if not fields:
        return
    sets = ", ".join(f"{k}=?" for k in fields)
    vals = list(fields.values()) + [habit_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE habits SET {sets} WHERE id=?", vals)


def capture_idea(book_id: int = None, habit_id: int = None, title: str = "", 
                description: str = "", chapter_section: str = ""):
    """Capture a key learning/idea from a book or habit."""
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO ideas(book_id, habit_id, title, description, chapter_section)
            VALUES(?, ?, ?, ?, ?)
        """, (book_id, habit_id, title, description, chapter_section))
        return conn.lastrowid


def apply_idea(idea_id: int, project_name: str, description: str = "", impact: str = ""):
    """Log application of an idea to a project."""
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO applications(idea_id, project_name, description, impact)
            VALUES(?, ?, ?, ?)
        """, (idea_id, project_name, description, impact))
        conn.execute(
            "UPDATE ideas SET status='applied', applied_date=date('now') WHERE id=?",
            (idea_id,)
        )


def get_book_ideas(book_id: int):
    """Get all ideas captured from a book."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT i.*, COUNT(a.id) as applications_count
            FROM ideas i
            LEFT JOIN applications a ON i.id = a.idea_id
            WHERE i.book_id = ?
            GROUP BY i.id
            ORDER BY i.captured_date DESC
        """, (book_id,)).fetchall()
        return [dict(r) for r in rows]


def get_idea_applications(idea_id: int):
    """Get all projects where an idea has been applied."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM applications WHERE idea_id = ?
            ORDER BY application_date DESC
        """, (idea_id,)).fetchall()
        return [dict(r) for r in rows]


def complete_habit(habit_id: int):
    """Mark habit as completed."""
    with get_conn() as conn:
        conn.execute(
            "UPDATE habits SET status='completed', completed_at=date('now') WHERE id=?",
            (habit_id,)
        )


def enhance_habit(old_habit_id: int, new_name: str, new_description: str, 
                  category: str, action_type: str, unit: str = None, target_value: float = None):
    """Complete old habit and create an evolved version."""
    with get_conn() as conn:
        # Create new habit
        conn.execute("""
            INSERT INTO habits(name, category, description, action_type, unit, target_value, status)
            VALUES(?, ?, ?, ?, ?, ?, 'active')
        """, (new_name, category, new_description, action_type, unit, target_value))
        
        # Get the new habit ID
        new_habit_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        # Record the transition
        conn.execute("""
            INSERT INTO habit_versions(original_habit_id, new_habit_id, reason)
            VALUES(?, ?, 'evolved')
        """, (old_habit_id, new_habit_id))
        
        # Archive old habit
        conn.execute(
            "UPDATE habits SET status='completed', completed_at=date('now') WHERE id=?",
            (old_habit_id,)
        )
        
        return new_habit_id


def archive_habit(habit_id: int):
    """Archive a habit without completing it."""
    with get_conn() as conn:
        conn.execute(
            "UPDATE habits SET status='archived', archived_at=date('now') WHERE id=?",
            (habit_id,)
        )


def log_habit(habit_id: int, date_str: str, value: float = 1.0, note: str = ""):
    """Log a habit action with value (for checkbox: 1.0, for quantity/duration: actual value)."""
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO habit_log(habit_id, log_date, value, note)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET value=excluded.value, note=excluded.note
        """, (habit_id, date_str, value, note))


def get_habit_log_for_date(date_str: str):
    """Get all active habit logs for a date."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT h.id, h.name, h.category, h.action_type, h.unit, h.target_value,
                   COALESCE(hl.value, 0) as value, COALESCE(hl.note, '') as note
            FROM habits h
            LEFT JOIN habit_log hl ON hl.habit_id = h.id AND hl.log_date = ?
            WHERE h.status = 'active'
            ORDER BY h.created_at DESC
        """, (date_str,)).fetchall()
        return [dict(r) for r in rows]


def get_habit_progress(habit_id: int, days: int = 30):
    """Get habit progress over last N days."""
    with get_conn() as conn:
        rows = conn.execute(f"""
            SELECT 
                h.id, h.name, h.unit, h.target_value,
                COUNT(hl.id) as days_logged,
                SUM(hl.value) as total_value,
                AVG(hl.value) as avg_value,
                MAX(hl.log_date) as last_logged
            FROM habits h
            LEFT JOIN habit_log hl ON hl.habit_id = h.id 
                AND hl.log_date >= date('now', '-{days} days')
            WHERE h.id = ?
            GROUP BY h.id
        """, (habit_id,)).fetchone()
        return dict(rows) if rows else None


def get_habit_stats(days: int = 30):
    """Get stats for all active habits over last N days."""
    with get_conn() as conn:
        rows = conn.execute(f"""
            SELECT 
                h.id, h.name, h.action_type, h.unit, h.target_value,
                COUNT(hl.id) as days_logged,
                SUM(hl.value) as total_value,
                AVG(hl.value) as avg_value,
                MAX(hl.log_date) as last_logged
            FROM habits h
            LEFT JOIN habit_log hl ON hl.habit_id = h.id 
                AND hl.log_date >= date('now', '-{days} days')
            WHERE h.status = 'active'
            GROUP BY h.id
            ORDER BY h.created_at DESC
        """).fetchall()
        return [dict(r) for r in rows]


def get_habit_timeline(habit_id: int, days: int = 60):
    """Get daily values for a habit over N days."""
    with get_conn() as conn:
        rows = conn.execute(f"""
            SELECT log_date, value FROM habit_log
            WHERE habit_id = ? AND log_date >= date('now', '-{days} days')
            ORDER BY log_date
        """, (habit_id,)).fetchall()
        return [dict(r) for r in rows]


def get_daily_completion_trend(days: int = 60):
    """Get daily habit completion % over N days."""
    with get_conn() as conn:
        rows = conn.execute(f"""
            SELECT
                d.log_date,
                ROUND(100.0 * COUNT(DISTINCT hl.habit_id) / NULLIF(COUNT(DISTINCT h.id), 0), 1) as pct
            FROM (
                WITH RECURSIVE dates(log_date) AS (
                    SELECT date('now')
                    UNION ALL
                    SELECT date(log_date, '-1 day')
                    FROM dates
                    WHERE log_date > date('now', '-{days} days')
                )
                SELECT log_date FROM dates
            ) d
            CROSS JOIN habits h
            LEFT JOIN habit_log hl ON h.id = hl.habit_id AND hl.log_date = d.log_date
            WHERE h.status = 'active'
            GROUP BY d.log_date
            ORDER BY d.log_date DESC
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

