from db import get_connection
from security import hash_password

conn = get_connection()
cur = conn.cursor()

# सभी users निकालो
cur.execute("SELECT UserID, Password FROM Users")
users = cur.fetchall()

for user_id, password in users:
    # अगर password पहले से hashed नहीं है
    if not password.startswith("$2b$"):
        hashed = hash_password(password)

        cur.execute(
            "UPDATE Users SET Password = %s WHERE UserID = %s",
            (hashed, user_id)
        )

        print(f"Password fixed for UserID {user_id}")

conn.commit()
cur.close()
conn.close()

print("✅ All plain passwords converted to hashed passwords")
