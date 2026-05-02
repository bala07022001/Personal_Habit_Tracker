# -*- coding: utf-8 -*-
"""
database_postgres.py - PostgreSQL Persistence Layer (Learning Edition)

This module demonstrates PostgreSQL best practices with educational comments.
Learn PostgreSQL concepts as you read through the code!

Key Learning Points:
1. Connection pooling (psycopg2 + connection parameters)
2. Using context managers for transaction safety
3. Parameterized queries to prevent SQL injection
4. SERIAL primary keys (auto-increment)
5. JSON/JSONB data types
6. Window functions and CTEs
7. Foreign key constraints with cascading
"""

import psycopg2
from psycopg2 import sql, extras
from psycopg2.pool import SimpleConnectionPool
from datetime import date, datetime, timedelta
from contextlib import contextmanager
import os

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

# 🔑 KEY CONCEPT: Connection Strings
# Format: postgresql://user:password@host:port/database
# All connection info in one string for easy deployment

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres_password_123@localhost:5432/habits_tracker"
)

# 💡 LEARNING: Connection Pooling
# Instead of creating a new connection for each query (slow),
# we maintain a pool of reusable connections (fast!)
# minconn: Minimum connections to keep alive
# maxconn: Maximum connections in pool
connection_pool = None


def init_connection_pool():
    """
    Initialize the connection pool on app startup.
    
    💡 CONNECTION POOLING CONCEPT:
    - Traditional approach: Open connection → Query → Close connection (slow)
    - Pool approach: Maintain 5-20 connections ready to use (fast!)
    - When you need a connection, grab from pool; when done, return to pool
    """
    global connection_pool
    if connection_pool is None:
        connection_pool = SimpleConnectionPool(
            minconn=2,  # Keep 2 connections always ready
            maxconn=10,  # Max 10 connections
            dsn=DATABASE_URL
        )


# ─────────────────────────────────────────────────────────────────────────────
# CONNECTION MANAGEMENT WITH CONTEXT MANAGERS
# ─────────────────────────────────────────────────────────────────────────────

