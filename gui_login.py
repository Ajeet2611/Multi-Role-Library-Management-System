"""
Modern Login Window for Library Management System
- Step 1: Role selection screen (कार्ड-style chooser)
- Step 2: Login form (with Forgot Password option)
- Navy + Gold theme matching documentation/presentation
"""

import tkinter as tk
from tkinter import messagebox
from auth import login
from forgot_password import open_forgot_password


# ===== Theme Colors =====
NAVY = "#0B1F3A"
NAVY_DEEP = "#081729"
GOLD = "#B8860B"
GOLD_LIGHT = "#D4A22E"
LIGHT_BG = "#F5F7FB"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#1F2937"
TEXT_MUTED = "#6B7280"
ACCENT_BLUE = "#1F4E79"
BORDER_GREY = "#E5E7EB"


# ===== Role configuration =====
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
        "accent": ACCENT_BLUE,
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


# ===== Main App Window =====
root = tk.Tk()
root.title("Library Management System — Login")
root.geometry("520x680")
root.resizable(False, False)
root.configure(bg=LIGHT_BG)

# Center the window on screen
root.update_idletasks()
w, h = 520, 680
x = (root.winfo_screenwidth() - w) // 2
y = (root.winfo_screenheight() - h) // 2
root.geometry(f"{w}x{h}+{x}+{y}")


# ===== Helper: clear current screen =====
def clear_root():
    for widget in root.winfo_children():
        widget.destroy()


# ===== Reusable: gradient-style top header =====
def build_header(parent, height=170):
    header = tk.Frame(parent, bg=NAVY, height=height)
    header.pack(fill="x")
    header.pack_propagate(False)

    # Decorative top gold band
    tk.Frame(header, bg=GOLD, height=4).pack(fill="x")

    # Logo emoji
    tk.Label(header, text="📚", bg=NAVY, fg=GOLD,
             font=("Segoe UI Emoji", 36)).pack(pady=(20, 0))

    # Title
    tk.Label(header, text="Library Management System",
             bg=NAVY, fg="white",
             font=("Segoe UI", 16, "bold")).pack()

    # Subtitle
    tk.Label(header, text="Multi-Role Secure Library Platform",
             bg=NAVY, fg="#B8C5D6",
             font=("Segoe UI", 9, "italic")).pack(pady=(2, 0))

    # Bottom gold band
    tk.Frame(parent, bg=GOLD, height=3).pack(fill="x")

    return header


# ===== Role Card Widget =====
def make_role_card(parent, role, on_click):
    """Create an attractive role card with hover effect."""
    card = tk.Frame(parent, bg=CARD_BG, highlightthickness=2,
                    highlightbackground=BORDER_GREY, cursor="hand2")
    card.pack(fill="x", pady=6)

    inner = tk.Frame(card, bg=CARD_BG)
    inner.pack(fill="x", padx=14, pady=10)

    # Left: Icon in colored circle
    icon_frame = tk.Frame(inner, bg=role["accent"], width=52, height=52)
    icon_frame.pack(side="left", padx=(0, 14))
    icon_frame.pack_propagate(False)
    tk.Label(icon_frame, text=role["icon"], bg=role["accent"], fg="white",
             font=("Segoe UI Emoji", 20)).place(relx=0.5, rely=0.5,
                                                anchor="center")

    # Middle: Text block
    text_frame = tk.Frame(inner, bg=CARD_BG)
    text_frame.pack(side="left", fill="both", expand=True)

    tk.Label(text_frame, text=role["title"], bg=CARD_BG, fg=TEXT_DARK,
             font=("Segoe UI", 12, "bold")).pack(anchor="w")
    tk.Label(text_frame, text=role["subtitle"], bg=CARD_BG, fg=role["accent"],
             font=("Segoe UI", 9, "bold")).pack(anchor="w")
    tk.Label(text_frame, text=role["desc"], bg=CARD_BG, fg=TEXT_MUTED,
             font=("Segoe UI", 8), wraplength=320,
             justify="left").pack(anchor="w", pady=(2, 0))

    # Right: Arrow
    arrow = tk.Label(inner, text="›", bg=CARD_BG, fg=role["accent"],
                     font=("Segoe UI", 24, "bold"))
    arrow.pack(side="right", padx=(8, 0))

    # Hover effects
    def on_enter(_):
        card.config(highlightbackground=role["accent"])
        for child in [card, inner, text_frame] + list(text_frame.winfo_children()):
            try:
                child.config(bg="#F9FAFB")
            except tk.TclError:
                pass
        arrow.config(bg="#F9FAFB")

    def on_leave(_):
        card.config(highlightbackground=BORDER_GREY)
        for child in [card, inner, text_frame] + list(text_frame.winfo_children()):
            try:
                child.config(bg=CARD_BG)
            except tk.TclError:
                pass
        arrow.config(bg=CARD_BG)

    def on_click_event(_):
        on_click(role)

    # Bind to all child widgets so click anywhere works
    for widget in [card, inner, text_frame, arrow] + \
                  list(text_frame.winfo_children()) + \
                  list(inner.winfo_children()):
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.bind("<Button-1>", on_click_event)


