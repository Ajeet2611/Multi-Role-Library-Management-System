import tkinter as tk
from tkinter import messagebox

from datetime import date

from db import get_connection


# =====================================================
# ================= RETURN BOOK =======================
# =====================================================
def return_book_window(institution_id):
    win = tk.Toplevel()
    win.title("Return Book")
    win.geometry("680x420")   # 🔥 compact window
    win.resizable(False, False)

    # ================= TITLE =================
    tk.Label(
        win,
        text="Return Book",
        font=("Arial", 16, "bold")
    ).pack(pady=(10, 5))

    tk.Label(
        win,
        text="Select Issued Book (Search & Scroll)",
        font=("Arial", 11, "bold")
    ).pack(anchor="w", padx=20, pady=(5, 3))

    # ================= SEARCH =================
    search_var = tk.StringVar()
    search_entry = tk.Entry(win, textvariable=search_var, width=55)
    search_entry.pack(padx=20, pady=(0, 6))

    # ================= LISTBOX FRAME =================
    list_frame = tk.Frame(win)
    list_frame.pack(padx=20)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    issued_list = tk.Listbox(
        list_frame,
        width=80,
        height=6,              # 🔥 SMALL BOX (important)
        yscrollcommand=scrollbar.set,
        exportselection=False
    )
    issued_list.pack(side="left", fill="x")

    scrollbar.config(command=issued_list.yview)

    # ================= LOAD DATA =================
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            T.IssueID,
            B.BookID,
            B.Title,
            M.Name,
            T.DueDate
        FROM Transactions T
        JOIN Books B ON T.BookID = B.BookID
        JOIN Members M ON T.MemberID = M.MemberID
        WHERE 
            T.ReturnStatus='ISSUED'
            AND T.InstitutionID=%s
        ORDER BY T.IssueDate
    """, (institution_id,))

    issued_data = []

    for issue_id, book_id, title, student, due in cur.fetchall():
        label = f"{title} | {student} | Due: {due}"
        issued_list.insert(tk.END, label)
        issued_data.append((label, issue_id, book_id, due))

    conn.close()

    # ================= SEARCH FILTER =================
    def filter_list(event=None):
        q = search_var.get().lower()
        issued_list.delete(0, tk.END)
        for label, _, _, _ in issued_data:
            if q in label.lower():
                issued_list.insert(tk.END, label)

    search_entry.bind("<KeyRelease>", filter_list)

    # ================= RETURN LOGIC =================
    def ret():
        if not issued_list.curselection():
            messagebox.showerror("Error", "Please select an issued book")
            return

        selected_label = issued_list.get(issued_list.curselection()[0])
        issue_id, book_id, due_date = next(
            (i, b, d) for lbl, i, b, d in issued_data if lbl == selected_label
        )

        today = date.today()
        late_days = max(0, (today - due_date).days)
        fine = late_days * 5

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE Transactions
            SET ReturnStatus='RETURNED'
            WHERE IssueID=%s
        """, (issue_id,))

        cur.execute("""
            UPDATE Books
            SET AvailableCopies = AvailableCopies + 1
            WHERE BookID=%s
        """, (book_id,))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Book Returned",
            f"Book returned successfully!\n"
            f"Late Days: {late_days}\n"
            f"Fine: ₹{fine}"
        )

        win.destroy()

    # ================= BUTTON =================
    tk.Button(
        win,
        text="Return Book",
        bg="#2e7d32",
        fg="white",
        font=("Arial", 12, "bold"),
        width=26,
        command=ret
    ).pack(pady=18)

