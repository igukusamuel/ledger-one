import sqlite3
import pandas as pd

DB_NAME = "ledger.db"


def initialize_coa():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chart_of_accounts (
            account_code TEXT PRIMARY KEY,
            account_name TEXT,
            account_type TEXT
        )
    """)

    conn.commit()
    conn.close()


def seed_default_accounts():

    accounts = [
        ("100000001", "Cash", "Asset"),
        ("110000001", "Interest Receivable", "Asset"),
        ("200000001", "Accounts Payable", "Liability"),
        ("400000001", "Interest Income", "Revenue"),
        ("500000001", "Interest Expense", "Expense"),
        ("900000001", "Retained Earnings", "Equity"),
        ("400000002", "Cafe Sales Revenue", "Revenue"),
        ("500000002", "Cost of Goods Sold", "Expense"),
        ("100000010", "Inventory", "Asset"),

    ]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for acc in accounts:
        cursor.execute("""
            INSERT OR IGNORE INTO chart_of_accounts
            VALUES (?, ?, ?)
        """, acc)

    conn.commit()
    conn.close()


def get_accounts():

    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        "SELECT * FROM chart_of_accounts ORDER BY account_code",
        conn
    )
    conn.close()

    return df


def get_account_type(account_code):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT account_type
        FROM chart_of_accounts
        WHERE account_code = ?
    """, (account_code,))

    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None
