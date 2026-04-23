import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import threading
import os
import winsound
import random
import string
import re
from datetime import date, timedelta

from PIL import Image, ImageTk
from openpyxl import Workbook

from db import get_connection
from security import hash_password
from permissions import get_user_permissions
from dashboard_charts import open_dashboard_charts

from admin_add_book import add_book_window
from admin_add_user import add_user_window
from admin_users_view import view_users_window, restore_users_window
from admin_books_list import show_books_window
from admin_issue_book import issue_book_window
from admin_return_book import return_book_window
from admin_user_activity import user_activity_window
from admin_messages import admin_messages_window


user = None  # Global default to avoid NameError if referenced unexpectedly
permissions = None
ERROR_BG = "#ffe6e6"
NORMAL_BG = "white"


# ================= PATH =================
BASE_DIR = os.path.dirname(__file__)
ASSETS = os.path.join(BASE_DIR, "assets")


# =====================================================
# ================= ADMIN DASHBOARD ===================
# =====================================================

def open_admin_dashboard(user):
    global permissions

    institution_id = user["InstitutionID"]
    permissions = get_user_permissions(user["Role"])

    root = tk.Tk()
    root.title("Admin Dashboard")
    root.state("zoomed")

    # ================= LOAD BG =================
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

    # ================= TITLE =================
    tk.Label(
        root,
        text="ADMIN DASHBOARD",
        font=("Arial", 26, "bold"),
        bg="black",
        fg="white",
        padx=40,
        pady=10
    ).place(relx=0.5, rely=0.06, anchor="center")

    # ================= ICON LOADER =================
    def load_icon(name, size):
        return ImageTk.PhotoImage(
            Image.open(os.path.join(ASSETS, name)).resize((size, size))
        )

    buttons = [
        ("Add Book", "add.png", "#ff6f00", lambda: add_book_window(institution_id)),
        ("Show Books", "show.png", "#039be5", lambda: show_books_window(institution_id)),
        ("Add Student", "user.png", "#1e88e5", lambda: add_user_window(institution_id)),

        ("Issue Book", "issue.png", "#8e24aa", lambda: issue_book_window(institution_id)),
        ("Return Book", "return.png", "#2e7d32", lambda: return_book_window(institution_id)),
        ("User Activity", "history.png", "#6a1b9a", lambda: user_activity_window(institution_id)),
        ("View Users", "user_d.png", "#0d47a1", lambda: view_users_window(institution_id)),
        ("User Messages", "history.png", "#7c3aed", lambda: admin_messages_window(institution_id)),

        ("Logout", "logout.png", "#37474f", root.destroy),
    ]

    # ================= BUTTON POSITIONS =================
    positions = [
        (0.25, 0.30), (0.50, 0.30), (0.75, 0.30),
        (0.25, 0.48), (0.50, 0.48), (0.75, 0.48),
        (0.25, 0.66), (0.50, 0.66), (0.75, 0.66),

    ]

    for (text, img, hover, cmd), (rx, ry) in zip(buttons, positions):

        icon = load_icon(img, 42)

        btn = tk.Button(
            root,
            text="  " + text,
            image=icon,
            compound="left",
            width=190,
            height=52,
            bg="#d35400",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="raised",
            bd=4,
            cursor="hand2",
            command=cmd
        )
        btn.image = icon
        btn.place(relx=rx, rely=ry, anchor="center")

        # SAFE hover (NO resize)
        btn.bind("<Enter>", lambda e, b=btn, c=hover: b.config(bg=c))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#d35400"))

import tkinter as tk
from tkinter import ttk
import threading

from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
from db import get_connection
from datetime import date, timedelta
import os
import winsound
import random
import string
from security import hash_password
import re
from openpyxl import Workbook
from permissions import get_user_permissions
from dashboard_charts import open_dashboard_charts



user = None  # Global default to avoid NameError if referenced unexpectedly
permissions = None
ERROR_BG = "#ffe6e6"
NORMAL_BG = "white"



# ================= PATH =================
BASE_DIR = os.path.dirname(__file__)
ASSETS = os.path.join(BASE_DIR, "assets")


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


# =====================================================
# ================= ADD STUDENT =======================
# =====================================================



