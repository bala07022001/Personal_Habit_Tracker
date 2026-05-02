# -*- coding: utf-8 -*-
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
import database_postgres as db
from database_postgres import get_conn

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
    completed_today = sum(1 for h in logged_today if h["value"] > 0)
    total_habits = len(logged_today)
    book_stats = db.get_books_stats()
    journal_today = db.get_journal(today_str)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="card card-green">
            <div class="metric-label">Actions Logged Today</div>
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
            <div class="metric-label">Journaled Today</div>
            <div class="big-metric">{j_icon}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### 📊 30-Day Action Performance")
        if habit_stats:
            names = [h["name"] for h in habit_stats]
            performance = []
            for h in habit_stats:
                if h["action_type"] == "checkbox":
                    # For checkbox: completion rate
                    perf = round(100 * (h["days_logged"] or 0) / max(30, 1))
                else:
                    # For value-based: % of target achieved (if target exists)
                    if h["target_value"]:
                        perf = round(100 * (h["total_value"] or 0) / (h["target_value"] * 30))
                    else:
                        perf = 100 if h["days_logged"] > 0 else 0
                performance.append(min(100, perf))
            
            fig = go.Figure(go.Bar(
                x=performance, y=names, orientation="h",
                marker=dict(color=performance, colorscale=[[0,"#b71c1c"],[0.5,"#ff9800"],[1,"#4caf50"]], showscale=False),
                text=[f"{p}%" for p in performance], textposition="outside"
            ))
            dark_layout(fig, 380)
            fig.update_layout(xaxis=dict(range=[0, 115], showgrid=False))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📝 Create habits in Settings to see performance.")

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
        st.plotly_chart(fig2, use_container_width=True)

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
    st.markdown("## ✅ Log Your Actions")
    st.markdown("*Extract ideas, apply learning, track progress*")
    
    sel_date = st.date_input("Date", value=date.today(), max_value=date.today())
    sel_date_str = str(sel_date)

    habits = db.get_habits("active")
    if not habits:
        st.warning("No active habits. Create one in ⚙️ Settings.")
        st.stop()

    existing = db.get_habit_log_for_date(sel_date_str)
    existing_map = {h["id"]: h for h in existing}

    st.markdown("---")
    st.markdown(f"### 📋 {sel_date.strftime('%A, %B %d %Y')}")
    
    # Group by category
    categories = {}
    for h in habits:
        categories.setdefault(h["category"], []).append(h)

    log_data = {}
    
    for cat, cat_habits in categories.items():
        with st.expander(f"**{cat}**", expanded=True):
            for h in cat_habits:
                existing_h = existing_map.get(h["id"], {})
                current_value = existing_h.get("value", 0)
                
                # Initialize session state for this habit's edit mode (use different key than button)
                state_key = f"show_edit_target_{h['id']}"
                if state_key not in st.session_state:
                    st.session_state[state_key] = False
                
                # Header with editable target
                col_name, col_target_edit = st.columns([3, 1])
                with col_name:
                    st.markdown(f"### {h['name']}")
                    if h['description']:
                        st.caption(f"*{h['description']}*")
                
                with col_target_edit:
                    if st.button(f"✏️ Target", key=f"btn_edit_target_{h['id']}", help="Edit your target"):
                        st.session_state[state_key] = True
                        st.rerun()
                    
                    if st.session_state.get(state_key):
                        new_target = st.number_input(
                            f"New target ({h['unit'] or 'units'})",
                            value=float(h['target_value'] or 0),
                            step=0.5,
                            key=f"inp_target_{h['id']}"
                        )
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("✅ Save", key=f"btn_save_target_{h['id']}"):
                                db.update_habit(h['id'], target_value=new_target)
                                st.session_state[state_key] = False
                                st.rerun()
                        with col_cancel:
                            if st.button("❌ Cancel", key=f"btn_cancel_target_{h['id']}"):
                                st.session_state[state_key] = False
                                st.rerun()
                
                # Input section
                col_input, col_note = st.columns([2, 2])
                
                if h['action_type'] == 'checkbox':
                    with col_input:
                        done = st.checkbox(
                            "✅ Done",
                            value=bool(current_value),
                            key=f"done_{h['id']}"
                        )
                        log_data[h["id"]] = (1.0 if done else 0.0, "")
                    with col_note:
                        if done:
                            st.markdown("✅ **Logged**")
                
                elif h['action_type'] == 'duration':
                    with col_input:
                        hours = st.number_input(
                            f"Hours ({h['unit']})",
                            min_value=0.0,
                            max_value=24.0,
                            step=0.25,
                            value=float(current_value),
                            key=f"hours_{h['id']}"
                        )
                        if h['target_value'] and hours > 0:
                            pct = min(100, int((hours / h['target_value']) * 100))
                            st.progress(min(pct/100, 1.0), text=f"{pct}% of target")
                    
                    with col_note:
                        note = st.text_input(
                            "Project/What",
                            value=existing_h.get("note", ""),
                            key=f"note_{h['id']}",
                            placeholder="e.g., Deep work on AI research"
                        )
                    log_data[h["id"]] = (hours, note)
                
                elif h['action_type'] == 'pages':
                    with col_input:
                        pages = st.number_input(
                            "Pages captured",
                            min_value=0,
                            step=1,
                            value=int(current_value),
                            key=f"pages_{h['id']}"
                        )
                        if h['target_value'] and pages > 0:
                            pct = min(100, int((pages / h['target_value']) * 100))
                            st.progress(min(pct/100, 1.0), text=f"{pct}% of target")
                    
                    with col_note:
                        book = st.text_input(
                            "Book title",
                            value=existing_h.get("note", ""),
                            key=f"book_{h['id']}",
                            placeholder="Which book?"
                        )
                    log_data[h["id"]] = (float(pages), book)
                
                else:  # quantity
                    with col_input:
                        qty = st.number_input(
                            h['unit'] or "Count",
                            min_value=0.0,
                            step=1.0,
                            value=float(current_value),
                            key=f"qty_{h['id']}"
                        )
                        if h['target_value'] and qty > 0:
                            pct = min(100, int((qty / h['target_value']) * 100))
                            st.progress(min(pct/100, 1.0), text=f"{pct}% of target")
                    
                    with col_note:
                        note = st.text_input(
                            "Details",
                            value=existing_h.get("note", ""),
                            key=f"qty_note_{h['id']}",
                            placeholder="What specifically?"
                        )
                    log_data[h["id"]] = (qty, note)
                
                st.divider()
    
    if st.button("💾 Save Today's Actions", type="primary"):
        for habit_id, (value, note) in log_data.items():
            if value > 0 or note:
                db.log_habit(habit_id, sel_date_str, value, note)
        st.success("✅ Actions logged!")
        st.rerun()


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
    st.markdown("## 📚 Your Reading & Ideas")
    st.markdown("*Mine books for ideas. Extract. Apply. Progress.*")

    tab_reading, tab_ideas, tab_capture = st.tabs(["📖 Currently Reading", "💡 Ideas Extracted", "✍️ Capture Idea"])

    with tab_reading:
        st.markdown("### 📖 Books in Progress")
        in_progress = db.get_books("Inprogress")
        
        if in_progress:
            for b in in_progress:
                # Initialize session state using separate keys (not widget keys)
                show_rating_edit = f"show_rating_edit_{b['id']}"
                show_year_edit = f"show_year_edit_{b['id']}"
                show_idea_form = f"show_idea_form_{b['id']}"
                
                if show_rating_edit not in st.session_state:
                    st.session_state[show_rating_edit] = False
                if show_year_edit not in st.session_state:
                    st.session_state[show_year_edit] = False
                if show_idea_form not in st.session_state:
                    st.session_state[show_idea_form] = False
                
                with st.expander(f"**{b['title']}** — {b['author'] or 'Unknown'}", expanded=True):
                    # Book metadata with inline editing
                    st.markdown("---")
                    col_meta1, col_meta2, col_meta3, col_meta4 = st.columns(4)
                    
                    with col_meta1:
                        st.markdown(f"📚 **Discipline**")
                        st.caption(b['discipline'] or "—")
                    
                    with col_meta2:
                        st.markdown(f"⭐ **Rating**")
                        if st.session_state.get(show_rating_edit):
                            new_rating = st.slider("Rate this book", 0, 5, int(b['rating'] or 0), key=f"rating_slider_{b['id']}")
                            col_sr1, col_sr2 = st.columns(2)
                            with col_sr1:
                                if st.button("✅ Save", key=f"btn_save_rating_{b['id']}", use_container_width=True):
                                    db.update_book(b['id'], rating=new_rating if new_rating > 0 else None)
                                    st.session_state[show_rating_edit] = False
                                    st.rerun()
                            with col_sr2:
                                if st.button("❌ Cancel", key=f"btn_cancel_rating_{b['id']}", use_container_width=True):
                                    st.session_state[show_rating_edit] = False
                                    st.rerun()
                        else:
                            st.caption(rating_stars(b['rating']))
                            if st.button("✏️ Edit", key=f"btn_edit_rating_{b['id']}", use_container_width=True):
                                st.session_state[show_rating_edit] = True
                                st.rerun()
                    
                    with col_meta3:
                        st.markdown(f"📅 **Year Read**")
                        if st.session_state.get(show_year_edit):
                            new_year = st.text_input("Year", value=b['year_read'] or "", key=f"inp_year_{b['id']}")
                            col_sy1, col_sy2 = st.columns(2)
                            with col_sy1:
                                if st.button("✅ Save", key=f"btn_save_year_{b['id']}", use_container_width=True):
                                    db.update_book(b['id'], year_read=new_year)
                                    st.session_state[show_year_edit] = False
                                    st.rerun()
                            with col_sy2:
                                if st.button("❌ Cancel", key=f"btn_cancel_year_{b['id']}", use_container_width=True):
                                    st.session_state[show_year_edit] = False
                                    st.rerun()
                        else:
                            st.caption(b['year_read'] or "—")
                            if st.button("✏️ Edit", key=f"btn_edit_year_{b['id']}", use_container_width=True):
                                st.session_state[show_year_edit] = True
                                st.rerun()
                    
                    with col_meta4:
                        ideas_list = db.get_book_ideas(b['id'])
                        st.markdown(f"💡 **Ideas**")
                        st.caption(f"{len(ideas_list)} captured")
                    
                    st.markdown("---")
                    
                    # Current focus
                    if b['activity']:
                        st.info(f"**📍 Current Focus:** _{b['activity']}_")
                    
                    # Key lessons
                    if b['key_lessons']:
                        st.markdown("**🧠 Key Lessons:**")
                        for lesson in b['key_lessons'].split("\n"):
                            if lesson.strip():
                                st.markdown(f"- {lesson.strip()}")
                    
                    # Favourite quote
                    if b['favourite_quote']:
                        st.success(f"💬 _{b['favourite_quote']}_")
                    
                    st.markdown("---")
                    
                    # Ideas from this book
                    ideas_list = db.get_book_ideas(b['id'])
                    if ideas_list:
                        st.markdown("**📋 Ideas from this book:**")
                        for idea in ideas_list:
                            with st.expander(f"💡 {idea['title']}"):
                                if idea['chapter_section']:
                                    st.caption(f"📍 {idea['chapter_section']}")
                                if idea['description']:
                                    st.write(idea['description'])
                                # Show applications
                                apps = db.get_idea_applications(idea['id'])
                                if apps:
                                    st.markdown("**Applied to:**")
                                    for app in apps:
                                        st.markdown(f"- {app['project_name']}")
                    
                    st.markdown("---")
                    
                    # Idea capture form (enhanced)
                    if st.session_state.get(show_idea_form):
                        st.markdown("### ✍️ Capture a New Idea")
                        with st.form(f"frm_idea_{b['id']}"):
                            idea_title = st.text_input("🎯 What's the core idea?", placeholder="Concise idea title", key=f"idea_title_{b['id']}")
                            idea_desc = st.text_area("📝 Why does this matter to you?", height=100, placeholder="How will you use this? What problem does it solve?", key=f"idea_desc_{b['id']}")
                            idea_chapter = st.text_input("📍 Chapter/Section/Page", placeholder="e.g., Chapter 3, pp. 45-52", key=f"idea_chapter_{b['id']}")
                            idea_project = st.text_input("🚀 Which project/work could this impact?", placeholder="Optional: where will you apply this?", key=f"idea_project_{b['id']}")
                            
                            col_submit, col_cancel = st.columns(2)
                            with col_submit:
                                if st.form_submit_button("✅ Save Idea", use_container_width=True):
                                    if idea_title.strip():
                                        db.capture_idea(b['id'], None, idea_title, idea_desc, idea_chapter)
                                        st.success("💡 Idea captured!")
                                        st.session_state[show_idea_form] = False
                                        st.rerun()
                                    else:
                                        st.error("Idea title required")
                            with col_cancel:
                                if st.form_submit_button("❌ Cancel", use_container_width=True):
                                    st.session_state[show_idea_form] = False
                                    st.rerun()
                    else:
                        if st.button("➕ Capture New Idea", key=f"btn_idea_form_{b['id']}", use_container_width=True):
                            st.session_state[show_idea_form] = True
                            st.rerun()
                    
                    st.markdown("---")
                    
                    # Action buttons
                    col_edit, col_activity, col_done = st.columns(3)
                    with col_edit:
                        if st.button("✏️ Full Edit", key=f"edit_full_{b['id']}", use_container_width=True):
                            st.session_state["edit_book_id"] = b["id"]
                            st.session_state["page_override"] = "📖 Book Detail"
                            st.rerun()
                    with col_activity:
                        new_activity = st.text_input("Current chapter/section", value=b['activity'] or "", key=f"activity_{b['id']}", label_visibility="collapsed")
                        if new_activity != (b['activity'] or ""):
                            db.update_book(b['id'], activity=new_activity)
                            st.rerun()
                    with col_done:
                        if st.button("✅ Mark Complete", key=f"done_{b['id']}", use_container_width=True):
                            db.update_book(b['id'], status="Completed")
                            st.success("📚 Book marked complete!")
                            st.rerun()
        else:
            st.info("No books in progress. Add one from the Reading Stack!")
        
        st.markdown("---")
        st.markdown("### 📚 All Books")
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by status", ["All", "Completed", "On Hold", "Yet To Start"])
        with col2:
            search_q = st.text_input("Search books", placeholder="title, author...")
        
        if search_q:
            books = db.search_books(search_q)
        elif status_filter == "All":
            books = db.get_books()
        else:
            books = db.get_books(status_filter)
        
        for b in books:
            status_icon = {"Completed": "✅", "Inprogress": "📖", "On Hold": "⏸️", "Yet To Start": "🔲"}.get(b["status"], "")
            with st.expander(f"{status_icon} {b['title']} — {b['author'] or 'Unknown'} {rating_stars(b['rating'])}"):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**Discipline:** {b['discipline']}")
                c2.markdown(f"**Status:** {b['status']}")
                c3.markdown(f"**Year:** {b['year_read'] or '—'}")
                
                col_edit_all, col_status_all = st.columns(2)
                with col_edit_all:
                    if st.button("✏️ Edit", key=f"edit_detail_{b['id']}", use_container_width=True):
                        st.session_state["edit_book_id"] = b["id"]
                        st.session_state["page_override"] = "📖 Book Detail"
                        st.rerun()
                with col_status_all:
                    new_status_all = st.selectbox("Change status", ["Yet To Start", "Inprogress", "On Hold", "Completed"], 
                                                  index=["Yet To Start", "Inprogress", "On Hold", "Completed"].index(b["status"]),
                                                  key=f"status_{b['id']}",
                                                  label_visibility="collapsed")
                    if new_status_all != b["status"]:
                        db.update_book(b['id'], status=new_status_all)
                        st.rerun()

    with tab_ideas:
        st.markdown("### 💡 Your Extracted Ideas")
        
        # Get all ideas
        with get_conn() as conn:
            all_ideas = conn.execute("""
                SELECT i.*, b.title as book_title
                FROM ideas i
                LEFT JOIN books b ON i.book_id = b.id
                ORDER BY i.captured_date DESC
            """).fetchall()
            ideas_list = [dict(r) for r in all_ideas]
        
        if ideas_list:
            status_filter = st.selectbox("Show", ["All", "Captured", "Applied"])
            
            for idea in ideas_list:
                if status_filter != "All" and idea['status'] != status_filter.lower():
                    continue
                
                badge = "💡" if idea['status'] == 'captured' else "✅"
                with st.expander(f"{badge} **{idea['title']}**"):
                    if idea['book_title']:
                        st.markdown(f"📖 From: _{idea['book_title']}_")
                    if idea['chapter_section']:
                        st.markdown(f"📍 {idea['chapter_section']}")
                    if idea['description']:
                        st.markdown(f"**Idea:** {idea['description']}")
                    
                    # Show applications
                    apps = db.get_idea_applications(idea['id'])
                    if apps:
                        st.markdown("**Applied to:**")
                        for app in apps:
                            st.markdown(f"- **{app['project_name']}** ({app['application_date']}) — {app['description']}")
                    
                    # Add application
                    with st.form(f"app_form_{idea['id']}"):
                        st.markdown("**Apply this idea to a project:**")
                        project = st.text_input("Project/Work name")
                        app_desc = st.text_area("How are you using this?", height=80)
                        impact = st.text_input("Expected impact")
                        if st.form_submit_button("🔗 Link Application"):
                            if project.strip():
                                db.apply_idea(idea['id'], project, app_desc, impact)
                                st.success("✅ Application logged!")
                                st.rerun()
        else:
            st.info("No ideas captured yet. Go to 📖 Currently Reading or use ✍️ Capture Idea tab.")

    with tab_capture:
        st.markdown("### ✍️ Capture a New Idea")
        st.markdown("*Extract learnings without needing to finish the book*")
        
        with st.form("capture_idea_form"):
            idea_type = st.radio("Where is this idea from?", ["From a book", "From a habit", "General learning"])
            
            idea_title = st.text_input("What's the core idea?")
            idea_desc = st.text_area("Describe it (why it matters to you)", height=100)
            
            if idea_type == "From a book":
                books_list = db.get_books()
                if books_list:
                    book = st.selectbox("Which book?", options=[b['id'] for b in books_list],
                                       format_func=lambda bid: next((b['title'] for b in books_list if b['id'] == bid), "Unknown"))
                    chapter = st.text_input("Chapter/Section/Page")
                    book_id = book
                else:
                    st.warning("Add a book first!")
                    book_id = None
                    chapter = ""
            else:
                book_id = None
                chapter = ""
            
            if st.form_submit_button("💡 Save Idea", type="primary"):
                if idea_title.strip():
                    db.capture_idea(book_id, None, idea_title, idea_desc, chapter if idea_type == "From a book" else "")
                    st.success("✅ Idea captured! You can now apply it to your projects.")
                    st.rerun()
                else:
                    st.error("Idea title is required.")



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
        habits = db.get_habits("active")
        if not habits:
            st.info("📝 Create habits in Settings to see analytics.")
        else:
            st.markdown("### 📊 Action Performance (30 days)")
            habit_stats_all = db.get_habit_stats(30)
            
            # Summary cards
            cols = st.columns(len(habit_stats_all))
            for i, h in enumerate(habit_stats_all):
                with cols[i % len(cols)]:
                    if h["action_type"] == "checkbox":
                        val = f"{h['days_logged']}/30"
                        unit = "Days"
                    else:
                        val = f"{h['total_value']:.1f}" if h['total_value'] else "0"
                        unit = h['unit'] or "Total"
                    st.metric(h['name'][:12], val, help=unit)
            
            st.divider()
            
            # Detailed table
            st.markdown("### 📋 Detailed Breakdown")
            table_data = []
            for h in habit_stats_all:
                table_data.append({
                    "Action": h["name"],
                    "Type": h["action_type"],
                    "Days Logged": h["days_logged"] or 0,
                    "Total": f"{h['total_value']:.2f}" if h['total_value'] else "0",
                    "Average": f"{h['avg_value']:.2f}" if h['avg_value'] else "0",
                    "Last Logged": h["last_logged"] or "—"
                })
            df_habits = pd.DataFrame(table_data)
            st.dataframe(df_habits, use_container_width=True, hide_index=True)
            
            # Individual habit timeline
            st.markdown("---")
            st.markdown("### 📈 Action Timeline")
            chosen = st.selectbox(
                "Select action",
                options=[h["id"] for h in habit_stats_all],
                format_func=lambda hid: next((h["name"] for h in habit_stats_all if h["id"] == hid), "Unknown")
            )
            
            timeline = db.get_habit_timeline(chosen, 60)
            if timeline:
                df_timeline = pd.DataFrame(timeline)
                fig_timeline = go.Figure()
                fig_timeline.add_trace(go.Scatter(
                    x=df_timeline["log_date"],
                    y=df_timeline["value"],
                    mode="lines+markers",
                    line=dict(color="#7c6fcd", width=2),
                    marker=dict(size=6),
                    fill="tozeroy",
                    fillcolor="rgba(124,111,205,0.15)"
                ))
                dark_layout(fig_timeline, 300)
                st.plotly_chart(fig_timeline, use_container_width=True)
            else:
                st.info("No data yet for this action.")

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
    st.markdown("## ⚙️ Habit Studio")
    st.markdown("*Design & evolve your action-based habits*")

    tab_active, tab_create, tab_evolve, tab_history = st.tabs(["🎯 Active", "✨ Create", "🔄 Evolve", "📜 History"])

    # ── ACTIVE HABITS ─────────────────────────────────────────────────────────
    with tab_active:
        st.markdown("### Your Active Actions")
        active_habits = db.get_habits("active")
        
        if not active_habits:
            st.info("No active habits. Create one in the ✨ Create tab.")
        else:
            for h in active_habits:
                with st.expander(f"**{h['name']}** — {h['category']}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Details:**")
                        st.markdown(f"- **Category:** {h['category']}")
                        st.markdown(f"- **Type:** {h['action_type']}")
                        if h['unit']:
                            st.markdown(f"- **Unit:** {h['unit']}")
                        if h['target_value']:
                            st.markdown(f"- **Target:** {h['target_value']} {h['unit'] or ''}")
                        st.markdown(f"- **Started:** {h['created_at']}")
                    
                    with col2:
                        st.markdown("**Progress (30d):**")
                        progress = db.get_habit_progress(h["id"], 30)
                        if progress:
                            st.metric("Days logged", progress['days_logged'])
                            if progress['total_value'] > 0:
                                st.metric("Total", f"{progress['total_value']:.1f} {h['unit'] or ''}")
                            st.metric("Average", f"{progress['avg_value']:.2f} {h['unit'] or ''}")
                    
                    if h['description']:
                        st.markdown(f"**Description:** {h['description']}")
                    
                    st.divider()
                    
                    col_enhance, col_archive = st.columns(2)
                    with col_enhance:
                        if st.button(f"🔄 Enhance '{h['name']}'", key=f"enhance_{h['id']}"):
                            st.session_state[f"enhance_habit_{h['id']}"] = True
                    with col_archive:
                        if st.button(f"📦 Archive '{h['name']}'", key=f"archive_{h['id']}"):
                            db.archive_habit(h["id"])
                            st.success(f"Archived! '{h['name']}' moved to history.")
                            st.rerun()
                    
                    # Enhance form (hidden by default)
                    if st.session_state.get(f"enhance_habit_{h['id']}"):
                        st.markdown("---")
                        st.markdown("### 🔄 Enhance This Habit")
                        with st.form(f"enhance_form_{h['id']}"):
                            st.markdown("*Your habit is evolving! Create the next version.*")
                            new_name = st.text_input("New action name", value=h['name'])
                            new_desc = st.text_area("What will you focus on next?", value=h['description'] or "")
                            new_action = st.selectbox(
                                "Action type",
                                ["checkbox", "duration", "quantity", "pages"],
                                index=["checkbox", "duration", "quantity", "pages"].index(h['action_type'])
                            )
                            new_unit = st.text_input("Unit", value=h['unit'] or "", help="e.g., hours, pages, count")
                            new_target = st.number_input("Target value", value=float(h['target_value'] or 0), step=0.5)
                            
                            if st.form_submit_button("✨ Create Enhanced Version", type="primary"):
                                new_id = db.enhance_habit(
                                    h["id"], new_name, new_desc, h['category'],
                                    new_action, new_unit, new_target
                                )
                                st.success(f"✅ Enhanced! Started tracking '{new_name}'")
                                st.session_state.pop(f"enhance_habit_{h['id']}", None)
                                st.rerun()

    # ── CREATE NEW HABIT ──────────────────────────────────────────────────────
    with tab_create:
        st.markdown("### ✨ Create New Action")
        st.markdown("*Define your next habit or action to track*")
        
        with st.form("create_habit_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Action name *", placeholder="e.g., Deep work, Reading, Meditation")
                category = st.text_input("Category", value="General", placeholder="e.g., Wellness, Learning")
            
            with col2:
                action_type = st.selectbox(
                    "Action type *",
                    ["checkbox", "duration", "quantity", "pages"],
                    help="checkbox=Yes/No | duration=Hours | quantity=Count | pages=Pages read"
                )
            
            description = st.text_area(
                "Description",
                placeholder="Why this habit? What's your intention?",
                height=80
            )
            
            col3, col4 = st.columns(2)
            with col3:
                unit = st.text_input("Unit", placeholder="e.g., hours, count, pages (optional)")
            with col4:
                target = st.number_input("Daily target (optional)", value=0.0, step=0.5)
            
            submitted = st.form_submit_button("✨ Create Habit", type="primary")
            if submitted:
                if name.strip():
                    db.create_habit(
                        name.strip(), category, description,
                        action_type, unit if unit else None,
                        target if target > 0 else None
                    )
                    st.success(f"🎯 '{name}' created! Start logging it in Daily Actions.")
                    st.rerun()
                else:
                    st.error("Action name is required.")

    # ── EVOLVE HABITS ─────────────────────────────────────────────────────────
    with tab_evolve:
        st.markdown("### 🔄 Habit Evolution")
        st.markdown("*Complete a habit and evolve it into something new*")
        
        active = db.get_habits("active")
        if active:
            selected = st.selectbox(
                "Select habit to evolve",
                options=[h["id"] for h in active],
                format_func=lambda hid: next((h["name"] for h in active if h["id"] == hid), "Unknown")
            )
            
            h = next((x for x in active if x["id"] == selected), None)
            if h:
                st.info(f"📍 Evolving: **{h['name']}** from {h['created_at']}")
                
                with st.form(f"evolve_form_{selected}"):
                    st.markdown("**Next version:**")
                    new_name = st.text_input("New action name")
                    new_desc = st.text_area("New focus")
                    new_action = st.selectbox("Action type", ["checkbox", "duration", "quantity", "pages"])
                    new_unit = st.text_input("Unit")
                    new_target = st.number_input("Target value", step=0.5)
                    
                    if st.form_submit_button("🔄 Complete & Evolve", type="primary"):
                        if new_name.strip():
                            new_id = db.enhance_habit(
                                selected, new_name, new_desc, h['category'],
                                new_action, new_unit, new_target
                            )
                            st.success(f"✅ Evolved! Now tracking '{new_name}'")
                            st.rerun()
                        else:
                            st.error("New action name required.")

    # ── HISTORY ──────────────────────────────────────────────────────────────
    with tab_history:
        st.markdown("### 📜 Completed & Archived")
        
        col_completed, col_archived = st.columns(2)
        
        with col_completed:
            st.markdown("**✅ Completed**")
            completed = db.get_habits("completed")
            if completed:
                for h in completed:
                    st.markdown(f"- **{h['name']}** ({h['category']}) — {h['completed_at']}")
            else:
                st.info("No completed habits yet.")
        
        with col_archived:
            st.markdown("**📦 Archived**")
            archived = db.get_habits("archived")
            if archived:
                for h in archived:
                    st.markdown(f"- **{h['name']}** ({h['category']}) — {h['archived_at']}")
            else:
                st.info("No archived habits yet.")
    
    st.markdown("---")
    st.markdown("### 🧹 Database Maintenance")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Remove duplicate books:**")
        if st.button("🔁 Deduplicate Books"):
            removed = db.deduplicate_books()
            if removed:
                st.success(f"Removed {removed} duplicate(s).")
            else:
                st.info("No duplicates found.")
    with col_b:
        st.markdown("**Database stats:**")
        book_stats = db.get_books_stats()
        st.json(book_stats)
    st.code(f"DB: {db.DB_PATH}", language="text")
