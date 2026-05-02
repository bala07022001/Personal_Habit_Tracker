# Migration Guide: SQLite → PostgreSQL

## 🎯 Quick Start (5 minutes to running)

### Step 1: Install PostgreSQL
Choose ONE approach:

#### Option A: Docker (Easiest - recommended for learning)
```powershell
# Make sure Docker is installed
# Then run:
docker-compose -f postgres-compose.yml up -d

# To check it's running:
docker ps
# Should show: habits_tracker_db container

# To stop:
docker-compose -f postgres-compose.yml down
```

#### Option B: Local Installation
1. Download PostgreSQL 15: https://www.postgresql.org/download/windows/
2. Run installer with default settings
3. Remember your superuser password!

### Step 2: Verify Connection
```powershell
# Test connection (replace password with your actual password)
psql -U postgres -h localhost -c "SELECT version();"

# Or use DBeaver GUI (more user-friendly for learning)
# Download: https://dbeaver.io/download/
```

### Step 3: Create Database
```powershell
# Option A: Using psql
psql -U postgres -h localhost -c "CREATE DATABASE habits_tracker;"

# Option B: Using DBeaver
# - New Database Connection
# - Server: localhost, Port: 5432, User: postgres
# - Right-click in connections → Create Database
```

### Step 4: Update App Code

#### 4a. Install PostgreSQL adapter
```powershell
cd c:\Users\bnbal\OneDrive\Documents\Habits_Tracker\tracker_app
.\.venv\Scripts\pip.exe install psycopg2-binary
```

#### 4b. Update app.py to use PostgreSQL
Edit `app.py` and change this line (near the top):
```python
# OLD (SQLite):
# import database as db

# NEW (PostgreSQL):
import database_postgres as db
```

#### 4c. Set environment variable (optional, uses default if not set)
```powershell
# In PowerShell (for current session only):
$env:DATABASE_URL="postgresql://postgres:postgres_password_123@localhost:5432/habits_tracker"

# Or set permanently in Windows:
# System Properties → Environment Variables → New
# Name: DATABASE_URL
# Value: postgresql://postgres:postgres_password_123@localhost:5432/habits_tracker
```

### Step 5: Run App
```powershell
cd c:\Users\bnbal\OneDrive\Documents\Habits_Tracker\tracker_app
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

**That's it!** Your app now uses PostgreSQL! 🎉

---

## 📚 Learning Path: PostgreSQL Concepts

### Week 1: Fundamentals
- [ ] Connection and authentication (done!)
- [ ] Creating databases and tables
- [ ] Data types (TEXT, INTEGER, DATE, TIMESTAMP)
- [ ] INSERT, SELECT, UPDATE, DELETE basics
- [ ] WHERE clauses and filtering

**Try these queries in DBeaver:**
```sql
-- See all tables
SELECT * FROM information_schema.tables 
WHERE table_schema = 'public';

-- See all habits
SELECT * FROM habits;

-- See habits created in last 7 days
SELECT * FROM habits 
WHERE created_at > NOW() - INTERVAL '7 days';

-- Count habits by status
SELECT status, COUNT(*) 
FROM habits 
GROUP BY status;
```

### Week 2: Relationships & Constraints
- [ ] PRIMARY KEY (unique identifier)
- [ ] FOREIGN KEY (linking tables)
- [ ] CASCADE (automatic cleanup)
- [ ] UNIQUE constraints
- [ ] NOT NULL constraints

**Try these queries:**
```sql
-- See how habit_log references habits
SELECT hl.*, h.name 
FROM habit_log hl
JOIN habits h ON hl.habit_id = h.id;

-- Try deleting a habit and watch its logs disappear too
-- (Because of ON DELETE CASCADE!)
DELETE FROM habits WHERE id = 999;  -- Won't work if habit exists with logs
```

### Week 3: Advanced Queries
- [ ] Aggregation (COUNT, SUM, AVG, GROUP BY)
- [ ] Joins (INNER, LEFT, RIGHT)
- [ ] Window functions (OVER clause)
- [ ] Common Table Expressions (WITH)
- [ ] Subqueries

**Try these queries:**
```sql
-- Habits with most logs
SELECT h.name, COUNT(hl.id) as log_count
FROM habits h
LEFT JOIN habit_log hl ON h.id = hl.habit_id
GROUP BY h.id, h.name
ORDER BY log_count DESC;

