import sqlite3
import pandas as pd

DB_PATH = "data/ledger.db"


# --------------------------------------------------
# CONNECTION
# --------------------------------------------------

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# --------------------------------------------------
# INIT INVENTORY TABLE + SEED
# --------------------------------------------------

def init_inventory():

    conn = get_connection()
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

    # Check if empty
    cursor.execute("SELECT COUNT(*) FROM inventory")
    count = cursor.fetchone()[0]

    if count == 0:
        seed_default_products(cursor)

    conn.commit()
    conn.close()


# --------------------------------------------------
# SEED DEFAULT PRODUCTS
# --------------------------------------------------

def seed_default_products(cursor):

    default_products = [
        ("Espresso", "Beverage", "Hot", 3.00, 1.00, 100),
        ("Latte", "Beverage", "Hot", 4.50, 1.50, 100),
        ("Iced Coffee", "Beverage", "Cold", 4.00, 1.20, 100),
        ("Croissant", "Pastry", "Bakery", 3.50, 1.00, 50),
        ("Muffin", "Pastry", "Bakery", 3.00, 0.90, 50),
    ]

    cursor.executemany("""
        INSERT INTO inventory
        (product, category, subcategory, price, cost, stock)
        VALUES (?, ?, ?, ?, ?, ?)
    """, default_products)


# --------------------------------------------------
# GET INVENTORY
# --------------------------------------------------

def get_inventory():

    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM inventory ORDER BY category, subcategory, product",
        conn
    )

    conn.close()

    return df


# --------------------------------------------------
# ADD PRODUCT
# --------------------------------------------------

def add_product(product, category, subcategory, price, cost, stock):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO inventory
        (product, category, subcategory, price, cost, stock)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (product, category, subcategory, price, cost, stock))

    conn.commit()
    conn.close()


# --------------------------------------------------
# UPDATE INVENTORY (Reduce Stock)
# --------------------------------------------------

def update_inventory(product, quantity):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE inventory
        SET stock = stock - ?
        WHERE product = ?
    """, (quantity, product))

    conn.commit()
    conn.close()
