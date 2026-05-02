# PostgreSQL Integration Guide
# Follow these steps to switch your app from SQLite to PostgreSQL

## ✅ Pre-Flight Checklist
Before starting, make sure you have:
- [ ] PostgreSQL running (Docker or local)
- [ ] Created `habits_tracker` database
- [ ] Installed psycopg2-binary
- [ ] All Python files in your workspace
- [ ] Terminal open in your project directory

---

## 🚀 Step 1: Install Dependencies

### Check current environment
```powershell
cd c:\Users\bnbal\OneDrive\Documents\Habits_Tracker\tracker_app

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Check what's installed
pip list | Select-String -Pattern "psycopg2|postgres"
```

### Install PostgreSQL adapter
```powershell
pip install psycopg2-binary==2.9.9
```

### Verify installation
```powershell
python -c "import psycopg2; print('✅ psycopg2 installed successfully!')"
```

---

## 🌍 Step 2: Set Up Environment Variable

### Option A: Temporary (current session only)
```powershell
$env:DATABASE_URL="postgresql://postgres:postgres_password_123@localhost:5432/habits_tracker"
```

### Option B: Permanent (Windows system-wide)
1. Right-click "This PC" or "My Computer" → Properties
2. Advanced system settings → Environment Variables
3. Click "New" under System variables
4. Variable name: `DATABASE_URL`
5. Variable value: `postgresql://postgres:postgres_password_123@localhost:5432/habits_tracker`
6. Click OK and restart terminal

### Verify it's set
```powershell
echo $env:DATABASE_URL
# Should output: postgresql://postgres:...
```

---

## 📝 Step 3: Update app.py

### Method 1: Using Text Editor
1. Open app.py in VS Code
2. Find the line: `import database as db` (around line 2-5)
3. Replace with: `import database_postgres as db`
4. Save file (Ctrl+S)

### Method 2: Using PowerShell (automated)
```powershell
# Backup original first
Copy-Item app.py app.py.backup

# Replace import statement
(Get-Content app.py) -replace 'import database as db', 'import database_postgres as db' | Set-Content app.py

# Verify change
Select-String -Path app.py -Pattern "import database" | Head -5
```

---

## 📚 Step 4: Update seed_data.py (if using)

If you want to reinitialize with fresh data:

### Edit seed_data.py
Find the line: `import database as db`
Replace with: `import database_postgres as db`

### Run seed data
```powershell
python seed_data.py
```

**Expected output:**
```
✅ Database initialized successfully!
✅ Created habit: Morning Meditation (ID: 1)
✅ Created habit: Exercise (ID: 2)
...
✅ Added 103 books to database
```

---

## 🧪 Step 5: Test Connection

### Quick connection test
```powershell
python -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres_password_123@localhost:5432/habits_tracker'
import database_postgres as db
db.init_connection_pool()
db.init_db()
print('✅ PostgreSQL connection successful!')
"
```

### Run seed data to populate
```powershell
python seed_data.py
```

---

## 🎨 Step 6: Start the App

### Launch Streamlit
```powershell
streamlit run app.py
```

### Expected startup
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### In your browser
1. Go to http://localhost:8501
2. You should see your Habits Tracker dashboard
3. All data should be there from seed_data or previous sessions

---

## ✨ Step 7: Verify Everything Works

### On Dashboard page
- [ ] See habit cards
- [ ] See recent logs
- [ ] See completion metrics

### On Daily Habits page
- [ ] See all active habits
- [ ] Can log a habit (click a button/input)
- [ ] Can edit targets
- [ ] Progress bars update

### On Reading Stack page
- [ ] See books
- [ ] Can add rating
- [ ] Can capture ideas
- [ ] Ideas display correctly

### On Analytics page
- [ ] Charts render without errors
- [ ] Data looks reasonable

### On Query Editor page
- [ ] Can run SELECT queries
- [ ] Can see schema
- [ ] Can try example queries from SQL_LEARNING_GUIDE.md

---

## 🔧 Troubleshooting

### Error: "connection refused"
```
Problem: Can't connect to PostgreSQL
Solution:
1. Check PostgreSQL is running:
   docker ps  # If using Docker
   Services.msc  # If local install
2. Check DATABASE_URL is set:
   echo $env:DATABASE_URL
3. Restart terminal after setting DATABASE_URL
```