@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    
    💡 CONTEXT MANAGERS & TRANSACTIONS:
    This ensures:
    1. Connection is taken from pool
    2. If query succeeds → COMMIT (save changes)
    3. If query fails → ROLLBACK (undo changes)
    4. Connection returned to pool either way
    
    Usage:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM habits")
            results = cur.fetchall()
    """
    conn = connection_pool.getconn()
    try:
        yield conn
        conn.commit()  # 💡 Implicit transaction: changes saved here
    except Exception as e:
        conn.rollback()  # 💡 If error, undo all changes
        print(f"Database error: {e}")
        raise
    finally:
        connection_pool.putconn(conn)  # Return to pool


# Alias for compatibility with SQLite interface
def get_conn():
    """
    Compatibility function to match SQLite interface.
    Returns the context manager (same as get_db_connection).
    """
    return get_db_connection()


# ─────────────────────────────────────────────────────────────────────────────
# INITIALIZATION: CREATE TABLES
# ─────────────────────────────────────────────────────────────────────────────

def init_db():
    """
    Create all tables if they don't exist.
    
    💡 PostgreSQL Data Types:
    - SERIAL = Auto-incrementing INTEGER (like SQLite AUTOINCREMENT)
    - TEXT = Variable-length strings (no length limit needed)
    - DATE = Just the date (YYYY-MM-DD)
    - TIMESTAMP = Date + time with microsecond precision
    - BOOLEAN = true/false (unlike SQLite's 0/1)
    - JSONB = Binary JSON (more efficient than JSON, can be indexed!)
    - INTEGER[] = Array of integers
    
    💡 Constraints:
    - PRIMARY KEY = Unique identifier for each row
    - NOT NULL = This column must always have a value
    - UNIQUE = No duplicates allowed
    - REFERENCES = Foreign key (links to another table)
    - ON DELETE CASCADE = If parent deleted, delete children too
    - DEFAULT = Use this value if not specified
    """
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 💡 CREATE TABLE IF NOT EXISTS = Safe to run multiple times
        cur.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                -- 💡 SERIAL: Auto-incrementing ID (use: INSERT ... RETURNING id)
                id SERIAL PRIMARY KEY,
                
                -- Core fields
                name TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'General',
                
                -- Action system fields
                action_type TEXT DEFAULT 'checkbox',  -- checkbox | duration | pages | quantity
                unit TEXT,  -- 'hours', 'pages', 'ideas', etc.
                target_value NUMERIC,  -- Float target for progress tracking
                
                -- Status tracking
                status TEXT DEFAULT 'active',  -- active | completed | archived
                
                -- 💡 TIMESTAMP with timezone: Stores when created/updated
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                completed_at TIMESTAMP WITH TIME ZONE,
                archived_at TIMESTAMP WITH TIME ZONE
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS habit_log (
                id SERIAL PRIMARY KEY,
                
                -- 💡 FOREIGN KEY: Links to habits table
                -- ON DELETE CASCADE: If habit deleted, delete its logs too
                habit_id INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
                
                log_date DATE NOT NULL,
                value NUMERIC,  -- Flexible: 1.0 for checkbox, 2.5 for hours, etc.
                note TEXT,
                
                -- 💡 UNIQUE constraint on (habit_id, log_date)
                -- Ensures only one entry per habit per day
                UNIQUE(habit_id, log_date)
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS habit_versions (
                id SERIAL PRIMARY KEY,
                original_habit_id INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
                new_habit_id INTEGER REFERENCES habits(id) ON DELETE SET NULL,
                transition_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                reason TEXT
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS journal (
                id SERIAL PRIMARY KEY,
                entry_date DATE NOT NULL UNIQUE,
                content TEXT,
                mood TEXT,
                gratitude TEXT,
                wins TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT,
                discipline TEXT,
                status TEXT DEFAULT 'Yet To Start',  -- Yet To Start | Inprogress | Completed | On Hold
                start_date DATE,
                completion_date DATE,
                year_read TEXT,
                activity TEXT,
                rating INTEGER,
                
                -- 💡 JSONB: Binary JSON - can store complex nested data
                -- Perfect for book reviews with multiple fields
                -- Can be indexed! Can query inside it!
                review TEXT,
                key_lessons TEXT,
                favourite_quote TEXT,
                tags TEXT,
                added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reading_log (
                id SERIAL PRIMARY KEY,
                book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
                log_date DATE NOT NULL,
                pages_read INTEGER DEFAULT 0,
                notes TEXT,
                UNIQUE(book_id, log_date)
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ideas (
                id SERIAL PRIMARY KEY,
                book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
                habit_id INTEGER REFERENCES habits(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                description TEXT,
                chapter_section TEXT,
                status TEXT DEFAULT 'captured',  -- captured | applied
                captured_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                applied_date TIMESTAMP WITH TIME ZONE
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id SERIAL PRIMARY KEY,
                idea_id INTEGER NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
                project_name TEXT NOT NULL,
                description TEXT,
                impact TEXT,
                application_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # 💡 INDEXES: Speed up common queries
        # Without index: PostgreSQL must scan every row (slow!)
        # With index: PostgreSQL can jump to matching rows (fast!)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_habit_log_date 
            ON habit_log(log_date);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_habit_status 
            ON habits(status);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_book_status 
            ON books(status);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_idea_book 
            ON ideas(book_id);
        """)
        
        print("✅ Database initialized successfully!")


# ─────────────────────────────────────────────────────────────────────────────
# HABIT OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def create_habit(name: str, category: str = "General", description: str = "",
                 action_type: str = "checkbox", unit: str = None, target_value: float = None):
    """
    Create a new habit.
    
    💡 PARAMETERIZED QUERIES:
    Notice: cur.execute(sql, (param1, param2, ...))
    This prevents SQL injection attacks! Never use f-strings for SQL!
    
    Bad (vulnerable):  cur.execute(f"INSERT INTO ... VALUES ('{name}')")
    Good (safe):       cur.execute("INSERT INTO ... VALUES (%s)", (name,))
    """
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 💡 Use %s placeholders (PostgreSQL style, not ? like SQLite)
        cur.execute("""
            INSERT INTO habits(name, category, description, action_type, unit, target_value, status)
            VALUES(%s, %s, %s, %s, %s, %s, 'active')
            RETURNING id;
        """, (name, category, description, action_type, unit, target_value))
        
        # 💡 RETURNING: Get the generated ID back
        habit_id = cur.fetchone()[0]
        print(f"✅ Created habit: {name} (ID: {habit_id})")
        return habit_id


