"""
Admin/Super-Admin window to manage Password Reset Requests.

Lets the logged-in admin:
  - View PENDING requests (with member info, reason, time)
  - Approve → system generates a random temp password, hashes it,
    updates the user's account, and shows the plain temp password
    in a copy-able dialog (one-time only — admin must share offline).
  - Reject → with optional note.
  - Toggle to view APPROVED / REJECTED history.

Theme: navy/gold matching the app design.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from password_reset_requests import (
    list_requests,
    approve_request,
    reject_request,
)


# ===== Theme =====
NAVY = "#0B1F3A"
GOLD = "#B8860B"
LIGHT_BG = "#F5F7FB"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#1F2937"
TEXT_MUTED = "#6B7280"
ACCENT_BLUE = "#1F4E79"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
ERROR = "#DC2626"
BORDER = "#E5E7EB"


def open_password_resets_window(approver_username,
                                institution_id=None,
                                is_super_admin=False):
    """
    Open the password-reset management window.

    Args:
        approver_username: Username of the logged-in admin (for audit).
        institution_id: For institution-scoped Admin; None for Super Admin.
        is_super_admin: If True, sees ALL requests (members + admin requests).
    """
    win = tk.Toplevel()
    win.title("Password Reset Requests — Management")
    win.geometry("1080x640")
    win.configure(bg=LIGHT_BG)
    win.minsize(900, 520)

    # ===== Header =====
    header = tk.Frame(win, bg=NAVY, height=70)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Frame(win, bg=GOLD, height=3).pack(fill="x")

    title_row = tk.Frame(header, bg=NAVY)
    title_row.pack(fill="both", expand=True, padx=20)
    tk.Label(title_row, text="🔑  Password Reset Requests",
             bg=NAVY, fg="white",
             font=("Segoe UI", 15, "bold")).pack(side="left", pady=18)
    role_text = ("Super Admin View — All institutions"
                 if is_super_admin
                 else f"Admin View — Institution #{institution_id}")
    tk.Label(title_row, text=role_text, bg=NAVY, fg=GOLD,
             font=("Segoe UI", 10, "italic")).pack(side="right", pady=20)

    # ===== Filter row =====
    filter_row = tk.Frame(win, bg=LIGHT_BG)
    filter_row.pack(fill="x", padx=18, pady=(14, 6))

    tk.Label(filter_row, text="Show:", bg=LIGHT_BG, fg=TEXT_DARK,
             font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 8))

    status_var = tk.StringVar(value="PENDING")
    for status, color in [("PENDING", WARNING),
                          ("APPROVED", SUCCESS),
                          ("REJECTED", ERROR)]:
        rb = tk.Radiobutton(filter_row, text=status, value=status,
                            variable=status_var, bg=LIGHT_BG, fg=color,
                            activebackground=LIGHT_BG, selectcolor=CARD_BG,
                            font=("Segoe UI", 10, "bold"),
                            cursor="hand2",
                            command=lambda: refresh_table())
        rb.pack(side="left", padx=4)

    refresh_btn = tk.Button(filter_row, text="🔄 Refresh", bg=ACCENT_BLUE,
                            fg="white", font=("Segoe UI", 9, "bold"),
                            relief="flat", cursor="hand2",
                            padx=10, pady=4,
                            command=lambda: refresh_table())
    refresh_btn.pack(side="right")

    count_label = tk.Label(filter_row, text="", bg=LIGHT_BG,
                           fg=TEXT_MUTED, font=("Segoe UI", 9, "italic"))
    count_label.pack(side="right", padx=10)

    # ===== Table =====
    table_card = tk.Frame(win, bg=CARD_BG, highlightthickness=1,
                          highlightbackground=BORDER)
    table_card.pack(fill="both", expand=True, padx=18, pady=(4, 8))

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Reset.Treeview", rowheight=32, font=("Segoe UI", 10),
                    fieldbackground=CARD_BG, background=CARD_BG)
    style.configure("Reset.Treeview.Heading",
                    font=("Segoe UI", 10, "bold"),
                    background=NAVY, foreground="white")
    style.map("Reset.Treeview",
              background=[("selected", "#DBEAFE")],
              foreground=[("selected", TEXT_DARK)])

    cols = ("ID", "Username", "Name", "Type", "Reason",
            "Requested At", "Status", "Approved By")
    tree = ttk.Treeview(table_card, columns=cols, show="headings",
                        style="Reset.Treeview")
    tree.pack(side="left", fill="both", expand=True)

    widths = {"ID": 50, "Username": 130, "Name": 160, "Type": 80,
              "Reason": 280, "Requested At": 145, "Status": 90,
              "Approved By": 110}
    anchors = {"ID": "center", "Username": "w", "Name": "w",
               "Type": "center", "Reason": "w",
               "Requested At": "center", "Status": "center",
               "Approved By": "center"}
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=widths[c], anchor=anchors[c])

    yscroll = ttk.Scrollbar(table_card, orient="vertical",
                            command=tree.yview)
    yscroll.pack(side="right", fill="y")
    tree.configure(yscrollcommand=yscroll.set)

    tree.tag_configure("pending", background="#FEF3C7")
    tree.tag_configure("approved", background="#D1FAE5")
    tree.tag_configure("rejected", background="#FEE2E2")

    # ===== Detail / actions panel =====
    detail = tk.Frame(win, bg=CARD_BG, highlightthickness=1,
                      highlightbackground=BORDER, height=140)
    detail.pack(fill="x", padx=18, pady=(0, 14))
    detail.pack_propagate(False)

    detail_inner = tk.Frame(detail, bg=CARD_BG)
    detail_inner.pack(fill="both", expand=True, padx=14, pady=10)

    info_label = tk.Label(detail_inner,
                          text="Click a row above to see details and act.",
                          bg=CARD_BG, fg=TEXT_MUTED,
                          font=("Segoe UI", 10, "italic"),
                          justify="left", anchor="w", wraplength=720)
    info_label.pack(side="left", fill="both", expand=True)

    btn_box = tk.Frame(detail_inner, bg=CARD_BG)
    btn_box.pack(side="right")

    approve_btn = tk.Button(btn_box, text="✓ Approve & Generate Temp PW",
                            bg=SUCCESS, fg="white",
                            font=("Segoe UI", 10, "bold"),
                            relief="flat", cursor="hand2",
                            padx=14, pady=8, state="disabled")
    approve_btn.pack(pady=(0, 6))

    reject_btn = tk.Button(btn_box, text="✗ Reject Request",
                           bg=ERROR, fg="white",
                           font=("Segoe UI", 10, "bold"),
                           relief="flat", cursor="hand2",
                           padx=14, pady=8, state="disabled")
    reject_btn.pack()

    selected = {"id": None, "row": None}

    # ----- Refresh -----
    def refresh_table():
        for r in tree.get_children():
            tree.delete(r)
        rows = list_requests(status=status_var.get(),
                             institution_id=institution_id,
                             include_admin_requests=is_super_admin
                             or institution_id is None)
        for r in rows:
            tag = (r["Status"] or "").lower()
            reason = (r.get("Reason") or "")[:80]
            req_at = (r["RequestedAt"].strftime("%d-%b-%Y %H:%M")
                      if r.get("RequestedAt") else "—")
            tree.insert("", "end",
                        values=(r["RequestID"], r["Username"],
                                r.get("DisplayName") or "—",
                                r["AccountType"], reason,
                                req_at, r["Status"],
                                r.get("ApprovedBy") or "—"),
                        tags=(tag,))
        count_label.config(
            text=f"{len(rows)} {status_var.get().lower()} request(s)")
        info_label.config(text="Click a row above to see details and act.",
                          fg=TEXT_MUTED)
        approve_btn.config(state="disabled")
        reject_btn.config(state="disabled")
        selected["id"] = None
        selected["row"] = None

    # ----- Selection handler -----
    def on_select(_event):
        sel = tree.selection()
        if not sel:
            return
        vals = tree.item(sel[0], "values")
        rid = int(vals[0])
        # Find full row from current data
        rows = list_requests(status=status_var.get(),
                             institution_id=institution_id,
                             include_admin_requests=is_super_admin
                             or institution_id is None)
        row = next((r for r in rows if r["RequestID"] == rid), None)
        if not row:
            return
        selected["id"] = rid
        selected["row"] = row

        full_reason = row.get("Reason") or "(no reason)"
        info_label.config(
            text=(f"📋 Request #{row['RequestID']}  "
                  f"|  Account: {row['Username']} ({row['AccountType']})  "
                  f"|  Name: {row.get('DisplayName') or '—'}\n"
                  f"📅 Requested: "
                  f"{row['RequestedAt'].strftime('%d %b %Y, %H:%M') if row.get('RequestedAt') else '—'}\n"
                  f"💬 Reason: {full_reason}"),
            fg=TEXT_DARK)

        if row["Status"] == "PENDING":
            approve_btn.config(state="normal")
            reject_btn.config(state="normal")
        else:
            approve_btn.config(state="disabled")
            reject_btn.config(state="disabled")

    tree.bind("<<TreeviewSelect>>", on_select)

    # ----- Approve action -----
    def do_approve():
        if not selected["id"]:
            return
        row = selected["row"]
        if not messagebox.askyesno(
                "Confirm Approval",
                f"क्या आप sure हैं कि आप '{row['Username']}' "
                f"({row.get('DisplayName') or ''}) के लिए "
                f"password reset approve करना चाहते हैं?\n\n"
                f"⚠ User का current password तुरंत invalidate हो जाएगा।",
                parent=win):
            return

        result = approve_request(selected["id"], approver_username)
        if not result["ok"]:
            messagebox.showerror("Approval Failed", result["message"],
                                 parent=win)
            return

        _show_temp_password_dialog(win, result)
        refresh_table()

    approve_btn.config(command=do_approve)

    # ----- Reject action -----
    def do_reject():
        if not selected["id"]:
            return
        row = selected["row"]
        note = _ask_rejection_reason(win)
        if note is None:
            return

        if not messagebox.askyesno(
                "Confirm Rejection",
                f"'{row['Username']}' की request reject करें?",
                parent=win):
            return

        result = reject_request(selected["id"], approver_username, note)
        if result["ok"]:
            messagebox.showinfo("Rejected",
                                "Request has been rejected.",
                                parent=win)
            refresh_table()
        else:
            messagebox.showerror("Failed", result["message"], parent=win)

    reject_btn.config(command=do_reject)

    # First load
    refresh_table()


# ============================================================
# Dialog: show temp password (one-time, copy-able)
# ============================================================
def _show_temp_password_dialog(parent, result):
    dlg = tk.Toplevel(parent)
    dlg.title("✓ Password Reset Approved")
    dlg.geometry("500x360")
    dlg.resizable(False, False)
    dlg.configure(bg=LIGHT_BG)
    dlg.transient(parent)
    dlg.grab_set()

    dlg.update_idletasks()
    w, h = 500, 360
    x = (dlg.winfo_screenwidth() - w) // 2
    y = (dlg.winfo_screenheight() - h) // 2
    dlg.geometry(f"{w}x{h}+{x}+{y}")

    head = tk.Frame(dlg, bg=SUCCESS, height=70)
    head.pack(fill="x")
    head.pack_propagate(False)
    tk.Label(head, text="✓ Approved Successfully", bg=SUCCESS, fg="white",
             font=("Segoe UI", 14, "bold")).pack(pady=(12, 0))
    tk.Label(head, text=f"For: {result['username']} ({result['account_type']})",
             bg=SUCCESS, fg="white",
             font=("Segoe UI", 9, "italic")).pack()

    body = tk.Frame(dlg, bg=LIGHT_BG)
    body.pack(fill="both", expand=True, padx=22, pady=18)

    tk.Label(body,
             text="🔐 Temporary Password (one-time display):",
             bg=LIGHT_BG, fg=TEXT_DARK,
             font=("Segoe UI", 10, "bold")).pack(anchor="w")

    pw_frame = tk.Frame(body, bg="#FEF3C7", highlightthickness=2,
                        highlightbackground=GOLD)
    pw_frame.pack(fill="x", pady=10)
    pw_label = tk.Label(pw_frame, text=result["temp_password"],
                        bg="#FEF3C7", fg=NAVY,
                        font=("Consolas", 22, "bold"),
                        pady=14)
    pw_label.pack()

    def copy_to_clipboard():
        dlg.clipboard_clear()
        dlg.clipboard_append(result["temp_password"])
        dlg.update()
        copy_btn.config(text="✓ Copied!", bg=SUCCESS)
        dlg.after(1500, lambda: copy_btn.config(text="📋 Copy Password",
                                                bg=ACCENT_BLUE))

    copy_btn = tk.Button(body, text="📋 Copy Password",
                         bg=ACCENT_BLUE, fg="white",
                         font=("Segoe UI", 10, "bold"),
                         relief="flat", cursor="hand2", padx=14, pady=6,
                         command=copy_to_clipboard)
    copy_btn.pack(pady=(0, 12))

    warn = tk.Frame(body, bg="#FEF2F2", highlightthickness=1,
                    highlightbackground="#FCA5A5")
    warn.pack(fill="x")
    tk.Label(warn,
             text="⚠ IMPORTANT:\n"
                  "• यह password सिर्फ एक बार दिखेगा — अभी note कर लें\n"
                  "• User को offline (in-person/phone) बताएं — chat/email से नहीं\n"
                  "• User पहली बार login करते ही password change कर लें",
             bg="#FEF2F2", fg="#991B1B",
             font=("Segoe UI", 9), justify="left",
             padx=12, pady=10).pack(anchor="w")

    tk.Button(body, text="Done", bg=NAVY, fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat",
              cursor="hand2", padx=20, pady=6,
              command=dlg.destroy).pack(pady=(14, 0))


# ============================================================
# Dialog: ask rejection reason
# ============================================================
def _ask_rejection_reason(parent):
    """Modal that asks for an optional rejection note. Returns str or None."""
    dlg = tk.Toplevel(parent)
    dlg.title("Reject — optional note")
    dlg.geometry("420x240")
    dlg.resizable(False, False)
    dlg.configure(bg=LIGHT_BG)
    dlg.transient(parent)
    dlg.grab_set()

    dlg.update_idletasks()
    x = (dlg.winfo_screenwidth() - 420) // 2
    y = (dlg.winfo_screenheight() - 240) // 2
    dlg.geometry(f"+{x}+{y}")

    tk.Label(dlg, text="Rejection note (optional)",
             bg=LIGHT_BG, fg=TEXT_DARK,
             font=("Segoe UI", 11, "bold")).pack(pady=(14, 4))
    tk.Label(dlg, text="User को बताने के लिए short reason दे सकते हैं।",
             bg=LIGHT_BG, fg=TEXT_MUTED,
             font=("Segoe UI", 9, "italic")).pack(pady=(0, 8))

    txt = tk.Text(dlg, height=4, font=("Segoe UI", 10), wrap="word",
                  bg=CARD_BG, relief="flat", highlightthickness=1,
                  highlightbackground="#D1D5DB")
    txt.pack(fill="x", padx=18, pady=(0, 10))

    result = {"value": None}

    def on_ok():
        result["value"] = txt.get("1.0", "end").strip()
        dlg.destroy()

    def on_cancel():
        result["value"] = None
        dlg.destroy()

    btn_row = tk.Frame(dlg, bg=LIGHT_BG)
    btn_row.pack(pady=4)
    tk.Button(btn_row, text="Cancel", bg="#9CA3AF", fg="white",
              font=("Segoe UI", 9, "bold"), relief="flat",
              padx=14, pady=5, cursor="hand2",
              command=on_cancel).pack(side="left", padx=4)
    tk.Button(btn_row, text="Continue with Rejection", bg=ERROR, fg="white",
              font=("Segoe UI", 9, "bold"), relief="flat",
              padx=14, pady=5, cursor="hand2",
              command=on_ok).pack(side="left", padx=4)

    txt.focus_set()
    dlg.wait_window()
    return result["value"]
