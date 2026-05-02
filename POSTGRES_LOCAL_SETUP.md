# PostgreSQL Local Installation Guide for Windows
## Setup Complete PostgreSQL in 10 Minutes

You don't have Docker, but that's fine! Installing PostgreSQL locally is straightforward and better for learning because you'll see how it works.

---

## 🚀 Step 1: Download PostgreSQL 15

**Go to:** https://www.postgresql.org/download/windows/

**Or direct link:** https://sbp.enterprisedb.com/getfile.jsp?fileid=1258453

Click "Download the installer" and save the .exe file.

---

## 📦 Step 2: Run the PostgreSQL Installer

1. Open the downloaded `.exe` file
2. Click **Next** to start installation
3. Keep default installation directory: `C:\Program Files\PostgreSQL\15`
4. When prompted for **password**, enter:
   ```
   postgres_password_123
   ```
   ⚠️ **IMPORTANT:** Write this down! You'll need it later.
   
5. Port: Keep as **5432** (default)
6. Locale: Keep as **[Default locale]**
7. Click **Next** → **Next** → **Install**
8. At the end, **uncheck** "Stack Builder" and click **Finish**

**Installation takes:** 2-3 minutes

---

## ✅ Step 3: Verify PostgreSQL is Running

Open PowerShell and run:

```powershell
psql -U postgres -h localhost -c "SELECT version();"
```

You'll be prompted for the password you set. Enter:
```
postgres_password_123
```

**Expected output:**
```
PostgreSQL 15.x (Windows)
```

If you see this, PostgreSQL is running! ✅

---

## 📝 Step 4: Create the `habits_tracker` Database

In the same PowerShell terminal, run:

```powershell
psql -U postgres -h localhost -c "CREATE DATABASE habits_tracker;"
```

Enter the password again: `postgres_password_123`

**Expected output:** (no error means success)

---

## 🧪 Step 5: Verify Database Created

```powershell
psql -U postgres -h localhost -l
```

You should see `habits_tracker` in the list.

---

## 🎯 Step 6: Update Your App

In PowerShell, navigate to your app folder:

```powershell
cd c:\Users\bnbal\OneDrive\Documents\Habits_Tracker\tracker_app
```

Activate virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Set environment variable (do this every session):

```powershell
$env:DATABASE_URL="postgresql://postgres:postgres_password_123@localhost:5432/habits_tracker"
```

---

## 🌱 Step 7: Populate Database with Sample Data

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

If you see this, your database is populated! ✅

---

## 🎨 Step 8: Start Your App

```powershell
streamlit run app.py
```

The app should open automatically at `http://localhost:8501`

If not, open your browser and go to that address.

---

## ✨ Step 9: Verify Everything Works

Click through each page in your app:

| Page | Check |
|------|-------|
| **Dashboard** | See habit cards with data |
| **Daily Habits** | See all your habits |
| **Log a Habit** | Click a button and verify it saves |
| **Reading Stack** | See your 103 books |
| **Analytics** | Charts display correctly |
| **Query Editor** | Can run SQL queries |

---

## 📊 You're Done! 🎉

Your Habits Tracker is now running on PostgreSQL!

### Quick Summary
```
PostgreSQL Server: Running ✅
Database: habits_tracker ✅
Sample Data: 13 habits + 103 books ✅
App: Running at http://localhost:8501 ✅
```

---

## 🎓 Next: Start Learning SQL

Go to the **Query Editor** page in your app and try these queries:

```sql
-- See all your habits
SELECT name, action_type, status FROM habits;

-- See today's logs
SELECT h.name, hl.value FROM habit_log hl
JOIN habits h ON hl.habit_id = h.id
WHERE hl.log_date = CURRENT_DATE;

-- See most logged habit
SELECT h.name, COUNT(*) as count 
FROM habit_log hl
JOIN habits h ON hl.habit_id = h.id
GROUP BY h.name
ORDER BY count DESC LIMIT 1;
```

More queries available in: `SQL_LEARNING_GUIDE.md`

---

## 🔧 Troubleshooting

### "psql: command not found"
PostgreSQL wasn't added to PATH. Try:
```powershell
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -h localhost
```

### "password authentication failed"
The password is wrong or you didn't enter it at the prompt.
Try again with: `postgres_password_123`

### "could not connect to server"
PostgreSQL service isn't running.
- Windows Services → Find PostgreSQL → Right-click → Start

### "database does not exist"
Run: `python seed_data.py` again

---

## 📞 Quick Commands Reference

```powershell
# Test PostgreSQL connection
psql -U postgres -h localhost -c "SELECT version();"

# List all databases
psql -U postgres -h localhost -l

# Connect to habits_tracker database
psql -U postgres -h localhost -d habits_tracker

# View all tables
psql -U postgres -h localhost -d habits_tracker -c "\dt"

# Run a SQL query
psql -U postgres -h localhost -d habits_tracker -c "SELECT * FROM habits;"

# Backup database
pg_dump -U postgres habits_tracker > backup.sql

# Restore database
psql -U postgres habits_tracker < backup.sql
```

---

## 💾 Making It Permanent (Set Database Path)

To avoid setting `DATABASE_URL` every time:

1. Right-click **This PC** → **Properties**
2. Click **Advanced system settings**
3. Click **Environment Variables** button
4. Click **New** under "System variables"
5. Variable name: `DATABASE_URL`
6. Variable value: `postgresql://postgres:postgres_password_123@localhost:5432/habits_tracker`
7. Click **OK** three times
8. **Restart PowerShell** for changes to take effect

Then you can just run:
```powershell
streamlit run app.py
```

Without setting `$env:DATABASE_URL` first.

---

## 🎓 Learning Resources

Read these in order:

1. **START_HERE.md** - Quick overview (5 min)
2. **database_postgres.py** - Read the code comments (30 min)
3. **SQL_LEARNING_GUIDE.md** - Try the 20 queries (2 hours)
4. **POSTGRES_MIGRATION.md** - 4-week learning path (ongoing)

---

## ✅ Success Checklist

After completing all steps:
- [x] PostgreSQL installed and running
- [x] `habits_tracker` database created
- [x] Database populated with seed data
- [x] App starts without errors
- [x] Can see data in Streamlit
- [x] Can run SQL queries in Query Editor
- [x] DATABASE_URL set (temporary or permanent)

---

**You're all set!** 🚀 Your app is running on PostgreSQL!

Now start exploring SQL queries in the Query Editor page to learn PostgreSQL hands-on! 📚
