"""Administrator dashboard and account management."""
import tkinter as tk
from tkinter import ttk, messagebox
from interfaces.base_dashboard import BaseDashboard
from database import list_users, create_user, toggle_user
from components.theme import *

class AdminDashboard(BaseDashboard):
    def show_users(self):
        self.active_page = "Manage Users"; self.mark_nav("Manage Users"); clear_frame(self.content)
        heading(self.content, "Manage users", "Create accounts and enable or disable regular user accounts.")
        toolbar = tk.Frame(self.content, bg=BG); toolbar.pack(fill="x", pady=(0, 12))
        button(toolbar, "+ Add user", self.user_form).pack(side="left")
        panel = tk.Frame(self.content, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        panel.pack(fill="both", expand=True)
        self.user_table = ttk.Treeview(panel, columns=("id","name","username","role","status"), show="headings")
        for col, title, width in [("id","ID",55),("name","Full name",230),("username","Username",180),("role","Role",100),("status","Status",100)]:
            self.user_table.heading(col, text=title); self.user_table.column(col, width=width, anchor="w")
        self.user_table.pack(fill="both", expand=True, padx=12, pady=12)
        self.refresh_users()
        button(panel, "Enable / disable selected user", self.change_user_status, False).pack(anchor="w", padx=12, pady=(0, 12))

    def refresh_users(self):
        for item in self.user_table.get_children(): self.user_table.delete(item)
        for u in list_users():
            self.user_table.insert("", "end", values=(u["user_id"],u["full_name"],u["username"],u["role"],
                "Active" if u["active"] else "Disabled"))

    def user_form(self):
        win = tk.Toplevel(self.root); win.title("Add user"); win.geometry("430x430"); win.configure(bg=WHITE)
        win.transient(self.root); win.grab_set()
        tk.Label(win, text="Create user account", bg=WHITE, fg=NAVY, font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=24, pady=20)
        inputs = {}
        for label in ["Full name", "Username", "Temporary password"]:
            tk.Label(win, text=label, bg=WHITE, fg=NAVY, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=24)
            e = tk.Entry(win, show="•" if label == "Temporary password" else "", relief="solid", bd=1)
            e.pack(fill="x", padx=24, pady=(4, 12), ipady=6); inputs[label] = e
        tk.Label(win, text="Role", bg=WHITE, fg=NAVY, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=24)
        role = ttk.Combobox(win, values=["user","admin"], state="readonly"); role.set("user")
        role.pack(fill="x", padx=24, pady=(4, 16))
        def save():
            try:
                create_user(inputs["Username"].get(), inputs["Full name"].get(), inputs["Temporary password"].get(), role.get())
            except Exception as exc:
                messagebox.showerror("Could not create user", str(exc), parent=win); return
            win.destroy(); self.refresh_users(); messagebox.showinfo("Success", "Account created.")
        button(win, "Create account", save).pack(fill="x", padx=24, pady=(0, 20))

    def change_user_status(self):
        selection = self.user_table.selection()
        if not selection:
            messagebox.showwarning("Select a user", "Please select a user first."); return
        user_id = int(self.user_table.item(selection[0], "values")[0])
        try: toggle_user(user_id)
        except Exception as exc: messagebox.showerror("Unable to update", str(exc)); return
        self.refresh_users()
