import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="NayaPassword123",
        database="cybershieldai"
    )

    print("Database Connected Successfully!")

except Exception as e:
    print("Error:", e)