def generate_unique_user_id(name, institution_id):
    base = re.sub(r'[^a-zA-Z]', '', name.lower())[:10]
    if not base:
        base = "user"

    conn = get_connection()
    cur = conn.cursor()

    while True:
        user_id = f"{base}{random.randint(1000, 9999)}"
        cur.execute(
            "SELECT 1 FROM Members WHERE UserID=%s AND InstitutionID=%s",
            (user_id, institution_id)
        )
        if not cur.fetchone():
            break

    conn.close()
    return user_id



def generate_password(length=10):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))


def valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)
# =====================================================
# ================= CHECK DUPLICATE USER ==============

def check_duplicate_user(email, contact, institution_id):
    conn = get_connection()
    cur = conn.cursor()

    # Email is GLOBAL unique
    cur.execute(
        "SELECT 1 FROM Members WHERE Email=%s",
        (email,)
    )
    if cur.fetchone():
        conn.close()
        return "EMAIL"

    # Contact is unique PER institution
    cur.execute(
        "SELECT 1 FROM Members WHERE Contact=%s AND InstitutionID=%s",
        (contact, institution_id)
    )
    if cur.fetchone():
        conn.close()
        return "CONTACT"

    conn.close()
    return None



# ======================================================
# ================= ADD USER WINDOW ====================
# ======================================================

