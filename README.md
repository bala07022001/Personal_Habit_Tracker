# Personal Habit & Reading Tracker

A full-featured personal tracker app built with Streamlit + SQLite (local) / PostgreSQL (cloud).

## Features
- **Daily Habit Tracking** — Log 13 custom habits, see streaks, 7-day overview grid
- **Expert Journalling** — Mood, Gratitude, Wins, full reflection entry per day
- **Reading Stack** — 100+ books with status, review, key lessons, quotes, ratings
- **Book Detail** — Edit review/notes per book, log reading sessions
- **Analytics** — Habit heatmap, completion % over time, books by discipline/year
- **Dark theme** with clean card UI

---

## Local Setup

```bash
cd tracker_app
pip install -r requirements.txt

# Seed your data (run once)
python seed_data.py

# Launch the app
streamlit run app.py
```

---

## Deploy to Streamlit Community Cloud (free, mobile-accessible)

> GitHub Pages only serves static sites — for a Python/Streamlit app use **Streamlit Community Cloud**.

### Step 1 — Free Supabase database
1. Go to [supabase.com](https://supabase.com) → **New project**
2. After creation: **Project Settings → Database → Connection string → URI**
3. Copy the URI (it looks like `postgresql://postgres.[ref]:[password]@...`)

### Step 2 — Push to GitHub
```bash
# Inside tracker_app/
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

### Step 3 — Deploy on Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
2. Connect your GitHub repo, set **Main file** = `app.py`
3. In **Advanced settings → Secrets**, paste:
   ```toml
   DATABASE_URL = "postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres"
   ```
4. Click **Deploy** — your app will be live at a public URL you can bookmark on mobile

### Step 4 — Seed cloud database (once)
After first deploy, in the Streamlit Cloud terminal (or locally with `DATABASE_URL` set):
```bash
DATABASE_URL="your-url-here" python seed_data.py
```

---

## Structure
```
tracker_app/
├── app.py                        # Main Streamlit application
├── database.py                   # SQLite (local) / PostgreSQL (cloud) layer
├── seed_data.py                  # One-time data seeder (habits + books)
├── requirements.txt
├── .gitignore
├── .streamlit/
│   ├── config.toml               # Theme + server settings
│   ├── secrets.toml              # Your DB URL — NOT committed (gitignored)
│   └── secrets.toml.example      # Template to copy from
└── tracker.db                    # Auto-created local SQLite DB (gitignored)
```