def get_habits(status: str = "active"):
    """
    Get habits by status.
    
    💡 RealDictCursor: Return rows as dictionaries instead of tuples
    Makes code more readable: row['name'] instead of row[1]
    """
    with get_db_connection() as conn:
        # 💡 Use RealDictCursor for dict-like row access
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        cur.execute("""
            SELECT * FROM habits 
            WHERE status = %s 
            ORDER BY created_at DESC;
        """, (status,))
        
        return cur.fetchall()


def update_habit(habit_id: int, **fields):
    """
    Update habit fields dynamically.
    
    💡 Dynamic SQL Building:
    Instead of writing separate UPDATE queries for each field,
    we build SQL dynamically using sql.SQL() for safe column names
    """
    if not fields:
        return
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 💡 sql.SQL and sql.Identifier for safe dynamic SQL
        # This prevents SQL injection on column names too
        query = sql.SQL("UPDATE habits SET {} WHERE id = %s").format(
            sql.SQL(", ").join(
                sql.Identifier(k) + sql.SQL("= %s") for k in fields
            )
        )
        
        values = list(fields.values()) + [habit_id]
        cur.execute(query, values)
        conn.commit()


def log_habit(habit_id: int, date_str: str, value: float = 1.0, note: str = ""):
    """
    Log a habit action.
    
    💡 INSERT ... ON CONFLICT (for upsert):
    PostgreSQL has a powerful UPSERT feature!
    If trying to insert duplicate (habit_id, log_date), UPDATE instead
    """
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # 💡 ON CONFLICT: Upsert pattern
        # INSERT or UPDATE if entry already exists
        cur.execute("""
            INSERT INTO habit_log(habit_id, log_date, value, note)
            VALUES(%s, %s, %s, %s)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET
                value = EXCLUDED.value,
                note = EXCLUDED.note;
        """, (habit_id, date_str, value, note))


def get_habit_stats(days: int = 30):
    """
    Get habit statistics with advanced SQL!
    
    💡 WINDOW FUNCTIONS:
    COUNT(*) OVER (...) lets you calculate aggregate values
    without losing row-by-row detail. Powerful!
    
    💡 LEFT JOIN:
    Habits with NO logs still appear (with NULL counts)
    """
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # 💡 This query demonstrates:
        # - Window functions (COUNT OVER)
        # - Aggregation with GROUP BY
        # - Date arithmetic (CURRENT_DATE - INTERVAL)
        # - COALESCE for NULL handling
        cur.execute(f"""
            SELECT
                h.id,
                h.name,
                h.action_type,
                h.unit,
                h.target_value,
                COUNT(DISTINCT hl.log_date) as days_logged,
                COALESCE(SUM(hl.value), 0) as total_value,
                COALESCE(AVG(hl.value), 0) as avg_value,
                MAX(hl.log_date) as last_logged
            FROM habits h
            LEFT JOIN habit_log hl ON h.id = hl.habit_id 
                AND hl.log_date >= CURRENT_DATE - INTERVAL '{days} days'
            WHERE h.status = 'active'
            GROUP BY h.id
            ORDER BY h.created_at DESC;
        """)
        
        return cur.fetchall()


def get_habit_timeline(habit_id: int, days: int = 60):
    """
    Get daily habit values for charting.
    
    💡 Date Range Queries:
    CURRENT_DATE - INTERVAL '60 days' = 60 days ago
    Much cleaner than Python timedelta calculations!
    """
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        cur.execute(f"""
            SELECT log_date, value 
            FROM habit_log
            WHERE habit_id = %s 
              AND log_date >= CURRENT_DATE - INTERVAL '{days} days'
            ORDER BY log_date;
        """, (habit_id,))
        
        return cur.fetchall()


