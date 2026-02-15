import sqlite3
import pandas as pd

DB_PATH = "data/ledger.db"


def init_inventory():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product TEXT PRIMARY KEY,
            category TEXT,
            price REAL,
            cost REAL,
            stock INTEGER
        )
    """)

    conn.commit()
    conn.close()


def seed_inventory():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM inventory")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany("""
            INSERT INTO inventory VALUES (?, ?, ?, ?, ?)
        """, [
            ("Espresso", "Beverage", 3.00, 1.00, 100),
            ("Latte", "Beverage", 4.50, 1.50, 100),
            ("Cappuccino", "Beverage", 4.00, 1.40, 100),
            ("Blueberry Muffin", "Bakery", 2.75, 1.00, 50),
        ])
        conn.commit()

    conn.close()


def get_inventory():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM inventory", conn)
    conn.close()
    return df


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
