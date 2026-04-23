import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import get_connection
from openpyxl import Workbook


# =====================================================
# ================= VIEW USERS ========================
# =====================================================
def view_users_window(institution_id):

    win = tk.Toplevel()
    win.title("Users Management")
    win.state("zoomed")              # 🔥 Fullscreen (Windows)
    win.configure(bg="#f2f4f7")
    win.minsize(1100, 600)

    # ================= TITLE =================
    tk.Label(
        win,
        text="Registered Users",
        font=("Segoe UI", 18, "bold"),
        bg="#f2f4f7"
    ).pack(pady=12)

    # ================= SEARCH =================
    search_frame = tk.Frame(win, bg="#f2f4f7")
    search_frame.pack(fill="x", padx=30)

    tk.Label(
        search_frame,
        text="Search:",
        font=("Segoe UI", 11, "bold"),
        bg="#f2f4f7"
    ).pack(side="left")

    search_var = tk.StringVar()
    tk.Entry(
        search_frame,
        textvariable=search_var,
        width=45,
        font=("Segoe UI", 10)
    ).pack(side="left", padx=10)

    tk.Label(
        search_frame,
        text="(Name / Email / Mobile)",
        fg="gray",
        bg="#f2f4f7"
    ).pack(side="left")

    # ================= TABLE FRAME =================
    table_frame = tk.Frame(win, bg="#f2f4f7")
    table_frame.pack(fill="both", expand=True, padx=25, pady=15)

    cols = ("MID", "S.No", "Name", "User ID", "Email", "Contact", "Role")
    tree = ttk.Treeview(table_frame, columns=cols, show="headings")

    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)

    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    tree.column("MID", width=0, stretch=False)
    tree.heading("MID", text="")

    tree.column("S.No", width=70, anchor="center")
    tree.column("Name", width=230)
    tree.column("User ID", width=160, anchor="center")
    tree.column("Email", width=280)
    tree.column("Contact", width=150, anchor="center")
    tree.column("Role", width=130, anchor="center")

    for c in cols[1:]:
        tree.heading(c, text=c)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    tree.tag_configure("odd", background="#ffffff")
    tree.tag_configure("even", background="#f1f3f6")

    # ================= LOAD USERS =================
    def load_users(filter_text=""):
        tree.delete(*tree.get_children())

        conn = get_connection()
        cur = conn.cursor()

        q = """
            SELECT MemberID, Name, UserID, Email, Contact, Role
            FROM Members
            WHERE InstitutionID=%s AND Status='ACTIVE'
        """
        params = [institution_id]

        if filter_text:
            like = f"%{filter_text}%"
            q += " AND (Name LIKE %s OR Email LIKE %s OR Contact LIKE %s)"
            params.extend([like, like, like])

        q += " ORDER BY Name ASC"

        cur.execute(q, params)
        rows = cur.fetchall()
        conn.close()

        for i, r in enumerate(rows, start=1):
            tree.insert(
                "", "end",
                values=(r[0], i, r[1], r[2], r[3], r[4], r[5]),
                tags=("even" if i % 2 == 0 else "odd",)
            )

    load_users()
    search_var.trace_add("write",
        lambda *_: load_users(search_var.get().strip()))

    # ================= DOUBLE CLICK =================
    def show_profile(event):
        sel = tree.selection()
        if not sel:
            return
        messagebox.showinfo("Info", "Profile edit logic unchanged")

    tree.bind("<Double-1>", show_profile)

    # ================= BUTTON BAR =================
    btn_frame = tk.Frame(win, bg="#f2f4f7")
    btn_frame.pack(pady=15)

    tk.Button(
        btn_frame,
        text="🗑 Delete User",
        bg="#d9534f",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=18
    ).pack(side="left", padx=8)

    tk.Button(
        btn_frame,
        text="📤 Export Excel",
        bg="#5cb85c",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=18
    ).pack(side="left", padx=8)

    tk.Button(
        btn_frame,
        text="♻ Restore Users",
        bg="#1e88e5",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=18,
        command=lambda: restore_users_window(institution_id)
    ).pack(side="left", padx=8)


# =====================================================
# ================= RESTORE USERS =====================
# =====================================================
def restore_users_window(institution_id):

    win = tk.Toplevel()
    win.title("Restore Deleted Users")
    win.geometry("900x520")
    win.minsize(800, 450)
    win.configure(bg="#f4f6f9")

    tk.Label(
        win,
        text="Inactive / Deleted Users",
        font=("Segoe UI", 16, "bold"),
        bg="#f4f6f9"
    ).pack(pady=12)

    # ================= TABLE =================
    table_frame = tk.Frame(win, bg="#f4f6f9")
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    cols = ("MID", "Name", "Email", "Contact", "Role")
    tree_restore = ttk.Treeview(table_frame, columns=cols, show="headings")

    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree_restore.yview)
    tree_restore.configure(yscrollcommand=vsb.set)

    tree_restore.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    tree_restore.column("MID", width=0, stretch=False)
    tree_restore.heading("MID", text="")

    for c in cols[1:]:
        tree_restore.heading(c, text=c)
        tree_restore.column(c, width=200)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT MemberID, Name, Email, Contact, Role
        FROM Members
        WHERE InstitutionID=%s AND Status='INACTIVE'
        ORDER BY Name
    """, (institution_id,))
    rows = cur.fetchall()
    conn.close()

    for r in rows:
        tree_restore.insert("", "end", values=r)

    # ================= RESTORE =================
    def restore_user():
        sel = tree_restore.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a user")
            return

        member_id = tree_restore.item(sel[0])["values"][0]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE Members
            SET Status='ACTIVE'
            WHERE MemberID=%s AND InstitutionID=%s
        """, (member_id, institution_id))
        conn.commit()
        conn.close()

        tree_restore.delete(sel[0])
        messagebox.showinfo("Restored", "User restored successfully")

    # ================= BOTTOM BAR (FIXED) =================
    bottom = tk.Frame(win, bg="#f4f6f9")
    bottom.pack(fill="x", pady=10)

    tk.Button(
        bottom,
        text="♻ Restore User",
        bg="#1e88e5",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=18,
        command=restore_user
    ).pack()