def get_daily_completion_trend(days: int = 60):
    """
    Get daily completion percentage.
    
    💡 WINDOW FUNCTIONS & CTEs (Common Table Expressions):
    - WITH clause creates temp "virtual tables"
    - Used to break complex queries into readable parts
    - Think of it as: "First, calculate X, then use X to calculate Y"
    """
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # 💡 CTE: WITH clause creates temporary result sets
        cur.execute(f"""
            WITH date_range AS (
                -- Generate all dates in the range
                SELECT CURRENT_DATE - (n || ' days')::INTERVAL as log_date
                FROM generate_series(0, {days}) as n
            ),
            daily_stats AS (
                -- Count habits logged each day
                SELECT
                    d.log_date,
                    COUNT(DISTINCT hl.habit_id) as habits_logged,
                    COUNT(DISTINCT h.id) as total_active_habits
                FROM date_range d
                LEFT JOIN habit_log hl ON d.log_date = hl.log_date
                LEFT JOIN habits h ON hl.habit_id = h.id AND h.status = 'active'
                CROSS JOIN habits h2 WHERE h2.status = 'active'
                GROUP BY d.log_date
            )
            SELECT
                log_date,
                ROUND(100.0 * habits_logged / NULLIF(total_active_habits, 0), 1) as pct
            FROM daily_stats
            ORDER BY log_date DESC;
        """)
        
        return cur.fetchall()


# ─────────────────────────────────────────────────────────────────────────────
# JOURNAL OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def save_journal(entry_date: str, content: str, mood: str, gratitude: str, wins: str):
    """Save or update journal entry."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO journal(entry_date, content, mood, gratitude, wins)
            VALUES(%s, %s, %s, %s, %s)
            ON CONFLICT(entry_date) DO UPDATE SET
                content = EXCLUDED.content,
                mood = EXCLUDED.mood,
                gratitude = EXCLUDED.gratitude,
                wins = EXCLUDED.wins;
        """, (entry_date, content, mood, gratitude, wins))


def get_journal(entry_date: str):
    """Get journal entry for a date."""
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        cur.execute("""
            SELECT * FROM journal WHERE entry_date = %s;
        """, (entry_date,))
        
        row = cur.fetchone()
        return dict(row) if row else None


def get_journal_history(limit: int = 30):
    """Get recent journal entries."""
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        cur.execute("""
            SELECT entry_date, mood, LEFT(content, 120) as preview
            FROM journal 
            ORDER BY entry_date DESC 
            LIMIT %s;
        """, (limit,))
        
        return cur.fetchall()


# ─────────────────────────────────────────────────────────────────────────────
# BOOK OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def add_book(title, author="", discipline="", status="Yet To Start",
             year_read="", activity="", rating=None, review="",
             key_lessons="", favourite_quote="", tags=""):
    """Add a new book."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO books(title, author, discipline, status, year_read, activity,
                             rating, review, key_lessons, favourite_quote, tags)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (title, author, discipline, status, year_read, activity,
              rating, review, key_lessons, favourite_quote, tags))


def update_book(book_id: int, **fields):
    """Update book dynamically."""
    if not fields:
        return
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        query = sql.SQL("UPDATE books SET {} WHERE id = %s").format(
            sql.SQL(", ").join(
                sql.Identifier(k) + sql.SQL("= %s") for k in fields
            )
        )
        
        values = list(fields.values()) + [book_id]
        cur.execute(query, values)


def get_books(status_filter=None):
    """Get books filtered by status."""
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        if status_filter:
            cur.execute("""
                SELECT * FROM books WHERE status = %s ORDER BY id;
            """, (status_filter,))
        else:
            cur.execute("SELECT * FROM books ORDER BY id;")
        
        return cur.fetchall()


def get_book(book_id: int):
    """Get single book by ID."""
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        cur.execute("SELECT * FROM books WHERE id = %s;", (book_id,))
        row = cur.fetchone()
        
        return dict(row) if row else None


def search_books(query: str):
    """Search books by title, author, or discipline."""
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # 💡 LIKE with wildcards for text search
        # || is string concatenation in PostgreSQL
        search_term = f"%{query}%"
        
        cur.execute("""
            SELECT * FROM books 
            WHERE title ILIKE %s 
               OR author ILIKE %s 
               OR discipline ILIKE %s 
               OR tags ILIKE %s
            ORDER BY id;
        """, (search_term, search_term, search_term, search_term))
        
        return cur.fetchall()


def get_books_stats():
    """Get book library statistics."""
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        cur.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status='Completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status='Inprogress' THEN 1 ELSE 0 END) as inprogress,
                SUM(CASE WHEN status='Yet To Start' THEN 1 ELSE 0 END) as yet_to_start,
                SUM(CASE WHEN status='On Hold' THEN 1 ELSE 0 END) as on_hold
            FROM books;
        """)
        
        row = cur.fetchone()
        return dict(row) if row else {}