-- Daily average for each habit
SELECT 
    h.name,
    AVG(hl.value) as daily_average,
    SUM(hl.value) as total
FROM habits h
LEFT JOIN habit_log hl ON h.id = hl.habit_id
WHERE hl.log_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY h.id, h.name;
```

### Week 4: Performance & Best Practices
- [ ] Indexes (speed up queries)
- [ ] EXPLAIN (see query plans)
- [ ] Transactions (ACID properties)
- [ ] Connection pooling (already done!)
- [ ] Backups and recovery

**Try these:**
```sql
-- See how a query is executed
EXPLAIN SELECT * FROM habit_log WHERE log_date > '2026-01-01';

-- Better version with index:
EXPLAIN SELECT * FROM habit_log 
WHERE log_date > '2026-01-01' 
AND habit_id = 5;
```

---

## 🔧 Troubleshooting

### "connection refused"
```powershell
# PostgreSQL not running?

# Docker version:
docker-compose -f postgres-compose.yml up -d

# Local install: Start PostgreSQL service
# Windows Services → PostgreSQL → Start

# Check status:
psql -U postgres -h localhost -c "SELECT 1;"
```

### "password authentication failed"
```powershell
# Wrong password? Default after install is usually blank or "postgres"
# Try:
psql -U postgres -h localhost  # Will prompt for password
```

### "database does not exist"
```powershell
# Create it:
psql -U postgres -h localhost -c "CREATE DATABASE habits_tracker;"

# Verify:
psql -U postgres -h localhost -l  # Lists all databases
```

### "psql: command not found"
```powershell
# PostgreSQL not in PATH. Add it:
# Set PATH to include: C:\Program Files\PostgreSQL\15\bin
# Or use full path:
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
```

---

## 🎓 Resources for Deep Learning

### PostgreSQL Documentation
- Official Docs: https://www.postgresql.org/docs/current/
- Interactive Tutorial: https://www.postgresql.org/docs/current/tutorial.html

### Practice Platforms
- PGExercises: https://www.pgexercises.com/ (highly recommended!)
- Mode Analytics SQL Tutorial: https://mode.com/sql-tutorial/
- LeetCode SQL (has PostgreSQL): https://leetcode.com/problemset/database/

### Tools for Learning
- DBeaver: GUI database tool (free, powerful)
- pgAdmin: Web-based PostgreSQL admin
- VS Code Extension: PostgreSQL Explorer

### YouTube Channels
- freeCodeCamp PostgreSQL Course
- PostgreSQL Official Channel
- Database Design Channel

---

## 🚀 Next Steps

After migrating to PostgreSQL:

1. **Explore the Query Editor page** in your app
   - Try writing SQL queries
   - See schema in real-time
   - Learn by doing!

2. **Optimize with indexes**
   - Identify slow queries with EXPLAIN
   - Add indexes to speed them up

3. **Set up backups**
   ```powershell
   pg_dump -U postgres habits_tracker > backup.sql
   ```

4. **Learn about roles and permissions**
   - Create specific users for app vs. admin
   - Grant minimal required permissions

5. **Explore advanced features**
   - JSON/JSONB for flexible data
   - Full-text search
   - Triggers for automation

---

## ✅ Verification Checklist

- [ ] PostgreSQL installed and running
- [ ] Created `habits_tracker` database
- [ ] Installed `psycopg2-binary`
- [ ] Updated app.py to import `database_postgres`
- [ ] Set DATABASE_URL (or using default)
- [ ] App starts without errors
- [ ] Can view data in Streamlit app
- [ ] Can see schema in Query Editor page
- [ ] Tried writing your own SQL queries

**Congratulations!** You now have a production-ready PostgreSQL setup! 🎉
