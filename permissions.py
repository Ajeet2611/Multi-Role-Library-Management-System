from db import get_connection

def get_user_permissions(role):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT PermissionCode
        FROM RolePermissions
        WHERE Role=%s
    """, (role,))

    perms = {row[0] for row in cur.fetchall()}

    conn.close()
    return perms




from db import get_connection

def has_permission(user, permission_code):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 1
        FROM InstitutionRolePermissions
        WHERE InstitutionID=%s
          AND Role=%s
          AND PermissionCode=%s
    """, (
        user["InstitutionID"],
        user["Role"],
        permission_code
    ))

    result = cur.fetchone()
    conn.close()

    return result is not None
