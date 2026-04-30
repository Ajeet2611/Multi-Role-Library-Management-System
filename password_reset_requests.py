"""
Password Reset Requests — data layer.

Stores user-submitted password reset requests (from login screen, no auth needed)
and admin-side approve/reject helpers.

Table: PasswordResetRequests
- RequestID:         auto increment PK
- Username:          user's UserID (Members.UserID) or admin Username (Users.Username)
- AccountType:       'MEMBER' | 'ADMIN'
- DisplayName:       cached display name for admin's recognition
- InstitutionID:     scope (NULL for admin/super-admin requests)
- Reason:            user-provided reason
- Status:            'PENDING' | 'APPROVED' | 'REJECTED'
- RequestedAt:       timestamp
- ApprovedBy:        admin's username who approved/rejected
- ApprovedAt:        timestamp of action
- AdminNote:         optional rejection note / admin remark
"""

import random
import string
from datetime import datetime
from db import get_connection
from security import hash_password


# ============================================================
# Table bootstrap
# ============================================================
def ensure_password_reset_table():
    """Create PasswordResetRequests table if it doesn't exist."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS PasswordResetRequests (
                RequestID       INT AUTO_INCREMENT PRIMARY KEY,
                Username        VARCHAR(100) NOT NULL,
                AccountType     ENUM('MEMBER', 'ADMIN') NOT NULL,
                DisplayName     VARCHAR(150),
                InstitutionID   INT NULL,
                Reason          TEXT,
                Status          ENUM('PENDING','APPROVED','REJECTED')
                                DEFAULT 'PENDING',
                RequestedAt     DATETIME DEFAULT CURRENT_TIMESTAMP,
                ApprovedBy      VARCHAR(100) NULL,
                ApprovedAt      DATETIME NULL,
                AdminNote       TEXT NULL,
                INDEX idx_status (Status),
                INDEX idx_username (Username)
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[PasswordResetRequests] table init failed: {e}")
        try:
            conn.close()
        except Exception:
            pass
        return False


# ============================================================
# Lookup user (no auth) — used at login screen
# ============================================================
def lookup_user(username):
    """
    Return (account_type, display_name, institution_id) if username exists,
    else (None, None, None).
    Checks Members first then Users.
    """
    conn = get_connection()
    if conn is None:
        return (None, None, None)
    try:
        cur = conn.cursor(dictionary=True)
        # Members
        cur.execute(
            "SELECT Name, InstitutionID FROM Members "
            "WHERE UserID=%s AND Status='ACTIVE' LIMIT 1",
            (username,))
        row = cur.fetchone()
        if row:
            cur.close()
            conn.close()
            return ("MEMBER", row["Name"], row.get("InstitutionID"))
        # Users (admin / super_admin)
        cur.execute(
            "SELECT Username, Role FROM Users WHERE Username=%s LIMIT 1",
            (username,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return ("ADMIN", row["Username"], None)
        return (None, None, None)
    except Exception as e:
        print(f"[lookup_user] {e}")
        try:
            conn.close()
        except Exception:
            pass
        return (None, None, None)


# ============================================================
# Submit request (called from login screen forgot_password.py)
# ============================================================
def submit_request(username, reason):
    """
    Submit a new password reset request. Auto-detects account type.
    Returns dict: {ok: bool, message: str, request_id: int|None}.
    Prevents duplicate PENDING requests for the same username.
    """
    if not ensure_password_reset_table():
        return {"ok": False, "message": "Database connection failed.",
                "request_id": None}

    account_type, display_name, inst_id = lookup_user(username)
    if not account_type:
        return {"ok": False,
                "message": "यह username database में नहीं मिला। "
                           "कृपया अपनी details verify करें।",
                "request_id": None}

    conn = get_connection()
    if conn is None:
        return {"ok": False, "message": "Database connection failed.",
                "request_id": None}
    try:
        cur = conn.cursor(dictionary=True)
        # Check for existing pending request
        cur.execute(
            "SELECT RequestID FROM PasswordResetRequests "
            "WHERE Username=%s AND Status='PENDING' LIMIT 1",
            (username,))
        existing = cur.fetchone()
        if existing:
            cur.close()
            conn.close()
            return {"ok": False,
                    "message": "इस username के लिए एक request पहले से "
                               "PENDING है। कृपया admin के response का "
                               "इंतज़ार करें।",
                    "request_id": existing["RequestID"]}

        cur2 = conn.cursor()
        cur2.execute("""
            INSERT INTO PasswordResetRequests
                (Username, AccountType, DisplayName, InstitutionID, Reason)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, account_type, display_name, inst_id,
              reason or ""))
        conn.commit()
        new_id = cur2.lastrowid
        cur2.close()
        cur.close()
        conn.close()

        target = ("Admin" if account_type == "MEMBER"
                  else "Super Admin")
        return {"ok": True,
                "message": f"✓ Request submitted! आपकी request "
                           f"{target} को भेज दी गई है। Approval के बाद "
                           f"नया temporary password आपको offline बताया "
                           f"जाएगा।",
                "request_id": new_id}
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return {"ok": False, "message": f"Error: {str(e)[:100]}",
                "request_id": None}


