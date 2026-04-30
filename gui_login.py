"""
Modern Login Window for Library Management System (v2.1)
- Step 1: Role selection — 2x2 card grid
- Step 2: Login form with "Remember me" + "Forgot password?"
- Light / Dark theme toggle
- Decorative library banner illustration
- Session persistence (~/.lms_session.json)
"""

import json
import os
import tkinter as tk
from tkinter import messagebox
from auth import login
from forgot_password import open_forgot_password


# ============================================================
# THEME PALETTES
# ============================================================
THEMES = {
    "light": {
        "name": "light",
        "NAVY": "#0B1F3A",
        "GOLD": "#B8860B",
        "GOLD_LIGHT": "#D4A22E",
        "BG": "#F5F7FB",
        "CARD_BG": "#FFFFFF",
        "TEXT": "#1F2937",
        "TEXT_MUTED": "#6B7280",
        "ACCENT": "#1F4E79",
        "BORDER": "#E5E7EB",
        "INPUT_BG": "#F9FAFB",
        "INPUT_BORDER": "#D1D5DB",
        "ERROR": "#DC2626",
        "SUCCESS": "#10B981",
        "INFO_BG": "#EFF6FF",
        "INFO_FG": "#1E40AF",
        "INFO_BORDER": "#BFDBFE",
        "BANNER": "assets/login_banner_light.png",
    },
    "dark": {
        "name": "dark",
        "NAVY": "#0F172A",
        "GOLD": "#D4A22E",
        "GOLD_LIGHT": "#F5C453",
        "BG": "#0B1220",
        "CARD_BG": "#1A2238",
        "TEXT": "#E5E7EB",
        "TEXT_MUTED": "#9CA3AF",
        "ACCENT": "#3B82F6",
        "BORDER": "#2A3550",
        "INPUT_BG": "#0F1A30",
        "INPUT_BORDER": "#3B4865",
        "ERROR": "#F87171",
        "SUCCESS": "#34D399",
        "INFO_BG": "#1E3A5F",
        "INFO_FG": "#BFDBFE",
        "INFO_BORDER": "#3B82F6",
        "BANNER": "assets/login_banner_dark.png",
    },
}


# ============================================================
# Session persistence
# ============================================================
SESSION_FILE = os.path.join(os.path.expanduser("~"), ".lms_session.json")


def load_session():
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_session(data):
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


SESSION = load_session()
CURRENT_THEME_NAME = SESSION.get("theme", "light")
T = THEMES[CURRENT_THEME_NAME]


# ============================================================
# Roles
# ============================================================
ROLES = [
    {
        "code": "SUPER_ADMIN",
        "title": "Super Admin",
        "subtitle": "Full system control",
        "desc": "Multi-institution access, permission management",
        "icon": "👑",
        "accent": "#7C3AED",
        "expected_db_roles": ("SUPER_ADMIN",),
    },
    {
        "code": "ADMIN",
        "title": "Admin / Librarian",
        "subtitle": "Library operations",
        "desc": "Manage books, users, transactions, messages",
        "icon": "🛠️",
        "accent": "#1F4E79",
        "expected_db_roles": ("ADMIN",),
    },
    {
        "code": "STUDENT",
        "title": "Student",
        "subtitle": "Browse & borrow",
        "desc": "View books, see issued items, fines, messages",
        "icon": "🎓",
        "accent": "#059669",
        "expected_db_roles": ("STUDENT", "USER", "OTHER"),
    },
    {
        "code": "TEACHER",
        "title": "Teacher / Faculty",
        "subtitle": "Faculty access",
        "desc": "Borrow research books, send queries to admin",
        "icon": "👨‍🏫",
        "accent": "#B91C1C",
        "expected_db_roles": ("TEACHER", "USER"),
    },
]


# ============================================================
# Root window
# ============================================================
root = tk.Tk()
root.title("Library Management System — Login")
root.geometry("620x780")
root.resizable(False, False)
root.configure(bg=T["BG"])

# Center window
root.update_idletasks()
W, H = 620, 780
x = (root.winfo_screenwidth() - W) // 2
y = (root.winfo_screenheight() - H) // 2
root.geometry(f"{W}x{H}+{x}+{y}")


# Holds in-memory PhotoImage refs (Tkinter requires keeping references)
IMG_REFS = {}


