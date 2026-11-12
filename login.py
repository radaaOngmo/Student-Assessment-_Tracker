"""Sign-in and student registration screens for Student Assessment Tracker."""
import tkinter as tk
from tkinter import messagebox

from database import authenticate, create_user
from components.theme import (
    BG, MAROON, MAROON_DARK, GOLD, WHITE, MUTED, BORDER, button
)


class LoginView:
    def __init__(self, root):
        self.root = root
        self.show_login()

    def clear(self):
        for child in self.root.winfo_children():
            child.destroy()
        self.root.configure(bg=BG)

    def shell(self):
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True, padx=34, pady=30)

        left = tk.Frame(outer, bg=MAROON_DARK, width=390)
        left.pack(side="left", fill="both")
        left.pack_propagate(False)
        tk.Frame(left, bg=GOLD, height=7).pack(fill="x")
        tk.Label(left, text="༄", bg=MAROON_DARK, fg=GOLD,
                 font=("Noto Sans", 42)).pack(anchor="w", padx=34, pady=(38, 0))
        tk.Label(left, text="STUDENT\nASSESSMENT\nTRACKER", bg=MAROON_DARK, fg=WHITE,
                 font=("Segoe UI", 25, "bold"), justify="left").pack(anchor="w", padx=34, pady=(12, 12))
        tk.Frame(left, bg=GOLD, height=3, width=84).pack(anchor="w", padx=34, pady=(5, 20))
        tk.Label(left, text="Plan clearly. Track progress.\nAchieve more every day.",
                 bg=MAROON_DARK, fg="#F2E6D4", font=("Segoe UI", 12),
                 justify="left").pack(anchor="w", padx=34)
        tk.Label(left, text="A focused workspace for your\nassessment-related tasks.",
                 bg=MAROON_DARK, fg="#D8C6B4", font=("Segoe UI", 10),
                 justify="left").pack(anchor="w", padx=34, pady=(22, 0))
        tk.Frame(left, bg=GOLD, height=7).pack(side="bottom", fill="x")

        right = tk.Frame(outer, bg=WHITE, padx=48, pady=34,
                         highlightbackground=BORDER, highlightthickness=1)
        right.pack(side="left", fill="both", expand=True)
        return right

    @staticmethod
    def add_password_field(parent, *, pady=(5, 17), width=None):
        """Create a masked password entry with a clickable show/hide eye control."""
        row = tk.Frame(parent, bg=WHITE)
        row.pack(fill="x", pady=pady)
        entry = tk.Entry(row, font=("Segoe UI", 11), show="•", relief="solid", bd=1)
        if width:
            entry.configure(width=width)
        entry.pack(side="left", fill="x", expand=True, ipady=8)
        visible = {"value": False}

        def toggle_visibility():
            visible["value"] = not visible["value"]
            entry.configure(show="" if visible["value"] else "•")
            toggle.configure(text="◉" if visible["value"] else "◎")
            toggle.configure(activebackground="#F0E7D8")

        toggle = tk.Button(
            row, text="◎", command=toggle_visibility, cursor="hand2",
            font=("Segoe UI Symbol", 14, "bold"), relief="flat", bd=0,
            bg="#F0E7D8", fg=MAROON_DARK, activeforeground=MAROON_DARK,
            padx=12, pady=4, takefocus=True,
        )
        toggle.pack(side="left", padx=(6, 0), fill="y")
        toggle.configure(takefocus=True)
        toggle.bind("<Return>", lambda event: toggle_visibility())
        return entry

    def show_login(self):
        self.clear()
        right = self.shell()
        tk.Label(right, text="Welcome back", bg=WHITE, fg=MAROON_DARK,
                 font=("Segoe UI", 25, "bold")).pack(anchor="w", pady=(30, 5))
        tk.Label(right, text="Sign in to continue to your personal workspace.",
                 bg=WHITE, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 25))

        tk.Label(right, text="Username", bg=WHITE, fg=MAROON_DARK,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.username = tk.Entry(right, font=("Segoe UI", 11), relief="solid", bd=1)
        self.username.pack(fill="x", ipady=9, pady=(7, 17))

        tk.Label(right, text="Password", bg=WHITE, fg=MAROON_DARK,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.password = self.add_password_field(right, pady=(7, 22))

        button(right, "Sign in  →", self.login).pack(fill="x")
        self.password.bind("<Return>", lambda event: self.login())
        self.username.bind("<Return>", lambda event: self.password.focus_set())
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", pady=(24, 18))
        row = tk.Frame(right, bg=WHITE)
        row.pack(fill="x")
        tk.Label(row, text="New to the tracker?", bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 10)).pack(side="left")
        tk.Button(row, text="Create student account", command=self.show_register,
                  bg=WHITE, fg=MAROON, activebackground=WHITE, relief="flat", bd=0,
                  cursor="hand2", font=("Segoe UI", 10, "bold", "underline")).pack(side="left", padx=(7, 0))
        tk.Label(right, text="Demo accounts are documented in README.md.", bg=WHITE,
                 fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(17, 0))

    def show_register(self):
        self.clear()
        right = self.shell()
        tk.Label(right, text="Create your account", bg=WHITE, fg=MAROON_DARK,
                 font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(8, 5))
        tk.Label(right, text="Register to keep your own tasks organised and private.",
                 bg=WHITE, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 16))

        self.reg_fields = {}
        for label in ("Full name", "Username", "Password", "Confirm password"):
            tk.Label(right, text=label, bg=WHITE, fg=MAROON_DARK,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")
            if label in ("Password", "Confirm password"):
                entry = self.add_password_field(right, pady=(4, 9))
            else:
                entry = tk.Entry(right, font=("Segoe UI", 11), relief="solid", bd=1)
                entry.pack(fill="x", ipady=7, pady=(4, 9))
            self.reg_fields[label] = entry

        actions = tk.Frame(right, bg=WHITE)
        actions.pack(fill="x", pady=(5, 0))
        button(actions, "Create account", self.register).pack(side="left", fill="x", expand=True, padx=(0, 8))
        button(actions, "Back to sign in", self.show_login, primary=False).pack(side="left", fill="x", expand=True)
        self.reg_fields["Confirm password"].bind("<Return>", lambda event: self.register())

    def register(self):
        full_name = self.reg_fields["Full name"].get().strip()
        username = self.reg_fields["Username"].get().strip()
        password = self.reg_fields["Password"].get()
        confirm = self.reg_fields["Confirm password"].get()
        if not full_name or not username or not password or not confirm:
            messagebox.showwarning("Missing information", "Please complete every field.", parent=self.root)
            return
        if password != confirm:
            messagebox.showerror("Passwords do not match", "Enter the same password in both password fields.", parent=self.root)
            return
        try:
            # Public registration always creates a regular student account.
            create_user(username, full_name, password, role="user")
        except Exception as exc:
            messagebox.showerror("Could not create account", str(exc), parent=self.root)
            return
        messagebox.showinfo("Account created", "Your account is ready. Please sign in with your new credentials.", parent=self.root)
        self.show_login()
        self.username.insert(0, username)
        self.password.focus_set()

    def login(self):
        user = authenticate(self.username.get(), self.password.get())
        if not user:
            messagebox.showerror(
                "Sign-in failed",
                "The username or password is incorrect, or the account is inactive.",
                parent=self.root,
            )
            return
        try:
            if user["role"] == "admin":
                from interfaces.admin_dashboard import AdminDashboard
                AdminDashboard(self.root, user)
            else:
                from interfaces.user_dashboard import UserDashboard
                UserDashboard(self.root, user)
        except Exception as exc:
            # Avoid silently leaving users with a blank window if a screen fails to load.
            messagebox.showerror(
                "Could not open dashboard",
                f"The sign-in was accepted, but the dashboard could not be opened.\n\n{type(exc).__name__}: {exc}\n\n"
                "Please copy this message when reporting the problem.",
                parent=self.root,
            )
            raise
