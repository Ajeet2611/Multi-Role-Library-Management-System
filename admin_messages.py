import tkinter as tk
from tkinter import ttk, messagebox

from db import get_connection
from messaging import ensure_user_messages_table


def admin_messages_window(institution_id):
    if not ensure_user_messages_table():
        messagebox.showerror("Database Error", "Unable to connect to database")
        return

    win = tk.Toplevel()
    win.title("User Messages")
    win.geometry("1180x700")
    win.minsize(1020, 620)
    win.configure(bg="#f4f6f9")

    main = tk.Frame(win, bg="#f4f6f9")
    main.pack(fill="both", expand=True, padx=12, pady=10)
    main.grid_rowconfigure(1, weight=1)
    main.grid_rowconfigure(2, weight=1, minsize=220)
    main.grid_columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("AdminMsg.Treeview", rowheight=30, font=("Segoe UI", 10))
    style.configure("AdminMsg.Treeview.Heading", font=("Segoe UI", 10, "bold"))

    tk.Label(
        main,
        text="User Messages and Replies",
        font=("Segoe UI", 15, "bold"),
        bg="#f4f6f9"
    ).grid(row=0, column=0, sticky="ew", pady=(0, 8))

    cols = ("ID", "Sent At", "User ID", "Name", "Message", "Reply", "Status", "Replied At")
    table_frame = tk.Frame(main, bg="#f4f6f9")
    table_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    tree = ttk.Treeview(
        table_frame,
        columns=cols,
        show="headings",
        style="AdminMsg.Treeview"
    )
    tree.grid(row=0, column=0, sticky="nsew")

    y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    x_scroll.grid(row=1, column=0, sticky="ew")
    tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

    tree.column("ID", width=0, stretch=False)
    tree.heading("ID", text="")
    tree.column("Sent At", width=160, minwidth=140, anchor="center", stretch=False)
    tree.column("User ID", width=120, minwidth=110, anchor="center", stretch=False)
    tree.column("Name", width=130, minwidth=110, anchor="w", stretch=False)
    tree.column("Message", width=300, minwidth=220, anchor="w", stretch=True)
    tree.column("Reply", width=300, minwidth=220, anchor="w", stretch=True)
    tree.column("Status", width=95, minwidth=80, anchor="center", stretch=False)
    tree.column("Replied At", width=160, minwidth=130, anchor="center", stretch=False)

    for col in cols[1:]:
        tree.heading(col, text=col)

    tree.tag_configure("open", background="#fff7ed")
    tree.tag_configure("replied", background="#ecfdf5")

    selected_message_id = {"value": None}

    details = tk.LabelFrame(main, text="Selected Message", padx=12, pady=12)
    details.grid(row=2, column=0, sticky="nsew", pady=(0, 4))
    details.grid_columnconfigure(1, weight=1)
    details.grid_rowconfigure(2, weight=1)

    tk.Label(details, text="From:", font=("Segoe UI", 10, "bold")).grid(
        row=0, column=0, sticky="w", padx=(2, 8), pady=5
    )
    from_value = tk.Label(details, text="-", anchor="w", justify="left", font=("Segoe UI", 10))
    from_value.grid(row=0, column=1, sticky="ew", pady=5)

    tk.Label(details, text="Message:", font=("Segoe UI", 10, "bold")).grid(
        row=1, column=0, sticky="nw", padx=(2, 8), pady=5
    )
    message_value = tk.Label(details, text="-", anchor="w", justify="left", wraplength=900, font=("Segoe UI", 10))
    message_value.grid(row=1, column=1, sticky="ew", pady=5)

    tk.Label(details, text="Reply:", font=("Segoe UI", 10, "bold")).grid(
        row=2, column=0, sticky="nw", padx=(2, 8), pady=5
    )
    reply_entry = tk.Text(details, height=5, font=("Segoe UI", 10), wrap="word")
    reply_entry.grid(row=2, column=1, sticky="nsew", pady=5)

    btn_frame = tk.Frame(details)
    btn_frame.grid(row=3, column=1, sticky="e", pady=(10, 2))

    def load_messages():
        tree.delete(*tree.get_children())

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT MessageID, SentAt, UserID, Username, UserMessage,
                   COALESCE(AdminReply, ''), Status, RepliedAt
            FROM UserMessages
            WHERE InstitutionID=%s
            ORDER BY SentAt DESC
            """,
            (institution_id,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        for row in rows:
            tag = "replied" if str(row[6]).upper() == "REPLIED" else "open"
            tree.insert("", "end", values=row, tags=(tag,))

    def on_select(_event=None):
        sel = tree.selection()
        if not sel:
            return

        vals = tree.item(sel[0])["values"]
        selected_message_id["value"] = vals[0]
        from_value.config(text=f"{vals[3]} ({vals[2]})")
        message_value.config(text=vals[4] if vals[4] else "-")

        reply_entry.delete("1.0", tk.END)
        if vals[5]:
            reply_entry.insert("1.0", vals[5])

    def send_reply():
        msg_id = selected_message_id["value"]
        reply_text = reply_entry.get("1.0", tk.END).strip()

        if not msg_id:
            messagebox.showwarning("Select Message", "Please select a user message")
            return
        if not reply_text:
            messagebox.showerror("Error", "Reply cannot be empty")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE UserMessages
            SET AdminReply=%s, Status='REPLIED', RepliedAt=NOW()
            WHERE MessageID=%s AND InstitutionID=%s
            """,
            (reply_text, msg_id, institution_id)
        )
        conn.commit()
        cur.close()
        conn.close()

        messagebox.showinfo("Success", "Reply sent successfully")
        load_messages()

    ttk.Button(btn_frame, text="Refresh", command=load_messages).pack(side="left", padx=6)
    ttk.Button(btn_frame, text="Send Reply", command=send_reply).pack(side="left", padx=6)

    tree.bind("<<TreeviewSelect>>", on_select)
    load_messages()
