import tkinter as tk
from tkinter import messagebox, ttk
from db import get_connection
from security import hash_password


def open_super_admin_dashboard(user):
    root = tk.Tk()
    root.title("Super Admin Dashboard")
    root.geometry("720x520")
    root.resizable(True, True)

    # ================= CANVAS + SCROLL =================
    canvas = tk.Canvas(root, highlightthickness=0)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ================= TITLE =================
    tk.Label(
        scroll_frame,
        text="SUPER ADMIN DASHBOARD",
        font=("Arial", 16, "bold")
    ).pack(pady=20)

    # ================= ADD INSTITUTION =================
    frame1 = tk.LabelFrame(scroll_frame, text="Add Institution", padx=25, pady=20)
    frame1.pack(fill="x", padx=40, pady=10)

    tk.Label(frame1, text="Institution Name").pack(anchor="w")
    inst_name = tk.Entry(frame1, width=55)
    inst_name.pack(pady=6)

    tk.Label(frame1, text="Address").pack(anchor="w")
    inst_addr = tk.Entry(frame1, width=55)
    inst_addr.pack(pady=6)

    def add_institution():
        name = inst_name.get().strip()
        addr = inst_addr.get().strip()

        if not name or not addr:
            messagebox.showerror("Error", "All fields required")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Institutions (InstitutionName, Address) VALUES (%s, %s)",
            (name, addr)
        )
        conn.commit()
        cur.close()
        conn.close()

        messagebox.showinfo("Success", "Institution Added Successfully")
        inst_name.delete(0, tk.END)
        inst_addr.delete(0, tk.END)

        load_institutions()  # refresh dropdown

    tk.Button(
        frame1,
        text="Add Institution",
        width=28,
        command=add_institution
    ).pack(pady=12)
    
    # ================= CREATE ADMIN =================
    frame2 = tk.LabelFrame(scroll_frame, text="Create Institution Admin", padx=25, pady=20)
    frame2.pack(fill="x", padx=40, pady=15)

    tk.Label(frame2, text="Admin Username").pack(anchor="w")
    admin_user = tk.Entry(frame2, width=50)
    admin_user.pack(pady=6)

    tk.Label(frame2, text="Admin Password").pack(anchor="w")
    admin_pass = tk.Entry(frame2, width=50, show="*")
    admin_pass.pack(pady=6)

    tk.Label(frame2, text="Select Institution").pack(anchor="w")

    inst_var = tk.StringVar()
    inst_dropdown = ttk.Combobox(
        frame2,
        textvariable=inst_var,
        state="readonly",
        width=47
    )
    inst_dropdown.pack(pady=6)

    institution_map = {}

    def load_institutions():
        institution_map.clear()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT InstitutionID, InstitutionName FROM Institutions")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        names = []
        for iid, name in rows:
            institution_map[name] = iid
            names.append(name)

        inst_dropdown["values"] = names
        if names:
            inst_dropdown.current(0)

    load_institutions()

    def create_admin():
        u = admin_user.get().strip()
        p = admin_pass.get().strip()
        inst_name = inst_var.get()

        if not u or not p or not inst_name:
            messagebox.showerror("Error", "All fields required")
            return

        institution_id = institution_map[inst_name]
        hashed = hash_password(p)

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO Users (Username, Password, Role, InstitutionID)
                VALUES (%s, %s, 'ADMIN', %s)
                """,
                (u, hashed, institution_id)
            )
            conn.commit()
            messagebox.showinfo("Success", "Admin Created Successfully")

            admin_user.delete(0, tk.END)
            admin_pass.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    tk.Button(
        frame2,
        text="Create Admin",
        width=28,
        command=create_admin
    ).pack(pady=14)

    # ================= LOGOUT =================
    tk.Button(
        scroll_frame,
        text="Logout",
        width=22,
        command=root.destroy
    ).pack(pady=25)

    root.mainloop()