def add_user_window(institution_id):

    win = tk.Toplevel()
    win.title("Add User")
    win.geometry("560x780")
    win.resizable(False, False)
    win.configure(bg="#f4f6f9")

    canvas = tk.Canvas(win, bg="#f4f6f9", highlightthickness=0)
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    form = tk.Frame(canvas, bg="white", bd=1, relief="solid")
    canvas.create_window((0, 0), window=form, anchor="nw", width=520)
    form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # ================= FORM STATE =================
    form_state = {
        "name": False,
        "email": False,
        "contact": False,
        "gender": False,
        "role": False,
        "student_ok": True,
        "teacher_ok": True,
        "other_ok": True
    }

    def check_form_ready():
        save_btn.config(
            state="normal" if all(form_state.values()) else "disabled"
        )

    # ================= TITLE =================
    tk.Label(
        form, text="Add New User",
        bg="white", font=("Segoe UI", 16, "bold")
    ).pack(pady=15)

    # ================= FIELD MAKER =================
    def field(parent, label, required=False):
        box = tk.Frame(parent, bg="white")
        box.pack(fill="x", padx=25, pady=6)

        tk.Label(
            box, text=label + (" *" if required else ""),
            bg="white", font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        entry = tk.Entry(box, font=("Segoe UI", 11))
        entry.pack(fill="x", ipady=6)

        err = tk.Label(box, text="", fg="red", bg="white", font=("Segoe UI", 9))
        err.pack(anchor="w")

        return entry, err

    # ================= COMMON =================
    name, name_err = field(form, "Full Name", True)
    email, email_err = field(form, "Email ID", True)
    contact, contact_err = field(form, "Mobile Number (10 digits)", True)

    contact.configure(
        validate="key",
        validatecommand=(win.register(lambda v: v.isdigit() or v == ""), "%P")
    )

    # ================= GENDER =================
    tk.Label(form, text="Gender *", bg="white",
             font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=25)

    gender_var = tk.StringVar()
    gender_cb = ttk.Combobox(
        form, textvariable=gender_var,
        values=["MALE", "FEMALE", "OTHER"],
        state="readonly"
    )
    gender_cb.pack(fill="x", padx=25, ipady=4)

    gender_cb.bind(
        "<<ComboboxSelected>>",
        lambda e: (form_state.update({"gender": True}), check_form_ready())
    )

    address, _ = field(form, "Address")

    # ================= ROLE =================
    tk.Label(form, text="Role *", bg="white",
             font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=25)

    role_var = tk.StringVar()
    role_cb = ttk.Combobox(
        form, textvariable=role_var,
        values=["STUDENT", "TEACHER", "OTHER"],
        state="readonly"
    )
    role_cb.pack(fill="x", padx=25, ipady=4)

    # ================= ROLE FRAMES =================
    student_frame = tk.Frame(form, bg="white")
    enroll, enroll_err = field(student_frame, "Enrollment Number", True)
    course, _ = field(student_frame, "Course / Branch", True)
    semester, _ = field(student_frame, "Semester / Year", True)
    batch, batch_err = field(student_frame, "Batch Year (YYYY)", True)

    teacher_frame = tk.Frame(form, bg="white")
    emp_id, emp_err = field(teacher_frame, "Employee ID", True)
    department, _ = field(teacher_frame, "Department")
    designation, _ = field(teacher_frame, "Designation")

    other_frame = tk.Frame(form, bg="white")
    other_role, other_role_err = field(other_frame, "Role Name", True)
    other_role_id, other_role_id_err = field(other_frame, "Role Unique ID", True)
    category, _ = field(other_frame, "Category")
    id_proof, _ = field(other_frame, "ID Proof")

    def hide_roles():
        student_frame.pack_forget()
        teacher_frame.pack_forget()
        other_frame.pack_forget()

    def on_role_change(e=None):
        hide_roles()
        form_state["role"] = True

        if role_var.get() == "STUDENT":
            student_frame.pack(fill="x")
            form_state["student_ok"] = False
            form_state["teacher_ok"] = True
            form_state["other_ok"] = True

        elif role_var.get() == "TEACHER":
            teacher_frame.pack(fill="x")
            form_state["teacher_ok"] = False
            form_state["student_ok"] = True
            form_state["other_ok"] = True

        else:
            other_frame.pack(fill="x")
            form_state["other_ok"] = False
            form_state["student_ok"] = True
            form_state["teacher_ok"] = True

        check_form_ready()

    role_cb.bind("<<ComboboxSelected>>", on_role_change)

    # ================= LIVE VALIDATION =================
    def v_name(*_):
        ok = len(name.get().strip()) >= 3
        form_state["name"] = ok
        name_err.config(text="" if ok else "Minimum 3 characters")
        check_form_ready()

    def v_email(*_):
        val = email.get().strip()
        if not valid_email(val):
            form_state["email"] = False
            email_err.config(text="Invalid email format")
        elif check_duplicate_user(val, contact.get(), institution_id) == "EMAIL":
            form_state["email"] = False
            email_err.config(text="Email already exists")
        else:
            form_state["email"] = True
            email_err.config(text="")
        check_form_ready()

    def v_contact(*_):
        val = contact.get().strip()
        if not val.isdigit() or len(val) != 10:
            form_state["contact"] = False
            contact_err.config(text="Enter 10 digits")
        elif check_duplicate_user(email.get(), val, institution_id) == "CONTACT":
            form_state["contact"] = False
            contact_err.config(text="Mobile already exists")
        else:
            form_state["contact"] = True
            contact_err.config(text="")
        check_form_ready()

    def v_student(*_):
        if role_var.get() == "STUDENT":
            form_state["student_ok"] = (
                enroll.get().strip() != "" and
                course.get().strip() != "" and
                semester.get().strip() != "" and
                batch.get().isdigit() and len(batch.get()) == 4
            )
        check_form_ready()

    def v_teacher(*_):
        if role_var.get() == "TEACHER":
            form_state["teacher_ok"] = emp_id.get().strip() != ""
        check_form_ready()

    def v_other(*_):
        if role_var.get() == "OTHER":
            form_state["other_ok"] = (
                other_role.get().strip() != "" and
                other_role_id.get().strip() != ""
            )
        check_form_ready()

    # Bind validations
    name.bind("<KeyRelease>", v_name)
    email.bind("<KeyRelease>", v_email)
    contact.bind("<KeyRelease>", v_contact)

    enroll.bind("<KeyRelease>", v_student)
    course.bind("<KeyRelease>", v_student)
    semester.bind("<KeyRelease>", v_student)
    batch.bind("<KeyRelease>", v_student)

    emp_id.bind("<KeyRelease>", v_teacher)

    other_role.bind("<KeyRelease>", v_other)
    other_role_id.bind("<KeyRelease>", v_other)

    # ================= SAVE =================
    def save():
        try:
            conn = get_connection()
            cur = conn.cursor()

            user_id = generate_unique_user_id(name.get(), institution_id)
            raw_pass = generate_password()

            cur.execute("""
                INSERT INTO Members
                (Name, Email, Contact, Gender, Address, UserID, Password, Role, InstitutionID)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                name.get().strip(),
                email.get().strip(),
                contact.get().strip(),
                gender_var.get(),
                address.get().strip(),
                user_id,
                hash_password(raw_pass),
                role_var.get(),
                institution_id
            ))

            member_id = cur.lastrowid

            if role_var.get() == "STUDENT":
                cur.execute("""
                    INSERT INTO StudentDetails
                    (MemberID, EnrollmentNo, Course, Semester, BatchYear)
                    VALUES (%s,%s,%s,%s,%s)
                """, (
                    member_id,
                    enroll.get().strip(),
                    course.get().strip(),
                    semester.get().strip(),
                    batch.get().strip()
                ))

            elif role_var.get() == "TEACHER":
                cur.execute("""
                    INSERT INTO TeacherDetails
                    (MemberID, EmployeeID, Department, Designation)
                    VALUES (%s,%s,%s,%s)
                """, (
                    member_id,
                    emp_id.get().strip(),
                    department.get().strip(),
                    designation.get().strip()
                ))

            else:
                cur.execute("""
                    INSERT INTO StaffDetails
                    (MemberID, RoleName, RoleUniqueID, Category, IDProof)
                    VALUES (%s,%s,%s,%s,%s)
                """, (
                    member_id,
                    other_role.get().strip(),
                    other_role_id.get().strip(),
                    category.get().strip(),
                    id_proof.get().strip()
                ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"User Added Successfully\n\nUser ID: {user_id}\nPassword: {raw_pass}"
            )
            win.destroy()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    save_btn = tk.Button(
        form, text="Save User",
        bg="#1e88e5", fg="white",
        font=("Segoe UI", 11, "bold"),
        height=2,
        state="disabled",
        command=save
    )
    save_btn.pack(pady=25, fill="x", padx=50)



# =====================================================

# =====================================================
# ================= VIEW USERS ========================
def view_users_window(institution_id):

    win = tk.Toplevel()
    win.title("Users Management")
    win.geometry("1180x560")
    win.configure(bg="#f2f4f7")
    win.resizable(False, False)

    # ================= TITLE =================
    tk.Label(
        win,
        text="Registered Users",
        font=("Segoe UI", 16, "bold"),
        bg="#f2f4f7"
    ).pack(pady=10)

    # ================= SEARCH =================
    search_frame = tk.Frame(win, bg="#f2f4f7")
    search_frame.pack(fill="x", padx=20)

    tk.Label(search_frame, text="Search:",
             font=("Segoe UI", 10, "bold"),
             bg="#f2f4f7").pack(side="left")

    search_var = tk.StringVar()
    tk.Entry(search_frame, textvariable=search_var, width=40)\
        .pack(side="left", padx=10)

    tk.Label(search_frame,
             text="(Name / Email / Mobile)",
             fg="gray", bg="#f2f4f7").pack(side="left")

    # ================= TREEVIEW =================
    cols = ("MID", "S.No", "Name", "User ID", "Email", "Contact", "Role")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    tree.pack(fill="both", expand=True, padx=20, pady=12)

    tree.column("MID", width=0, stretch=False)
    tree.heading("MID", text="")

    tree.column("S.No", width=60, anchor="center")
    tree.column("Name", width=220)
    tree.column("User ID", width=160, anchor="center")
    tree.column("Email", width=260)
    tree.column("Contact", width=130, anchor="center")
    tree.column("Role", width=120, anchor="center")

    for c in cols[1:]:
        tree.heading(c, text=c)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    tree.tag_configure("odd", background="#ffffff")
    tree.tag_configure("even", background="#f5f5f5")

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

    # ================= DOUBLE CLICK → PROFILE + EDIT =================
    def show_profile(event):
        sel = tree.selection()
        if not sel:
            return

        member_id, _, name, user_id, email, contact, role = tree.item(sel[0])["values"]

        prof = tk.Toplevel(win)
        prof.title("Edit User Profile")
        prof.geometry("480x520")
        prof.configure(bg="#ffffff")
        prof.resizable(False, False)

        tk.Label(
            prof, text="User Profile",
            font=("Segoe UI", 14, "bold"),
            bg="#ffffff"
        ).pack(pady=10)

        form = tk.Frame(prof, bg="#ffffff")
        form.pack(padx=20, fill="both")

        fields = {}

        def field(label, value, readonly=False):
            row = tk.Frame(form, bg="#ffffff")
            row.pack(fill="x", pady=6)

            tk.Label(row, text=label,
                     font=("Segoe UI", 10, "bold"),
                     width=14, anchor="w",
                     bg="#ffffff").pack(side="left")

            e = tk.Entry(row, width=30)
            e.pack(side="left", padx=5)
            e.insert(0, value)
            if readonly:
                e.config(state="readonly")
            fields[label] = e

        # Common
        field("Name", name)
        field("User ID", user_id, True)
        field("Email", email)
        field("Contact", contact)
        field("Role", role, True)

        conn = get_connection()
        cur = conn.cursor()

        if role == "STUDENT":
            cur.execute("""
                SELECT Course, Semester, BatchYear
                FROM StudentDetails WHERE MemberID=%s
            """, (member_id,))
            r = cur.fetchone()
            if r:
                field("Course", r[0])
                field("Semester", r[1])
                field("Batch", r[2])

        elif role == "TEACHER":
            cur.execute("""
                SELECT EmployeeID, Department, Designation
                FROM TeacherDetails WHERE MemberID=%s
            """, (member_id,))
            r = cur.fetchone()
            if r:
                field("Employee ID", r[0])
                field("Department", r[1])
                field("Designation", r[2])

        else:
            cur.execute("""
                SELECT Category, IDProof
                FROM StaffDetails WHERE MemberID=%s
            """, (member_id,))
            r = cur.fetchone()
            if r:
                field("Category", r[0])
                field("ID Proof", r[1])

        conn.close()

        def save_changes():
            try:
                conn = get_connection()
                cur = conn.cursor()

                cur.execute("""
                    UPDATE Members
                    SET Name=%s, Email=%s, Contact=%s
                    WHERE MemberID=%s
                """, (
                    fields["Name"].get(),
                    fields["Email"].get(),
                    fields["Contact"].get(),
                    member_id
                ))

                if role == "STUDENT":
                    cur.execute("""
                        UPDATE StudentDetails
                        SET Course=%s, Semester=%s, BatchYear=%s
                        WHERE MemberID=%s
                    """, (
                        fields["Course"].get(),
                        fields["Semester"].get(),
                        fields["Batch"].get(),
                        member_id
                    ))

                elif role == "TEACHER":
                    cur.execute("""
                        UPDATE TeacherDetails
                        SET EmployeeID=%s, Department=%s, Designation=%s
                        WHERE MemberID=%s
                    """, (
                        fields["Employee ID"].get(),
                        fields["Department"].get(),
                        fields["Designation"].get(),
                        member_id
                    ))

                else:
                    cur.execute("""
                        UPDATE StaffDetails
                        SET Category=%s, IDProof=%s
                        WHERE MemberID=%s
                    """, (
                        fields["Category"].get(),
                        fields["ID Proof"].get(),
                        member_id
                    ))

                conn.commit()
                conn.close()

                load_users()
                messagebox.showinfo("Updated", "User updated successfully")
                prof.destroy()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(
            prof, text="💾 Save Changes",
            bg="#1e88e5", fg="white",
            font=("Segoe UI", 10, "bold"),
            width=18,
            command=save_changes
        ).pack(pady=15)

    tree.bind("<Double-1>", show_profile)

    # ================= DELETE (SOFT) =================
    def delete_user():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Select User", "Please select a user")
            return

        member_id = tree.item(sel[0])["values"][0]

        if not messagebox.askyesno(
            "Confirm Delete",
            "User will be deactivated.\nYou can restore later.\n\nContinue?"
        ):
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE Members
            SET Status='INACTIVE'
            WHERE MemberID=%s AND InstitutionID=%s
        """, (member_id, institution_id))
        conn.commit()
        conn.close()

        load_users()
        messagebox.showinfo("Deleted", "User moved to inactive list")

    # ================= EXPORT =================
    def export_excel():
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if not path:
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT Name, UserID, Email, Contact, Role
            FROM Members
            WHERE InstitutionID=%s AND Status='ACTIVE'
            ORDER BY Name
        """, (institution_id,))
        rows = cur.fetchall()
        conn.close()

        if not rows:
            messagebox.showwarning("No Data", "No users to export")
            return

        wb = Workbook()
        ws = wb.active
        ws.append(("Name", "User ID", "Email", "Contact", "Role"))

        for r in rows:
            ws.append(r)

        wb.save(path)
        messagebox.showinfo("Exported", f"Excel saved:\n{path}")

    # ================= BUTTON BAR =================
    btn_frame = tk.Frame(win, bg="#f2f4f7")
    btn_frame.pack(pady=8)

    tk.Button(btn_frame, text="🗑 Delete User",
              bg="#d9534f", fg="white",
              width=16, command=delete_user)\
        .pack(side="left", padx=6)

    tk.Button(btn_frame, text="📤 Export Excel",
              bg="#5cb85c", fg="white",
              width=16, command=export_excel)\
        .pack(side="left", padx=6)

    tk.Button(btn_frame, text="♻ Restore Users",
              bg="#6f42c1", fg="white",
              width=16,
              command=lambda: restore_users_window(institution_id))\
        .pack(side="left", padx=6)

    
# =====================================================
# ================= RESTORE USERS =====================
def restore_users_window(institution_id):

    win = tk.Toplevel()
    win.title("Restore Deleted Users")
    win.geometry("900x420")
    win.configure(bg="#f4f6f9")

    tk.Label(
        win,
        text="Inactive / Deleted Users",
        font=("Segoe UI", 15, "bold"),
        bg="#f4f6f9"
    ).pack(pady=10)

    cols = ("MID", "Name", "Email", "Contact", "Role")
    tree_restore = ttk.Treeview(win, columns=cols, show="headings")
    tree_restore.pack(fill="both", expand=True, padx=15, pady=10)

    tree_restore.column("MID", width=0, stretch=False)
    tree_restore.heading("MID", text="")

    for c in cols[1:]:
        tree_restore.heading(c, text=c)
        tree_restore.column(c, width=180)

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

    tk.Button(
        win,
        text="♻ Restore User",
        bg="#1e88e5", fg="white",
        width=18,
        command=restore_user
    ).pack(pady=10)



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


# =====================================================
# ================= USER ACTIVITY =====================
# =====================================================
import tkinter as tk
from tkinter import ttk
# Assuming get_connection() and winsound functions are defined elsewhere

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
# =====================================================
# ================= ADMIN DASHBOARD ===================
# =====================================================

def open_admin_dashboard(user):
    global permissions

    institution_id = user["InstitutionID"]
    permissions = get_user_permissions(user["Role"])

    root = tk.Tk()
    root.title("Admin Dashboard")
    root.state("zoomed")

    # ================= LOAD BG =================
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

    # ================= TITLE =================
    tk.Label(
        root,
        text="ADMIN DASHBOARD",
        font=("Arial", 26, "bold"),
        bg="black",
        fg="white",
        padx=40,
        pady=10
    ).place(relx=0.5, rely=0.06, anchor="center")

    # ================= ICON LOADER =================
    def load_icon(name, size):
        return ImageTk.PhotoImage(
            Image.open(os.path.join(ASSETS, name)).resize((size, size))
        )

    buttons = [
        ("Add Book", "add.png", "#ff6f00", lambda: add_book_window(institution_id)),
        ("Show Books", "show.png", "#039be5", lambda: show_books_window(institution_id)),
        ("Add Student", "user.png", "#1e88e5", lambda: add_user_window(institution_id)),

        ("Issue Book", "issue.png", "#8e24aa", lambda: issue_book_window(institution_id)),
        ("Return Book", "return.png", "#2e7d32", lambda: return_book_window(institution_id)),
        ("User Activity", "history.png", "#6a1b9a", lambda: user_activity_window(institution_id)),
        ("View Users", "user_d.png", "#0d47a1", lambda: view_users_window(institution_id)),
        ("User Messages", "history.png", "#7c3aed", lambda: admin_messages_window(institution_id)),


        ("Logout", "logout.png", "#37474f", root.destroy),
    ]

    # ================= BUTTON POSITIONS =================
    positions = [
        (0.25, 0.30), (0.50, 0.30), (0.75, 0.30),
        (0.25, 0.48), (0.50, 0.48), (0.75, 0.48),
        (0.25, 0.66), (0.50, 0.66), (0.75, 0.66),

    ]

    for (text, img, hover, cmd), (rx, ry) in zip(buttons, positions):

        icon = load_icon(img, 42)

        btn = tk.Button(
            root,
            text="  " + text,
            image=icon,
            compound="left",
            width=190,
            height=52,
            bg="#d35400",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="raised",
            bd=4,
            cursor="hand2",
            command=cmd
        )
        btn.image = icon
        btn.place(relx=rx, rely=ry, anchor="center")

        # SAFE hover (NO resize)
        btn.bind("<Enter>", lambda e, b=btn, c=hover: b.config(bg=c))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#d35400"))

