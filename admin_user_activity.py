import tkinter as tk
from tkinter import ttk

from db import get_connection
import winsound  # Assuming winsound functions are used/available elsewhere


# =====================================================
# ================= USER ACTIVITY =====================
# =====================================================
def user_activity_window(institution_id):
    win = tk.Toplevel()
    win.title("User Activity")
    win.geometry("1000x550")
    win.configure(bg="#e0e0e0")

    # --- 1. SEARCH LOGIC ---
    def search_data():
        query = search_entry.get().lower()
        for item in tree.get_children():
            tree.delete(item)
        
        count = 1
        for r in all_data:
            if any(query in str(val).lower() for val in r):
                tag = "evenrow" if count % 2 == 0 else "oddrow"
                tree.insert("", "end", values=(count,) + r, tags=(tag,))
                count += 1

    # --- 2. UNIVERSAL SORTING FUNCTION ---
    def sort_column(col, reverse):
        # Treeview se data nikalna
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        
        # Sorting logic (Dates aur Numbers ko handle karne ke liye)
        try:
            # Agar data numeric hai ya date string hai toh us hisab se sort karega
            l.sort(key=lambda t: t[0].lower(), reverse=reverse)
        except:
            l.sort(reverse=reverse)

        # Re-arrange items in treeview
        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)
            
            # S.No. ko hamesha 1, 2, 3 ke sequence mein rakhne ke liye update
            current_vals = list(tree.item(k, 'values'))
            current_vals[0] = index + 1
            tree.item(k, values=tuple(current_vals))
            
            # Row colors maintain rakhein
            tag = "evenrow" if (index + 1) % 2 == 0 else "oddrow"
            tree.item(k, tags=(tag,))

        # Agli click par opposite sort ho
        tree.heading(col, command=lambda: sort_column(col, not reverse))

    # --- SEARCH UI ---
    search_frame = tk.Frame(win, bg="#e0e0e0")
    search_frame.pack(fill="x", padx=10, pady=5)
    
    tk.Label(search_frame, text="Search Activity:", bg="#e0e0e0", font=("Arial", 10, "bold")).pack(side="left", padx=5)
    search_entry = tk.Entry(search_frame, font=("Arial", 10))
    search_entry.pack(side="left", fill="x", expand=True, padx=5)
    search_entry.bind("<KeyRelease>", lambda e: search_data())

    # --- TREEVIEW SETUP ---
    cols = ("SNo", "Student", "Book", "Issue Date", "Due Date", "Status")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Style
    style = ttk.Style()
    style.theme_use("clam") 
    style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", rowheight=30)
    style.configure("Treeview.Heading", background="#d0d0d0", font=("Arial", 10, "bold"))
    
    # Tag colors
    tree.tag_configure("oddrow", background="#f0f0f0")
    tree.tag_configure("evenrow", background="#ffffff")
    tree.tag_configure("not_returned", foreground="red") # Status ke liye special tag

    # --- HEADINGS WITH SORTING ---
    for c in cols:
        display_name = "S.No." if c == "SNo" else c
        # Har column ki heading par sorting function laga diya
        tree.heading(c, text=display_name, command=lambda _c=c: sort_column(_c, False))
        
        width = 60 if c == "SNo" else 180
        tree.column(c, width=width, anchor="center")

    # --- DATABASE DATA ---
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT M.Name, B.Title, T.IssueDate, T.DueDate, T.ReturnStatus
        FROM Transactions T
        JOIN Members M ON T.MemberID=M.MemberID
        JOIN Books B ON T.BookID=B.BookID
        WHERE T.InstitutionID=%s
        ORDER BY T.IssueDate DESC
    """, (institution_id,))
    
    global all_data
    all_data = cur.fetchall()
    conn.close()

    # --- INITIAL INSERT ---
    for i, r in enumerate(all_data):
        count = i + 1
        # Check if status is "Not Returned" for color
        tag_list = ["evenrow" if count % 2 == 0 else "oddrow"]
        if "issued" in str(r[4]).lower(): # Agar Status mein "not" word hai
             tag_list.append("not_returned")
             
        tree.insert("", "end", values=(count,) + r, tags=tuple(tag_list))

