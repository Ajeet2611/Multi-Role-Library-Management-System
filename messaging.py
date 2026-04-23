from db import get_connection


def ensure_user_messages_table():
    conn = get_connection()
    if conn is None:
        return False

    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS UserMessages (
            MessageID INT AUTO_INCREMENT PRIMARY KEY,
            UserID VARCHAR(100) NOT NULL,
            Username VARCHAR(150) NOT NULL,
            UserMessage TEXT NOT NULL,
            AdminReply TEXT NULL,
            Status VARCHAR(20) NOT NULL DEFAULT 'OPEN',
            SentAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            RepliedAt DATETIME NULL,
            InstitutionID INT NOT NULL
        )
        """
    )
    conn.commit()
    cur.close()
    conn.close()
    return True
