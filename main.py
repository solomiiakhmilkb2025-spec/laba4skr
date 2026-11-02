
from getpass import getpass

import psycopg

password = getpass("Введи пароль PostgreSQL: ")

try:
    with psycopg.connect(
        dbname="store_db",
        user="postgres",
        password=password,
        host="localhost",
        port=5432
    ) as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM products")
        result = cur.fetchone()
        count = result[0] if result is not None else 0
        print("Підключення успішне!")
        print("Кількість товарів:", count)

except psycopg.Error as error:
    print("Помилка підключення:", error)
