
"""
STUDENT ASSESSMENT TRACKER
Gradio Companion Application
Samtse College of Education

Uses the same SQLite database as Streamlit.
Compatible with Gradio 6.x.
"""

import gradio as gr
import pandas as pd

from database import (
    initialize_database,
    authenticate,
    dashboard_stats,
    get_tasks,
    save_task,
    delete_task,
)

# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

initialize_database()

# --------------------------------------------------
# PROJECT COLOURS
# --------------------------------------------------

MAROON = "#6E1F2A"
DARK_MAROON = "#43131B"
GOLD = "#C69A3A"
IVORY = "#F7F2E8"
WHITE = "#FFFEFB"
TEXT = "#2E2925"
MUTED = "#776D64"

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

CSS = """
.gradio-container {
    background: #F7F2E8 !important;
    color: #2E2925 !important;
    font-family: 'Segoe UI', Arial, sans-serif !important;
    max-width: 1200px !important;
}

/* HEADER */

#sat-header {
    background: #43131B;
    color: white;
    border-top: 7px solid #C69A3A;
    border-radius: 8px;
    padding: 22px 28px;
    margin-bottom: 18px;
}

#sat-header h1 {
    color: white !important;
    margin: 0;
}

#sat-header p {
    color: #F2E6D4 !important;
    margin: 6px 0 0 0;
}

/* STATISTICS */

.sat-stat {
    background: #FFFEFB;
    border: 1px solid #E3D8C8;
    border-left: 5px solid #C69A3A;
    border-radius: 8px;
    padding: 14px 18px;
}

.sat-stat-label {
    color: #776D64;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}

.sat-stat-value {
    color: #43131B;
    font-size: 28px;
    font-weight: 800;
}

/* BUTTONS */

.gradio-container button.primary {
    background: #6E1F2A !important;
    color: white !important;
    border: 1px solid #6E1F2A !important;
}

.gradio-container button.primary:hover {
    background: #C69A3A !important;
    color: #43131B !important;
}

/* NAVIGATION TABS */

.gradio-container [role="tablist"] button,
.gradio-container button[role="tab"] {
    color: #43131B !important;
    background-color: #F7F2E8 !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}

.gradio-container [role="tablist"] button *,
.gradio-container button[role="tab"] * {
    color: #43131B !important;
    opacity: 1 !important;
}

/* SELECTED TAB */

.gradio-container [role="tablist"] button[aria-selected="true"],
.gradio-container button[role="tab"][aria-selected="true"] {
    background-color: #6E1F2A !important;
    color: #FFFEFB !important;
    border-bottom: 3px solid #C69A3A !important;
}

.gradio-container [role="tablist"] button[aria-selected="true"] *,
.gradio-container button[role="tab"][aria-selected="true"] * {
    color: #FFFEFB !important;
}

/* HEADINGS AND LABELS */

.gradio-container label,
.gradio-container h2,
.gradio-container h3 {
    color: #43131B !important;
    opacity: 1 !important;
}

/* INPUTS */

.gradio-container input,
.gradio-container textarea {
    color: #2E2925 !important;
}
"""

# --------------------------------------------------
# EMPTY DATAFRAME
# --------------------------------------------------

def empty_dataframe():
    return pd.DataFrame(
        columns=[
            "ID",
            "Task",
            "Priority",
            "Status",
            "Due date"
        ]
    )


# --------------------------------------------------
# DASHBOARD STATISTICS
# --------------------------------------------------

def stats_html(user):

    stats = dashboard_stats(user)

    values = [
        ("All Tasks", stats["total"]),
        ("Pending", stats["pending"]),
        ("In Progress", stats["progress"]),
        ("Completed", stats["completed"]),
    ]

    if user["role"] == "admin":
        values.append(("Total Users", stats["users"]))

    cards = "".join(
        f'<div class="sat-stat">'
        f'<div class="sat-stat-label">{label}</div>'
        f'<div class="sat-stat-value">{value}</div>'
        f'</div>'
        for label, value in values
    )

    return (
        f'<div style="display:grid;'
        f'grid-template-columns:repeat({len(values)}, minmax(0, 1fr));'
        f'gap:12px;">{cards}</div>'
    )


# --------------------------------------------------
# TASK TABLE
# --------------------------------------------------

def task_dataframe(user, completed_only=False):

    tasks = get_tasks(user)

    if completed_only:
        tasks = [
            task for task in tasks
            if task["status"] == "Completed"
        ]

    headers = [
        "ID",
        "Task",
        "Priority",
        "Status",
        "Due date"
    ]

    if user["role"] == "admin":
        headers.insert(2, "Student")

    rows = []

    for task in tasks:

        row = [
            task["task_id"],
            task["task_name"]
        ]

        if user["role"] == "admin":
            row.append(task.get("owner_name", ""))

        row.extend([
            task["priority"],
            task["status"],
            task["due_date"]
        ])

        rows.append(row)

    return pd.DataFrame(rows, columns=headers)


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

