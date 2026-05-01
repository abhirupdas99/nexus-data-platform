
import pyodbc

conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=nexus-sql-abhirup.database.windows.net;'
    'DATABASE=clearbank-db;'
    'UID=nexusadmin;'
    'PWD=NexusP@ss2026!;'
    'Encrypt=yes;TrustServerCertificate=no;'
)

conn = pyodbc.connect(conn_str, timeout=30)
cursor = conn.cursor()

cursor.execute('''
    SELECT s.name + '.' + t.name AS table_name,
           p.rows AS row_count
    FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    JOIN sys.partitions p ON t.object_id = p.object_id
    WHERE p.index_id IN (0,1)
    ORDER BY s.name, t.name
''')

rows = cursor.fetchall()
print(f'Tables created: {len(rows)}')
print('-' * 35)
for row in rows:
    print(f'{row[0]:<35} {row[1]} rows')

conn.close()
