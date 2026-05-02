# PostgreSQL Setup Guide - Hands-On Learning

## 🎯 What You'll Learn
- Installing PostgreSQL locally
- Creating databases and tables
- Understanding relational constraints
- Working with transactions
- Connection pooling
- JSON/JSONB data types
- Window functions
- Common Table Expressions (CTEs)

## 1️⃣ Installation

### Option A: Windows (Recommended for beginners)
```powershell
# Download PostgreSQL 15 from:
# https://www.postgresql.org/download/windows/

# Run installer, accept defaults
# When prompted for password, use something like: postgres_password_123
# Keep port as 5432 (default)
# Stack Builder: Skip unless you want additional tools

# Verify installation
psql --version
```

### Option B: Docker (More advanced, but cleaner)
```powershell
# Make sure you have Docker installed
# https://www.docker.com/products/docker-desktop

# Create docker-compose.yml file and run:
docker-compose -f postgres-compose.yml up -d

# Stop later with:
docker-compose -f postgres-compose.yml down
```

## 2️⃣ Connect to PostgreSQL

### Using psql (Command Line)
```powershell
# Connect as superuser
psql -U postgres -h localhost

# Create new database
CREATE DATABASE habits_tracker;

# Connect to it
\c habits_tracker

# See all tables
\dt

# Exit
\q
```

### Using DBeaver (GUI - Recommended for learning)
1. Download: https://dbeaver.io/download/
2. New Database Connection → PostgreSQL
3. Hostname: localhost
4. Port: 5432
5. Database: postgres
6. Username: postgres
7. Password: (what you set during install)
8. Test connection
9. Click "SQL Editor" to write queries

## 3️⃣ Key PostgreSQL Concepts

### Connection String Format
```
postgresql://username:password@localhost:5432/database_name

Example:
postgresql://postgres:password@localhost:5432/habits_tracker
```

### Data Types (vs SQLite)
```sql
-- TEXT (no length limit, like SQLite TEXT)
-- INTEGER (like SQLite INTEGER)
-- REAL (like SQLite REAL)
-- DATE (stored as date only)
-- TIMESTAMP (date + time, with timezone option)
-- BOOLEAN (true/false, SQLite uses 0/1)
-- SERIAL/BIGSERIAL (auto-incrementing integers)
-- JSON/JSONB (SQLite doesn't have native JSON support!)
```

### Transactions
```sql
BEGIN;  -- Start transaction
-- Run multiple queries
COMMIT; -- All succeed together
-- Or ROLLBACK if something goes wrong
```

### Foreign Keys with Cascading
```sql
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL
);

CREATE TABLE reading_log (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    pages_read INTEGER
);
-- If you delete a book, all reading_logs for that book are deleted too!
```

### Common Table Expressions (CTEs)
```sql
-- Use WITH to create temporary named result sets
WITH dates AS (
    SELECT CURRENT_DATE - i AS log_date
    FROM generate_series(0, 30) AS i
)
SELECT * FROM dates;
```

## 4️⃣ Performance Tips

### Indexes (Speed up queries)
```sql
-- Without index: PostgreSQL scans every row
CREATE INDEX idx_habit_log_date ON habit_log(log_date);

-- Now queries with WHERE log_date > ... are FAST
SELECT * FROM habit_log WHERE log_date > '2026-01-01';
```

### EXPLAIN (See how PostgreSQL executes queries)
```sql
EXPLAIN SELECT * FROM habits WHERE status = 'active';
-- Shows execution plan - helps identify slow queries
```

## 5️⃣ PostgreSQL vs SQLite

| Feature | SQLite | PostgreSQL |
|---------|--------|-----------|
| **Setup** | Just a file | Separate server |
| **Users** | Single user | Multiple users |
| **Performance** | Good for <1GB | Excellent for large datasets |
| **JSON** | Requires extension | Native JSONB |
| **Transactions** | Basic | Advanced (MVCC) |
| **Learning** | Simple | Industry standard |
| **Deployment** | Embedded | Server-based |

## 6️⃣ Next Steps in This Project

1. Create PostgreSQL database with migrations
2. Update Python code to use `psycopg2` driver
3. Use `sqlalchemy` ORM for cleaner code (optional)
4. Write raw SQL for learning queries
5. Optimize with indexes based on usage patterns

## 7️⃣ Resources

- Official Docs: https://www.postgresql.org/docs/
- Interactive Tutorial: https://www.postgresql.org/docs/current/tutorial.html
- DBeaver Tutorial: https://dbeaver.io/docs/
- SQL Practice: https://www.pgexercises.com/

---

**Ready? Let's create the database schema next!**