def login(username, password):

    user = authenticate(
        username or "",
        password or ""
    )

    if not user:

        return (
            None,
            gr.update(visible=True),
            gr.update(visible=False),
            "Login failed. Check your username and password.",
            "",
            empty_dataframe()
        )

    return (
        user,
        gr.update(visible=False),
        gr.update(visible=True),
        f"Welcome, {user['full_name']}!",
        stats_html(user),
        task_dataframe(user)
    )


# --------------------------------------------------
# REFRESH DASHBOARD
# --------------------------------------------------

def refresh_dashboard(user):

    if not user:
        return "<p>Please sign in.</p>", empty_dataframe()

    return (
        stats_html(user),
        task_dataframe(user)
    )


# --------------------------------------------------
# ADD TASK
# --------------------------------------------------

def add_task(user, title, description, priority, status, due_date):

    if not user:
        return "Please sign in again.", empty_dataframe()

    try:

        save_task(
            user,
            None,
            title or "",
            description or "",
            priority,
            status,
            due_date or ""
        )

        return (
            "Task added successfully.",
            task_dataframe(user)
        )

    except Exception as exc:

        return (
            f"Could not add task: {exc}",
            task_dataframe(user)
        )


# --------------------------------------------------
# UPDATE TASK
# --------------------------------------------------

def update_task(
    user,
    task_id,
    title,
    description,
    priority,
    status,
    due_date
):

    if not user:
        return "Please sign in again.", empty_dataframe()

    if task_id is None:
        return (
            "Enter the task ID you want to update.",
            task_dataframe(user)
        )

    try:

        save_task(
            user,
            int(task_id),
            title or "",
            description or "",
            priority,
            status,
            due_date or ""
        )

        return (
            "Task updated successfully.",
            task_dataframe(user)
        )

    except Exception as exc:

        return (
            f"Could not update task: {exc}",
            task_dataframe(user)
        )


# --------------------------------------------------
# DELETE TASK
# --------------------------------------------------

def remove_task(user, task_id):

    if not user:
        return "Please sign in again.", empty_dataframe()

    if task_id is None:
        return (
            "Enter the task ID you want to delete.",
            task_dataframe(user)
        )

    try:

        delete_task(user, int(task_id))

        return (
            "Task deleted successfully.",
            task_dataframe(user)
        )

    except Exception as exc:

        return (
            f"Could not delete task: {exc}",
            task_dataframe(user)
        )


# --------------------------------------------------
# COMPLETED TASKS
# --------------------------------------------------

def show_completed(user):

    if not user:
        return empty_dataframe()

    return task_dataframe(
        user,
        completed_only=True
    )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

def logout():

    return (
        None,
        gr.update(visible=True),
        gr.update(visible=False),
        "You have signed out.",
        "",
        empty_dataframe()
    )


# ==================================================
# GRADIO INTERFACE
# ==================================================

# Gradio 6: theme and CSS are passed to launch(),
# not to the Blocks constructor.

