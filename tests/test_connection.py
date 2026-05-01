import pyodbc
import time

server   = "nexus-sql-abhirup.database.windows.net"
database = "clearbank-db"
username = "nexusadmin"
password = "NexusP@ss2026!"

conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
)

print("Waking up clearbank-db (Serverless auto-pause)...")
print("This can take 30-60 seconds on first connection...")

for attempt in range(1, 6):
    try:
        print(f"  Attempt {attempt}/5...")
        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        print(f"Connected successfully!")
        print(f"SQL Server: {row[0][:60]}")
        conn.close()
        break
    except Exception as e:
        if "40613" in str(e):
            print(f"  Database still waking up — waiting 20 seconds...")
            time.sleep(20)
        else:
            print(f"  Different error: {e}")
            break