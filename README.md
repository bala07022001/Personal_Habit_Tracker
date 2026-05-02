# Personal Habit & Reading Tracker

A **flow-based habit tracker** that evolves with you. Track dynamic, action-oriented habits with real metrics—hours spent, pages read, goals achieved. Your habits aren't fixed; they evolve as you complete them.

## 🎯 Key Concepts

**Action-Based Habits:** Instead of "Gym," track "Spend 1 hour in gym/walking" with actual duration logged.

**Flow Thinking:** Habits are fluid. When you master a mental model habit by February, evolve it—now you're tracking "Read collected mental models" with pages logged.

**Wisdom Wellbeing:** Motivating, energizing actions tracked in real time. Every session matters.

## Features

- **✅ Daily Actions** — Log habits with values, not just checkboxes
  - Checkbox (Did you do it?)
  - Duration (Hours spent)
  - Quantity (Count/reps)
  - Pages (For reading)
- **🔄 Habit Evolution** — Complete a habit → Evolve it into the next version
- **📊 Action Analytics** — See performance: total hours, pages read, days logged, averages
- **📓 Daily Journal** — Mood, Gratitude, Wins, Reflections
- **📚 Reading Stack** — 100+ books, status, ratings, key lessons
- **🔍 SQL Query Editor** — Direct database access for power users
- **Dark UI** — Focused, beautiful, distraction-free

---

## Local Setup

```bash
pip install -r requirements.txt
python seed_data.py
streamlit run app.py
```

Data saved to local `tracker.db`

---

## Workflow

### 1. Create an Action
**Settings → ✨ Create**
- Name: "Deep work session"
- Type: Duration (hours)
- Category: Learning
- Description: "Focused coding/writing"
- Target: 2 hours/day

### 2. Log Daily
**Daily Actions → Select date**
- Log 1.5 hours of deep work
- Add a note: "Implemented query editor"
- Save

### 3. Evolve When Ready
**Settings → 🎯 Active → Enhance**

Complete the habit and create its next version:
- Old: "Mental models study" (30 pages/week) ✅ Completed
- New: "Apply mental models" (in projects, duration-based)

The system tracks this transition and archives the old habit.

### 4. Analyze
**Analytics → 📊 Action Performance**
- See total hours across 30 days
- Track progress toward daily targets
- Review timeline of each action

---

## Action Types

| Type | Unit | Use For |
|------|------|---------|
| **checkbox** | — | Binary (done/not done) |
| **duration** | hours | Time-based: gym, work, meditation |
| **quantity** | count | Reps/items: exercises, tasks completed |
| **pages** | pages | Reading: books, articles |

---

## Database

**Tables:**
- `habits` — Your action definitions + status (active/completed/archived)
- `habit_log` — Daily values + notes for each action
- `habit_versions` — Track habit evolution history
- `journal` — Daily reflections
- `books` — Your library
- `reading_log` — Reading sessions

**Query Editor:** Run custom SQL anytime in **🔍 Query Editor**

Example: Get total hours logged this month:
```sql
SELECT h.name, SUM(hl.value) as total_hours
FROM habits h
JOIN habit_log hl ON h.id = hl.habit_id
WHERE hl.log_date >= date('now', 'start of month')
  AND h.action_type = 'duration'
GROUP BY h.name
ORDER BY total_hours DESC;
```

---

## Project Structure

```
tracker_app/
├── app.py              # Streamlit UI (Dashboard, Daily Actions, Analytics, etc.)
├── database.py         # SQLite layer + Query Editor API
├── seed_data.py        # Seeder for books + initial habits
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   ├── config.toml     # Dark theme config
│   └── secrets.toml    # (empty for local)
└── tracker.db          # Your data (auto-created)
```

---

## Tips for Flow

1. **Be specific:** "Gym" → "Strength training - 1 hour"
2. **Set targets:** Helps measure progress
3. **Evolve regularly:** Complete → Archive → Create new version
4. **Connect:** Habit for reading? Log into Reading Stack page too
5. **Review:** Check Analytics weekly to see patterns
6. **Journal:** Link daily actions to reflections for deeper insights

---

## Migration from Old Schema

If you had habits with the old checkbox-only system:
- Old habits remain but won't display in new action-based flow
- Create new habits with action types via **Settings → ✨ Create**
- Use **🔍 Query Editor** to migrate old data if needed



