
from db import get_db_connection

try:
    connection = get_db_connection()

    print("Success! Python connected to MySQL.")

    cursor = connection.cursor()
    cursor.execute("SELECT VERSION()")
    print("MySQL version:", cursor.fetchone()[0])

    cursor.close()
    connection.close()

except Exception as error:
    print("Database connection failed:", error)
