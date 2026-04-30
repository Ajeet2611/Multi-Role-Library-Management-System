"""
Forgot Password modal — supports light/dark theme.
Verifies user via Username + Registered Email और bcrypt-hashed
new password DB में set करता है.
"""

import tkinter as tk
from tkinter import messagebox
from db import get_connection
from security import hash_password


# ===== Default (light) theme — used if caller does not supply one =====
DEFAULT_THEME = {
    "name": "light",
    "NAVY": "#0B1F3A",
    "GOLD": "#B8860B",
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
}


def open_forgot_password(parent, theme=None):
    """Open the forgot password modal as a toplevel window."""
    T = theme if theme else DEFAULT_THEME

    win = tk.Toplevel(parent)
    win.title("Forgot Password — Reset")
    win.geometry("480x620")
    win.resizable(False, False)
    win.configure(bg=T["BG"])
    win.transient(parent)
    win.grab_set()

    # Center on screen
    win.update_idletasks()
    w, h = 480, 620
    x = (win.winfo_screenwidth() - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

    # ===== Header =====
    header = tk.Frame(win, bg=T["NAVY"], height=130)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(header, text="🔐", bg=T["NAVY"], fg=T["GOLD"],
             font=("Segoe UI Emoji", 32)).pack(pady=(20, 0))
    tk.Label(header, text="Reset Your Password", bg=T["NAVY"], fg="white",
             font=("Segoe UI", 16, "bold")).pack()
    tk.Label(header, text="Verify identity to set a new password",
             bg=T["NAVY"],
             fg="#B8C5D6" if T["name"] == "light" else "#94A3B8",
             font=("Segoe UI", 9, "italic")).pack(pady=(2, 0))

    # Gold separator
    tk.Frame(win, bg=T["GOLD"], height=3).pack(fill="x")

    # ===== Card body =====
    body = tk.Frame(win, bg=T["BG"])
    body.pack(fill="both", expand=True, padx=24, pady=18)

    card = tk.Frame(body, bg=T["CARD_BG"], highlightthickness=1,
                    highlightbackground=T["BORDER"])
    card.pack(fill="both", expand=True)

    inner = tk.Frame(card, bg=T["CARD_BG"])
    inner.pack(fill="both", expand=True, padx=22, pady=18)

    def make_label(parent, text):
        return tk.Label(parent, text=text, bg=T["CARD_BG"], fg=T["TEXT"],
                        font=("Segoe UI", 10, "bold"))

    def make_entry(parent, show=None):
        e = tk.Entry(parent, font=("Segoe UI", 11), bg=T["INPUT_BG"],
                     fg=T["TEXT"], insertbackground=T["TEXT"],
                     relief="flat", highlightthickness=1,
                     highlightcolor=T["ACCENT"],
                     highlightbackground=T["INPUT_BORDER"])
        if show:
            e.config(show=show)
        return e

    # Username
    make_label(inner, "Username / User ID").pack(anchor="w")
    user_entry = make_entry(inner)
    user_entry.pack(fill="x", ipady=8, pady=(4, 12))

    # Email
    make_label(inner, "Registered Email").pack(anchor="w")
    email_entry = make_entry(inner)
    email_entry.pack(fill="x", ipady=8, pady=(4, 12))

    # New Password
    make_label(inner, "New Password").pack(anchor="w")
    new_pw_entry = make_entry(inner, show="●")
    new_pw_entry.pack(fill="x", ipady=8, pady=(4, 12))

    # Confirm Password
    make_label(inner, "Confirm New Password").pack(anchor="w")
    confirm_pw_entry = make_entry(inner, show="●")
    confirm_pw_entry.pack(fill="x", ipady=8, pady=(4, 14))

    # Status label
    status_label = tk.Label(inner, text="", bg=T["CARD_BG"], fg=T["ERROR"],
                            font=("Segoe UI", 9), wraplength=380,
                            justify="left")
    status_label.pack(fill="x", pady=(2, 8))

    # Submit
    def do_reset():
        username = user_entry.get().strip()
        email = email_entry.get().strip()
        new_pw = new_pw_entry.get()
        confirm_pw = confirm_pw_entry.get()

        if not all([username, email, new_pw, confirm_pw]):
            status_label.config(text="⚠ All fields are required.",
                                fg=T["ERROR"])
            return
        if len(new_pw) < 6:
            status_label.config(
                text="⚠ Password must be at least 6 characters long.",
                fg=T["ERROR"])
            return
        if new_pw != confirm_pw:
            status_label.config(text="⚠ Passwords do not match.",
                                fg=T["ERROR"])
            return

        conn = get_connection()
        if conn is None:
            status_label.config(
                text="⚠ Database connection failed. Try again later.",
                fg=T["ERROR"])
            return

        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT MemberID, UserID, Email FROM Members "
                "WHERE UserID=%s AND Email=%s AND Status='ACTIVE'",
                (username, email))
            member = cur.fetchone()

            if member:
                hashed = hash_password(new_pw)
                cur2 = conn.cursor()
                cur2.execute(
                    "UPDATE Members SET Password=%s WHERE MemberID=%s",
                    (hashed, member["MemberID"]))
                conn.commit()
                cur2.close()
                cur.close()
                conn.close()
                messagebox.showinfo(
                    "Password Reset Successful",
                    "✓ Your password has been reset successfully!\n\n"
                    "अब आप अपने नए password से login कर सकते हैं।",
                    parent=win)
                win.destroy()
                return

            cur.execute("SELECT UserID FROM Users WHERE Username=%s",
                        (username,))
            admin_user = cur.fetchone()
            cur.close()
            conn.close()

            if admin_user:
                status_label.config(
                    text="⚠ Admin password reset requires Super Admin help. "
                         "कृपया अपने Super Admin से contact करें।",
                    fg=T["ERROR"])
            else:
                status_label.config(
                    text="⚠ Username + Email combination match नहीं हो रहा। "
                         "कृपया details verify करें या admin से contact करें।",
                    fg=T["ERROR"])
        except Exception as e:
            try:
                conn.close()
            except Exception:
                pass
            status_label.config(text=f"⚠ Error: {str(e)[:80]}",
                                fg=T["ERROR"])

    # Reset button
    btn_frame = tk.Frame(inner, bg=T["CARD_BG"])
    btn_frame.pack(fill="x", pady=(4, 0))

    reset_btn = tk.Button(btn_frame, text="🔓  Reset Password",
                          bg=T["NAVY"], fg="white",
                          font=("Segoe UI", 11, "bold"),
                          relief="flat", cursor="hand2",
                          activebackground=T["ACCENT"],
                          activeforeground="white",
                          command=do_reset)
    reset_btn.pack(fill="x", ipady=10)

    def on_enter(_):
        reset_btn.config(bg=T["ACCENT"])

    def on_leave(_):
        reset_btn.config(bg=T["NAVY"])

    reset_btn.bind("<Enter>", on_enter)
    reset_btn.bind("<Leave>", on_leave)

    # Cancel link
    cancel = tk.Label(inner, text="← Back to Login", bg=T["CARD_BG"],
                      fg=T["ACCENT"],
                      font=("Segoe UI", 9, "underline"), cursor="hand2")
    cancel.pack(pady=(12, 0))
    cancel.bind("<Button-1>", lambda e: win.destroy())

    # Help note
    help_bg = "#FEF3C7" if T["name"] == "light" else "#3F2D14"
    help_fg = "#78350F" if T["name"] == "light" else "#FCD34D"
    help_border = "#FCD34D" if T["name"] == "light" else "#92400E"

    help_note = tk.Frame(body, bg=help_bg, highlightthickness=1,
                         highlightbackground=help_border)
    help_note.pack(fill="x", pady=(14, 0))
    tk.Label(help_note,
             text="💡 Note: Admin accounts के लिए password reset Super Admin "
                  "से ही possible है — यह security best practice है।",
             bg=help_bg, fg=help_fg,
             font=("Segoe UI", 8), wraplength=400, justify="left",
             padx=10, pady=8).pack()

    user_entry.focus_set()