# ─────────────────────────────────────────────────────────────────────────────
# IDEAS & APPLICATIONS
# ─────────────────────────────────────────────────────────────────────────────

def capture_idea(book_id: int = None, habit_id: int = None, title: str = "",
                 description: str = "", chapter_section: str = ""):
    """Capture an idea from a book or habit."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO ideas(book_id, habit_id, title, description, chapter_section, status)
            VALUES(%s, %s, %s, %s, %s, 'captured')
            RETURNING id;
        """, (book_id, habit_id, title, description, chapter_section))
        
        idea_id = cur.fetchone()[0]
        return idea_id


def get_book_ideas(book_id: int):
    """Get all ideas from a book."""
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        cur.execute("""
            SELECT * FROM ideas WHERE book_id = %s ORDER BY captured_date DESC;
        """, (book_id,))
        
        return cur.fetchall()


def get_idea_applications(idea_id: int):
    """Get all applications of an idea."""
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        cur.execute("""
            SELECT * FROM applications 
            WHERE idea_id = %s 
            ORDER BY application_date DESC;
        """, (idea_id,))
        
        return cur.fetchall()


def apply_idea(idea_id: int, project_name: str, description: str = "", impact: str = ""):
    """Link an idea to a project/application."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO applications(idea_id, project_name, description, impact)
            VALUES(%s, %s, %s, %s);
        """, (idea_id, project_name, description, impact))
        
        # Mark idea as applied
        cur.execute("""
            UPDATE ideas SET status = 'applied', applied_date = NOW()
            WHERE id = %s;
        """, (idea_id,))


# ─────────────────────────────────────────────────────────────────────────────
# SQL QUERY EDITOR (Learn Raw SQL!)
# ─────────────────────────────────────────────────────────────────────────────

def execute_query(sql_query: str):
    """
    Execute a raw SQL query (for Query Editor page).
    
    💡 LEARNING OPPORTUNITY:
    Use this to write and test your own PostgreSQL queries!
    Great for learning advanced SQL features.
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            
            if sql_query.strip().upper().startswith("SELECT"):
                cur.execute(sql_query)
                rows = cur.fetchall()
                return {
                    "success": True,
                    "data": [dict(row) for row in rows],
                    "count": len(rows)
                }
            else:
                cur.execute(sql_query)
                return {
                    "success": True,
                    "data": None,
                    "count": cur.rowcount
                }
    except Exception as e:
        return {"success": False, "error": str(e), "count": 0}


def get_table_schema():
    """
    Get schema information for all tables.
    
    💡 INTROSPECTION:
    This queries PostgreSQL's information_schema
    to see table structure without looking at the code!
    """
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        # 💡 information_schema.tables is a special PostgreSQL system table
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = [row['table_name'] for row in cur.fetchall()]
        
        schema = {}
        for table in tables:
            # 💡 information_schema.columns describes each column
            cur.execute("""
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                ORDER BY ordinal_position;
            """, (table,))
            
            schema[table] = [
                {
                    "name": row['column_name'],
                    "type": row['data_type'],
                    "nullable": row['is_nullable'] == 'YES',
                    "default": row['column_default']
                }
                for row in cur.fetchall()
            ]
        
        return schema


# ─────────────────────────────────────────────────────────────────────────────
# INITIALIZATION ON APP START
# ─────────────────────────────────────────────────────────────────────────────

# This is called when the app starts
# Initialize connection pool and create tables
try:
    init_connection_pool()
    init_db()
except Exception as e:
    print(f"❌ Database initialization failed: {e}")
    print("Check your PostgreSQL connection and DATABASE_URL environment variable")