### Error: "column does not exist"
```
Problem: Table schema mismatch
Solution:
1. Delete old database: DROP DATABASE habits_tracker;
2. Recreate: CREATE DATABASE habits_tracker;
3. Run seed_data.py to reinitialize
```

### Error: "UNIQUE constraint violated"
```
Problem: Duplicate entry (usually when reinitializing)
Solution:
DROP DATABASE habits_tracker;
CREATE DATABASE habits_tracker;
python seed_data.py
```

### Error: "psycopg2 module not found"
```
Solution: pip install psycopg2-binary
```

### Error: "could not translate host name"
```
Problem: DATABASE_URL host is wrong
Check: Your CONNECTION_URL has correct hostname
localhost = local machine
127.0.0.1 = loopback address
hostname:5432 = remote server
```

---

## 📊 Verification Queries

Run these in Query Editor to verify setup:

### Check all tables exist
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```
**Expected output:** habits, habit_log, habit_versions, journal, books, reading_log, ideas, applications

### Check data exists
```sql
SELECT 'habits' as table_name, COUNT(*) as count FROM habits
UNION
SELECT 'habit_log', COUNT(*) FROM habit_log
UNION
SELECT 'books', COUNT(*) FROM books
UNION
SELECT 'ideas', COUNT(*) FROM ideas
ORDER BY table_name;
```
**Expected:** All counts > 0 if seed_data.py was run

### Check today's logging works
```sql
INSERT INTO habit_log(habit_id, log_date, value, note)
VALUES(1, CURRENT_DATE, 1.0, 'Test log from PostgreSQL')
RETURNING id;
```
**Expected:** Returns new ID (e.g., 1234)

---

## 🎓 Learning Resources

### Try These SQL Queries
Open Query Editor page and copy/paste from SQL_LEARNING_GUIDE.md

### Important Files to Read
1. POSTGRES_MIGRATION.md - detailed setup guide
2. database_postgres.py - read comments to learn concepts
3. SQL_LEARNING_GUIDE.md - hands-on SQL exercises

### Next Steps
1. Run 5 queries from SQL_LEARNING_GUIDE.md
2. Write your own query to answer: "What's my top habit?"
3. Try using EXPLAIN to see query performance
4. Read database_postgres.py code with comments

---

## 🐛 Rollback Plan (Back to SQLite)

If something goes wrong, you can revert:

### Restore from backup
```powershell
# If you created one
Copy-Item app.py.backup app.py

# Then restart:
streamlit run app.py
```

### Or manually
Edit app.py and change:
```python
# FROM:
import database_postgres as db

# TO:
import database as db
```

---

## ✅ Success Checklist

After completing all steps:
- [ ] DATABASE_URL environment variable is set
- [ ] psycopg2-binary is installed (pip list shows it)
- [ ] app.py imports database_postgres
- [ ] seed_data.py initialized (or manually populated)
- [ ] Streamlit app starts without errors
- [ ] Can view data in dashboard
- [ ] Can log new habits
- [ ] Can query in Query Editor page
- [ ] SQL_LEARNING_GUIDE queries run successfully

**🎉 Congratulations!** You're now running a production PostgreSQL database!

---

## 📞 Quick Commands Reference

```powershell
# Check PostgreSQL status
docker ps  # If using Docker

# Connect to database
psql -U postgres -h localhost -d habits_tracker

# Backup database
pg_dump -U postgres habits_tracker > backup.sql

# Restore database
psql -U postgres habits_tracker < backup.sql

# Start app
cd c:\Users\bnbal\OneDrive\Documents\Habits_Tracker\tracker_app
.\.venv\Scripts\Activate.ps1
streamlit run app.py

# Stop app
# Ctrl+C in terminal
```

---

## 🚀 Performance Tips

### Monitor slow queries
```sql
-- See slow queries
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;
```

### Add indexes for common queries
```sql
-- Already created in init_db(), but you can add more:
CREATE INDEX idx_habit_log_date ON habit_log(log_date);
CREATE INDEX idx_book_status ON books(status);
```

### Use EXPLAIN to optimize
```sql
-- See query plan
EXPLAIN SELECT * FROM habit_log WHERE log_date > '2026-01-01';

-- See actual execution
EXPLAIN ANALYZE SELECT * FROM habit_log WHERE log_date > '2026-01-01';
```

---

**Need help?** Check the troubleshooting section or read the other markdown files!
