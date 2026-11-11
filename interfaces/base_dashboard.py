"""Shared dashboard layout and task-management screens."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from pathlib import Path
import shutil
from components.theme import *
from database import get_tasks, save_task, delete_task, dashboard_stats, list_users, update_profile, change_password
from interfaces.login import LoginView

class BaseDashboard:
    def __init__(self, root, user):
        self.root, self.user = root, user
        self.search_var = tk.StringVar()
        self.active_page = "Dashboard"
        self.render_shell()
        self.show_dashboard()

    def render_shell(self):
        clear_frame(self.root)
        shell = tk.Frame(self.root, bg=BG)
        shell.pack(fill="both", expand=True)
        sidebar = tk.Frame(shell, bg=NAVY, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        # Small institutional logo, kept intentionally modest so it does not
        # dominate the dashboard. The local asset makes the project portable.
        brand = tk.Frame(sidebar, bg=NAVY)
        brand.pack(fill="x", padx=16, pady=(18, 8))
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "samtse_college_logo.png"
        try:
            logo = tk.PhotoImage(file=str(logo_path))
            factor = max(1, (max(logo.width(), logo.height()) + 79) // 80)
            self.logo_image = logo.subsample(factor, factor)
            tk.Label(brand, image=self.logo_image, bg=NAVY).pack(side="left", padx=(0, 10))
        except (tk.TclError, OSError):
            tk.Label(brand, text="༄", bg=NAVY, fg=GOLD,
                     font=("Noto Sans", 30, "bold")).pack(side="left", padx=(0, 10))
        brand_text = tk.Frame(brand, bg=NAVY)
        brand_text.pack(side="left", fill="x", expand=True)
        tk.Label(brand_text, text="STUDENT", bg=NAVY, fg=GOLD,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(brand_text, text="ASSESSMENT\nTRACKER", bg=NAVY, fg="#F7F0E5",
                 font=("Segoe UI", 8, "bold"), justify="left").pack(anchor="w")
        # Decorative gold line inspired by traditional Bhutanese architectural trim.
        tk.Frame(sidebar, bg=GOLD, height=3).pack(fill="x", padx=16, pady=(4, 20))
        self.nav_buttons = {}
        pages = [("▦  Dashboard", self.show_dashboard), ("☷  Manage Tasks", self.show_tasks), ("✓  Completed Tasks", self.show_completed_tasks)]
        if self.user["role"] == "admin":
            pages.append(("♙  Manage Users", self.show_users))
        pages.extend([("⚙  Settings", self.show_settings), ("⇥  Sign out", self.logout)])
        for label, callback in pages:
            b = tk.Button(sidebar, text="  " + label, anchor="w", command=callback,
                bg=NAVY, fg=WHITE, activebackground=BLUE, activeforeground=WHITE,
                relief="flat", bd=0, padx=16, pady=12, font=("Segoe UI", 10), cursor="hand2")
            b.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[label] = b
        tk.Label(sidebar, text="Organise • Focus • Achieve", bg=NAVY, fg="#AFC3D4",
                 font=("Segoe UI", 8)).pack(side="bottom", pady=20)
        main = tk.Frame(shell, bg=BG)
        main.pack(side="left", fill="both", expand=True)
        top = tk.Frame(main, bg=WHITE, height=76, highlightbackground=BORDER, highlightthickness=1)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="༄  Workspace", bg=WHITE, fg=NAVY,
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=24)
        # Repeat the college mark at a small size in the top corner as requested.
        try:
            header_logo = tk.PhotoImage(file=str(logo_path))
            self.header_logo_image = header_logo.subsample(max(1, (max(header_logo.width(), header_logo.height()) + 59) // 60))
            tk.Label(top, image=self.header_logo_image, bg=WHITE).pack(side="right", padx=(8, 18), pady=5)
        except (tk.TclError, OSError):
            pass
        # User profile image appears beside the display name; the college logo remains separate.
        self.header_profile_widget = tk.Label(top, text=self.user.get("full_name", "U")[:1].upper(),
                 bg=GOLD_LIGHT, fg=MAROON_DARK, font=("Segoe UI", 11, "bold"), width=3, height=1)
        self.header_profile_widget.pack(side="right", padx=(8, 12), pady=8)
        self.refresh_header_profile()
        tk.Label(top, text=f'{self.user["full_name"]}  ·  {self.user["role"].title()}',
                 bg=WHITE, fg=MUTED, font=("Segoe UI", 10)).pack(side="right", padx=10)
        self.content = tk.Frame(main, bg=BG, padx=28, pady=24)
        self.content.pack(fill="both", expand=True)

    def mark_nav(self, page):
        for label, b in self.nav_buttons.items():
            is_active = label.endswith(page) or label.strip().endswith(page)
            b.configure(bg=BLUE if is_active else NAVY)

    def show_dashboard(self):
        self.active_page = "Dashboard"; self.mark_nav("Dashboard"); clear_frame(self.content)
        heading(self.content, f'Welcome, {self.user["full_name"]}', "Here is a quick overview of your task progress.")
        stats = dashboard_stats(self.user)
        cards = tk.Frame(self.content, bg=BG); cards.pack(fill="x", pady=(8, 22))
        values = [("All tasks", stats["total"], BLUE), ("Pending", stats["pending"], GOLD),
                  ("In progress", stats["progress"], "#7B68B2"), ("Completed", stats["completed"], GREEN)]
        if self.user["role"] == "admin":
            values.insert(0, ("Registered users", stats["users"], NAVY))
        for i, (title, value, accent) in enumerate(values):
            cards.grid_columnconfigure(i, weight=1)
            card(cards, title, value, accent).grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 0))
        # Lightweight native Tkinter charts keep the application dependency-free.
        chart_row = tk.Frame(self.content, bg=BG)
        chart_row.pack(fill="x", pady=(0, 16))
        tasks = get_tasks(self.user)
        chart_specs = [
            ("Tasks by priority", [("High", sum(t["priority"] == "High" for t in tasks), RED),
                                   ("Medium", sum(t["priority"] == "Medium" for t in tasks), GOLD),
                                   ("Low", sum(t["priority"] == "Low" for t in tasks), GREEN)]),
            ("Task status", [("Pending", sum(t["status"] == "Pending" for t in tasks), GOLD),
                              ("In progress", sum(t["status"] == "In Progress" for t in tasks), PURPLE),
                              ("Completed", sum(t["status"] == "Completed" for t in tasks), GREEN)])
        ]
        for title, items in chart_specs:
            panel = tk.Frame(chart_row, bg=WHITE, padx=16, pady=12, highlightbackground=BORDER, highlightthickness=1)
            panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
            tk.Label(panel, text=title, bg=WHITE, fg=MAROON_DARK, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 7))
            max_value = max([value for _, value, _ in items] + [1])
            for label, value, color in items:
                line = tk.Frame(panel, bg=WHITE); line.pack(fill="x", pady=3)
                tk.Label(line, text=label, bg=WHITE, fg=MUTED, width=12, anchor="w", font=("Segoe UI", 9)).pack(side="left")
                track = tk.Frame(line, bg="#F0E7D8", height=12)
                track.pack(side="left", fill="x", expand=True, padx=(4, 8))
                track.pack_propagate(False)
                tk.Frame(track, bg=color, height=12, width=max(2, int(150 * value / max_value))).pack(side="left", fill="y")
                tk.Label(line, text=str(value), bg=WHITE, fg=TEXT, width=3, anchor="e", font=("Segoe UI", 9, "bold")).pack(side="right")
        section = tk.Frame(self.content, bg=WHITE, padx=18, pady=16, highlightbackground=BORDER, highlightthickness=1)
        section.pack(fill="both", expand=True)
        tk.Label(section, text="Recent tasks", bg=WHITE, fg=MAROON_DARK, font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 12))
        self.task_table(section, compact=True)

    def task_table(self, parent, compact=False, query="", status_filter=None):
        columns = ("id", "task", "priority", "status", "due")
        if self.user["role"] == "admin":
            columns = ("id", "task", "owner", "priority", "status", "due")
        table = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")
        labels = {"id":"ID","task":"Task","owner":"Owner","priority":"Priority","status":"Status","due":"Due date"}
        widths = {"id":50,"task":260,"owner":150,"priority":100,"status":120,"due":110}
        for col in columns:
            table.heading(col, text=labels[col]); table.column(col, width=widths[col], anchor="w")
        table.pack(fill="both", expand=True)
        for task in get_tasks(self.user):
            haystack = f'{task["task_name"]} {task["description"]} {task["status"]} {task["priority"]} {task.get("owner_name","")}'.lower()
            if query.lower() not in haystack: continue
            if status_filter and task["status"] != status_filter: continue
            vals = [task["task_id"], task["task_name"]]
            if self.user["role"] == "admin": vals.append(task.get("owner_name",""))
            vals.extend([task["priority"], task["status"], task["due_date"]])
            table.insert("", "end", values=vals, tags=(task["task_id"],))
        return table

    def show_tasks(self):
        self.active_page = "Manage Tasks"; self.mark_nav("Manage Tasks"); clear_frame(self.content)
        heading(self.content, "Manage tasks", "Create, update, search, and track tasks.")
        toolbar = tk.Frame(self.content, bg=BG); toolbar.pack(fill="x", pady=(0, 12))
        self.search_var = tk.StringVar()
        tk.Entry(toolbar, textvariable=self.search_var, font=("Segoe UI", 10), relief="solid", bd=1).pack(side="left", fill="x", expand=True, ipady=7)
        button(toolbar, "Search", lambda: self.refresh_task_table(), False).pack(side="left", padx=8)
        button(toolbar, "+ Add task", lambda: self.task_form()).pack(side="left")
        self.table_holder = tk.Frame(self.content, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        self.table_holder.pack(fill="both", expand=True)
        self.refresh_task_table()

    def refresh_task_table(self, status_filter=None):
        if status_filter is None and self.active_page == "Completed Tasks":
            status_filter = "Completed"
        clear_frame(self.table_holder)
        self.table = self.task_table(self.table_holder, query=self.search_var.get(), status_filter=status_filter)
        actions = tk.Frame(self.table_holder, bg=WHITE, padx=12, pady=12); actions.pack(fill="x")
        button(actions, "Mark complete", self.mark_selected_complete).pack(side="left", padx=(0, 8))
        button(actions, "Edit selected", self.edit_selected, False).pack(side="left", padx=(0, 8))
        button(actions, "Delete selected", self.remove_selected, False).pack(side="left")

    def show_completed_tasks(self):
        self.active_page = "Completed Tasks"
        self.mark_nav("Completed Tasks")
        clear_frame(self.content)
        heading(self.content, "Completed tasks", "A focused list of tasks whose status is Completed.")
        self.search_var = tk.StringVar()
        toolbar = tk.Frame(self.content, bg=BG)
        toolbar.pack(fill="x", pady=(0, 12))
        tk.Entry(toolbar, textvariable=self.search_var, font=("Segoe UI", 10),
                 relief="solid", bd=1).pack(side="left", fill="x", expand=True, ipady=7)
        button(toolbar, "Search", lambda: self.refresh_task_table(status_filter="Completed"), False).pack(side="left", padx=8)
        self.table_holder = tk.Frame(self.content, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        self.table_holder.pack(fill="both", expand=True)
        self.refresh_task_table(status_filter="Completed")

    def mark_selected_complete(self):
        task_id = self.selected_task()
        if task_id is None:
            return
        task = next((t for t in get_tasks(self.user) if t["task_id"] == task_id), None)
        if not task:
            messagebox.showerror("Task unavailable", "The selected task could not be found.")
            return
        try:
            save_task(self.user, task_id, task["task_name"], task["description"],
                      task["priority"], "Completed", task["due_date"])
        except Exception as exc:
            messagebox.showerror("Unable to update task", str(exc))
            return
        if self.active_page == "Dashboard":
            self.show_dashboard()
        elif self.active_page == "Completed Tasks":
            self.show_completed_tasks()
        else:
            self.refresh_task_table()

    def selected_task(self):
        selection = self.table.selection()
        if not selection:
            messagebox.showwarning("Select a task", "Please select a task from the table."); return None
        return int(self.table.item(selection[0], "values")[0])

    def edit_selected(self):
        task_id = self.selected_task()
        if task_id is None: return
        task = next((t for t in get_tasks(self.user) if t["task_id"] == task_id), None)
        if task: self.task_form(task)

    def remove_selected(self):
        task_id = self.selected_task()
        if task_id is None: return
        if messagebox.askyesno("Confirm deletion", "Delete this task permanently?"):
            try: delete_task(self.user, task_id)
            except Exception as exc: messagebox.showerror("Unable to delete", str(exc)); return
            self.refresh_task_table()

    def task_form(self, task=None):
        win = tk.Toplevel(self.root); win.title("Task details"); win.geometry("470x520")
        win.configure(bg=WHITE); win.transient(self.root); win.grab_set()
        tk.Label(win, text="Edit task" if task else "Create a task", bg=WHITE, fg=NAVY,
                 font=("Segoe UI", 19, "bold")).pack(anchor="w", padx=24, pady=(22, 16))
        fields = {}
        def entry(label, value=""):
            tk.Label(win, text=label, bg=WHITE, fg=NAVY, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=24)
            e = tk.Entry(win, font=("Segoe UI", 10), relief="solid", bd=1)
            e.pack(fill="x", padx=24, pady=(5, 12), ipady=6); e.insert(0, value); fields[label] = e
        entry("Task title", task["task_name"] if task else "")
        entry("Description", task["description"] if task else "")
        entry("Due date (YYYY-MM-DD, optional)", task["due_date"] if task else "")
        tk.Label(win, text="Priority", bg=WHITE, fg=NAVY, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=24)
        priority = ttk.Combobox(win, values=["Low","Medium","High"], state="readonly")
        priority.set(task["priority"] if task else "Medium"); priority.pack(fill="x", padx=24, pady=(5, 12))
        tk.Label(win, text="Status", bg=WHITE, fg=NAVY, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=24)
        status = ttk.Combobox(win, values=["Pending","In Progress","Completed"], state="readonly")
        status.set(task["status"] if task else "Pending"); status.pack(fill="x", padx=24, pady=(5, 16))
        def save():
            due_date = fields["Due date (YYYY-MM-DD, optional)"].get().strip()
            if due_date:
                try:
                    parsed_date = date.fromisoformat(due_date)
                    if parsed_date.isoformat() != due_date:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Invalid due date", "Enter a real date in YYYY-MM-DD format, or leave it blank.", parent=win)
                    return
            try:
                save_task(self.user, task["task_id"] if task else None, fields["Task title"].get(),
                          fields["Description"].get(), priority.get(), status.get(), due_date)
            except Exception as exc:
                messagebox.showerror("Unable to save", str(exc), parent=win); return
            win.destroy()
            if self.active_page == "Dashboard": self.show_dashboard()
            elif self.active_page == "Completed Tasks": self.show_completed_tasks()
            else: self.refresh_task_table()
        button(win, "Save task", save).pack(fill="x", padx=24, pady=(0, 20))

    def show_users(self):
        messagebox.showinfo("Admin feature", "User management is available to administrators only.")

    def refresh_header_profile(self):
        """Show a chosen profile photo in the header, or a simple initial avatar."""
        path_value = self.user.get("profile_picture") or ""
        if path_value:
            path = Path(path_value)
            if not path.is_absolute():
                path = Path(__file__).resolve().parent.parent / path
            if path.exists():
                try:
                    from PIL import Image, ImageTk
                    with Image.open(path) as source:
                        image = source.convert("RGB")
                        image.thumbnail((42, 42))
                        avatar = ImageTk.PhotoImage(image)
                    self.header_profile_widget.configure(image=avatar, text="", width=42, height=42, bg=WHITE)
                    self.header_profile_widget.image = avatar
                    return
                except Exception:
                    pass
        self.header_profile_widget.configure(image="", text=(self.user.get("full_name") or "U")[:1].upper(),
                                             bg=GOLD_LIGHT, fg=MAROON_DARK, width=3, height=1)
        self.header_profile_widget.image = None

    def show_settings(self):
        self.active_page = "Settings"; self.mark_nav("Settings"); clear_frame(self.content)
        heading(self.content, "Settings", "Update your profile, profile picture, and password.")
        panel = tk.Frame(self.content, bg=WHITE, padx=24, pady=22, highlightbackground=BORDER, highlightthickness=1)
        panel.pack(fill="x", pady=(0, 14))
        tk.Label(panel, text="PROFILE INFORMATION", bg=WHITE, fg=GOLD,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 12))

        photo_row = tk.Frame(panel, bg=WHITE); photo_row.pack(fill="x", pady=(0, 14))
        self.settings_photo = tk.Label(photo_row, text=(self.user.get("full_name") or "U")[:1].upper(),
                                       bg="#F0E7D8", fg=MAROON_DARK, font=("Segoe UI", 20, "bold"),
                                       width=5, height=2)
        self.settings_photo.pack(side="left", padx=(0, 16))
        self.refresh_settings_photo()
        photo_actions = tk.Frame(photo_row, bg=WHITE); photo_actions.pack(side="left", fill="y")
        tk.Label(photo_actions, text="Profile picture", bg=WHITE, fg=NAVY,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(3, 6))
        button(photo_actions, "Choose picture…", self.choose_profile_picture, primary=False).pack(anchor="w")
        tk.Label(photo_actions, text="PNG, JPG, or JPEG. Your image is stored locally on this computer.",
                 bg=WHITE, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 0))

        tk.Label(panel, text="Full name", bg=WHITE, fg=NAVY, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.profile_name_entry = tk.Entry(panel, font=("Segoe UI", 10), relief="solid", bd=1)
        self.profile_name_entry.pack(fill="x", pady=(5, 12), ipady=7)
        self.profile_name_entry.insert(0, self.user.get("full_name", ""))
        for label, value in [("Username (cannot be changed)", self.user["username"]),
                             ("Access role", self.user["role"].title())]:
            row = tk.Frame(panel, bg=WHITE); row.pack(fill="x", pady=5)
            tk.Label(row, text=label, bg=WHITE, fg=MUTED, width=27, anchor="w").pack(side="left")
            tk.Label(row, text=value, bg=WHITE, fg=NAVY, font=("Segoe UI", 10, "bold")).pack(side="left")
        button(panel, "Save profile changes", self.save_profile_changes).pack(anchor="w", pady=(15, 0))

        password_panel = tk.Frame(self.content, bg=WHITE, padx=24, pady=20,
                                  highlightbackground=BORDER, highlightthickness=1)
        password_panel.pack(fill="x")
        tk.Label(password_panel, text="CHANGE PASSWORD", bg=WHITE, fg=GOLD,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 12))
        self.password_entries = {}
        for label in ("Current password", "New password", "Confirm new password"):
            tk.Label(password_panel, text=label, bg=WHITE, fg=NAVY,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")
            entry = tk.Entry(password_panel, show="•", font=("Segoe UI", 10), relief="solid", bd=1)
            entry.pack(fill="x", pady=(5, 10), ipady=6)
            self.password_entries[label] = entry
        tk.Label(password_panel, text="Use at least 8 characters. Your current password is required to change it.",
                 bg=WHITE, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 10))
        button(password_panel, "Change password", self.save_password_change).pack(anchor="w")

    def refresh_settings_photo(self):
        path_value = self.user.get("profile_picture") or ""
        path = Path(path_value) if path_value else None
        if path and not path.is_absolute():
            path = Path(__file__).resolve().parent.parent / path
        if path and path.exists():
            try:
                from PIL import Image, ImageTk
                with Image.open(path) as source:
                    image = source.convert("RGB")
                    image.thumbnail((86, 86))
                    photo = ImageTk.PhotoImage(image)
                self.settings_photo.configure(image=photo, text="", width=86, height=86, bg=WHITE)
                self.settings_photo.image = photo
            except Exception:
                pass

    def choose_profile_picture(self):
        chosen = filedialog.askopenfilename(parent=self.root, title="Choose profile picture",
            filetypes=[("Image files", "*.png *.jpg *.jpeg"), ("PNG images", "*.png"), ("JPEG images", "*.jpg *.jpeg")])
        if not chosen:
            return
        try:
            from PIL import Image
            with Image.open(chosen) as image:
                image.verify()
        except ImportError:
            messagebox.showerror("Image support unavailable", "Install the required image library by running: python -m pip install -r requirements.txt", parent=self.root)
            return
        except Exception:
            messagebox.showerror("Invalid image", "Please choose a valid PNG or JPEG image.", parent=self.root)
            return
        project_dir = Path(__file__).resolve().parent.parent
        picture_dir = project_dir / "assets" / "profile_pictures"
        picture_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(chosen).suffix.lower()
        if suffix not in (".png", ".jpg", ".jpeg"):
            suffix = ".png"
        destination = picture_dir / f"user_{self.user['user_id']}{suffix}"
        try:
            shutil.copy2(chosen, destination)
            relative = destination.relative_to(project_dir).as_posix()
            self.user = update_profile(self.user["user_id"], self.user.get("full_name", ""), relative)
            self.refresh_settings_photo()
            self.refresh_header_profile()
            messagebox.showinfo("Profile picture updated", "Your profile picture has been saved.", parent=self.root)
        except Exception as exc:
            messagebox.showerror("Could not save picture", str(exc), parent=self.root)

    def save_profile_changes(self):
        try:
            self.user = update_profile(self.user["user_id"], self.profile_name_entry.get(), None)
        except Exception as exc:
            messagebox.showerror("Could not update profile", str(exc), parent=self.root)
            return
        # Refresh name in the header and page content so the change is immediately visible.
        self.render_shell()
        self.show_settings()
        messagebox.showinfo("Profile updated", "Your full name has been updated.", parent=self.root)

    def save_password_change(self):
        current = self.password_entries["Current password"].get()
        new = self.password_entries["New password"].get()
        confirm = self.password_entries["Confirm new password"].get()
        if not current or not new or not confirm:
            messagebox.showwarning("Missing information", "Complete all password fields.", parent=self.root)
            return
        if new != confirm:
            messagebox.showerror("Passwords do not match", "The new password and confirmation must match.", parent=self.root)
            return
        try:
            change_password(self.user["user_id"], current, new)
        except Exception as exc:
            messagebox.showerror("Could not change password", str(exc), parent=self.root)
            return
        for entry in self.password_entries.values():
            entry.delete(0, "end")
        messagebox.showinfo("Password changed", "Your password has been changed successfully.", parent=self.root)

    def logout(self):
        if messagebox.askyesno("Sign out", "Are you sure you want to sign out?"):
            LoginView(self.root)
