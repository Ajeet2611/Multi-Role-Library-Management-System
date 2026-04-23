import tkinter as tk
from tkinter import ttk

from db import get_connection


# =====================================================
# ================= SHOW BOOKS ========================
# =====================================================
def show_books_window(institution_id):
    win = tk.Toplevel()
    win.title("Books List")
    win.geometry("980x480")
    win.resizable(False, False)

    # ================= SORTING FUNCTION =================
    def sort_column(tree, col, reverse):
        # Treeview se saara data uthayein
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        
        # Data ko sort karein (Numbers ke liye int conversion try karein)
        try:
            l.sort(key=lambda t: int(t[0]), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)

        # Sorted data ko wapas treeview mein arrange karein
        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)
            # Zebra striping fix karein sorting ke baad
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            tree.item(k, tags=(tag,))

        # Agli baar click karne par reverse sort ho, isliye command update karein
        tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

    # ================= TITLE =================
    tk.Label(win, text="Books List", font=("Arial", 16, "bold")).pack(pady=8)

    # ================= STYLE =================
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", font=("Arial", 11), rowheight=34, background="#ffffff", fieldbackground="#ffffff")
    style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#e5e7eb", relief="solid")
    style.map("Treeview", background=[("selected", "#2563eb")], foreground=[("selected", "white")])

    # ================= FRAME =================
    frame = tk.Frame(win, bd=2, relief="groove")
    frame.pack(fill="both", expand=True, padx=12, pady=8)

    y_scroll = ttk.Scrollbar(frame, orient="vertical")
    y_scroll.pack(side="right", fill="y")
    x_scroll = ttk.Scrollbar(frame, orient="horizontal")
    x_scroll.pack(side="bottom", fill="x")

    # ================= TREEVIEW (S.No. Added) =================
    cols = ("SNo", "Title", "Author", "ISBN", "Total", "Available")
    tree = ttk.Treeview(frame, columns=cols, show="headings", yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
    tree.pack(fill="both", expand=True)

    y_scroll.config(command=tree.yview)
    x_scroll.config(command=tree.xview)

    # ================= HEADINGS (With Sort Command) =================
    # Har heading par click karne se sort_column function chalega
    for col in cols:
        display_text = "S.No." if col == "SNo" else col
        if col == "Total": display_text = "Total Copies"
        if col == "Available": display_text = "Available Copies"
        
        tree.heading(col, text=display_text, anchor="center", 
                     command=lambda _col=col: sort_column(tree, _col, False))

    # ================= COLUMNS =================
    tree.column("SNo", width=60, anchor="center", stretch=False)
    tree.column("Title", width=270, anchor="center", stretch=False)
    tree.column("Author", width=180, anchor="center", stretch=False)
    tree.column("ISBN", width=140, anchor="center", stretch=False)
    tree.column("Total", width=120, anchor="center", stretch=False)
    tree.column("Available", width=130, anchor="center", stretch=False)

    # ================= LOAD DATA =================
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT Title, Author, ISBN, TotalCopies, AvailableCopies
        FROM Books
        WHERE InstitutionID=%s
        ORDER BY Title
    """, (institution_id,))
    rows = cur.fetchall()
    conn.close()

    # ================= INSERT DATA (S.No. Logic) =================
    for i, row in enumerate(rows):
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        # Row ki shuruat mein Serial Number (i+1) add kar rahe hain
        display_row = (i + 1,) + row
        tree.insert("", "end", values=display_row, tags=(tag,))

    tree.tag_configure("evenrow", background="#f9fafb")
    tree.tag_configure("oddrow", background="#f3f4f6") 
    # Purple color hata kar light grey kiya hai readable dikhne ke liye

