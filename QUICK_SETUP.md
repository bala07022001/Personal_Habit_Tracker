# ⚡ PostgreSQL Setup - Quick Reference Card

Print this or pin it to your terminal! 

---

## 🚀 DO THIS NOW (5 STEPS)

### Step 1️⃣: Download PostgreSQL
```
Go to: https://www.postgresql.org/download/windows/
Click: Download the installer (.exe)
```

### Step 2️⃣: Run Installer
```
Double-click the .exe file you downloaded
When asked for PASSWORD, type: postgres_password_123
Keep EVERYTHING ELSE as default
Click through and Finish
```

### Step 3️⃣: Test It Works
```powershell
psql -U postgres -h localhost -c "SELECT version();"
# When asked for password: postgres_password_123
# Should show: PostgreSQL 15.x
```

### Step 4️⃣: Create Database
```powershell
psql -U postgres -h localhost -c "CREATE DATABASE habits_tracker;"
```

### Step 5️⃣: Populate & Run App
```powershell
cd c:\Users\bnbal\OneDrive\Documents\Habits_Tracker\tracker_app
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL="postgresql://postgres:postgres_password_123@localhost:5432/habits_tracker"
python seed_data.py
streamlit run app.py
```

**Open:** http://localhost:8501

---

## ✅ Done!

Your Habits Tracker is running on PostgreSQL! 🎉

---

## 📞 If Something Goes Wrong

| Problem | Solution |
|---------|----------|
| "psql: command not found" | Use full path: `"C:\Program Files\PostgreSQL\15\bin\psql.exe"` |
| "password authentication failed" | Password is: `postgres_password_123` |
| "could not connect" | Restart your computer or check Windows Services |
| "database does not exist" | Run: `python seed_data.py` again |

---

## 💡 Pro Tips

**Set permanent connection (no typing each session):**
1. Search: "Edit environment variables"
2. New variable: `DATABASE_URL`
3. Value: `postgresql://postgres:postgres_password_123@localhost:5432/habits_tracker`
4. Restart PowerShell

**Then just run:**
```powershell
streamlit run app.py
```

---

**Detailed guide:** See POSTGRES_LOCAL_SETUP.md
