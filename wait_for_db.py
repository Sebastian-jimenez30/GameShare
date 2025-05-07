import time
import MySQLdb
import os

host = os.environ.get("DB_HOST", "localhost")
port = int(os.environ.get("DB_PORT", 3306))
user = os.environ.get("DB_USER", "root")
password = os.environ.get("DB_PASSWORD", "")
db = os.environ.get("DB_NAME", "")

while True:
    try:
        conn = MySQLdb.connect(
            host=host,
            port=port,
            user=user,
            passwd=password,
            db=db
        )
        print("✅ Conexión exitosa con la base de datos.")
        break
    except MySQLdb.OperationalError as e:
        print("⏳ Esperando que MySQL esté listo... error:", e)
        time.sleep(2)