def load_banner():
    """Load banner image for current theme; return PhotoImage or None."""
    path = T["BANNER"]
    if not os.path.exists(path):
        return None
    try:
        # Use tk.PhotoImage for PNG (works without PIL at runtime)
        # PNG with alpha is supported in Tk 8.6+
        img = tk.PhotoImage(file=path)
        IMG_REFS[T["name"]] = img
        return img
    except Exception:
        return None


# ============================================================
# Helpers
# ============================================================
def clear_root():
    for widget in root.winfo_children():
        widget.destroy()


def apply_theme(theme_name):
    """Switch the active theme and re-render the current screen."""
    global CURRENT_THEME_NAME, T
    CURRENT_THEME_NAME = theme_name
    T = THEMES[theme_name]
    SESSION["theme"] = theme_name
    save_session(SESSION)
    root.configure(bg=T["BG"])
    # Re-render whichever screen we're on
    SCREEN_STATE["render"]()


SCREEN_STATE = {"render": None, "selected_role": None}


# ============================================================
# Header (with banner + theme toggle)
# ============================================================
def build_header(parent):
    header = tk.Frame(parent, bg=T["NAVY"])
    header.pack(fill="x")

    # Top gold band
    tk.Frame(header, bg=T["GOLD"], height=4).pack(fill="x")

    # Title row with theme toggle on the right
    title_row = tk.Frame(header, bg=T["NAVY"])
    title_row.pack(fill="x", pady=(14, 6))

    spacer_l = tk.Frame(title_row, bg=T["NAVY"], width=44)
    spacer_l.pack(side="left")

    title_block = tk.Frame(title_row, bg=T["NAVY"])
    title_block.pack(side="left", expand=True)
    tk.Label(title_block, text="📚 Library Management System",
             bg=T["NAVY"], fg="white",
             font=("Segoe UI", 15, "bold")).pack()
    tk.Label(title_block, text="Multi-Role Secure Library Platform",
             bg=T["NAVY"], fg="#B8C5D6" if T["name"] == "light" else "#94A3B8",
             font=("Segoe UI", 9, "italic")).pack()

    # Theme toggle button
    toggle_text = "🌙" if T["name"] == "light" else "☀️"
    next_theme = "dark" if T["name"] == "light" else "light"
    toggle_btn = tk.Label(title_row, text=toggle_text, bg=T["NAVY"],
                          fg=T["GOLD_LIGHT"],
                          font=("Segoe UI Emoji", 16),
                          cursor="hand2", padx=12)
    toggle_btn.pack(side="right")
    toggle_btn.bind("<Button-1>", lambda e: apply_theme(next_theme))

    # Banner illustration
    banner_img = load_banner()
    if banner_img is not None:
        banner_label = tk.Label(header, image=banner_img, bg=T["NAVY"],
                                bd=0)
        banner_label.image = banner_img
        banner_label.pack(pady=(4, 8))
    else:
        # Fallback decorative line if image missing
        tk.Frame(header, bg=T["BG"], height=20).pack()

    # Bottom gold band
    tk.Frame(parent, bg=T["GOLD"], height=3).pack(fill="x")
    return header


# ============================================================
# Role Card (2x2 grid version)
# ============================================================
def make_role_card(parent, role, on_click, row, col):
    card = tk.Frame(parent, bg=T["CARD_BG"], highlightthickness=2,
                    highlightbackground=T["BORDER"], cursor="hand2")
    card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

    inner = tk.Frame(card, bg=T["CARD_BG"])
    inner.pack(fill="both", expand=True, padx=12, pady=12)

    # Icon circle (top)
    icon_frame = tk.Frame(inner, bg=role["accent"], width=48, height=48)
    icon_frame.pack()
    icon_frame.pack_propagate(False)
    icon_lbl = tk.Label(icon_frame, text=role["icon"], bg=role["accent"],
                        fg="white", font=("Segoe UI Emoji", 20))
    icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

    title_lbl = tk.Label(inner, text=role["title"], bg=T["CARD_BG"],
                         fg=T["TEXT"], font=("Segoe UI", 12, "bold"))
    title_lbl.pack(pady=(8, 0))

    sub_lbl = tk.Label(inner, text=role["subtitle"], bg=T["CARD_BG"],
                       fg=role["accent"], font=("Segoe UI", 9, "bold"))
    sub_lbl.pack()

    desc_lbl = tk.Label(inner, text=role["desc"], bg=T["CARD_BG"],
                        fg=T["TEXT_MUTED"], font=("Segoe UI", 8),
                        wraplength=180, justify="center")
    desc_lbl.pack(pady=(4, 6))

    arrow_lbl = tk.Label(inner, text="Continue  ›", bg=T["CARD_BG"],
                         fg=role["accent"], font=("Segoe UI", 9, "bold"))
    arrow_lbl.pack()

    hover_bg = "#F3F4F6" if T["name"] == "light" else "#22304D"

    def set_bg(color):
        for w in (card, inner, title_lbl, sub_lbl, desc_lbl, arrow_lbl):
            try:
                w.config(bg=color)
            except tk.TclError:
                pass

    def on_enter(_):
        card.config(highlightbackground=role["accent"])
        set_bg(hover_bg)

    def on_leave(_):
        card.config(highlightbackground=T["BORDER"])
        set_bg(T["CARD_BG"])

    def on_click_event(_):
        on_click(role)

    for w in (card, inner, icon_frame, icon_lbl, title_lbl,
              sub_lbl, desc_lbl, arrow_lbl):
        w.bind("<Enter>", on_enter)
        w.bind("<Leave>", on_leave)
        w.bind("<Button-1>", on_click_event)


