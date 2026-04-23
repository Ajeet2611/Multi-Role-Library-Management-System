import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection


def open_permission_manager():

    win = tk.Toplevel()
    win.title("Institution Permission Management")
    win.geometry("560x560")
    win.configure(bg="#f4f6f9")

    # ================= TITLE =================
    tk.Label(
        win,
        text="Institution Permission Management",
        font=("Segoe UI", 15, "bold"),
        bg="#f4f6f9"
    ).pack(pady=10)

    # ================= SELECT INSTITUTION =================
    tk.Label(win, text="Select Institution", bg="#f4f6f9",
             font=("Segoe UI", 10, "bold")).pack()

    inst_var = tk.StringVar()
    inst_cb = ttk.Combobox(win, state="readonly", width=30)
    inst_cb.pack(pady=4)

    inst_map = {}

    # ================= SELECT ROLE =================
    tk.Label(win, text="Select Role", bg="#f4f6f9",
             font=("Segoe UI", 10, "bold")).pack()

    role_var = tk.StringVar()
    role_cb = ttk.Combobox(
        win,
        textvariable=role_var,
        values=["ADMIN", "USER"],
        state="readonly",
        width=30
    )
    role_cb.pack(pady=4)

    # ================= PERMISSION FRAME =================
    perm_frame = tk.LabelFrame(
        win, text="Permissions",
        bg="white", padx=15, pady=10
    )
    perm_frame.pack(fill="both", expand=True, padx=20, pady=10)

    perm_vars = {}

    # ================= LOAD INSTITUTIONS =================
    def load_institutions():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT InstitutionID, InstitutionName FROM Institutions")
        rows = cur.fetchall()
        conn.close()

        names = []
        for i, n in rows:
            inst_map[n] = i
            names.append(n)

        inst_cb["values"] = names
        if names:
            inst_cb.current(0)

    load_institutions()

    # ================= LOAD PERMISSIONS =================
    def load_permissions():
        for w in perm_frame.winfo_children():
            w.destroy()
        perm_vars.clear()

        inst_name = inst_cb.get()
        role = role_var.get()

        if not inst_name or not role:
            return

        inst_id = inst_map[inst_name]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT PermissionCode, Description FROM Permissions")
        all_perms = cur.fetchall()

        cur.execute("""
            SELECT PermissionCode
            FROM InstitutionRolePermissions
            WHERE InstitutionID=%s AND Role=%s
        """, (inst_id, role))
        role_perms = {r[0] for r in cur.fetchall()}

        conn.close()

        for code, desc in all_perms:
            var = tk.BooleanVar(value=code in role_perms)
            perm_vars[code] = var

            tk.Checkbutton(
                perm_frame,
                text=f"{code} — {desc}",
                variable=var,
                bg="white",
                anchor="w"
            ).pack(fill="x", pady=2)

    inst_cb.bind("<<ComboboxSelected>>", lambda e: load_permissions())
    role_cb.bind("<<ComboboxSelected>>", lambda e: load_permissions())

    # ================= SAVE =================
    def save_permissions():
        inst_name = inst_cb.get()
        role = role_var.get()

        if not inst_name or not role:
            messagebox.showwarning("Missing", "Select Institution & Role")
            return

        inst_id = inst_map[inst_name]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM InstitutionRolePermissions
            WHERE InstitutionID=%s AND Role=%s
        """, (inst_id, role))

        for perm, var in perm_vars.items():
            if var.get():
                cur.execute("""
                    INSERT INTO InstitutionRolePermissions
                    VALUES (%s,%s,%s)
                """, (inst_id, role, perm))

        conn.commit()
        conn.close()

        messagebox.showinfo("Saved", "Permissions updated successfully")

    tk.Button(
        win,
        text="💾 Save Permissions",
        bg="#1e88e5", fg="white",
        width=24,
        command=save_permissions
    ).pack(pady=10)
