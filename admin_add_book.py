import tkinter as tk
from tkinter import messagebox

from db import get_connection


# =====================================================
# ================= ADD BOOK ==========================
# =====================================================
def add_book_window(institution_id):
    win = tk.Toplevel()
    win.title("Add Book")
    win.geometry("420x480")
    win.resizable(False, False)

    tk.Label(win, text="Add New Book",
             font=("Arial", 16, "bold")).pack(pady=10)

    def field(lbl):
        label = tk.Label(win, text=lbl, font=("Arial", 10, "bold"))
        label.pack(anchor="w", padx=20, pady=(8, 0))
        e = tk.Entry(win, width=38)
        e.pack(padx=20, pady=5)
        return label, e

    title_lbl, title = field("Book Title *")
    author_lbl, author = field("Author *")
    isbn_lbl, isbn = field("ISBN (Unique) *")
    copies_lbl, copies = field("Total Copies *")

    mode = {"type": "NEW", "book_id": None}

    # ================= ISBN CHECK =================
    def check_existing(event=None):
        mode["type"] = "NEW"
        mode["book_id"] = None

        copies_lbl.config(text="Total Copies *")
        action_btn.config(text="Save Book", bg="#16a34a")

        if not isbn.get():
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT BookID, Title, Author
            FROM Books
            WHERE InstitutionID=%s AND ISBN=%s
        """, (institution_id, isbn.get()))

        row = cur.fetchone()
        conn.close()

        if row:
            book_id, t, a = row

            title.delete(0, tk.END)
            author.delete(0, tk.END)
            title.insert(0, t)
            author.insert(0, a)

            copies_lbl.config(text="Add Copies *")
            action_btn.config(text="Update Book", bg="#2563eb")

            mode["type"] = "UPDATE"
            mode["book_id"] = book_id

    isbn.bind("<FocusOut>", check_existing)

    # ================= SAVE / UPDATE =================
    def save_or_update():
        if not title.get() or not author.get() or not isbn.get() or not copies.get():
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            qty = int(copies.get())
            if qty <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Copies must be a positive number")
            return

        conn = get_connection()
        cur = conn.cursor()

        if mode["type"] == "UPDATE":
            cur.execute("""
                UPDATE Books
                SET 
                    TotalCopies = TotalCopies + %s,
                    AvailableCopies = AvailableCopies + %s
                WHERE BookID=%s
            """, (qty, qty, mode["book_id"]))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Updated",
                f"Book updated successfully\nAdded Copies: {qty}"
            )
            win.destroy()
            return

        # 🆕 NEW BOOK
        cur.execute("""
            INSERT INTO Books
            (Title, Author, ISBN, TotalCopies, AvailableCopies, Status, InstitutionID)
            VALUES (%s,%s,%s,%s,%s,'AVAILABLE',%s)
        """, (
            title.get(),
            author.get(),
            isbn.get(),
            qty,
            qty,
            institution_id
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "New book added successfully")
        win.destroy()

    # ================= BUTTON =================
    action_btn = tk.Button(
        win,
        text="Save Book",
        bg="#16a34a",
        fg="white",
        width=20,
        font=("Arial", 11, "bold"),
        command=save_or_update
    )
    action_btn.pack(pady=25)

