import sqlite3
import pandas as pd
import os

os.makedirs("data", exist_ok=True)
DB_PATH = "data/ledger.db"


def init_inventory():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product TEXT PRIMARY KEY,
            category TEXT,
            subcategory TEXT,
            price REAL,
            cost REAL,
            stock INTEGER
        )
    """)

    conn.commit()
    conn.close()


def get_inventory():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM inventory", conn)
    conn.close()
    return df


def add_product(product, category, subcategory, price, cost, stock):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO inventory
        VALUES (?, ?, ?, ?, ?, ?)
    """, (product, category, subcategory, price, cost, stock))

    conn.commit()
    conn.close()


def update_inventory(product, quantity):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE inventory
        SET stock = stock - ?
        WHERE product = ?
    """, (quantity, product))

    conn.commit()
    conn.close()
