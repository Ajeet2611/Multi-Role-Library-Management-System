"""
Forgot Password modal for the Library Management System.
Verifies user via Username + Registered Email और bcrypt-hashed
new password set करता है DB में.
"""

import tkinter as tk
from tkinter import messagebox
from db import get_connection
from security import hash_password


# ===== Theme (must match gui_login.py) =====
NAVY = "#0B1F3A"
GOLD = "#B8860B"
LIGHT_BG = "#F5F7FB"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#1F2937"
TEXT_MUTED = "#6B7280"
ACCENT_BLUE = "#1F4E79"
ERROR_RED = "#DC2626"
SUCCESS_GREEN = "#10B981"


def open_forgot_password(parent):
    """Open the forgot password modal as a toplevel window."""
    win = tk.Toplevel(parent)
    win.title("Forgot Password — Reset")
    win.geometry("460x600")
    win.resizable(False, False)
    win.configure(bg=LIGHT_BG)
    win.transient(parent)
    win.grab_set()

    # Center on screen
    win.update_idletasks()
    w, h = 460, 600
    x = (win.winfo_screenwidth() - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

    # ===== Top Navy Header =====
    header = tk.Frame(win, bg=NAVY, height=130)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(header, text="🔐", bg=NAVY, fg=GOLD,
             font=("Segoe UI Emoji", 32)).pack(pady=(20, 0))
    tk.Label(header, text="Reset Your Password", bg=NAVY, fg="white",
             font=("Segoe UI", 16, "bold")).pack()
    tk.Label(header, text="Verify identity to set a new password",
             bg=NAVY, fg="#B8C5D6",
             font=("Segoe UI", 9, "italic")).pack(pady=(2, 0))

    # Gold separator
    tk.Frame(win, bg=GOLD, height=3).pack(fill="x")

    # ===== White Card Body =====
    body = tk.Frame(win, bg=LIGHT_BG)
    body.pack(fill="both", expand=True, padx=24, pady=22)

    card = tk.Frame(body, bg=CARD_BG, highlightthickness=1,
                    highlightbackground="#E5E7EB")
    card.pack(fill="both", expand=True)

    inner = tk.Frame(card, bg=CARD_BG)
    inner.pack(fill="both", expand=True, padx=22, pady=20)

    # Username
    tk.Label(inner, text="Username / User ID", bg=CARD_BG, fg=TEXT_DARK,
             font=("Segoe UI", 10, "bold")).pack(anchor="w")
    user_entry = tk.Entry(inner, font=("Segoe UI", 11), bg="#F9FAFB",
                          relief="flat", highlightthickness=1,
                          highlightcolor=ACCENT_BLUE,
                          highlightbackground="#D1D5DB")
    user_entry.pack(fill="x", ipady=8, pady=(4, 12))

    # Email
    tk.Label(inner, text="Registered Email", bg=CARD_BG, fg=TEXT_DARK,
             font=("Segoe UI", 10, "bold")).pack(anchor="w")
    email_entry = tk.Entry(inner, font=("Segoe UI", 11), bg="#F9FAFB",
                           relief="flat", highlightthickness=1,
                           highlightcolor=ACCENT_BLUE,
                           highlightbackground="#D1D5DB")
    email_entry.pack(fill="x", ipady=8, pady=(4, 12))

    # New Password
    tk.Label(inner, text="New Password", bg=CARD_BG, fg=TEXT_DARK,
             font=("Segoe UI", 10, "bold")).pack(anchor="w")
    new_pw_entry = tk.Entry(inner, show="●", font=("Segoe UI", 11),
                            bg="#F9FAFB", relief="flat", highlightthickness=1,
                            highlightcolor=ACCENT_BLUE,
                            highlightbackground="#D1D5DB")
    new_pw_entry.pack(fill="x", ipady=8, pady=(4, 12))

    # Confirm Password
    tk.Label(inner, text="Confirm New Password", bg=CARD_BG, fg=TEXT_DARK,
             font=("Segoe UI", 10, "bold")).pack(anchor="w")
    confirm_pw_entry = tk.Entry(inner, show="●", font=("Segoe UI", 11),
                                bg="#F9FAFB", relief="flat",
                                highlightthickness=1,
                                highlightcolor=ACCENT_BLUE,
                                highlightbackground="#D1D5DB")
    confirm_pw_entry.pack(fill="x", ipady=8, pady=(4, 14))

    # Status label
    status_label = tk.Label(inner, text="", bg=CARD_BG, fg=ERROR_RED,
                            font=("Segoe UI", 9), wraplength=350,
                            justify="left")
    status_label.pack(fill="x", pady=(2, 8))

    # Submit button
    def do_reset():
        username = user_entry.get().strip()
        email = email_entry.get().strip()
        new_pw = new_pw_entry.get()
        confirm_pw = confirm_pw_entry.get()

        # Validation
        if not all([username, email, new_pw, confirm_pw]):
            status_label.config(text="⚠ All fields are required.",
                                fg=ERROR_RED)
            return
        if len(new_pw) < 6:
            status_label.config(
                text="⚠ Password must be at least 6 characters long.",
                fg=ERROR_RED)
            return
        if new_pw != confirm_pw:
            status_label.config(text="⚠ Passwords do not match.",
                                fg=ERROR_RED)
            return

        # DB verification
        conn = get_connection()
        if conn is None:
            status_label.config(
                text="⚠ Database connection failed. Try again later.",
                fg=ERROR_RED)
            return

        try:
            cur = conn.cursor(dictionary=True)
            # Try Members table first (most common for forgot password)
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

            # If not a member, indicate admin contact required
            cur.execute("SELECT UserID FROM Users WHERE Username=%s",
                        (username,))
            admin_user = cur.fetchone()
            cur.close()
            conn.close()

            if admin_user:
                status_label.config(
                    text="⚠ Admin password reset requires Super Admin assistance. "
                         "कृपया अपने Super Admin से contact करें।",
                    fg=ERROR_RED)
            else:
                status_label.config(
                    text="⚠ Username + Email combination match नहीं हो रहा। "
                         "कृपया details verify करें या admin से contact करें।",
                    fg=ERROR_RED)
        except Exception as e:
            try:
                conn.close()
            except Exception:
                pass
            status_label.config(text=f"⚠ Error: {str(e)[:80]}",
                                fg=ERROR_RED)

    # Reset button
    btn_frame = tk.Frame(inner, bg=CARD_BG)
    btn_frame.pack(fill="x", pady=(4, 0))

    reset_btn = tk.Button(btn_frame, text="🔓  Reset Password",
                          bg=NAVY, fg="white", font=("Segoe UI", 11, "bold"),
                          relief="flat", cursor="hand2",
                          activebackground=ACCENT_BLUE,
                          activeforeground="white",
                          command=do_reset)
    reset_btn.pack(fill="x", ipady=10)

    def on_enter(e):
        reset_btn.config(bg=ACCENT_BLUE)

    def on_leave(e):
        reset_btn.config(bg=NAVY)

    reset_btn.bind("<Enter>", on_enter)
    reset_btn.bind("<Leave>", on_leave)

    # Cancel link
    cancel = tk.Label(inner, text="← Back to Login", bg=CARD_BG, fg=ACCENT_BLUE,
                      font=("Segoe UI", 9, "underline"), cursor="hand2")
    cancel.pack(pady=(12, 0))
    cancel.bind("<Button-1>", lambda e: win.destroy())

    # Help note
    help_note = tk.Frame(body, bg="#FEF3C7", highlightthickness=1,
                         highlightbackground="#FCD34D")
    help_note.pack(fill="x", pady=(14, 0))
    tk.Label(help_note,
             text="💡 Note: Admin accounts के लिए password reset Super Admin "
                  "से ही possible है — यह security best practice है।",
             bg="#FEF3C7", fg="#78350F",
             font=("Segoe UI", 8), wraplength=380, justify="left",
             padx=10, pady=8).pack()

    user_entry.focus_set()