# ============================================================
# SCREEN 1 — Role selection (2x2 grid)
# ============================================================
def show_role_selection():
    SCREEN_STATE["render"] = show_role_selection
    clear_root()
    build_header(root)

    body = tk.Frame(root, bg=T["BG"])
    body.pack(fill="both", expand=True, padx=24, pady=14)

    tk.Label(body, text="आप कैसे login करना चाहते हैं?",
             bg=T["BG"], fg=T["TEXT"],
             font=("Segoe UI", 14, "bold")).pack(anchor="w")
    tk.Label(body, text="Choose your role to continue",
             bg=T["BG"], fg=T["TEXT_MUTED"],
             font=("Segoe UI", 9, "italic")).pack(anchor="w", pady=(0, 10))

    # 2x2 grid
    grid_frame = tk.Frame(body, bg=T["BG"])
    grid_frame.pack(fill="both", expand=True)
    grid_frame.columnconfigure(0, weight=1, uniform="role")
    grid_frame.columnconfigure(1, weight=1, uniform="role")
    grid_frame.rowconfigure(0, weight=1, uniform="role")
    grid_frame.rowconfigure(1, weight=1, uniform="role")

    for idx, role in enumerate(ROLES):
        r, c = divmod(idx, 2)
        make_role_card(grid_frame, role, show_login_form, r, c)

    # Footer
    footer = tk.Frame(root, bg=T["BG"])
    footer.pack(fill="x", side="bottom", pady=8)
    tk.Label(footer, text="Developed by Ajeet Prasad  •  v2.1",
             bg=T["BG"], fg=T["TEXT_MUTED"],
             font=("Segoe UI", 8, "italic")).pack()


