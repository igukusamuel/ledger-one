import sqlite3
from datetime import datetime

DB_NAME = "ledger.db"


def initialize_period_table():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounting_period (
            id INTEGER PRIMARY KEY,
            closed_through TEXT
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO accounting_period (id, closed_through)
        VALUES (1, NULL)
    """)

    conn.commit()
    conn.close()


def get_closed_through():

    initialize_period_table()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT closed_through FROM accounting_period WHERE id=1")
    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        return datetime.strptime(result[0], "%Y-%m-%d").date()

    return None


def close_through(date_value):

    initialize_period_table()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE accounting_period
        SET closed_through = ?
        WHERE id = 1
    """, (str(date_value),))

    conn.commit()
    conn.close()
