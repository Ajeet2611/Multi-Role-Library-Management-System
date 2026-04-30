"""
Forgot Password modal — submits a password-reset REQUEST from the
login screen (no authentication required).

Architecture: User submits Username + Reason → row inserted in
PasswordResetRequests table with status PENDING. Admin / Super Admin
sees it in their dashboard, approves, generates a temp password, and
shares it with the user offline.
"""

import tkinter as tk
from tkinter import messagebox
from password_reset_requests import submit_request, lookup_user


# ===== Default (light) theme =====
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
    """Open the forgot-password request submission modal."""
    T = theme if theme else DEFAULT_THEME

    win = tk.Toplevel(parent)
    win.title("Forgot Password — Submit Request")
    win.geometry("500x640")
    win.resizable(False, False)
    win.configure(bg=T["BG"])
    win.transient(parent)
    win.grab_set()

    win.update_idletasks()
    w, h = 500, 640
    x = (win.winfo_screenwidth() - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

    # ===== Header =====
    header = tk.Frame(win, bg=T["NAVY"], height=130)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(header, text="🔐", bg=T["NAVY"], fg=T["GOLD"],
             font=("Segoe UI Emoji", 32)).pack(pady=(18, 0))
    tk.Label(header, text="Password Reset Request", bg=T["NAVY"],
             fg="white", font=("Segoe UI", 16, "bold")).pack()
    tk.Label(header, text="Admin will review and reset your password",
             bg=T["NAVY"],
             fg="#B8C5D6" if T["name"] == "light" else "#94A3B8",
             font=("Segoe UI", 9, "italic")).pack(pady=(2, 0))

    tk.Frame(win, bg=T["GOLD"], height=3).pack(fill="x")

    # ===== Body =====
    body = tk.Frame(win, bg=T["BG"])
    body.pack(fill="both", expand=True, padx=22, pady=16)

    card = tk.Frame(body, bg=T["CARD_BG"], highlightthickness=1,
                    highlightbackground=T["BORDER"])
    card.pack(fill="both", expand=True)

    inner = tk.Frame(card, bg=T["CARD_BG"])
    inner.pack(fill="both", expand=True, padx=22, pady=18)

    # Username
    tk.Label(inner, text="Username / User ID", bg=T["CARD_BG"],
             fg=T["TEXT"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
    user_entry = tk.Entry(inner, font=("Segoe UI", 11), bg=T["INPUT_BG"],
                          fg=T["TEXT"], insertbackground=T["TEXT"],
                          relief="flat", highlightthickness=1,
                          highlightcolor=T["ACCENT"],
                          highlightbackground=T["INPUT_BORDER"])
    user_entry.pack(fill="x", ipady=8, pady=(4, 4))

    # Detected account info (live preview)
    detected_label = tk.Label(inner, text="", bg=T["CARD_BG"],
                              fg=T["TEXT_MUTED"],
                              font=("Segoe UI", 9, "italic"))
    detected_label.pack(anchor="w", pady=(0, 10))

    def on_username_change(_event=None):
        u = user_entry.get().strip()
        if not u:
            detected_label.config(text="", fg=T["TEXT_MUTED"])
            return
        # Defer DB lookup until user pauses typing
        win.after_cancel(detected_label._job) if hasattr(
            detected_label, "_job") and detected_label._job else None
        detected_label._job = win.after(450, lambda: do_lookup(u))

    def do_lookup(u):
        acc_type, name, _ = lookup_user(u)
        if acc_type == "MEMBER":
            detected_label.config(
                text=f"✓ Found: {name} (Member account)",
                fg=T["SUCCESS"])
        elif acc_type == "ADMIN":
            detected_label.config(
                text=f"✓ Found: {name} (Admin account → "
                     f"goes to Super Admin)",
                fg=T["SUCCESS"])
        elif u:
            detected_label.config(
                text="⚠ Username not found in database.",
                fg=T["ERROR"])

    detected_label._job = None
    user_entry.bind("<KeyRelease>", on_username_change)

    # Reason
    tk.Label(inner, text="Reason for reset (कारण)",
             bg=T["CARD_BG"], fg=T["TEXT"],
             font=("Segoe UI", 10, "bold")).pack(anchor="w")
    tk.Label(inner, text="जैसे: 'Password भूल गया हूँ', "
                         "'Account locked हो गया', etc.",
             bg=T["CARD_BG"], fg=T["TEXT_MUTED"],
             font=("Segoe UI", 8, "italic")).pack(anchor="w", pady=(0, 4))

    reason_text = tk.Text(inner, height=4, font=("Segoe UI", 10),
                          bg=T["INPUT_BG"], fg=T["TEXT"],
                          insertbackground=T["TEXT"],
                          relief="flat", highlightthickness=1,
                          highlightcolor=T["ACCENT"],
                          highlightbackground=T["INPUT_BORDER"],
                          wrap="word")
    reason_text.pack(fill="x", pady=(0, 12))

    # Status
    status_label = tk.Label(inner, text="", bg=T["CARD_BG"],
                            fg=T["ERROR"], font=("Segoe UI", 9),
                            wraplength=400, justify="left")
    status_label.pack(fill="x", pady=(2, 6))

    # ===== Submit =====
    def do_submit():
        username = user_entry.get().strip()
        reason = reason_text.get("1.0", "end").strip()

        if not username:
            status_label.config(text="⚠ Username field खाली है।",
                                fg=T["ERROR"])
            return
        if not reason or len(reason) < 5:
            status_label.config(
                text="⚠ कृपया एक meaningful reason दीजिए "
                     "(कम-से-कम 5 characters)।",
                fg=T["ERROR"])
            return

        status_label.config(text="🔄 Submitting request...",
                            fg=T["TEXT_MUTED"])
        win.update_idletasks()

        result = submit_request(username, reason)
        if result["ok"]:
            messagebox.showinfo(
                "Request Submitted",
                f"{result['message']}\n\n"
                f"Request ID: #{result['request_id']}\n\n"
                f"📞 Approval के बाद admin आपको offline "
                f"(in-person/phone/message) नया temporary password "
                f"बताएगा। पहली बार login करने पर password change "
                f"करना न भूलें।",
                parent=win)
            win.destroy()
        else:
            status_label.config(text=result["message"], fg=T["ERROR"])

    btn_frame = tk.Frame(inner, bg=T["CARD_BG"])
    btn_frame.pack(fill="x", pady=(4, 0))

    submit_btn = tk.Button(btn_frame, text="📨  Submit Reset Request",
                           bg=T["NAVY"], fg="white",
                           font=("Segoe UI", 11, "bold"),
                           relief="flat", cursor="hand2",
                           activebackground=T["ACCENT"],
                           activeforeground="white",
                           command=do_submit)
    submit_btn.pack(fill="x", ipady=10)

    submit_btn.bind("<Enter>",
                    lambda e: submit_btn.config(bg=T["ACCENT"]))
    submit_btn.bind("<Leave>",
                    lambda e: submit_btn.config(bg=T["NAVY"]))

    # Cancel link
    cancel = tk.Label(inner, text="← Back to Login", bg=T["CARD_BG"],
                      fg=T["ACCENT"],
                      font=("Segoe UI", 9, "underline"), cursor="hand2")
    cancel.pack(pady=(12, 0))
    cancel.bind("<Button-1>", lambda e: win.destroy())

    # Info note
    info_bg = "#EFF6FF" if T["name"] == "light" else "#1E3A5F"
    info_fg = "#1E40AF" if T["name"] == "light" else "#BFDBFE"
    info_border = "#BFDBFE" if T["name"] == "light" else "#3B82F6"

    note = tk.Frame(body, bg=info_bg, highlightthickness=1,
                    highlightbackground=info_border)
    note.pack(fill="x", pady=(12, 0))
    tk.Label(note,
             text="ℹ How it works:\n"
                  "  1. आप यहाँ request submit करते हैं\n"
                  "  2. Admin/Super Admin अपने dashboard में देखते हैं\n"
                  "  3. वे approve करके एक temporary password generate करते हैं\n"
                  "  4. वो password आपको offline बता दिया जाता है\n"
                  "  5. आप उससे login करके अपना नया password set करें",
             bg=info_bg, fg=info_fg,
             font=("Segoe UI", 8), wraplength=420, justify="left",
             padx=10, pady=8).pack()

    user_entry.focus_set()