with gr.Blocks(
    title="Student Assessment Tracker | Gradio"
) as demo:

    user_state = gr.State(None)

    # HEADER

    gr.HTML("""
    <div id="sat-header">
        <h1>STUDENT ASSESSMENT TRACKER</h1>
        <p>
            Samtse College of Education
            · Organise · Focus · Achieve
        </p>
    </div>
    """)

    # LOGIN PANEL

    with gr.Column(visible=True) as login_panel:

        gr.Markdown("## Welcome back")

        gr.Markdown(
            "Sign in to access your assessment workspace."
        )

        username_input = gr.Textbox(
            label="Username",
            placeholder="Enter your username"
        )

        password_input = gr.Textbox(
            label="Password",
            type="password",
            placeholder="Enter your password"
        )

        login_button = gr.Button(
            "Sign in",
            variant="primary"
        )

        login_message = gr.Markdown()

    # MAIN APPLICATION

    with gr.Column(visible=False) as app_panel:

        welcome_message = gr.Markdown()

        stats_display = gr.HTML()

        refresh_button = gr.Button(
            "Refresh dashboard"
        )

        # NAVIGATION TABS

        with gr.Tabs():

            # DASHBOARD

            with gr.Tab("Dashboard"):

                gr.Markdown(
                    "### Recent assessment tasks"
                )

                task_table = gr.Dataframe(
                    value=empty_dataframe(),
                    interactive=False,
                    wrap=True
                )

            # MANAGE TASKS

            with gr.Tab("Manage Tasks"):

                gr.Markdown("### Add a task")

                new_title = gr.Textbox(
                    label="Task title"
                )

                new_description = gr.Textbox(
                    label="Description",
                    lines=3
                )

                with gr.Row():

                    new_priority = gr.Dropdown(
                        ["Low", "Medium", "High"],
                        value="Medium",
                        label="Priority"
                    )

                    new_status = gr.Dropdown(
                        [
                            "Pending",
                            "In Progress",
                            "Completed"
                        ],
                        value="Pending",
                        label="Status"
                    )

                    new_due = gr.Textbox(
                        label="Due date (YYYY-MM-DD)"
                    )

                add_button = gr.Button(
                    "Add task",
                    variant="primary"
                )

                add_message = gr.Markdown()

                gr.Markdown(
                    "### Update or delete a task"
                )

                edit_id = gr.Number(
                    label="Task ID",
                    precision=0
                )

                edit_title = gr.Textbox(
                    label="Updated task title"
                )

                edit_description = gr.Textbox(
                    label="Updated description",
                    lines=2
                )

                with gr.Row():

                    edit_priority = gr.Dropdown(
                        ["Low", "Medium", "High"],
                        value="Medium",
                        label="Priority"
                    )

                    edit_status = gr.Dropdown(
                        [
                            "Pending",
                            "In Progress",
                            "Completed"
                        ],
                        value="Pending",
                        label="Status"
                    )

                    edit_due = gr.Textbox(
                        label="Due date (YYYY-MM-DD)"
                    )

                with gr.Row():

                    update_button = gr.Button(
                        "Save changes",
                        variant="primary"
                    )

                    delete_button = gr.Button(
                        "Delete task"
                    )

            # COMPLETED TASKS

            with gr.Tab("Completed Tasks"):

                gr.Markdown(
                    "### Completed assessment tasks"
                )

                completed_button = gr.Button(
                    "Load completed tasks"
                )

                completed_table = gr.Dataframe(
                    value=empty_dataframe(),
                    interactive=False,
                    wrap=True
                )

        logout_button = gr.Button(
            "Sign out"
        )

        action_message = gr.Markdown()

    # --------------------------------------------------
    # LOGIN EVENT
    # --------------------------------------------------

    login_button.click(
        fn=login,
        inputs=[
            username_input,
            password_input
        ],
        outputs=[
            user_state,
            login_panel,
            app_panel,
            login_message,
            welcome_message,
            stats_display
        ]
    ).then(
        fn=lambda user:
            task_dataframe(user)
            if user else empty_dataframe(),
        inputs=[user_state],
        outputs=[task_table]
    )

    # --------------------------------------------------
    # REFRESH EVENT
    # --------------------------------------------------

    refresh_button.click(
        fn=refresh_dashboard,
        inputs=[user_state],
        outputs=[
            stats_display,
            task_table
        ]
    )

    # --------------------------------------------------
    # ADD TASK EVENT
    # --------------------------------------------------

    add_button.click(
        fn=add_task,
        inputs=[
            user_state,
            new_title,
            new_description,
            new_priority,
            new_status,
            new_due
        ],
        outputs=[
            add_message,
            task_table
        ]
    ).then(
        fn=lambda user:
            stats_html(user) if user else "",
        inputs=[user_state],
        outputs=[stats_display]
    )

    # --------------------------------------------------
    # UPDATE TASK EVENT
    # --------------------------------------------------

    update_button.click(
        fn=update_task,
        inputs=[
            user_state,
            edit_id,
            edit_title,
            edit_description,
            edit_priority,
            edit_status,
            edit_due
        ],
        outputs=[
            action_message,
            task_table
        ]
    ).then(
        fn=lambda user:
            stats_html(user) if user else "",
        inputs=[user_state],
        outputs=[stats_display]
    )

    # --------------------------------------------------
    # DELETE TASK EVENT
    # --------------------------------------------------

    delete_button.click(
        fn=remove_task,
        inputs=[
            user_state,
            edit_id
        ],
        outputs=[
            action_message,
            task_table
        ]
    ).then(
        fn=lambda user:
            stats_html(user) if user else "",
        inputs=[user_state],
        outputs=[stats_display]
    )

    # --------------------------------------------------
    # COMPLETED TASKS EVENT
    # --------------------------------------------------

    completed_button.click(
        fn=show_completed,
        inputs=[user_state],
        outputs=[completed_table]
    )

    # --------------------------------------------------
    # LOGOUT EVENT
    # --------------------------------------------------

    logout_button.click(
        fn=logout,
        outputs=[
            user_state,
            login_panel,
            app_panel,
            login_message,
            welcome_message,
            stats_display
        ]
    )


# ==================================================
# RUN APPLICATION - GRADIO 6
# ==================================================

if __name__ == "__main__":

    demo.launch(
        server_name="127.0.0.1",
        server_port=7861,
        inbrowser=True,
        theme=gr.themes.Soft(),
        css=CSS
    )
