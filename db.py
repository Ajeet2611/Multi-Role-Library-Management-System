import mysql.connector

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Ajeet@26112003MySQL",
            database="library_db"
        )
        print("Database Connected Successfully")
        return conn
    except:
        print("Database Connection Failed")
        return None
