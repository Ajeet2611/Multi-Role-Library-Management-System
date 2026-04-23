import tkinter as tk
from tkinter import ttk, messagebox

import random
import string
import re

from db import get_connection
from security import hash_password


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