# ===== SCREEN 1: Role Selection =====
def show_role_selection():
    clear_root()
    build_header(root, height=160)

    body = tk.Frame(root, bg=LIGHT_BG)
    body.pack(fill="both", expand=True, padx=24, pady=18)

    tk.Label(body, text="आप कैसे login करना चाहते हैं?",
             bg=LIGHT_BG, fg=TEXT_DARK,
             font=("Segoe UI", 13, "bold")).pack(anchor="w")
    tk.Label(body, text="Choose your role to continue",
             bg=LIGHT_BG, fg=TEXT_MUTED,
             font=("Segoe UI", 9, "italic")).pack(anchor="w", pady=(0, 12))

    # 4 role cards
    cards_container = tk.Frame(body, bg=LIGHT_BG)
    cards_container.pack(fill="both", expand=True)

    for role in ROLES:
        make_role_card(cards_container, role, show_login_form)

    # Footer
    footer = tk.Frame(root, bg=LIGHT_BG)
    footer.pack(fill="x", side="bottom", pady=10)
    tk.Label(footer, text="Developed by Ajeet Prasad  •  v2.0",
             bg=LIGHT_BG, fg=TEXT_MUTED,
             font=("Segoe UI", 8, "italic")).pack()


# ===== SCREEN 2: Login Form =====
def show_login_form(selected_role):
    clear_root()
    build_header(root, height=160)

    body = tk.Frame(root, bg=LIGHT_BG)
    body.pack(fill="both", expand=True, padx=28, pady=20)

    # Back link
    back_link = tk.Label(body, text="←  Change Role", bg=LIGHT_BG,
                        fg=ACCENT_BLUE,
                        font=("Segoe UI", 9, "underline"), cursor="hand2")
    back_link.pack(anchor="w")
    back_link.bind("<Button-1>", lambda e: show_role_selection())

    # Selected role badge
    badge_frame = tk.Frame(body, bg=selected_role["accent"])
    badge_frame.pack(anchor="w", pady=(10, 0))
    tk.Label(badge_frame,
             text=f"  {selected_role['icon']}  {selected_role['title']}  ",
             bg=selected_role["accent"], fg="white",
             font=("Segoe UI", 10, "bold"),
             padx=8, pady=4).pack()

    # Welcome
    tk.Label(body, text="Welcome Back!", bg=LIGHT_BG, fg=TEXT_DARK,
             font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(14, 0))
    tk.Label(body, text="कृपया अपनी credentials enter करें",
             bg=LIGHT_BG, fg=TEXT_MUTED,
             font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 16))

    # White login card
    card = tk.Frame(body, bg=CARD_BG, highlightthickness=1,
                    highlightbackground=BORDER_GREY)
    card.pack(fill="x")

    inner = tk.Frame(card, bg=CARD_BG)
    inner.pack(fill="x", padx=22, pady=20)

    # Username
    tk.Label(inner, text="Username / User ID", bg=CARD_BG, fg=TEXT_DARK,
             font=("Segoe UI", 10, "bold")).pack(anchor="w")
    user_entry = tk.Entry(inner, font=("Segoe UI", 11), bg="#F9FAFB",
                          relief="flat", highlightthickness=1,
                          highlightcolor=selected_role["accent"],
                          highlightbackground="#D1D5DB")
    user_entry.pack(fill="x", ipady=9, pady=(4, 14))

    # Password
    pw_label_row = tk.Frame(inner, bg=CARD_BG)
    pw_label_row.pack(fill="x")
    tk.Label(pw_label_row, text="Password", bg=CARD_BG, fg=TEXT_DARK,
             font=("Segoe UI", 10, "bold")).pack(side="left")

    forgot_link = tk.Label(pw_label_row, text="Forgot password?",
                           bg=CARD_BG, fg=ACCENT_BLUE,
                           font=("Segoe UI", 9, "underline"),
                           cursor="hand2")
    forgot_link.pack(side="right")
    forgot_link.bind("<Button-1>",
                     lambda e: open_forgot_password(root))

    # Password input + show/hide
    pw_frame = tk.Frame(inner, bg=CARD_BG)
    pw_frame.pack(fill="x", pady=(4, 4))

    pw_entry = tk.Entry(pw_frame, show="●", font=("Segoe UI", 11),
                        bg="#F9FAFB", relief="flat", highlightthickness=1,
                        highlightcolor=selected_role["accent"],
                        highlightbackground="#D1D5DB")
    pw_entry.pack(side="left", fill="x", expand=True, ipady=9)

    show_pw = tk.BooleanVar(value=False)

    def toggle_pw():
        if show_pw.get():
            pw_entry.config(show="")
            eye_btn.config(text="🙈")
        else:
            pw_entry.config(show="●")
            eye_btn.config(text="👁")
        show_pw.set(not show_pw.get())

    eye_btn = tk.Label(pw_frame, text="👁", bg="#F9FAFB", fg=TEXT_MUTED,
                       font=("Segoe UI Emoji", 12), cursor="hand2",
                       padx=8)
    eye_btn.pack(side="right", fill="y")
    eye_btn.bind("<Button-1>", lambda e: toggle_pw())

    # Status label for inline errors
    status_label = tk.Label(inner, text="", bg=CARD_BG, fg="#DC2626",
                            font=("Segoe UI", 9), wraplength=400,
                            justify="left")
    status_label.pack(fill="x", pady=(8, 0))

    # Login button
    def do_login():
        username = user_entry.get().strip()
        password = pw_entry.get()

        if not username or not password:
            status_label.config(text="⚠ कृपया दोनों fields भरें।")
            return

        status_label.config(text="🔄 Verifying credentials...",
                           fg=TEXT_MUTED)
        root.update_idletasks()

        user = login(username, password)

        if not user:
            status_label.config(text="✗ गलत username या password। "
                                "कृपया दुबारा try करें।", fg="#DC2626")
            return

        # Verify selected role matches DB role (helpful guidance)
        actual_role = (user.get("Role") or "").upper()
        expected = selected_role["expected_db_roles"]
        if actual_role not in expected:
            status_label.config(
                text=f"⚠ यह account '{actual_role}' role का है — "
                     f"लेकिन आपने '{selected_role['title']}' select किया है। "
                     f"कृपया सही role select करें।",
                fg="#DC2626")
            return

        # Success
        status_label.config(text="✓ Login successful! Loading dashboard...",
                           fg="#10B981")
        root.update_idletasks()
        root.after(400, lambda: launch_dashboard(user))

    btn_container = tk.Frame(inner, bg=CARD_BG)
    btn_container.pack(fill="x", pady=(14, 0))

    login_btn = tk.Button(btn_container, text="🔓  Login Securely",
                          bg=NAVY, fg="white",
                          font=("Segoe UI", 11, "bold"),
                          relief="flat", cursor="hand2",
                          activebackground=ACCENT_BLUE,
                          activeforeground="white",
                          command=do_login)
    login_btn.pack(fill="x", ipady=11)

    def hover_in(_):
        login_btn.config(bg=ACCENT_BLUE)

    def hover_out(_):
        login_btn.config(bg=NAVY)

    login_btn.bind("<Enter>", hover_in)
    login_btn.bind("<Leave>", hover_out)

    # Enter key to submit
    root.bind("<Return>", lambda e: do_login())

    # Help note
    note = tk.Frame(body, bg="#EFF6FF", highlightthickness=1,
                    highlightbackground="#BFDBFE")
    note.pack(fill="x", pady=(16, 0))
    tk.Label(note,
             text=f"🔒 Your password protected by bcrypt encryption. "
                  f"Login as '{selected_role['title']}' • Secure session.",
             bg="#EFF6FF", fg="#1E40AF",
             font=("Segoe UI", 8), wraplength=420, justify="left",
             padx=10, pady=8).pack()

    # Footer
    footer = tk.Frame(root, bg=LIGHT_BG)
    footer.pack(fill="x", side="bottom", pady=10)
    tk.Label(footer, text="Developed by Ajeet Prasad  •  v2.0",
             bg=LIGHT_BG, fg=TEXT_MUTED,
             font=("Segoe UI", 8, "italic")).pack()

    user_entry.focus_set()


# ===== Dashboard launcher =====
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


# ===== Boot =====
print("WELCOME TO LOGIN WINDOW (v2.0 — Modern UI)")
show_role_selection()
root.mainloop()
print("LOGIN WINDOW CLOSED")
