# Personal Habit & Reading Tracker

A full-featured personal tracker app built with Streamlit + local SQLite database.

## Features
- **Daily Habit Tracking** — Log 13 custom habits, see streaks, 7-day overview grid
- **Expert Journalling** — Mood, Gratitude, Wins, full reflection entry per day
- **Reading Stack** — 100+ books with status, review, key lessons, quotes, ratings
- **Book Detail** — Edit review/notes per book, log reading sessions
- **Analytics** — Habit heatmap, completion % over time, books by discipline/year
- **🔍 SQL Query Editor** — Direct database access to CREATE, READ, UPDATE, DELETE data
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

Your app will open at `http://localhost:8501`

**Database location:** `tracker_app/tracker.db` (SQLite file on your computer)

---

## Using the Query Editor

Go to **🔍 Query Editor** to run custom SQL directly:

**View all habits:**
```sql
SELECT * FROM habits WHERE is_active = 1;
```

**Get today's habit log:**
```sql
SELECT h.name, COALESCE(hl.done, 0) as done
FROM habits h
LEFT JOIN habit_log hl ON h.id = hl.habit_id AND hl.log_date = date('now')
WHERE h.is_active = 1;
```

**Find all completed books:**
```sql
SELECT * FROM books WHERE status = 'Completed';
```

**Add a new habit (INSERT):**
```sql
INSERT INTO habits (name, category) VALUES ('Meditation', 'Wellness');
```

**Update book status (UPDATE):**
```sql
UPDATE books SET status = 'Completed' WHERE title = 'Atomic Habits';
```

**Delete old entries (DELETE):**
```sql
DELETE FROM habit_log WHERE log_date < date('now', '-1 year');
```

---

## Database Structure

| Table | Purpose |
|-------|---------|
| `habits` | Your habit definitions + active status |
| `habit_log` | Daily logs (done/missed + notes) |
| `journal` | Daily journal entries with mood |
| `books` | Your book library |
| `reading_log` | Reading sessions (pages read + notes) |

---

## Project Structure

```
tracker_app/
├── app.py                        # Main Streamlit application
├── database.py                   # SQLite persistence + Query Editor API
├── seed_data.py                  # One-time data seeder (habits + books)
├── requirements.txt
├── .gitignore
├── README.md
├── .streamlit/
│   ├── config.toml               # Theme + server settings
│   └── secrets.toml              # Empty (local mode)
└── tracker.db                    # SQLite database (auto-created, your data)
```

---

## Customization

- **Edit dark theme:** Modify colors in `.streamlit/config.toml`
- **Add more habits:** Use Query Editor or Settings → Add Habit
- **Backup data:** Copy `tracker.db` to another folder
- **Export data:** Use Query Editor to SELECT data and download as CSV


