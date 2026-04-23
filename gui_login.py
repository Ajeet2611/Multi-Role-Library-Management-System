import tkinter as tk
from tkinter import messagebox
from auth import login

print("WELCOME TO LOGIN WINDOW")

# ================= MAIN WINDOW =================
root = tk.Tk()
root.title("Library Management System")
root.geometry("400x350")  
root.resizable(False, False)

# ================= HEADING =================
tk.Label(
    root,
    text="Library Management System",
    font=("Arial", 15, "bold")
).pack(pady=15)

# ================= USERNAME =================
tk.Label(root, text="Username").pack()
username_entry = tk.Entry(root)
username_entry.pack()

# ================= PASSWORD =================
tk.Label(root, text="Password").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

# ================= LOGIN FUNCTION =================
def do_login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showerror("Error", "All fields required")
        return

    user = login(username, password)

    if not user:
        messagebox.showerror("Login Failed", "Invalid credentials")
        return

    root.destroy()

    from gui_super_admin import open_super_admin_dashboard
    from gui_admin import open_admin_dashboard
    from gui_user import open_user_dashboard

    role = user.get("Role")

    if role == "SUPER_ADMIN":
        open_super_admin_dashboard(user)
    elif role == "ADMIN":
        open_admin_dashboard(user)
    elif role in ("USER", "STUDENT", "TEACHER", "OTHER"):
        open_user_dashboard(user)
    else:
        messagebox.showerror("Error", "Unknown role")

# ================= LOGIN BUTTON =================
tk.Button(
    root,
    text="Login",
    width=15,
    command=do_login
).pack(pady=20)

# ================= FOOTER (Mera Naam) =================

footer = tk.Label(
    root, 
    text="Developed by Ajeet Prasad", 
    font=("Arial", 10, "italic"),
    fg="gray" 
)
footer.pack(side="bottom", pady=10)

root.mainloop()
print("LOGIN WINDOW CLOSED")
