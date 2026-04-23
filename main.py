"""
Library Management System (CLI)
Aligned with GUI + Secure Login
"""

from db import get_connection
from auth import login
from datetime import date, timedelta


# ================= BOOK FUNCTIONS =================

def add_book(institution_id):
    conn = get_connection()
    cur = conn.cursor()

    title = input("Enter Book Title: ")
    author = input("Enter Author Name: ")
    isbn = input("Enter ISBN: ")
    total = int(input("Enter Total Copies: "))

    cur.execute(
        """
        INSERT INTO Books
        (Title, Author, ISBN, Status, TotalCopies, AvailableCopies, InstitutionID)
        VALUES (%s, %s, %s, 'AVAILABLE', %s, %s, %s)
        """,
        (title, author, isbn, total, total, institution_id)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Book Added Successfully")


def show_books(institution_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT BookID, Title, Author, AvailableCopies
        FROM Books
        WHERE InstitutionID = %s
        """,
        (institution_id,)
    )

    print("\n--- BOOK LIST ---")
    for b in cur.fetchall():
        print(b)

    cur.close()
    conn.close()


# ================= ISSUE / RETURN =================

def issue_book(institution_id):
    conn = get_connection()
    cur = conn.cursor()

    book_id = input("Enter BookID: ")
    user_id = input("Enter UserID: ")

    cur.execute(
        """
        SELECT AvailableCopies FROM Books
        WHERE BookID = %s AND InstitutionID = %s
        """,
        (book_id, institution_id)
    )
    book = cur.fetchone()

    if not book or book[0] <= 0:
        print("Book not available")
        conn.close()
        return

    issue_date = date.today()
    due_date = issue_date + timedelta(days=7)

    cur.execute(
        """
        INSERT INTO Transactions
        (BookID, MemberID, IssueDate, DueDate, ReturnStatus)
        VALUES (%s, %s, %s, %s, 'ISSUED')
        """,
        (book_id, user_id, issue_date, due_date)
    )

    cur.execute(
        """
        UPDATE Books
        SET AvailableCopies = AvailableCopies - 1
        WHERE BookID = %s
        """,
        (book_id,)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Book Issued Successfully")


def return_book(institution_id):
    conn = get_connection()
    cur = conn.cursor()

    book_id = input("Enter BookID: ")

    cur.execute(
        """
        SELECT IssueID, DueDate
        FROM Transactions T
        JOIN Books B ON T.BookID = B.BookID
        WHERE T.BookID = %s
          AND T.ReturnStatus = 'ISSUED'
          AND B.InstitutionID = %s
        ORDER BY IssueID DESC
        LIMIT 1
        """,
        (book_id, institution_id)
    )
    record = cur.fetchone()

    if not record:
        print("No active issue found")
        conn.close()
        return

    issue_id, due_date = record
    late = (date.today() - due_date).days

    if late > 0:
        print(f"Late by {late} days | Fine ₹{late * 5}")
    else:
        print("Returned on time")

    cur.execute(
        "UPDATE Transactions SET ReturnStatus='RETURNED' WHERE IssueID=%s",
        (issue_id,)
    )

    cur.execute(
        "UPDATE Books SET AvailableCopies = AvailableCopies + 1 WHERE BookID=%s",
        (book_id,)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Book Returned Successfully")


# ================= PROGRAM START =================

user = login()
if not user:
    exit()

role = user["Role"]
institution_id = user["InstitutionID"]
user_id = user["UserID"]

if role == "ADMIN":
    while True:
        print("\n--- ADMIN MENU ---")
        print("1. Add Book")
        print("2. Show Books")
        print("3. Issue Book")
        print("4. Return Book")
        print("5. Exit")

        ch = input("Enter choice: ")

        if ch == "1":
            add_book(institution_id)
        elif ch == "2":
            show_books(institution_id)
        elif ch == "3":
            issue_book(institution_id)
        elif ch == "4":
            return_book(institution_id)
        elif ch == "5":
            break
        else:
            print("Invalid choice")

else:
    while True:
        print("\n--- USER MENU ---")
        print("1. View Books")
        print("2. Exit")

        ch = input("Enter choice: ")

        if ch == "1":
            show_books(institution_id)
        elif ch == "2":
            break
        else:
            print("Invalid choice")