# ============================================================
# SCREEN 2 — Login form
# ============================================================
def show_login_form(selected_role):
    SCREEN_STATE["selected_role"] = selected_role
    SCREEN_STATE["render"] = lambda: show_login_form(selected_role)

    clear_root()
    build_header(root)

    body = tk.Frame(root, bg=T["BG"])
    body.pack(fill="both", expand=True, padx=28, pady=12)

    # Top row: back link + role badge
    top_row = tk.Frame(body, bg=T["BG"])
    top_row.pack(fill="x")

    back_link = tk.Label(top_row, text="←  Change Role", bg=T["BG"],
                         fg=T["ACCENT"],
                         font=("Segoe UI", 9, "underline"), cursor="hand2")
    back_link.pack(side="left")
    back_link.bind("<Button-1>", lambda e: show_role_selection())

    badge = tk.Label(top_row,
                     text=f"  {selected_role['icon']}  {selected_role['title']}  ",
                     bg=selected_role["accent"], fg="white",
                     font=("Segoe UI", 10, "bold"),
                     padx=8, pady=4)
    badge.pack(side="right")

    # Welcome
    tk.Label(body, text="Welcome Back!", bg=T["BG"], fg=T["TEXT"],
             font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(12, 0))
    tk.Label(body, text="कृपया अपनी credentials enter करें",
             bg=T["BG"], fg=T["TEXT_MUTED"],
             font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 10))

    # Card
    card = tk.Frame(body, bg=T["CARD_BG"], highlightthickness=1,
                    highlightbackground=T["BORDER"])
    card.pack(fill="x")

    inner = tk.Frame(card, bg=T["CARD_BG"])
    inner.pack(fill="x", padx=22, pady=18)

    # Username
    tk.Label(inner, text="Username / User ID", bg=T["CARD_BG"], fg=T["TEXT"],
             font=("Segoe UI", 10, "bold")).pack(anchor="w")
    user_entry = tk.Entry(inner, font=("Segoe UI", 11), bg=T["INPUT_BG"],
                          fg=T["TEXT"], insertbackground=T["TEXT"],
                          relief="flat", highlightthickness=1,
                          highlightcolor=selected_role["accent"],
                          highlightbackground=T["INPUT_BORDER"])
    user_entry.pack(fill="x", ipady=9, pady=(4, 12))

    # Pre-fill if remembered
    last_role = SESSION.get("last_role")
    if SESSION.get("remember") and last_role == selected_role["code"]:
        last_username = SESSION.get("last_username", "")
        if last_username:
            user_entry.insert(0, last_username)

    # Password label row with forgot link
    pw_row = tk.Frame(inner, bg=T["CARD_BG"])
    pw_row.pack(fill="x")
    tk.Label(pw_row, text="Password", bg=T["CARD_BG"], fg=T["TEXT"],
             font=("Segoe UI", 10, "bold")).pack(side="left")

    forgot_link = tk.Label(pw_row, text="Forgot password?",
                           bg=T["CARD_BG"], fg=T["ACCENT"],
                           font=("Segoe UI", 9, "underline"),
                           cursor="hand2")
    forgot_link.pack(side="right")
    forgot_link.bind("<Button-1>",
                     lambda e: open_forgot_password(root, theme=T))

    # Password input + eye toggle
    pw_frame = tk.Frame(inner, bg=T["CARD_BG"])
    pw_frame.pack(fill="x", pady=(4, 10))

    pw_entry = tk.Entry(pw_frame, show="●", font=("Segoe UI", 11),
                        bg=T["INPUT_BG"], fg=T["TEXT"],
                        insertbackground=T["TEXT"],
                        relief="flat", highlightthickness=1,
                        highlightcolor=selected_role["accent"],
                        highlightbackground=T["INPUT_BORDER"])
    pw_entry.pack(side="left", fill="x", expand=True, ipady=9)

    show_pw = tk.BooleanVar(value=False)

    def toggle_pw():
        if show_pw.get():
            pw_entry.config(show="●")
            eye_btn.config(text="👁")
            show_pw.set(False)
        else:
            pw_entry.config(show="")
            eye_btn.config(text="🙈")
            show_pw.set(True)

    eye_btn = tk.Label(pw_frame, text="👁", bg=T["INPUT_BG"],
                       fg=T["TEXT_MUTED"],
                       font=("Segoe UI Emoji", 12), cursor="hand2",
                       padx=8)
    eye_btn.pack(side="right", fill="y")
    eye_btn.bind("<Button-1>", lambda e: toggle_pw())

    # Remember me checkbox
    remember_var = tk.BooleanVar(value=bool(SESSION.get("remember", False)
                                            and last_role == selected_role["code"]))

    rem_row = tk.Frame(inner, bg=T["CARD_BG"])
    rem_row.pack(fill="x", pady=(0, 8))

    rem_cb = tk.Checkbutton(rem_row, text=" Remember me",
                            variable=remember_var,
                            bg=T["CARD_BG"], fg=T["TEXT"],
                            activebackground=T["CARD_BG"],
                            activeforeground=T["TEXT"],
                            selectcolor=T["INPUT_BG"],
                            font=("Segoe UI", 9), cursor="hand2",
                            bd=0, highlightthickness=0,
                            anchor="w")
    rem_cb.pack(side="left")

    rem_hint = tk.Label(rem_row, text="(saves username only — never password)",
                        bg=T["CARD_BG"], fg=T["TEXT_MUTED"],
                        font=("Segoe UI", 8, "italic"))
    rem_hint.pack(side="left", padx=(2, 0))

    # Status label
    status_label = tk.Label(inner, text="", bg=T["CARD_BG"], fg=T["ERROR"],
                            font=("Segoe UI", 9), wraplength=460,
                            justify="left")
    status_label.pack(fill="x", pady=(2, 0))

    # Login action
    def do_login():
        username = user_entry.get().strip()
        password = pw_entry.get()

        if not username or not password:
            status_label.config(text="⚠ कृपया दोनों fields भरें।",
                                fg=T["ERROR"])
            return

        status_label.config(text="🔄 Verifying credentials...",
                            fg=T["TEXT_MUTED"])
        root.update_idletasks()

        user = login(username, password)

        if not user:
            status_label.config(
                text="✗ गलत username या password। कृपया दुबारा try करें।",
                fg=T["ERROR"])
            return

        actual_role = (user.get("Role") or "").upper()
        expected = selected_role["expected_db_roles"]
        if actual_role not in expected:
            status_label.config(
                text=f"⚠ यह account '{actual_role}' role का है — "
                     f"लेकिन आपने '{selected_role['title']}' select किया है। "
                     f"कृपया सही role select करें।",
                fg=T["ERROR"])
            return

        # Persist remember-me
        if remember_var.get():
            SESSION["remember"] = True
            SESSION["last_username"] = username
            SESSION["last_role"] = selected_role["code"]
        else:
            SESSION["remember"] = False
            SESSION.pop("last_username", None)
            SESSION.pop("last_role", None)
        save_session(SESSION)

        status_label.config(text="✓ Login successful! Loading dashboard...",
                            fg=T["SUCCESS"])
        root.update_idletasks()
        root.after(400, lambda: launch_dashboard(user))

    # Login button
    btn_container = tk.Frame(inner, bg=T["CARD_BG"])
    btn_container.pack(fill="x", pady=(10, 0))

    login_btn = tk.Button(btn_container, text="🔓  Login Securely",
                          bg=T["NAVY"], fg="white",
                          font=("Segoe UI", 11, "bold"),
                          relief="flat", cursor="hand2",
                          activebackground=T["ACCENT"],
                          activeforeground="white",
                          command=do_login)
    login_btn.pack(fill="x", ipady=10)

    def hover_in(_):
        login_btn.config(bg=T["ACCENT"])

    def hover_out(_):
        login_btn.config(bg=T["NAVY"])

    login_btn.bind("<Enter>", hover_in)
    login_btn.bind("<Leave>", hover_out)

    # Enter key submits
    root.bind("<Return>", lambda e: do_login())

    # Info note
    note = tk.Frame(body, bg=T["INFO_BG"], highlightthickness=1,
                    highlightbackground=T["INFO_BORDER"])
    note.pack(fill="x", pady=(14, 0))
    tk.Label(note,
             text=f"🔒 Password protected by bcrypt. "
                  f"Logging in as '{selected_role['title']}' • Secure session.",
             bg=T["INFO_BG"], fg=T["INFO_FG"],
             font=("Segoe UI", 8), wraplength=480, justify="left",
             padx=10, pady=8).pack()

    # Footer
    footer = tk.Frame(root, bg=T["BG"])
    footer.pack(fill="x", side="bottom", pady=8)
    tk.Label(footer, text="Developed by Ajeet Prasad  •  v2.1",
             bg=T["BG"], fg=T["TEXT_MUTED"],
             font=("Segoe UI", 8, "italic")).pack()

    # Focus
    if not user_entry.get():
        user_entry.focus_set()
    else:
        pw_entry.focus_set()


# ============================================================
# Dashboard launcher
# ============================================================
def launch_dashboard(user):
    role = (user.get("Role") or "").upper()
    root.destroy()

    from gui_super_admin import open_super_admin_dashboard
    from gui_admin import open_admin_dashboard
    from gui_user import open_user_dashboard

    if role == "SUPER_ADMIN":
        open_super_admin_dashboard(user)
    elif role == "ADMIN":
        open_admin_dashboard(user)
    elif role in ("USER", "STUDENT", "TEACHER", "OTHER"):
        open_user_dashboard(user)
    else:
        messagebox.showerror("Error", f"Unknown role: {role}")


# ============================================================
# Boot
# ============================================================
print("WELCOME TO LOGIN WINDOW (v2.1 — Modern UI + Theme + Remember)")

# Auto-open last role's login form if remember-me was set
last = SESSION.get("last_role") if SESSION.get("remember") else None
if last:
    matched = next((r for r in ROLES if r["code"] == last), None)
    if matched:
        show_login_form(matched)
    else:
        show_role_selection()
else:
    show_role_selection()

root.mainloop()
print("LOGIN WINDOW CLOSED")
