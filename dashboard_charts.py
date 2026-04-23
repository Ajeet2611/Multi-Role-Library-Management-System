import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from db import get_connection


def open_dashboard_charts(parent, user):

    frame = tk.Frame(parent, bg="#f2f4f7")
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    # ================= DB DATA =================
    conn = get_connection()
    cur = conn.cursor()

    # Total Users
    cur.execute("""
        SELECT COUNT(*) FROM Members
        WHERE InstitutionID=%s
    """, (user["InstitutionID"],))
    total_users = cur.fetchone()[0]

    # Active vs Inactive
    cur.execute("""
        SELECT Status, COUNT(*)
        FROM Members
        WHERE InstitutionID=%s
        GROUP BY Status
    """, (user["InstitutionID"],))
    status_data = dict(cur.fetchall())

    # Role distribution
    cur.execute("""
        SELECT Role, COUNT(*)
        FROM Members
        WHERE InstitutionID=%s
        GROUP BY Role
    """, (user["InstitutionID"],))
    role_data = dict(cur.fetchall())

    conn.close()

    # ================= METRIC CARDS =================
    card = tk.Frame(frame, bg="#ffffff", bd=1, relief="solid")
    card.pack(fill="x", pady=10)

    tk.Label(
        card, text=f"Total Users : {total_users}",
        font=("Segoe UI", 14, "bold"),
        bg="#ffffff"
    ).pack(pady=10)

    # ================= PIE CHART =================
    fig1 = Figure(figsize=(4, 3), dpi=100)
    ax1 = fig1.add_subplot(111)

    labels = status_data.keys()
    values = status_data.values()

    ax1.pie(values, labels=labels, autopct="%1.1f%%")
    ax1.set_title("Active vs Inactive Users")

    canvas1 = FigureCanvasTkAgg(fig1, frame)
    canvas1.get_tk_widget().pack(side="left", padx=10, pady=10)

    # ================= BAR CHART =================
    fig2 = Figure(figsize=(4, 3), dpi=100)
    ax2 = fig2.add_subplot(111)

    roles = list(role_data.keys())
    counts = list(role_data.values())

    ax2.bar(roles, counts)
    ax2.set_title("Role Distribution")
    ax2.set_ylabel("Users")

    canvas2 = FigureCanvasTkAgg(fig2, frame)
    canvas2.get_tk_widget().pack(side="left", padx=10, pady=10)
