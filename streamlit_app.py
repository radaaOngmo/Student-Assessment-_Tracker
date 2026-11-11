import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date
import html

from database import (
    initialize_database, authenticate, create_user,
    get_tasks, save_task, delete_task, dashboard_stats,
    list_users, toggle_user, update_profile, change_password
)

# ============================================================
# STUDENT ASSESSMENT TRACKER - STREAMLIT WEB INTERFACE
# Mirrors the supplied Tkinter screens and uses the same
# database.py functions and SQLite database.
# ============================================================

st.set_page_config(
    page_title="Student Assessment Tracker | Samtse College of Education",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
LOGO = ASSETS / "samtse_college_logo.png"
BG = "#F7F2E8"
MAROON = "#6E1F2A"
DARK = "#43131B"
GOLD = "#C69A3A"
WHITE = "#FFFEFB"
TEXT = "#2E2925"
MUTED = "#776D64"
BORDER = "#E3D8C8"
BLUE = "#7D3944"
RED = "#A83A3A"
GREEN = "#35745B"
PURPLE = "#79628B"
GOLD_LIGHT = "#E8D5A2"

initialize_database()

# -------------------------- CSS -----------------------------

st.markdown(f"""
<style>
:root {{
    --sat-bg: {BG};
    --sat-maroon: {MAROON};
    --sat-dark: {DARK};
    --sat-gold: {GOLD};
    --sat-white: {WHITE};
    --sat-text: {TEXT};
    --sat-muted: {MUTED};
    --sat-border: {BORDER};
}}
.stApp, [data-testid="stAppViewContainer"] {{
    background: var(--sat-bg) !important;
    color: var(--sat-text) !important;
    font-family: "Segoe UI", Arial, sans-serif !important;
}}
[data-testid="stHeader"] {{ background: transparent !important; }}
[data-testid="stToolbar"] {{ right: 1rem; }}
.block-container {{
    max-width: 100% !important;
    padding: 0 !important;
}}
[data-testid="stMainBlockContainer"] {{
    padding: 0 !important;
}}
[data-testid="stSidebar"] {{
    background: var(--sat-dark) !important;
    min-width: 220px !important;
    max-width: 220px !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    background: var(--sat-dark) !important;
}}
[data-testid="stSidebar"] * {{
    color: #FFFEFB;
}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
    color: #FFFEFB !important;
}}
[data-testid="stSidebar"] hr {{
    border-color: rgba(232,213,162,.55) !important;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label {{
    background: transparent;
    border-radius: 0;
    padding: 10px 12px;
    color: #FFFEFB !important;
    font-size: 14px;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
    background: #7D3944;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] + div {{
    color: white !important;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] input {{
    accent-color: {GOLD};
}}
[data-testid="stSidebar"] .stButton button {{
    width: 100%;
    background: {DARK} !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,.2) !important;
}}
.sat-brand {{
    display:flex; align-items:center; gap:12px;
    padding:18px 16px 12px 16px;
}}
.sat-brand img {{
    width:68px; height:68px; object-fit:contain;
    background:white; padding:4px;
}}
.sat-brand-name {{
    color:{GOLD} !important; font-weight:700; font-size:13px;
    line-height:1.35; letter-spacing:.2px;
}}
.sat-brand-line {{ height:3px; background:{GOLD}; margin:0 16px 18px 16px; }}
.sat-sidebar-footer {{
    position: fixed; bottom: 15px; left: 24px;
    color:#AFC3D4 !important; font-size:11px;
}}
.sat-topbar {{
    height:76px; background:{WHITE}; border-bottom:1px solid {BORDER};
    display:flex; align-items:center; justify-content:space-between;
    padding:0 25px; margin:0;
}}
.sat-workspace {{ color:{DARK}; font-weight:700; font-size:16px; }}
.sat-userline {{ color:{MUTED}; font-size:13px; }}
.sat-header-logo {{ width:48px; height:48px; object-fit:contain; margin-left:14px; }}
.sat-content {{ padding:24px 28px 20px 28px; }}
.sat-page-title {{
    color:{DARK}; font-size:29px; font-weight:750;
    margin:0 0 4px 0; line-height:1.25;
}}
.sat-subtitle {{ color:{MUTED}; font-size:13px; margin:0 0 24px 0; }}
.sat-card {{
    background:{WHITE}; border:1px solid {BORDER}; border-radius:0;
    min-height:100px; display:flex; overflow:hidden;
}}
.sat-accent {{ width:5px; flex-shrink:0; }}
.sat-card-inner {{ padding:16px 18px; }}
.sat-card-label {{ color:{MUTED}; font-size:11px; font-weight:700; text-transform:uppercase; }}
.sat-card-value {{ color:{DARK}; font-size:30px; font-weight:750; margin-top:8px; }}
.sat-panel {{
    background:{WHITE}; border:1px solid {BORDER};
    padding:16px 18px; margin-bottom:14px;
}}
.sat-panel-title {{ color:{DARK}; font-size:15px; font-weight:700; margin:0 0 12px 0; }}
.sat-progress-row {{
    display:grid; grid-template-columns:84px 1fr 24px;
    gap:10px; align-items:center; margin:8px 0;
    color:{MUTED}; font-size:12px;
}}
.sat-track {{ height:12px; background:#F0E7D8; }}
.sat-fill {{ height:12px; }}
.sat-count {{ text-align:right; color:{TEXT}; font-weight:700; }}
.sat-login-shell {{
    display:grid; grid-template-columns:390px 1fr;
    min-height:calc(100vh - 60px); margin:30px 34px;
    background:{WHITE}; border:1px solid {BORDER};
}}
.sat-login-left {{
    background:{DARK}; color:white; border-top:7px solid {GOLD};
    padding:35px 34px; position:relative;
}}
.sat-login-left h1 {{
    color:white !important; font-size:32px !important;
    line-height:1.4; margin:12px 0 16px 0;
}}
.sat-login-left p {{ color:#F2E6D4 !important; font-size:14px; }}
.sat-login-right {{ background:{WHITE}; padding:55px 48px; }}
.sat-login-title {{ color:{DARK}; font-size:32px; font-weight:750; margin:0 0 6px 0; }}
.sat-login-note {{ color:{MUTED}; font-size:13px; margin-bottom:25px; }}
.sat-login-bottom {{ border-top:1px solid {BORDER}; margin-top:22px; padding-top:18px; color:{MUTED}; font-size:13px; }}
.stApp h1,.stApp h2,.stApp h3 {{ color:{DARK}; }}
.stApp label, .stApp p {{ color:{TEXT}; }}
.stTextInput label, .stTextArea label, .stSelectbox label, .stDateInput label {{
    color:{DARK} !important; font-weight:700 !important; font-size:13px !important;
}}
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"],
.stDateInput input {{
    background:{WHITE} !important; color:{TEXT} !important;
    border:1px solid #B9AA97 !important; border-radius:0 !important;
}}
.stButton button, .stFormSubmitButton button {{
    border-radius:0 !important; font-weight:700 !important;
    background:{MAROON} !important; color:white !important;
    border:1px solid {MAROON} !important; min-height:38px;
}}

/* Force readable text on Streamlit buttons (including nested paragraph/span text) */
.stButton button, .stButton button *,
.stFormSubmitButton button, .stFormSubmitButton button *,
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primary"] *,
[data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-secondary"] * {{
    color: #FFFEFB !important;
    -webkit-text-fill-color: #FFFEFB !important;
    opacity: 1 !important;
}}
.stButton button:disabled, .stFormSubmitButton button:disabled {{
    color: #FFFEFB !important;
    -webkit-text-fill-color: #FFFEFB !important;
    opacity: .65 !important;
}}

.stButton button:hover, .stFormSubmitButton button:hover {{
    background:{GOLD} !important; color:{DARK} !important; border-color:{GOLD} !important;
}}

.sat-login-content {{
    padding: 10px 26px 18px 26px;
    max-width: 760px;
    margin: 0 auto;
}}
/* Keep text visible across Streamlit's nested widgets */
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li,
.stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stCaptionContainer"] {{
    color: #2E2925;
}}
.stApp input, .stApp textarea {{
    color: #2E2925 !important;
    -webkit-text-fill-color: #2E2925 !important;
}}
.stApp [data-testid="stDataFrame"] * {{
    color: #2E2925 !important;
}}

.stDataFrame {{ border:1px solid #A99D8D; }}
[data-testid="stDataFrame"] {{ background:{WHITE}; }}
[data-testid="stAlert"] {{ border-radius:0 !important; }}
hr {{ border-color:{BORDER} !important; }}
.sat-footer {{ color:{MUTED}; font-size:11px; text-align:center; padding:18px 0 4px 0; }}
@media(max-width:850px) {{
    .sat-login-shell {{ grid-template-columns:1fr; margin:10px; }}
    .sat-login-left {{ min-height:250px; }}
    .sat-login-right {{ padding:28px; }}
}}
</style>
""", unsafe_allow_html=True)

# ---------------------- SESSION STATE -----------------------

for key, default in {
    "user": None,
    "page": "Dashboard",
    "task_search": "",
    "completed_search": "",
    "register_mode": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def safe_img(path, width=None):
    if path and Path(path).exists():
        st.image(str(path), width=width)


def profile_path(user):
    value = (user or {}).get("profile_picture") or ""
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return path if path.exists() else None


def topbar(user):
    left, right = st.columns([5, 3])
    with left:
        st.markdown('<div class="sat-topbar"><span class="sat-workspace">༄ &nbsp;Workspace</span>', unsafe_allow_html=True)
    with right:
        pic = profile_path(user)
        c1, c2, c3 = st.columns([5, 1, 1])
        with c1:
            st.markdown(
                f'<div style="text-align:right;padding-top:28px;color:{MUTED};font-size:13px;">'
                f'{html.escape(user["full_name"])} &nbsp; · &nbsp; {html.escape(user["role"].title())}</div>',
                unsafe_allow_html=True
            )
        with c2:
            if pic:
                st.image(str(pic), width=38)
            else:
                st.markdown(f'<div style="margin-top:18px;background:{GOLD_LIGHT};color:{DARK};'
                            f'width:34px;height:34px;text-align:center;padding-top:7px;font-weight:bold;">'
                            f'{html.escape(user["full_name"][:1].upper())}</div>', unsafe_allow_html=True)
        with c3:
            safe_img(LOGO, 42)
    st.markdown("</div>", unsafe_allow_html=True)


def page_heading(title, subtitle=""):
    st.markdown(f'<div class="sat-content"><div class="sat-page-title">{html.escape(title)}</div>'
                f'<div class="sat-subtitle">{html.escape(subtitle)}</div>', unsafe_allow_html=True)


def end_content():
    st.markdown('<div class="sat-footer">Organise • Focus • Achieve</div></div>', unsafe_allow_html=True)


# ------------------------- LOGIN ----------------------------

def login_screen():
    left, right = st.columns([1, 1.9], gap="small")

    with left:
        st.markdown(f"""
        <div style="background:{DARK};min-height:calc(100vh - 60px);margin:30px 0 30px 34px;
        border-top:7px solid {GOLD};padding:35px 34px;">
          <div style="color:{GOLD};font-size:38px;margin:18px 0;">༄</div>
          <div style="color:white;font-size:32px;font-weight:750;line-height:1.4;">
          STUDENT<br>ASSESSMENT<br>TRACKER</div>
          <div style="width:84px;height:3px;background:{GOLD};margin:18px 0 24px;"></div>
          <div style="color:#F2E6D4;font-size:14px;line-height:1.5;">
          Plan clearly. Track progress.<br>Achieve more every day.</div>
          <div style="color:#D8C6B4;font-size:12px;line-height:1.5;margin-top:28px;">
          A focused workspace for your<br>assessment-related tasks.</div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        # Keep the login/register panel at the TOP, level with the title panel.
        # No photograph and no tall empty placeholder above the form.
        with st.container(border=True):
            st.markdown('<div class="sat-login-content">', unsafe_allow_html=True)

            if not st.session_state.register_mode:
                st.markdown(
                    f'<div class="sat-login-title">Welcome back</div>'
                    f'<div class="sat-login-note">Sign in to continue to your personal workspace.</div>',
                    unsafe_allow_html=True
                )
                with st.form("web_login", clear_on_submit=False):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    submit = st.form_submit_button("Sign in  →", use_container_width=True)
                    if submit:
                        found = authenticate(username, password)
                        if found:
                            st.session_state.user = found
                            st.session_state.page = "Dashboard"
                            st.rerun()
                        else:
                            st.error("The username or password is incorrect, or the account is inactive.")

                st.markdown(
                    f'<div class="sat-login-bottom">New to the tracker?</div>',
                    unsafe_allow_html=True
                )
                if st.button("Create student account", key="open_register"):
                    st.session_state.register_mode = True
                    st.rerun()
                st.caption("Demo accounts are documented in README.md.")

            else:
                st.markdown(
                    f'<div class="sat-login-title">Create your account</div>'
                    f'<div class="sat-login-note">Register to keep your tasks organised and private.</div>',
                    unsafe_allow_html=True
                )
                with st.form("web_register"):
                    full_name = st.text_input("Full name")
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    confirm = st.text_input("Confirm password", type="password")
                    a, b = st.columns(2)
                    with a:
                        create = st.form_submit_button("Create account", use_container_width=True)
                    with b:
                        back = st.form_submit_button("Back to sign in", use_container_width=True)
                    if create:
                        if not all([full_name.strip(), username.strip(), password, confirm]):
                            st.error("Please complete every field.")
                        elif password != confirm:
                            st.error("The new password and confirmation must match.")
                        else:
                            try:
                                create_user(username, full_name, password, role="user")
                                st.success("Your account is ready. Please sign in.")
                                st.session_state.register_mode = False
                                st.rerun()
                            except Exception as exc:
                                st.error(str(exc))
                    if back:
                        st.session_state.register_mode = False
                        st.rerun()
                st.caption("Create a private student account for your tasks.")

            st.markdown('</div>', unsafe_allow_html=True)


# --------------------- SHARED NAVIGATION --------------------

def sidebar(user):
    with st.sidebar:
        if LOGO.exists():
            st.markdown('<div class="sat-brand">', unsafe_allow_html=True)
            st.image(str(LOGO), width=68)
            st.markdown('<div class="sat-brand-name">STUDENT<br>ASSESSMENT<br>TRACKER</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="sat-brand"><div style="font-size:38px;color:{GOLD};">༄</div>'
                        '<div class="sat-brand-name">STUDENT<br>ASSESSMENT<br>TRACKER</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="sat-brand-line"></div>', unsafe_allow_html=True)
        pages = ["Dashboard", "Manage Tasks", "Completed Tasks"]
        if user["role"] == "admin":
            pages.append("Manage Users")
        pages.append("Settings")
        current = st.session_state.page if st.session_state.page in pages else "Dashboard"
        selected = st.radio("Navigation", pages, index=pages.index(current), label_visibility="collapsed",
                            format_func=lambda x: {
                                "Dashboard":"▦  Dashboard",
                                "Manage Tasks":"☷  Manage Tasks",
                                "Completed Tasks":"✓  Completed Tasks",
                                "Manage Users":"♙  Manage Users",
                                "Settings":"⚙  Settings"
                            }.get(x, x))
        if selected != st.session_state.page:
            st.session_state.page = selected
            st.rerun()
        st.markdown('<div class="sat-sidebar-footer">Organise • Focus • Achieve</div>', unsafe_allow_html=True)
        if st.button("⇥  Sign out", key="signout"):
            st.session_state.user = None
            st.session_state.page = "Dashboard"
            st.rerun()


# ------------------------ DASHBOARD -------------------------

def render_bar_panel(title, items):
    max_value = max([v for _, v, _ in items] + [1])
    rows = ""
    for label, value, color in items:
        pct = (value / max_value) * 100 if max_value else 0
        rows += f"""
        <div class="sat-progress-row">
          <span>{html.escape(label)}</span>
          <div class="sat-track"><div class="sat-fill" style="width:{pct}%;background:{color};"></div></div>
          <span class="sat-count">{value}</span>
        </div>"""
    st.markdown(f'<div class="sat-panel"><div class="sat-panel-title">{title}</div>{rows}</div>',
                unsafe_allow_html=True)


def dashboard_page(user):
    stats = dashboard_stats(user)
    tasks = get_tasks(user)
    page_heading(f"Welcome, {user['full_name']}", "Here is a quick overview of your task progress.")
    values = [
        ("All tasks", stats["total"], BLUE),
        ("Pending", stats["pending"], GOLD),
        ("In progress", stats["progress"], "#7B68B2"),
        ("Completed", stats["completed"], GREEN)
    ]
    if user["role"] == "admin":
        values.insert(0, ("Registered users", stats["users"], DARK))
    cols = st.columns(len(values), gap="small")
    for col, (label, value, accent) in zip(cols, values):
        with col:
            st.markdown(f'<div class="sat-card"><div class="sat-accent" style="background:{accent};"></div>'
                        f'<div class="sat-card-inner"><div class="sat-card-label">{label}</div>'
                        f'<div class="sat-card-value">{value}</div></div></div>', unsafe_allow_html=True)
    st.write("")
    c1, c2 = st.columns(2, gap="small")
    with c1:
        render_bar_panel("Tasks by priority", [
            ("High", sum(t["priority"] == "High" for t in tasks), RED),
            ("Medium", sum(t["priority"] == "Medium" for t in tasks), GOLD),
            ("Low", sum(t["priority"] == "Low" for t in tasks), GREEN)
        ])
    with c2:
        render_bar_panel("Task status", [
            ("Pending", stats["pending"], GOLD),
            ("In progress", stats["progress"], PURPLE),
            ("Completed", stats["completed"], GREEN)
        ])
    st.markdown(f'<div class="sat-panel"><div class="sat-panel-title" style="font-size:18px;">Recent tasks</div>',
                unsafe_allow_html=True)
    if tasks:
        df = pd.DataFrame(tasks)
        cols = ["task_id", "task_name"]
        if user["role"] == "admin":
            cols.append("owner_name")
        cols += ["priority", "status", "due_date"]
        df = df[cols].rename(columns={
            "task_id":"ID", "task_name":"Task", "owner_name":"Owner",
            "priority":"Priority", "status":"Status", "due_date":"Due date"
        })
        st.dataframe(df, use_container_width=True, hide_index=True, height=240)
    else:
        st.dataframe(pd.DataFrame(columns=["ID", "Task", "Priority", "Status", "Due date"]),
                     use_container_width=True, hide_index=True, height=170)
    st.markdown("</div>", unsafe_allow_html=True)
    end_content()


# ---------------------- TASK MANAGEMENT ---------------------

def task_table(user, tasks, key):
    if not tasks:
        st.dataframe(pd.DataFrame(columns=["ID", "Task", "Priority", "Status", "Due date"]),
                     use_container_width=True, hide_index=True, height=360)
        return
    df = pd.DataFrame(tasks)
    cols = ["task_id", "task_name"]
    if user["role"] == "admin":
        cols.append("owner_name")
    cols += ["priority", "status", "due_date"]
    df = df[cols].rename(columns={
        "task_id":"ID", "task_name":"Task", "owner_name":"Owner",
        "priority":"Priority", "status":"Status", "due_date":"Due date"
    })
    st.dataframe(df, use_container_width=True, hide_index=True, height=360, key=key)


def task_editor(user, existing=None):
    is_edit = existing is not None
    st.markdown(f'<div class="sat-panel"><div class="sat-panel-title">{ "Edit task" if is_edit else "Create a task"}</div>',
                unsafe_allow_html=True)
    with st.form("task_editor_form", clear_on_submit=True):
        title = st.text_input("Task title", value=existing["task_name"] if is_edit else "")
        description = st.text_area("Description", value=existing["description"] if is_edit else "", height=90)
        due = st.text_input("Due date (YYYY-MM-DD, optional)", value=existing["due_date"] if is_edit else "")
        c1, c2 = st.columns(2)
        with c1:
            priority = st.selectbox("Priority", ["Low", "Medium", "High"],
                                    index=["Low", "Medium", "High"].index(existing["priority"]) if is_edit else 1)
        with c2:
            status = st.selectbox("Status", ["Pending", "In Progress", "Completed"],
                                  index=["Pending", "In Progress", "Completed"].index(existing["status"]) if is_edit else 0)
        owner_id = None
        if user["role"] == "admin" and not is_edit:
            users = [u for u in list_users() if u["role"] == "user" and u["active"]]
            if users:
                labels = {f'{u["full_name"]} (@{u["username"]})': u["user_id"] for u in users}
                choice = st.selectbox("Assign to student", list(labels.keys()))
                owner_id = labels[choice]
        submitted = st.form_submit_button("Save task", use_container_width=True)
        if submitted:
            if due.strip():
                try:
                    if date.fromisoformat(due.strip()).isoformat() != due.strip():
                        raise ValueError
                except ValueError:
                    st.error("Enter a real date in YYYY-MM-DD format, or leave it blank.")
                    st.stop()
            try:
                save_task(user, existing["task_id"] if is_edit else None,
                          title, description, priority, status, due.strip(), owner_id=owner_id)
                st.success("Task saved successfully.")
                st.session_state.show_task_form = False
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    st.markdown("</div>", unsafe_allow_html=True)


def manage_tasks_page(user, completed=False):
    title = "Completed tasks" if completed else "Manage tasks"
    subtitle = "A focused list of tasks whose status is Completed." if completed else "Create, update, search, and track tasks."
    page_heading(title, subtitle)
    search_key = "completed_search" if completed else "task_search"
    if completed:
        c1, c2 = st.columns([9, 1])
        c3 = None
    else:
        c1, c2, c3 = st.columns([8, 1, 1])
    with c1:
        query = st.text_input(" ", key=search_key, label_visibility="collapsed", placeholder="Search tasks...")
    with c2:
        search_clicked = st.button("Search", use_container_width=True, key=f"search_{search_key}")
    if not completed:
        with c3:
            add_clicked = st.button("+ Add task", use_container_width=True)
    else:
        add_clicked = False
    tasks = get_tasks(user)
    if completed:
        tasks = [t for t in tasks if t["status"] == "Completed"]
    if query:
        tasks = [t for t in tasks if query.lower() in
                 f'{t["task_name"]} {t["description"]} {t["priority"]} {t["status"]} {t.get("owner_name","")}'.lower()]
    if add_clicked:
        st.session_state.show_task_form = True
        st.session_state.edit_task_id = None
    if st.session_state.get("show_task_form", False):
        selected_id = st.session_state.get("edit_task_id")
        existing = next((t for t in get_tasks(user) if t["task_id"] == selected_id), None) if selected_id else None
        task_editor(user, existing)
    st.markdown('<div class="sat-panel" style="padding:0;">', unsafe_allow_html=True)
    task_table(user, tasks, "completed_table" if completed else "manage_table")
    if not completed:
        options = {f'#{t["task_id"]} — {t["task_name"]}': t["task_id"] for t in tasks}
        selected_label = st.selectbox("Select a task for actions", [""] + list(options.keys()), key="selected_task_action")
        selected_id = options.get(selected_label)
        b1, b2, b3 = st.columns([1.2, 1.1, 1.1])
        with b1:
            if st.button("Mark complete", use_container_width=True):
                if not selected_id:
                    st.warning("Please select a task first.")
                else:
                    task = next(t for t in get_tasks(user) if t["task_id"] == selected_id)
                    save_task(user, selected_id, task["task_name"], task["description"],
                              task["priority"], "Completed", task["due_date"])
                    st.rerun()
        with b2:
            if st.button("Edit selected", use_container_width=True):
                if not selected_id:
                    st.warning("Please select a task first.")
                else:
                    st.session_state.show_task_form = True
                    st.session_state.edit_task_id = selected_id
                    st.rerun()
        with b3:
            if st.button("Delete selected", use_container_width=True):
                if not selected_id:
                    st.warning("Please select a task first.")
                else:
                    try:
                        delete_task(user, selected_id)
                        st.success("Task deleted.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
    st.markdown("</div>", unsafe_allow_html=True)
    end_content()


# ------------------------ SETTINGS --------------------------

def settings_page(user):
    page_heading("Settings", "Update your profile, profile picture, and password.")
    st.markdown('<div class="sat-panel"><div class="sat-panel-title" style="color:#C69A3A;">PROFILE INFORMATION</div>',
                unsafe_allow_html=True)
    pic_col, action_col = st.columns([1, 5])
    with pic_col:
        p = profile_path(user)
        if p:
            st.image(str(p), width=86)
        else:
            st.markdown(f'<div style="width:86px;height:86px;background:#F0E7D8;color:{DARK};'
                        f'display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:bold;">'
                        f'{html.escape(user["full_name"][:1].upper())}</div>', unsafe_allow_html=True)
    with action_col:
        st.markdown("**Profile picture**")
        uploaded = st.file_uploader("Choose picture…", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        st.caption("PNG, JPG, or JPEG. Your image is stored locally on this computer.")
    with st.form("profile_form"):
        full_name = st.text_input("Full name", value=user.get("full_name", ""))
        st.text_input("Username (cannot be changed)", value=user["username"], disabled=True)
        st.text_input("Access role", value=user["role"].title(), disabled=True)
        save_profile = st.form_submit_button("Save profile changes")
        if save_profile:
            picture_value = None
            if uploaded:
                ext = Path(uploaded.name).suffix.lower()
                dest_dir = ASSETS / "profile_pictures"
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest = dest_dir / f'web_user_{user["user_id"]}{ext}'
                dest.write_bytes(uploaded.getbuffer())
                picture_value = dest.relative_to(ROOT).as_posix()
            try:
                updated = update_profile(user["user_id"], full_name, picture_value)
                st.session_state.user = updated
                st.success("Your profile has been updated.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="sat-panel"><div class="sat-panel-title" style="color:#C69A3A;">CHANGE PASSWORD</div>',
                unsafe_allow_html=True)
    with st.form("password_form"):
        current = st.text_input("Current password", type="password")
        new = st.text_input("New password", type="password")
        confirm = st.text_input("Confirm new password", type="password")
        st.caption("Use at least 8 characters. Your current password is required to change it.")
        change = st.form_submit_button("Change password")
        if change:
            if not current or not new or not confirm:
                st.error("Complete all password fields.")
            elif new != confirm:
                st.error("The new password and confirmation must match.")
            else:
                try:
                    change_password(user["user_id"], current, new)
                    st.success("Your password has been changed successfully.")
                except Exception as exc:
                    st.error(str(exc))
    st.markdown("</div>", unsafe_allow_html=True)
    end_content()


# ---------------------- ADMIN USERS -------------------------

def users_page(user):
    if user["role"] != "admin":
        st.error("This page is available to administrators only.")
        return
    page_heading("Manage users", "Create accounts and enable or disable regular user accounts.")
    if st.button("+ Add user"):
        st.session_state.show_add_user = not st.session_state.get("show_add_user", False)
    if st.session_state.get("show_add_user", False):
        with st.form("add_user_form"):
            full_name = st.text_input("Full name")
            username = st.text_input("Username")
            password = st.text_input("Temporary password", type="password")
            role = st.selectbox("Role", ["user", "admin"])
            add = st.form_submit_button("Create account")
            if add:
                try:
                    create_user(username, full_name, password, role)
                    st.success("Account created.")
                    st.session_state.show_add_user = False
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
    users = list_users()
    df = pd.DataFrame(users)
    if not df.empty:
        df["status"] = df["active"].map({1:"Active", 0:"Disabled"})
        df = df[["user_id", "full_name", "username", "role", "status"]]
        df.columns = ["ID", "Full name", "Username", "Role", "Status"]
    else:
        df = pd.DataFrame(columns=["ID", "Full name", "Username", "Role", "Status"])
    st.markdown('<div class="sat-panel">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True, height=350)
    st.markdown("</div>", unsafe_allow_html=True)
    user_choices = {f'#{u["user_id"]} — {u["full_name"]} ({u["username"]}) — {"Active" if u["active"] else "Disabled"}':u
                    for u in users if u["role"] != "admin"}
    if user_choices:
        choice = st.selectbox("Select a regular user", [""] + list(user_choices.keys()))
        if st.button("Enable / disable selected user"):
            if not choice:
                st.warning("Please select a user.")
            else:
                try:
                    toggle_user(user_choices[choice]["user_id"])
                    st.success("User status updated.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
    end_content()


# ---------------------- APPLICATION -------------------------

if st.session_state.user is None:
    login_screen()
else:
    user = st.session_state.user
    sidebar(user)
    topbar(user)
    page = st.session_state.page
    if page == "Dashboard":
        dashboard_page(user)
    elif page == "Manage Tasks":
        manage_tasks_page(user, completed=False)
    elif page == "Completed Tasks":
        manage_tasks_page(user, completed=True)
    elif page == "Settings":
        settings_page(user)
    elif page == "Manage Users":
        users_page(user)
    else:
        st.session_state.page = "Dashboard"
        st.rerun()
