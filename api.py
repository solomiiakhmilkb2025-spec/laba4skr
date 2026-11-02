
from getpass import getpass

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Магазин — варіант 24")

password = getpass("Введи пароль PostgreSQL: ")

def connect():
    return psycopg.connect(
        dbname="store_db",
        user="postgres",
        password=password,
        host="localhost",
        port=5432
    )

class Product(BaseModel):
    store_id: int
    category_id: int
    name: str
    sku: str

@app.get("/")
def home():
    return {"message": "API магазину працює!"}

@app.get("/products")
def get_products():
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, store_id, category_id, name, sku FROM products ORDER BY id"
        )
        rows = cur.fetchall()
        return [
            dict(zip(
                ["id", "store_id", "category_id", "name", "sku"], row
            ))
            for row in rows
        ]

@app.get("/products/{product_id}")
def get_product(product_id: int):
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, store_id, category_id, name, sku FROM products WHERE id = %s",
            (product_id,)
        )
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Товар не знайдено")
        return dict(zip(
            ["id", "store_id", "category_id", "name", "sku"], row
        ))

@app.post("/products", status_code=201)
def add_product(product: Product):
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO products (store_id, category_id, name, sku)
                   VALUES (%s, %s, %s, %s) RETURNING id""",
            (product.store_id, product.category_id,
             product.name, product.sku)
        )
        new_id = cur.fetchone()[0]
        return {"message": "Товар додано", "id": new_id}

@app.put("/products/{product_id}")
def update_product(product_id: int, product: Product):
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """UPDATE products
                   SET store_id=%s, category_id=%s, name=%s, sku=%s
                   WHERE id=%s RETURNING id""",
            (product.store_id, product.category_id,
             product.name, product.sku, product_id)
        )
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Товар не знайдено")
        return {"message": "Товар оновлено"}

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "DELETE FROM products WHERE id=%s RETURNING id",
            (product_id,)
        )
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Товар не знайдено")
        return {"message": "Товар видалено"}
