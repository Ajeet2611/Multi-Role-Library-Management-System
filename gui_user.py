import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from db import get_connection
from security import check_password, hash_password
from messaging import ensure_user_messages_table
from datetime import date
import os

# ================= PATH =================
BASE_DIR = os.path.dirname(__file__)
ASSETS = os.path.join(BASE_DIR, "assets")


def open_user_dashboard(user):
    username = user["Username"]
    user_id = user["UserID"]
    role = user["Role"]
    institution_id = user["InstitutionID"]

    root = tk.Tk()
    root.title("User Dashboard")
    root.geometry("1200x760")
    root.minsize(1080, 680)
    root.resizable(True, True)

    # ================= BACKGROUND =================
    original_bg = Image.open(os.path.join(ASSETS, "bg.jpg"))
    bg_label = tk.Label(root)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def resize_bg(event):
        if event.widget != root:
            return
        img = original_bg.resize((event.width, event.height), Image.LANCZOS)
        bg = ImageTk.PhotoImage(img)
        bg_label.config(image=bg)
        bg_label.image = bg

    root.bind("<Configure>", resize_bg)

    # ================= MAIN LAYOUT =================
    main = tk.Frame(root, bg="#000000")
    main.place(relx=0.02, rely=0.03, relwidth=0.96, relheight=0.94)

    main.grid_rowconfigure(0, weight=0)  # header
    main.grid_rowconfigure(1, weight=1)  # tables
    main.grid_rowconfigure(2, weight=0)  # message bar
    main.grid_rowconfigure(3, weight=0)  # password bar
    main.grid_columnconfigure(0, weight=1)
    main.grid_columnconfigure(1, weight=1)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", rowheight=28, font=("Arial", 10))
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    # ================= HEADER =================
    header = tk.Frame(main, bg="#111111", bd=1, relief="ridge")
    header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 8))
    header.grid_columnconfigure(0, weight=1)

    tk.Label(
        header,
        text=f"Welcome, {username}",
        font=("Arial", 24, "bold"),
        bg="#111111",
        fg="white"
    ).grid(row=0, column=0, sticky="w", padx=16, pady=10)

    tk.Button(
        header, text="Logout",
        bg="#dc2626", fg="white",
        width=14, font=("Arial", 11, "bold"),
        command=root.destroy
    ).grid(row=0, column=1, sticky="e", padx=16, pady=10)

    # ================= AVAILABLE BOOKS =================
    frame1 = tk.LabelFrame(
        main, text="Available Books",
        font=("Arial", 12, "bold"),
        padx=10, pady=10,
        bg="#f8fafc"
    )
    frame1.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=8)
    frame1.grid_rowconfigure(0, weight=1)
    frame1.grid_columnconfigure(0, weight=1)

    cols1 = ("Title", "Author", "Available")
    tree_books = ttk.Treeview(frame1, columns=cols1, show="headings", height=14)
    tree_books.grid(row=0, column=0, sticky="nsew")

    books_y_scroll = ttk.Scrollbar(frame1, orient="vertical", command=tree_books.yview)
    books_y_scroll.grid(row=0, column=1, sticky="ns")
    tree_books.configure(yscrollcommand=books_y_scroll.set)

    for c in cols1:
        tree_books.heading(c, text=c)
    tree_books.column("Title", width=240, minwidth=180, anchor="w", stretch=True)
    tree_books.column("Author", width=190, minwidth=140, anchor="w", stretch=True)
    tree_books.column("Available", width=110, minwidth=100, anchor="center", stretch=False)

    def load_books():
        tree_books.delete(*tree_books.get_children())

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT Title, Author, AvailableCopies
            FROM Books
            WHERE InstitutionID=%s AND AvailableCopies>0
            """,
            (institution_id,)
        )
        for row in cur.fetchall():
            tree_books.insert("", "end", values=row)

        cur.close()
        conn.close()

    tk.Button(
        frame1, text="Refresh",
        bg="#2563eb", fg="white",
        command=load_books
    ).grid(row=1, column=0, pady=10, sticky="e")

    load_books()

    # ================= MY ISSUED BOOKS =================
    frame2 = tk.LabelFrame(
        main, text="My Issued Books",
        font=("Arial", 12, "bold"),
        padx=10, pady=10,
        bg="#f8fafc"
    )
    frame2.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=8)
    frame2.grid_rowconfigure(0, weight=1)
    frame2.grid_columnconfigure(0, weight=1)

    cols2 = ("Title", "Issue Date", "Due Date", "Status", "Fine")
    tree_issue = ttk.Treeview(frame2, columns=cols2, show="headings", height=14)
    tree_issue.grid(row=0, column=0, sticky="nsew")

    issue_y_scroll = ttk.Scrollbar(frame2, orient="vertical", command=tree_issue.yview)
    issue_y_scroll.grid(row=0, column=1, sticky="ns")
    tree_issue.configure(yscrollcommand=issue_y_scroll.set)

    for c in cols2:
        tree_issue.heading(c, text=c)
    tree_issue.column("Title", width=230, minwidth=170, anchor="w", stretch=True)
    tree_issue.column("Issue Date", width=130, minwidth=120, anchor="center", stretch=False)
    tree_issue.column("Due Date", width=130, minwidth=120, anchor="center", stretch=False)
    tree_issue.column("Status", width=110, minwidth=100, anchor="center", stretch=False)
    tree_issue.column("Fine", width=95, minwidth=90, anchor="center", stretch=False)

    def load_issued():
        tree_issue.delete(*tree_issue.get_children())

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT B.Title, T.IssueDate, T.DueDate, T.ReturnStatus
            FROM Transactions T
            JOIN Books B ON T.BookID = B.BookID
            JOIN Members M ON T.MemberID = M.MemberID
            WHERE M.Name=%s AND T.InstitutionID=%s
            """,
            (username, institution_id)
        )

        today = date.today()

        for r in cur.fetchall():
            fine = 0
            status = r[3]

            if status == "ISSUED" and today > r[2]:
                fine = (today - r[2]).days * 5
                tag = "late"
            else:
                tag = "ok"

            tree_issue.insert(
                "", "end",
                values=(r[0], r[1], r[2], status, f"₹{fine}"),
                tags=(tag,)
            )

        tree_issue.tag_configure("late", background="#fca5a5")
        tree_issue.tag_configure("ok", background="#bbf7d0")

        cur.close()
        conn.close()

    tk.Button(
        frame2, text="Refresh",
        bg="#16a34a", fg="white",
        command=load_issued
    ).grid(row=1, column=0, pady=10, sticky="e")

    load_issued()

    # ================= MESSAGE TO ADMIN =================
    ensure_user_messages_table()

    frame3 = tk.LabelFrame(
        main, text="Messages with Admin",
        font=("Arial", 12, "bold"),
        padx=10, pady=10
    )
    frame3.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(8, 12))
    frame3.grid_columnconfigure(0, weight=1)
    frame3.grid_rowconfigure(0, weight=1)

    msg_cols = ("Sent At", "My Message", "Admin Reply", "Status")
    msg_tree = ttk.Treeview(frame3, columns=msg_cols, show="headings", height=5)
    msg_tree.grid(row=0, column=0, columnspan=3, sticky="ew", padx=4, pady=(4, 8))

    for c in msg_cols:
        msg_tree.heading(c, text=c)
    msg_tree.column("Sent At", width=150, anchor="center", stretch=False)
    msg_tree.column("My Message", width=370, anchor="w", stretch=True)
    msg_tree.column("Admin Reply", width=370, anchor="w", stretch=True)
    msg_tree.column("Status", width=90, anchor="center", stretch=False)

    msg_tree.tag_configure("open", background="#fff7ed")
    msg_tree.tag_configure("replied", background="#ecfdf5")

    msg_entry = tk.Entry(frame3, font=("Arial", 11))
    msg_entry.grid(row=1, column=0, padx=(4, 8), pady=4, sticky="ew", ipady=5)

    def load_user_messages():
        msg_tree.delete(*msg_tree.get_children())

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT SentAt, UserMessage, COALESCE(AdminReply, ''), Status
            FROM UserMessages
            WHERE UserID=%s AND InstitutionID=%s
            ORDER BY SentAt DESC
            LIMIT 100
            """,
            (user_id, institution_id)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        for row in rows:
            tag = "replied" if str(row[3]).upper() == "REPLIED" else "open"
            msg_tree.insert("", "end", values=row, tags=(tag,))

    def send_msg():
        msg = msg_entry.get().strip()
        if not msg:
            messagebox.showerror("Error", "Message cannot be empty")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO UserMessages
            (UserID, Username, UserMessage, Status, InstitutionID)
            VALUES (%s, %s, %s, 'OPEN', %s)
            """,
            (user_id, username, msg, institution_id)
        )
        conn.commit()
        cur.close()
        conn.close()

        messagebox.showinfo("Sent", "Message sent to Admin")
        msg_entry.delete(0, tk.END)
        load_user_messages()

    tk.Button(
        frame3, text="Send Message",
        bg="#f59e0b", fg="black",
        width=15, font=("Arial", 10, "bold"),
        command=send_msg
    ).grid(row=1, column=1, padx=(0, 4), pady=4)

    tk.Button(
        frame3, text="Refresh",
        bg="#16a34a", fg="white",
        width=12, font=("Arial", 10, "bold"),
        command=load_user_messages
    ).grid(row=1, column=2, padx=(0, 4), pady=4)

    load_user_messages()

    # ================= CHANGE PASSWORD =================
    frame4 = tk.LabelFrame(
        main, text="Change Password",
        font=("Arial", 12, "bold"),
        padx=10, pady=10
    )
    frame4.grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))
    frame4.grid_columnconfigure(1, weight=1)
    frame4.grid_columnconfigure(3, weight=1)
    frame4.grid_columnconfigure(5, weight=1)

    tk.Label(frame4, text="Current", font=("Arial", 10, "bold")).grid(
        row=0, column=0, padx=(4, 6), pady=4, sticky="w"
    )
    current_pass_entry = tk.Entry(frame4, show="*", font=("Arial", 10))
    current_pass_entry.grid(row=0, column=1, padx=(0, 12), pady=4, sticky="ew", ipady=2)

    tk.Label(frame4, text="New", font=("Arial", 10, "bold")).grid(
        row=0, column=2, padx=(0, 6), pady=4, sticky="w"
    )
    new_pass_entry = tk.Entry(frame4, show="*", font=("Arial", 10))
    new_pass_entry.grid(row=0, column=3, padx=(0, 12), pady=4, sticky="ew", ipady=2)

    tk.Label(frame4, text="Confirm", font=("Arial", 10, "bold")).grid(
        row=0, column=4, padx=(0, 6), pady=4, sticky="w"
    )
    confirm_pass_entry = tk.Entry(frame4, show="*", font=("Arial", 10))
    confirm_pass_entry.grid(row=0, column=5, padx=(0, 12), pady=4, sticky="ew", ipady=2)

    def change_password():
        current_pw = current_pass_entry.get().strip()
        new_pw = new_pass_entry.get().strip()
        confirm_pw = confirm_pass_entry.get().strip()

        if not current_pw or not new_pw or not confirm_pw:
            messagebox.showerror("Error", "All password fields are required")
            return

        if len(new_pw) < 6:
            messagebox.showerror("Error", "New password must be at least 6 characters")
            return

        if new_pw != confirm_pw:
            messagebox.showerror("Error", "New and confirm password do not match")
            return

        conn = get_connection()
        cur = conn.cursor()

        if role in ("STUDENT", "TEACHER", "OTHER"):
            cur.execute(
                """
                SELECT Password FROM Members
                WHERE UserID=%s AND InstitutionID=%s AND Status='ACTIVE'
                """,
                (user_id, institution_id)
            )
            row = cur.fetchone()
            table_name = "Members"
            where_clause = "UserID=%s AND InstitutionID=%s"
            where_params = (user_id, institution_id)
        else:
            cur.execute(
                """
                SELECT Password FROM Users
                WHERE UserID=%s AND InstitutionID=%s
                """,
                (user_id, institution_id)
            )
            row = cur.fetchone()
            table_name = "Users"
            where_clause = "UserID=%s AND InstitutionID=%s"
            where_params = (user_id, institution_id)

        if not row:
            cur.close()
            conn.close()
            messagebox.showerror("Error", "User not found")
            return

        if not check_password(current_pw, row[0]):
            cur.close()
            conn.close()
            messagebox.showerror("Error", "Current password is incorrect")
            return

        new_hash = hash_password(new_pw)
        cur.execute(
            f"UPDATE {table_name} SET Password=%s WHERE {where_clause}",
            (new_hash, *where_params)
        )
        conn.commit()
        cur.close()
        conn.close()

        current_pass_entry.delete(0, tk.END)
        new_pass_entry.delete(0, tk.END)
        confirm_pass_entry.delete(0, tk.END)
        messagebox.showinfo("Success", "Password updated successfully")

    tk.Button(
        frame4, text="Update Password",
        bg="#2563eb", fg="white",
        width=16, font=("Arial", 10, "bold"),
        command=change_password
    ).grid(row=0, column=6, padx=(4, 4), pady=4)

    root.mainloop()