# ============================================================
# Admin-side: list pending requests
# ============================================================
def list_requests(status="PENDING", institution_id=None,
                  include_admin_requests=False):
    """
    List requests filtered by status.
    - For Admin dashboard: pass institution_id to get only that
      institution's MEMBER requests.
    - For Super Admin: pass include_admin_requests=True to also
      see ADMIN-account requests (no institution filter).
    """
    if not ensure_password_reset_table():
        return []
    conn = get_connection()
    if conn is None:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        clauses = ["Status=%s"]
        params = [status]
        if include_admin_requests and institution_id is None:
            # Super admin sees ALL
            pass
        elif institution_id is not None:
            # Admin sees their institution's members + (optionally) admin reqs
            if include_admin_requests:
                clauses.append("(InstitutionID=%s OR AccountType='ADMIN')")
                params.append(institution_id)
            else:
                clauses.append("InstitutionID=%s AND AccountType='MEMBER'")
                params.append(institution_id)

        sql = (f"SELECT * FROM PasswordResetRequests "
               f"WHERE {' AND '.join(clauses)} "
               f"ORDER BY RequestedAt DESC")
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"[list_requests] {e}")
        try:
            conn.close()
        except Exception:
            pass
        return []


# ============================================================
# Generate a random temporary password
# ============================================================
def generate_temp_password(length=10):
    """
    Generate human-friendly temporary password:
    e.g. 'Lib-A7K9R3'  (prefix + dash + 6 random alnum chars)
    """
    chars = string.ascii_uppercase + string.digits
    # Avoid easily confused chars
    chars = chars.replace("O", "").replace("0", "").replace("I", "").replace("1", "")
    suffix = "".join(random.choices(chars, k=length - 4))
    return f"Lib-{suffix}"


# ============================================================
# Approve a request — generates temp pw, hashes it, updates user
# ============================================================
def approve_request(request_id, approver_username):
    """
    Approve a pending request:
      1. Generate temp password
      2. Hash it via bcrypt
      3. Update Members.Password OR Users.Password
      4. Mark request APPROVED
    Returns: {ok: bool, message: str, temp_password: str|None,
              username: str|None, account_type: str|None}.
    """
    if not ensure_password_reset_table():
        return {"ok": False, "message": "DB connection failed.",
                "temp_password": None, "username": None,
                "account_type": None}

    conn = get_connection()
    if conn is None:
        return {"ok": False, "message": "DB connection failed.",
                "temp_password": None, "username": None,
                "account_type": None}
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM PasswordResetRequests WHERE RequestID=%s",
            (request_id,))
        req = cur.fetchone()
        if not req:
            cur.close()
            conn.close()
            return {"ok": False, "message": "Request not found.",
                    "temp_password": None, "username": None,
                    "account_type": None}
        if req["Status"] != "PENDING":
            cur.close()
            conn.close()
            return {"ok": False,
                    "message": f"This request is already {req['Status']}.",
                    "temp_password": None, "username": None,
                    "account_type": None}

        temp_pw = generate_temp_password()
        hashed = hash_password(temp_pw)

        cur2 = conn.cursor()
        if req["AccountType"] == "MEMBER":
            cur2.execute(
                "UPDATE Members SET Password=%s WHERE UserID=%s",
                (hashed, req["Username"]))
        else:  # ADMIN
            cur2.execute(
                "UPDATE Users SET Password=%s WHERE Username=%s",
                (hashed, req["Username"]))

        cur2.execute("""
            UPDATE PasswordResetRequests
            SET Status='APPROVED', ApprovedBy=%s, ApprovedAt=%s
            WHERE RequestID=%s
        """, (approver_username, datetime.now(), request_id))
        conn.commit()
        cur2.close()
        cur.close()
        conn.close()
        return {"ok": True,
                "message": "Approved. Share this temp password offline.",
                "temp_password": temp_pw,
                "username": req["Username"],
                "account_type": req["AccountType"]}
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return {"ok": False, "message": f"Error: {str(e)[:120]}",
                "temp_password": None, "username": None,
                "account_type": None}


# ============================================================
# Reject a request
# ============================================================
def reject_request(request_id, approver_username, note=""):
    """Mark a pending request as REJECTED with optional note."""
    if not ensure_password_reset_table():
        return {"ok": False, "message": "DB connection failed."}
    conn = get_connection()
    if conn is None:
        return {"ok": False, "message": "DB connection failed."}
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE PasswordResetRequests
            SET Status='REJECTED', ApprovedBy=%s, ApprovedAt=%s,
                AdminNote=%s
            WHERE RequestID=%s AND Status='PENDING'
        """, (approver_username, datetime.now(), note or "",
              request_id))
        affected = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        if affected == 0:
            return {"ok": False,
                    "message": "Request not found or not pending."}
        return {"ok": True, "message": "Request rejected."}
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return {"ok": False, "message": f"Error: {str(e)[:120]}"}


# ============================================================
# Pending count (for badge in dashboard)
# ============================================================
def pending_count(institution_id=None, include_admin_requests=False):
    """Return number of PENDING requests visible to the caller."""
    return len(list_requests(status="PENDING",
                             institution_id=institution_id,
                             include_admin_requests=include_admin_requests))
