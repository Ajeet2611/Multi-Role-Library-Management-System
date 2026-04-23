# auth.py
from db import get_connection
from security import check_password

def login(username=None, password=None):
    conn = get_connection()
    if conn is None:
        return None

    # CLI mode
    if username is None and password is None:
        username = input("Enter Username: ")
        password = input("Enter Password: ")

    cursor = conn.cursor(dictionary=True)

    query_users = """
    SELECT UserID, Username, Password, Role, InstitutionID
    FROM Users
    WHERE Username = %s
    """
    cursor.execute(query_users, (username,))
    user = cursor.fetchone()

    # If not found in Users, try Members (end-user accounts)
    if not user:
        query_members = """
        SELECT MemberID, UserID, Name, Password, Role, InstitutionID
        FROM Members
        WHERE UserID = %s AND Status = 'ACTIVE'
        """
        cursor.execute(query_members, (username,))
        member = cursor.fetchone()
    else:
        member = None

    cursor.close()
    conn.close()

    if not user and not member:
        return None

    # 🔐 Password verify for Users table records
    if user and check_password(password, user["Password"]):
        return {
            "UserID": user["UserID"],
            "Username": user["Username"],
            "Role": user["Role"],
            "InstitutionID": user["InstitutionID"]
        }

    # 🔐 Password verify for Members table records
    if member and check_password(password, member["Password"]):
        return {
            "UserID": member["UserID"],
            "Username": member["Name"],
            "Role": member["Role"],
            "InstitutionID": member["InstitutionID"]
        }

    return None
