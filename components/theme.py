"""Shared Bhutan-inspired visual theme and reusable widgets."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path

# Inspired by traditional Bhutanese colours and architecture; intentionally restrained
MAROON = "#6E1F2A"
MAROON_DARK = "#43131B"
NAVY = MAROON_DARK  # Shared dashboard colour alias; keeps all screens consistent
RED = "#A83A3A"
GOLD = "#C69A3A"
GOLD_LIGHT = "#E8D5A2"
BG = "#F7F2E8"
WHITE = "#FFFEFB"
TEXT = "#2E2925"
MUTED = "#776D64"
BORDER = "#E3D8C8"
GREEN = "#35745B"
BLUE = "#7D3944"
PURPLE = "#79628B"


def configure_theme(root):
    root.title("Student Assessment Tracker | Samtse College of Education")
    root.geometry("1200x760")
    root.minsize(1000, 650)
    root.configure(bg=BG)
    # Restrained Bhutan-inspired palette: maroon, gold, ivory, with a subtle
    # traditional-window motif made from simple Tkinter shapes and borders.
    try:
        icon_path = Path(__file__).resolve().parent.parent / "assets" / "assessment_tracker_icon.png"
        if icon_path.exists():
            app_icon = tk.PhotoImage(file=str(icon_path))
            root.iconphoto(True, app_icon.subsample(max(1, app_icon.width() // 48)))
            root._app_icon_ref = app_icon
    except tk.TclError:
        pass
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Treeview", background=WHITE, foreground=TEXT, fieldbackground=WHITE,
                    rowheight=34, borderwidth=0, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", background="#EFE4D2", foreground=MAROON_DARK,
                    font=("Segoe UI", 10, "bold"), relief="flat", padding=8)
    style.map("Treeview", background=[("selected", "#F0E1BD")], foreground=[("selected", MAROON_DARK)])
    style.configure("TCombobox", padding=6)
    style.configure("TEntry", padding=7)


def button(parent, text, command, primary=True):
    return tk.Button(parent, text=text, command=command, cursor="hand2",
        font=("Segoe UI", 10, "bold"), relief="flat", bd=0, padx=15, pady=9,
        bg=MAROON if primary else "#F0E7D8", fg=WHITE if primary else MAROON_DARK,
        activebackground=GOLD if primary else GOLD_LIGHT,
        activeforeground=MAROON_DARK)


def heading(parent, title, subtitle=""):
    tk.Label(parent, text=title, bg=BG, fg=MAROON_DARK, font=("Segoe UI", 22, "bold")).pack(anchor="w")
    if subtitle:
        tk.Label(parent, text=subtitle, bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 16))


def card(parent, title, value, accent=MAROON):
    frame = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
    tk.Frame(frame, bg=accent, width=5).pack(side="left", fill="y")
    inner = tk.Frame(frame, bg=WHITE, padx=16, pady=13)
    inner.pack(side="left", fill="both", expand=True)
    tk.Label(inner, text=title.upper(), bg=WHITE, fg=MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w")
    tk.Label(inner, text=str(value), bg=WHITE, fg=MAROON_DARK, font=("Segoe UI", 23, "bold")).pack(anchor="w", pady=(4, 0))
    return frame


def clear_frame(frame):
    for child in frame.winfo_children():
        child.destroy()
