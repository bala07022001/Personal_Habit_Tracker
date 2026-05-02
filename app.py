"""
Personal Habit & Reading Tracker — Streamlit App
Expert-level journalling, habit tracking, and reading log in one place.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta, datetime
import calendar
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import database as db

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="My Personal Tracker",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #1a1d27; }
    .card {
        background: #1e2130; border-radius: 12px;
        padding: 16px 20px; margin-bottom: 12px;
        border-left: 4px solid #7c6fcd;
    }
    .card-green  { border-left-color: #4caf50; }
    .card-orange { border-left-color: #ff9800; }
    .card-blue   { border-left-color: #2196f3; }
    .card-red    { border-left-color: #f44336; }
    .big-metric { font-size: 2.4rem; font-weight: 700; color: #7c6fcd; }
    .metric-label { font-size: 0.85rem; color: #9e9e9e; text-transform: uppercase; letter-spacing: 1px; }
    .done-pill { background:#1b5e20; color:#a5d6a7; border-radius:20px; padding:2px 12px; font-size:0.82rem; }
    .miss-pill { background:#b71c1c; color:#ef9a9a; border-radius:20px; padding:2px 12px; font-size:0.82rem; }
    #MainMenu, footer, header { visibility: hidden; }
    .book-card { background:#1e2130; border-radius:10px; padding:14px 18px; margin-bottom:10px; border-left:4px solid #2196f3; }
    .book-card.inprogress { border-left-color:#ff9800; }
    .journal-entry { background:#1e2130; border-radius:10px; padding:18px; margin-bottom:10px; }
    .streak { background:#ff6f00; color:white; border-radius:20px; padding:2px 10px; font-weight:700; }
    .htable { width:100%; border-collapse:collapse; font-size:0.88rem; }
    .htable th { background:#2d3150; color:#b0b8e0; padding:7px 10px; text-align:left; }
    .htable td { padding:6px 10px; border-bottom:1px solid #2d3150; }
    .htable tr:hover td { background:#1e2130; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# INIT DB
# ─────────────────────────────────────────────────────────────────────────────
db.init_db()

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def mood_emoji(mood):
    return {"Happy":"😄","Neutral":"😐","Low":"😔","Reflective":"🤔","Energetic":"⚡"}.get(mood or "", "")

def status_color(s):
    return {"Completed":"green","Inprogress":"orange","On Hold":"purple","Yet To Start":"gray"}.get(s,"gray")

def rating_stars(r):
    if not r:
        return "☆☆☆☆☆"
    return "★" * int(r) + "☆" * (5 - int(r))

def dark_layout(fig, height=320):
    fig.update_layout(
        paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
        font=dict(color="#e0e0e0", size=12),
        height=height, margin=dict(l=10, r=10, t=30, b=30),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11))
    )
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — respects page_override set by Edit buttons
# ─────────────────────────────────────────────────────────────────────────────
PAGES = ["🏠 Dashboard", "✅ Daily Habits", "📓 Journal",
         "📚 Reading Stack", "📖 Book Detail", "📊 Analytics", "🔍 Query Editor", "⚙️ Settings"]

default_idx = 0
if "page_override" in st.session_state:
    try:
        default_idx = PAGES.index(st.session_state.pop("page_override"))
    except ValueError:
        default_idx = 0

with st.sidebar:
    st.markdown("## 🧠 Personal Tracker")
    st.markdown(f"**{date.today().strftime('%A, %B %d %Y')}**")
    st.markdown("---")
    page = st.radio("Navigate", PAGES, index=default_idx, label_visibility="collapsed")
    st.markdown("---")
    stats = db.get_books_stats()
    st.markdown(f"**📚 Library:** {stats['total']} books")
    st.markdown(f"**✅ Completed:** {stats['completed']}")
    st.markdown(f"**📖 Reading:** {stats['inprogress']}")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if page == "🏠 Dashboard":
    st.markdown("## 🏠 Dashboard")
    today_str = str(date.today())

    habit_stats = db.get_habit_stats(30)
    logged_today = db.get_habit_log_for_date(today_str)
    completed_today = sum(1 for h in logged_today if h["done"] == 1)
    total_habits = len(habit_stats)
    book_stats = db.get_books_stats()
    journal_today = db.get_journal(today_str)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="card card-green">
            <div class="metric-label">Habits Done Today</div>
            <div class="big-metric">{completed_today}/{total_habits}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="card card-blue">
            <div class="metric-label">Books Completed</div>
            <div class="big-metric">{book_stats['completed']}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="card card-orange">
            <div class="metric-label">Currently Reading</div>
            <div class="big-metric">{book_stats['inprogress']}</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        j_icon = "✅" if journal_today else "❌"
        st.markdown(f"""<div class="card">
            <div class="metric-label">Journal Today</div>
            <div class="big-metric">{j_icon}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### 📈 30-Day Habit Completion")
        if habit_stats:
            names = [h["name"] for h in habit_stats]
            pcts = [round(100 * (h["done_count"] or 0) / max(h["total_logged"] or 1, 1)) for h in habit_stats]
            fig = go.Figure(go.Bar(
                x=pcts, y=names, orientation="h",
                marker=dict(color=pcts, colorscale=[[0,"#b71c1c"],[0.5,"#ff9800"],[1,"#4caf50"]], showscale=False),
                text=[f"{p}%" for p in pcts], textposition="outside"
            ))
            dark_layout(fig, 380)
            fig.update_layout(xaxis=dict(range=[0, 115], showgrid=False))
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Log some habits to see stats.")

    with col_right:
        st.markdown("### 📚 Library Status")
        labels = ["Completed", "In Progress", "Yet To Start", "On Hold"]
        values = [book_stats["completed"], book_stats["inprogress"],
                  book_stats["yet_to_start"], book_stats["on_hold"]]
        fig2 = go.Figure(go.Pie(
            labels=labels, values=values, hole=0.55,
            marker=dict(colors=["#4caf50","#ff9800","#607d8b","#9c27b0"]),
            textfont_size=12,
        ))
        dark_layout(fig2, 280)
        st.plotly_chart(fig2, width='stretch')

        st.markdown("### 📓 Recent Journal")
        history = db.get_journal_history(5)
        if history:
            for j in history:
                emoji = mood_emoji(j["mood"])
                st.markdown(f"""<div class="journal-entry">
                    <b>{j['entry_date']}</b> {emoji} <span style="color:#9e9e9e">{j['mood'] or ''}</span><br>
                    <small>{j['preview'] or ''}{'...' if j['preview'] else ''}</small>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No journal entries yet.")

    st.markdown("---")
    st.markdown("### 📖 Currently Reading")
    active_books = db.get_books("Inprogress")
    if active_books:
        cols = st.columns(min(len(active_books), 3))
        for i, b in enumerate(active_books[:6]):
            with cols[i % 3]:
                st.markdown(f"""<div class="book-card inprogress">
                    <b>{b['title']}</b><br>
                    <small style="color:#9e9e9e">✍️ {b['author'] or 'Unknown'} &nbsp;|&nbsp; {b['discipline'] or ''}</small><br>
                    <small style="color:#ff9800">{b['activity'] or ''}</small>
                </div>""", unsafe_allow_html=True)
    else:
        st.info("No books in progress.")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: DAILY HABITS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "✅ Daily Habits":
    st.markdown("## ✅ Daily Habits")

    sel_date = st.date_input("Date", value=date.today(), max_value=date.today())
    sel_date_str = str(sel_date)

    habits = db.get_habits()
    if not habits:
        st.warning("No habits found. Add habits in ⚙️ Settings.")
        st.stop()

    existing = db.get_habit_log_for_date(sel_date_str)
    existing_map = {h["id"]: h for h in existing}

    st.markdown("---")
    st.markdown(f"### Log for **{sel_date.strftime('%A, %B %d %Y')}**")

    categories = {}
    for h in habits:
        categories.setdefault(h["category"], []).append(h)

    log_data = {}
    for cat, cat_habits in categories.items():
        st.markdown(f"#### 🏷️ {cat}")
        for h in cat_habits:
            existing_h = existing_map.get(h["id"], {})
            streak = db.get_habit_streak(h["id"])
            cols = st.columns([0.05, 3, 4, 1])
            with cols[0]:
                done = st.checkbox("", value=bool(existing_h.get("done", 0)), key=f"done_{h['id']}_{sel_date_str}")
            with cols[1]:
                st.markdown(f"**{h['name']}**")
                if streak > 0:
                    st.markdown(f"<span class='streak'>🔥 {streak}d streak</span>", unsafe_allow_html=True)
            with cols[2]:
                note = st.text_input("Note", value=existing_h.get("note", ""),
                                     key=f"note_{h['id']}_{sel_date_str}",
                                     label_visibility="collapsed", placeholder="Quick note...")
            with cols[3]:
                if done:
                    st.markdown("<span class='done-pill'>✓ Done</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='miss-pill'>✗ Miss</span>", unsafe_allow_html=True)
            log_data[h["id"]] = (done, note)

    if st.button("💾 Save Habit Log", type="primary"):
        db.log_habits(sel_date_str, log_data)
        done_count = sum(1 for d, _ in log_data.values() if d)
        st.success(f"Saved! {done_count}/{len(habits)} habits completed.")
        st.rerun()

    # ── Last 7 Days Overview (HTML table — no pyarrow) ────────────────────────
    st.markdown("---")
    st.markdown("### 📅 Last 7 Days Overview")
    dates_7 = [str(date.today() - timedelta(days=i)) for i in range(6, -1, -1)]
    head_html = "<th>Habit</th>" + "".join(f"<th>{d[-5:]}</th>" for d in dates_7)
    rows_html = ""
    for h in habits:
        cells = f"<td><b>{h['name']}</b></td>"
        for d in dates_7:
            logs = db.get_habit_log_for_date(d)
            m = {x["id"]: x for x in logs}
            val = m.get(h["id"], {})
            if val.get("done"):
                cell = "<td style='text-align:center;font-size:1.1rem'>✅</td>"
            elif "id" in val:
                cell = "<td style='text-align:center;font-size:1.1rem'>❌</td>"
            else:
                cell = "<td style='text-align:center;color:#555'>—</td>"
            cells += cell
        rows_html += f"<tr>{cells}</tr>"
    st.markdown(
        f"<table class='htable'><thead><tr>{head_html}</tr></thead><tbody>{rows_html}</tbody></table>",
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: JOURNAL
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📓 Journal":
    st.markdown("## 📓 Daily Journal")

    col1, col2 = st.columns([2, 1])
    with col1:
        sel_date = st.date_input("Entry Date", value=date.today(), max_value=date.today())
    sel_date_str = str(sel_date)
    existing_j = db.get_journal(sel_date_str)

    with col2:
        moods = ["Happy", "Neutral", "Low", "Reflective", "Energetic"]
        mood_idx = moods.index(existing_j["mood"]) if existing_j and existing_j.get("mood") in moods else 1
        mood = st.selectbox("Mood", moods, index=mood_idx)

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**🙏 Gratitude (3 things)**")
        gratitude = st.text_area("", value=existing_j.get("gratitude", "") if existing_j else "",
                                  height=100, key="gratitude", label_visibility="collapsed",
                                  placeholder="1.\n2.\n3.")
    with col_b:
        st.markdown("**🏆 Wins of the Day**")
        wins = st.text_area("", value=existing_j.get("wins", "") if existing_j else "",
                             height=100, key="wins", label_visibility="collapsed",
                             placeholder="What went well today?")

    st.markdown("**✍️ Journal Entry**")
    content = st.text_area(
        "", height=280,
        value=existing_j.get("content", "") if existing_j else "",
        key="journal_content", label_visibility="collapsed",
        placeholder="Write your thoughts, reflections, ideas, lessons of the day..."
    )

    if st.button("💾 Save Journal Entry", type="primary"):
        db.save_journal(sel_date_str, content, mood, gratitude, wins)
        st.success("Journal entry saved!")
        st.rerun()

    st.markdown("---")
    st.markdown("### 📜 Past Entries")
    history = db.get_journal_history(20)
    if history:
        for j in history:
            emoji = mood_emoji(j["mood"])
            with st.expander(f"{j['entry_date']} {emoji} {j['mood'] or ''}"):
                full = db.get_journal(j["entry_date"])
                if full:
                    if full.get("gratitude"):
                        st.markdown(f"**🙏 Gratitude:**\n{full['gratitude']}")
                    if full.get("wins"):
                        st.markdown(f"**🏆 Wins:**\n{full['wins']}")
                    if full.get("content"):
                        st.markdown(full["content"])
    else:
        st.info("No journal entries yet.")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: READING STACK
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📚 Reading Stack":
    st.markdown("## 📚 Reading Stack")

    tab1, tab2, tab3 = st.tabs(["📖 All Books", "➕ Add Book", "📝 Log Reading Session"])

    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Status", ["All", "Completed", "Inprogress", "On Hold", "Yet To Start"])
        with col2:
            search_q = st.text_input("🔍 Search", placeholder="title, author, discipline...")
        with col3:
            sort_by = st.selectbox("Sort", ["id", "title", "author", "discipline", "completion_date"])

        if search_q:
            books = db.search_books(search_q)
        elif status_filter == "All":
            books = db.get_books()
        else:
            books = db.get_books(status_filter)

        books = sorted(books, key=lambda x: (x.get(sort_by) or "") if sort_by != "id" else x["id"])

        st.markdown(f"**{len(books)} books**")
        st.markdown("---")

        for b in books:
            status_icon = {"Completed": "✅", "Inprogress": "📖", "On Hold": "⏸️", "Yet To Start": "🔲"}.get(b["status"], "")
            with st.expander(f"{status_icon} **{b['title']}** — _{b['author'] or 'Unknown'}_  {rating_stars(b['rating'])}"):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**Discipline:** {b['discipline'] or '—'}")
                c2.markdown(f"**Status:** :{status_color(b['status'])}[{b['status']}]")
                c3.markdown(f"**Year:** {b['year_read'] or '—'}")
                if b["activity"]:
                    st.markdown(f"**Activity/Chapter:** {b['activity']}")
                if b["key_lessons"]:
                    st.markdown("**🧠 Key Lessons:**")
                    for lesson in b["key_lessons"].split("\n"):
                        if lesson.strip():
                            st.markdown(f"- {lesson.strip()}")
                if b["favourite_quote"]:
                    st.markdown(f"> _{b['favourite_quote']}_")
                if b["review"]:
                    st.markdown("**📝 Review:**")
                    st.markdown(b["review"])
                if b["tags"]:
                    st.markdown(f"**🏷️ Tags:** {b['tags']}")

                btn_col1, btn_col2 = st.columns([1, 1])
                with btn_col1:
                    if st.button("✏️ Edit", key=f"edit_{b['id']}"):
                        st.session_state["edit_book_id"] = b["id"]
                        st.session_state["page_override"] = "📖 Book Detail"
                        st.rerun()
                with btn_col2:
                    if st.button("🗑️ Delete", key=f"del_{b['id']}", type="secondary"):
                        st.session_state[f"confirm_del_{b['id']}"] = True
                        st.rerun()

                if st.session_state.get(f"confirm_del_{b['id']}"):
                    st.warning(f"Are you sure you want to delete **{b['title']}**?")
                    yes_col, no_col = st.columns(2)
                    with yes_col:
                        if st.button("✅ Yes, delete", key=f"yes_del_{b['id']}"):
                            db.delete_book(b["id"])
                            st.session_state.pop(f"confirm_del_{b['id']}", None)
                            st.success("Deleted.")
                            st.rerun()
                    with no_col:
                        if st.button("❌ Cancel", key=f"no_del_{b['id']}"):
                            st.session_state.pop(f"confirm_del_{b['id']}", None)
                            st.rerun()

    with tab2:
        st.markdown("### ➕ Add New Book")
        with st.form("add_book_form"):
            t1, t2 = st.columns(2)
            title = t1.text_input("Title *")
            author = t2.text_input("Author")
            d1, d2 = st.columns(2)
            discipline = d1.text_input("Discipline")
            status = d2.selectbox("Status", ["Yet To Start", "Inprogress", "Completed", "On Hold"])
            y1, y2 = st.columns(2)
            year_read = y1.text_input("Year Read")
            activity = y2.text_input("Current Chapter / Activity")
            rating = st.slider("Rating", 0, 5, 0)
            tags = st.text_input("Tags (comma separated)")
            key_lessons = st.text_area("Key Lessons (one per line)")
            favourite_quote = st.text_area("Favourite Quote", height=80)
            review = st.text_area("Review / Thoughts", height=120)
            submitted = st.form_submit_button("Add Book", type="primary")
            if submitted:
                if not title.strip():
                    st.error("Title is required.")
                else:
                    db.add_book(
                        title=title.strip(), author=author, discipline=discipline,
                        status=status, year_read=year_read, activity=activity,
                        rating=rating if rating > 0 else None,
                        review=review, key_lessons=key_lessons,
                        favourite_quote=favourite_quote, tags=tags
                    )
                    st.success(f"'{title}' added!")
                    st.rerun()

    with tab3:
        st.markdown("### 📝 Log a Reading Session")
        books_list = db.get_books()
        if books_list:
            book_options = {f"[{b['id']}] {b['title']}": b["id"] for b in books_list}
            chosen = st.selectbox("Book", list(book_options.keys()))
            book_id = book_options[chosen]
            log_date = st.date_input("Date", value=date.today(), max_value=date.today(), key="rl_date")
            pages = st.number_input("Pages Read", min_value=0, value=0)
            notes = st.text_area("Session Notes", height=100)
            if st.button("💾 Log Session", type="primary"):
                db.log_reading_session(book_id, str(log_date), pages, notes)
                st.success("Reading session logged!")
        else:
            st.info("Add books first.")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: BOOK DETAIL
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📖 Book Detail":
    st.markdown("## 📖 Book Detail & Edit")

    books_list = db.get_books()
    if not books_list:
        st.info("No books yet.")
        st.stop()

    book_options = {f"[{b['id']}] {b['title']}": b["id"] for b in books_list}
    default_idx = 0
    if "edit_book_id" in st.session_state:
        for i, (k, v) in enumerate(book_options.items()):
            if v == st.session_state["edit_book_id"]:
                default_idx = i
                break

    chosen = st.selectbox("Select Book", list(book_options.keys()), index=default_idx)
    book_id = book_options[chosen]
    st.session_state["edit_book_id"] = book_id
    b = db.get_book(book_id)

    if b:
        with st.form("edit_book_form"):
            st.markdown(f"### {b['title']}")
            c1, c2 = st.columns(2)
            title = c1.text_input("Title", value=b["title"] or "")
            author = c2.text_input("Author", value=b["author"] or "")
            c3, c4 = st.columns(2)
            discipline = c3.text_input("Discipline", value=b["discipline"] or "")
            statuses = ["Yet To Start", "Inprogress", "Completed", "On Hold"]
            status = c4.selectbox("Status", statuses,
                                   index=statuses.index(b["status"]) if b["status"] in statuses else 0)
            c5, c6 = st.columns(2)
            year_read = c5.text_input("Year Read", value=b["year_read"] or "")
            activity = c6.text_input("Current Activity / Chapter", value=b["activity"] or "")
            rating = st.slider("Rating ★", 0, 5, int(b["rating"]) if b["rating"] else 0)
            tags = st.text_input("Tags", value=b["tags"] or "")
            key_lessons = st.text_area("🧠 Key Lessons (one per line)", value=b["key_lessons"] or "", height=150)
            favourite_quote = st.text_area("💬 Favourite Quote", value=b["favourite_quote"] or "", height=80)
            review = st.text_area("📝 Full Review / Thoughts", value=b["review"] or "", height=200,
                                   placeholder="What did this book teach you? How did it change your thinking?")
            saved = st.form_submit_button("💾 Save Changes", type="primary")
            if saved:
                db.update_book(
                    book_id, title=title, author=author, discipline=discipline,
                    status=status, year_read=year_read, activity=activity,
                    rating=rating if rating > 0 else None,
                    review=review, key_lessons=key_lessons,
                    favourite_quote=favourite_quote, tags=tags
                )
                st.success("Book updated!")
                st.rerun()

        # ── Reading sessions (HTML table — no pyarrow) ───────────────────────
        st.markdown("---")
        st.markdown("### 📅 Reading Sessions")
        sessions = db.get_reading_sessions(book_id)
        if sessions:
            rows_html = "".join(
                f"<tr><td>{s['log_date']}</td><td>{s['pages_read']}</td><td>{s['notes'] or ''}</td></tr>"
                for s in sessions
            )
            st.markdown(
                f"<table class='htable'><thead><tr><th>Date</th><th>Pages</th><th>Notes</th></tr></thead>"
                f"<tbody>{rows_html}</tbody></table>",
                unsafe_allow_html=True
            )
            st.markdown(f"**Total pages logged: {sum(s['pages_read'] for s in sessions)}**")
        else:
            st.info("No reading sessions logged for this book.")

        st.markdown("---")
        with st.expander("⚠️ Danger Zone"):
            st.warning(f"This will permanently delete **{b['title']}** and all its reading sessions.")
            if st.button("🗑️ Delete This Book", type="secondary"):
                db.delete_book(book_id)
                st.session_state.pop("edit_book_id", None)
                st.success("Book deleted.")
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📊 Analytics":
    st.markdown("## 📊 Analytics")

    tab_h, tab_b = st.tabs(["🔄 Habit Analytics", "📚 Book Analytics"])

    # ── HABIT ANALYTICS ───────────────────────────────────────────────────────
    with tab_h:
        habits = db.get_habits()
        if not habits:
            st.info("No habits yet.")
        else:
            # Row 1: Heatmap + Category Breakdown
            col_heat, col_cat = st.columns([3, 2])

            with col_heat:
                st.markdown("### 🗓️ Habit Heatmap")
                chosen_habit = st.selectbox("Habit", [h["name"] for h in habits])
                chosen_id = next(h["id"] for h in habits if h["name"] == chosen_habit)
                year_sel = st.number_input("Year", min_value=2024, max_value=2030,
                                           value=date.today().year, key="heatmap_year")
                heatmap_data = db.get_habit_heatmap(chosen_id, year_sel)

                all_days = []
                for m in range(1, 13):
                    for d in range(1, calendar.monthrange(year_sel, m)[1] + 1):
                        day_str = f"{year_sel}-{m:02d}-{d:02d}"
                        all_days.append({
                            "date": day_str,
                            "done": heatmap_data.get(day_str, -1),
                            "weekday": date(year_sel, m, d).weekday()
                        })
                df_heat = pd.DataFrame(all_days)
                df_heat["week"] = pd.to_datetime(df_heat["date"]).dt.isocalendar().week.astype(int)
                color_map = {1: "#4caf50", 0: "#b71c1c", -1: "#2d3150"}
                fig_heat = go.Figure()
                for _, row in df_heat.iterrows():
                    fig_heat.add_trace(go.Scatter(
                        x=[row["week"]], y=[row["weekday"]], mode="markers",
                        marker=dict(color=color_map.get(row["done"], "#2d3150"), size=10, symbol="square"),
                        showlegend=False,
                        hovertext=f"{row['date']} {'✅' if row['done']==1 else ('❌' if row['done']==0 else '—')}",
                        hoverinfo="text"
                    ))
                fig_heat.update_layout(
                    paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                    font=dict(color="#e0e0e0"), height=200,
                    yaxis=dict(tickvals=list(range(7)),
                               ticktext=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], showgrid=False),
                    xaxis=dict(showgrid=False, title="Week of Year"),
                    margin=dict(l=50, r=10, t=10, b=30)
                )
                st.plotly_chart(fig_heat, width='stretch')
                st.caption("🟩 Done  🟥 Missed  ◻️ Not logged")

            with col_cat:
                st.markdown("### 🏷️ Completion by Category (30d)")
                habit_stats_all = db.get_habit_stats(30)
                cat_map = {h["name"]: h["category"] for h in habits}
                cat_done, cat_total = {}, {}
                for hs in habit_stats_all:
                    cat = cat_map.get(hs["name"], "Other")
                    cat_done[cat] = cat_done.get(cat, 0) + (hs["done_count"] or 0)
                    cat_total[cat] = cat_total.get(cat, 0) + max(hs["total_logged"] or 1, 1)
                cat_pct = {c: round(100 * cat_done[c] / cat_total[c]) for c in cat_done}
                if cat_pct:
                    fig_cat = go.Figure(go.Bar(
                        x=list(cat_pct.values()), y=list(cat_pct.keys()), orientation="h",
                        marker=dict(color=list(cat_pct.values()),
                                    colorscale=[[0,"#b71c1c"],[0.5,"#ff9800"],[1,"#4caf50"]],
                                    showscale=False),
                        text=[f"{v}%" for v in cat_pct.values()], textposition="outside"
                    ))
                    dark_layout(fig_cat, 260)
                    fig_cat.update_layout(xaxis=dict(range=[0, 115]))
                    st.plotly_chart(fig_cat, width='stretch')

            st.markdown("---")

            # Row 2: Daily Completion % + Best Day of Week
            col_line, col_dow = st.columns([3, 2])

            with col_line:
                st.markdown("### 📈 Daily Completion % (Last 60 Days)")
                line_rows = db.get_daily_completion_trend(60)
                if line_rows:
                    df_line = pd.DataFrame(line_rows)
                    fig_line = go.Figure()
                    fig_line.add_trace(go.Scatter(
                        x=df_line["log_date"], y=df_line["pct"],
                        mode="lines+markers", line=dict(color="#7c6fcd", width=2.5),
                        marker=dict(size=5), fill="tozeroy",
                        fillcolor="rgba(124,111,205,0.15)"
                    ))
                    dark_layout(fig_line, 280)
                    fig_line.update_layout(yaxis=dict(range=[0, 105]))
                    st.plotly_chart(fig_line, width='stretch')
                else:
                    st.info("Not enough data yet — log your habits daily.")

            with col_dow:
                st.markdown("### 📅 Best Day of Week")
                dow_rows = db.get_dow_completion()
                if dow_rows:
                    dow_names = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
                    dow_dict = {r["dow"]: r["pct"] for r in dow_rows}
                    xs = [dow_names[int(k)] for k in sorted(dow_dict.keys())]
                    ys = [dow_dict[k] for k in sorted(dow_dict.keys())]
                    fig_dow = go.Figure(go.Bar(
                        x=xs, y=ys,
                        marker=dict(color=ys,
                                    colorscale=[[0,"#b71c1c"],[0.5,"#ff9800"],[1,"#4caf50"]],
                                    showscale=False),
                        text=[f"{v}%" for v in ys], textposition="outside"
                    ))
                    dark_layout(fig_dow, 280)
                    fig_dow.update_layout(yaxis=dict(range=[0, 115]))
                    st.plotly_chart(fig_dow, width='stretch')
                else:
                    st.info("Not enough data yet.")

            st.markdown("---")

            # Row 3: Habit Scorecard
            st.markdown("### 📋 Habit Scorecard (Last 30 Days)")
            rows_html = ""
            for hs in habit_stats_all:
                pct = round(100 * (hs["done_count"] or 0) / max(hs["total_logged"] or 1, 1))
                streak = db.get_habit_streak(hs["id"])
                bar = f"<div style='background:#4caf50;width:{pct}%;height:8px;border-radius:4px;min-width:2px'></div>"
                rows_html += (
                    f"<tr><td><b>{hs['name']}</b></td>"
                    f"<td>{hs['done_count'] or 0}/{hs['total_logged'] or 0}</td>"
                    f"<td>{pct}%&nbsp;{bar}</td>"
                    f"<td>🔥 {streak}d</td>"
                    f"<td>{hs['last_logged'] or '—'}</td></tr>"
                )
            st.markdown(
                "<table class='htable'><thead><tr>"
                "<th>Habit</th><th>Done/Logged</th><th>Rate</th><th>Streak</th><th>Last Logged</th>"
                f"</tr></thead><tbody>{rows_html}</tbody></table>",
                unsafe_allow_html=True
            )

    # ── BOOK ANALYTICS ────────────────────────────────────────────────────────
    with tab_b:
        all_books = db.get_books()
        completed_books = [b for b in all_books if b["status"] == "Completed"]

        # Row 1: Books per year + Status donut
        col_yr, col_status = st.columns([3, 2])

        with col_yr:
            st.markdown("### 📅 Books Completed Per Year")
            year_counts = {}
            for b in completed_books:
                for yr in (b.get("year_read") or "").replace(";", ",").split(","):
                    yr = yr.strip()
                    if yr:
                        year_counts[yr] = year_counts.get(yr, 0) + 1
            if year_counts:
                sorted_yrs = sorted(year_counts.keys())
                fig_yr = go.Figure(go.Bar(
                    x=sorted_yrs, y=[year_counts[y] for y in sorted_yrs],
                    marker_color="#7c6fcd",
                    text=[year_counts[y] for y in sorted_yrs], textposition="outside"
                ))
                dark_layout(fig_yr, 280)
                st.plotly_chart(fig_yr, width='stretch')
            else:
                st.info("No year data yet.")

        with col_status:
            st.markdown("### 📊 Library Status")
            book_stats = db.get_books_stats()
            fig_status = go.Figure(go.Pie(
                labels=["Completed", "In Progress", "Yet To Start", "On Hold"],
                values=[book_stats["completed"], book_stats["inprogress"],
                        book_stats["yet_to_start"], book_stats["on_hold"]],
                hole=0.55,
                marker=dict(colors=["#4caf50", "#ff9800", "#607d8b", "#9c27b0"]),
                textfont_size=12,
            ))
            dark_layout(fig_status, 280)
            fig_status.update_layout(showlegend=True, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_status, width='stretch')

        st.markdown("---")

        # Row 2: Discipline breakdown
        col_all_disc, col_comp_disc = st.columns(2)

        with col_all_disc:
            st.markdown("### 🏷️ All Books by Discipline")
            disc_all = {}
            for b in all_books:
                d = b["discipline"] or "Other"
                disc_all[d] = disc_all.get(d, 0) + 1
            if disc_all:
                sorted_disc = sorted(disc_all.items(), key=lambda x: x[1], reverse=True)[:20]
                fig_disc = go.Figure(go.Bar(
                    x=[v for _, v in sorted_disc], y=[k for k, _ in sorted_disc],
                    orientation="h", marker_color="#2196f3",
                    text=[v for _, v in sorted_disc], textposition="outside"
                ))
                dark_layout(fig_disc, 480)
                fig_disc.update_layout(xaxis=dict(range=[0, max(v for _, v in sorted_disc) * 1.3]))
                st.plotly_chart(fig_disc, width='stretch')

        with col_comp_disc:
            st.markdown("### ✅ Completed by Discipline")
            disc_comp = {}
            for b in completed_books:
                d = b["discipline"] or "Other"
                disc_comp[d] = disc_comp.get(d, 0) + 1
            if disc_comp:
                sorted_comp = sorted(disc_comp.items(), key=lambda x: x[1], reverse=True)[:20]
                fig_comp = go.Figure(go.Bar(
                    x=[v for _, v in sorted_comp], y=[k for k, _ in sorted_comp],
                    orientation="h", marker_color="#4caf50",
                    text=[v for _, v in sorted_comp], textposition="outside"
                ))
                dark_layout(fig_comp, 480)
                fig_comp.update_layout(xaxis=dict(range=[0, max(v for _, v in sorted_comp) * 1.3]))
                st.plotly_chart(fig_comp, width='stretch')

        st.markdown("---")

        # Row 3: Sunburst
        st.markdown("### 🌐 Library Sunburst: Discipline → Status")
        sun_ids, sun_labels, sun_parents, sun_values = [], [], [], []
        disc_status: dict = {}
        for b in all_books:
            disc = b["discipline"] or "Other"
            stat = b["status"] or "Unknown"
            disc_status.setdefault(disc, {})
            disc_status[disc][stat] = disc_status[disc].get(stat, 0) + 1
        for disc, stats_map in disc_status.items():
            total = sum(stats_map.values())
            sun_ids.append(disc)
            sun_labels.append(disc)
            sun_parents.append("")
            sun_values.append(total)
            for stat, cnt in stats_map.items():
                sun_ids.append(f"{disc}::{stat}")
                sun_labels.append(stat)
                sun_parents.append(disc)
                sun_values.append(cnt)
        if sun_ids:
            fig_sun = go.Figure(go.Sunburst(
                ids=sun_ids, labels=sun_labels, parents=sun_parents,
                values=sun_values, branchvalues="total",
                textfont=dict(size=11), insidetextorientation="radial",
                marker=dict(colorscale="Viridis")
            ))
            fig_sun.update_layout(
                paper_bgcolor="#0f1117", font=dict(color="#e0e0e0"),
                height=500, margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig_sun, width='stretch')

        st.markdown("---")

        # Row 4: Discipline table (no pyarrow)
        st.markdown("### 📋 Discipline Breakdown Table")
        disc_table: dict = {}
        for b in all_books:
            d = b["discipline"] or "Other"
            if d not in disc_table:
                disc_table[d] = {"Discipline": d, "Total": 0, "Completed": 0, "Reading": 0, "Yet To Start": 0, "On Hold": 0}
            disc_table[d]["Total"] += 1
            sk = {"Completed": "Completed", "Inprogress": "Reading",
                  "Yet To Start": "Yet To Start", "On Hold": "On Hold"}.get(b["status"], "Yet To Start")
            disc_table[d][sk] += 1
        sorted_dt = sorted(disc_table.values(), key=lambda x: x["Total"], reverse=True)
        cols_dt = ["Discipline", "Total", "Completed", "Reading", "Yet To Start", "On Hold"]
        head_dt = "".join(f"<th>{c}</th>" for c in cols_dt)
        rows_dt = "".join(
            "<tr>" + "".join(f"<td>{row[c]}</td>" for c in cols_dt) + "</tr>"
            for row in sorted_dt
        )
        st.markdown(
            f"<table class='htable'><thead><tr>{head_dt}</tr></thead><tbody>{rows_dt}</tbody></table>",
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: QUERY EDITOR
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔍 Query Editor":
    st.markdown("## 🔍 SQL Query Editor")
    st.markdown("Run custom SQL queries to manage your data directly.")
    
    tab_query, tab_schema = st.tabs(["Execute Query", "Schema"])
    
    with tab_query:
        st.markdown("### Write & Execute SQL")
        sql_input = st.text_area(
            "SQL Query",
            placeholder="SELECT * FROM habits;\nINSERT INTO habits (name, category) VALUES ('New Habit', 'General');\nUPDATE books SET status='Completed' WHERE id=5;",
            height=200,
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            execute_btn = st.button("▶️ Execute", type="primary")
        with col2:
            st.markdown("*Supports: SELECT, INSERT, UPDATE, DELETE*")
        
        if execute_btn and sql_input.strip():
            result = db.execute_query(sql_input)
            
            if result["success"]:
                st.success(f"✅ Query executed successfully ({result['count']} rows)")
                
                if result["data"]:
                    st.markdown("### Results")
                    df = pd.DataFrame(result["data"])
                    st.dataframe(df, use_container_width=True)
                    
                    # Download as CSV
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name="query_results.csv",
                        mime="text/csv"
                    )
            else:
                st.error(f"❌ Error: {result['error']}")
        
        st.markdown("---")
        st.markdown("### 📖 Quick References")
        with st.expander("View all tables", expanded=False):
            st.markdown("""
**Tables in your database:**
- `habits` — Your daily habits
- `habit_log` — Daily logs for each habit
- `journal` — Daily journal entries
- `books` — Your book library
- `reading_log` — Reading sessions logged per book

**Example queries:**
```sql
-- Get all active habits
SELECT * FROM habits WHERE is_active = 1;

-- Get habit completion for today
SELECT h.name, COALESCE(hl.done, 0) as done
FROM habits h
LEFT JOIN habit_log hl ON h.id = hl.habit_id AND hl.log_date = date('now')
WHERE h.is_active = 1;

-- Get books completed this year
SELECT * FROM books WHERE status = 'Completed' AND year_read LIKE '%2026%';

-- Count entries by mood
SELECT mood, COUNT(*) as count FROM journal GROUP BY mood;

-- Update a habit name
UPDATE habits SET name = 'New Name' WHERE id = 1;

-- Delete a book
DELETE FROM books WHERE id = 5;
```
            """)
    
    with tab_schema:
        st.markdown("### Database Schema")
        schema = db.get_table_schema()
        
        for table, columns in schema.items():
            with st.expander(f"📋 {table} ({len(columns)} columns)", expanded=False):
                df_schema = pd.DataFrame(columns)
                st.dataframe(
                    df_schema[["name", "type", "notnull", "pk"]],
                    use_container_width=True,
                    hide_index=True
                )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SETTINGS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "⚙️ Settings":
    st.markdown("## ⚙️ Settings")

    st.markdown("### 🏷️ Manage Habits")
    tab_view, tab_add = st.tabs(["View / Toggle", "Add Habit"])

    with tab_view:
        all_habits = db.get_habits(active_only=False)
        for h in all_habits:
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{h['name']}** `{h['category']}`")
            active = bool(h["is_active"])
            toggle = c2.checkbox("Active", value=active, key=f"active_{h['id']}")
            if toggle != active:
                db.toggle_habit_active(h["id"], toggle)
                st.rerun()

    with tab_add:
        with st.form("add_habit_form"):
            h_name = st.text_input("Habit Name")
            h_cat = st.text_input("Category", value="General")
            add_sub = st.form_submit_button("Add Habit", type="primary")
            if add_sub:
                if h_name.strip():
                    db.add_habit(h_name.strip(), h_cat.strip())
                    st.success(f"Habit '{h_name}' added!")
                    st.rerun()
                else:
                    st.error("Name required.")

    st.markdown("---")
    st.markdown("### 🧹 Database Maintenance")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Remove duplicate books** (keeps oldest entry per title):")
        if st.button("🔁 Deduplicate Books"):
            removed = db.deduplicate_books()
            if removed:
                st.success(f"Removed {removed} duplicate(s). Refresh to see changes.")
            else:
                st.info("No duplicates found.")
    with col_b:
        st.markdown("**Database stats:**")
        book_stats = db.get_books_stats()
        st.json(book_stats)
    st.code(f"DB path: {db.DB_PATH}", language="text")
