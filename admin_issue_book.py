import tkinter as tk
from tkinter import messagebox

from datetime import date, timedelta

from db import get_connection


# =====================================================
# ================= ISSUE BOOK ========================
# =====================================================
def issue_book_window(institution_id):
    win = tk.Toplevel()
    win.title("Issue Book")
    win.geometry("720x520")
    win.resizable(False, False)

    # ================= TITLE =================
    tk.Label(
        win,
        text="Issue Book",
        font=("Arial", 16, "bold")
    ).pack(pady=10)

    # ==================================================
    # ================= STUDENT ========================
    # ==================================================
    tk.Label(
        win,
        text="Select Student (Search & Scroll)",
        font=("Arial", 11, "bold")
    ).pack(anchor="w", padx=20)

    student_search = tk.Entry(win, width=60)
    student_search.pack(padx=20, pady=5)

    student_frame = tk.Frame(win)
    student_frame.pack(padx=20, fill="x")

    student_scroll = tk.Scrollbar(student_frame)
    student_scroll.pack(side="right", fill="y")

    student_list = tk.Listbox(
        student_frame,
        height=3,                     # ✅ FIXED SMALL BOX
        yscrollcommand=student_scroll.set,
        exportselection=False
    )
    student_list.pack(side="left", fill="x", expand=True)
    student_scroll.config(command=student_list.yview)

    # ==================================================
    # ================= BOOK ===========================
    # ==================================================
    tk.Label(
        win,
        text="Select Book (Search & Scroll)",
        font=("Arial", 11, "bold")
    ).pack(anchor="w", padx=20, pady=(15, 0))

    book_search = tk.Entry(win, width=60)
    book_search.pack(padx=20, pady=5)

    book_frame = tk.Frame(win)
    book_frame.pack(padx=20, fill="x")

    book_scroll = tk.Scrollbar(book_frame)
    book_scroll.pack(side="right", fill="y")

    book_list = tk.Listbox(
        book_frame,
        height=3,                     # ✅ FIXED SMALL BOX
        yscrollcommand=book_scroll.set,
        exportselection=False
    )
    book_list.pack(side="left", fill="x", expand=True)
    book_scroll.config(command=book_list.yview)

    # ==================================================
    # ================= LOAD DATA ======================
    # ==================================================
    conn = get_connection()
    cur = conn.cursor()

    # ---- Students ----
    students = []
    cur.execute("""
        SELECT MemberID, Name, UserID
        FROM Members
        WHERE InstitutionID=%s AND Role='STUDENT'
        ORDER BY Name
    """, (institution_id,))
    for mid, name, uid in cur.fetchall():
        label = f"{name} ({uid})"
        students.append((label, mid))
        student_list.insert(tk.END, label)

    # ---- Books ----
    books = []
    cur.execute("""
        SELECT BookID, Title, AvailableCopies
        FROM Books
        WHERE InstitutionID=%s AND AvailableCopies > 0
        ORDER BY Title
    """, (institution_id,))
    for bid, title, copies in cur.fetchall():
        label = f"{title} | Available: {copies}"
        books.append((label, bid))
        book_list.insert(tk.END, label)

    conn.close()

    # ==================================================
    # ================= SEARCH =========================
    # ==================================================
    def filter_students(e=None):
        q = student_search.get().lower()
        student_list.delete(0, tk.END)
        for label, _ in students:
            if q in label.lower():
                student_list.insert(tk.END, label)

    def filter_books(e=None):
        q = book_search.get().lower()
        book_list.delete(0, tk.END)
        for label, _ in books:
            if q in label.lower():
                book_list.insert(tk.END, label)

    student_search.bind("<KeyRelease>", filter_students)
    book_search.bind("<KeyRelease>", filter_books)

    # ==================================================
    # ================= ISSUE LOGIC ====================
    # ==================================================
    def issue():
        if not student_list.curselection():
            messagebox.showerror("Error", "Please select a student")
            return
        if not book_list.curselection():
            messagebox.showerror("Error", "Please select a book")
            return

        student_label = student_list.get(student_list.curselection()[0])
        book_label = book_list.get(book_list.curselection()[0])

        member_id = next(mid for lbl, mid in students if lbl == student_label)
        book_id = next(bid for lbl, bid in books if lbl == book_label)

        conn = get_connection()
        cur = conn.cursor()

        # 🔴 SAME BOOK SAME STUDENT CHECK
        cur.execute("""
            SELECT 1 FROM Transactions
            WHERE MemberID=%s AND BookID=%s
              AND ReturnStatus='ISSUED'
              AND InstitutionID=%s
        """, (member_id, book_id, institution_id))

        if cur.fetchone():
            messagebox.showerror(
                "Already Issued",
                "This student already has this book.\nPlease return it first."
            )
            conn.close()
            return

        issue_date = date.today()
        due_date = issue_date + timedelta(days=7)

        cur.execute("""
            INSERT INTO Transactions
            (BookID, MemberID, IssueDate, DueDate, ReturnStatus, InstitutionID)
            VALUES (%s,%s,%s,%s,'ISSUED',%s)
        """, (book_id, member_id, issue_date, due_date, institution_id))

        cur.execute("""
            UPDATE Books
            SET AvailableCopies = AvailableCopies - 1
            WHERE BookID=%s
        """, (book_id,))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            f"Book issued successfully!\nDue Date: {due_date}"
        )
        win.destroy()

    # ==================================================
    # ================= BUTTON =========================
    # ==================================================
    tk.Button(
        win,
        text="Issue Book",
        bg="#8e24aa",
        fg="white",
        font=("Arial", 12, "bold"),
        width=30,
        command=issue
    ).pack(pady=25)

