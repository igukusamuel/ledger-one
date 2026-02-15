import sqlite3

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
        ("1000", "Cash", "Asset"),
        ("1100", "Interest Receivable", "Asset"),
        ("2000", "Accounts Payable", "Liability"),
        ("3000", "Equity", "Equity"),
        ("4000", "Interest Income", "Revenue"),
        ("5000", "Interest Expense", "Expense"),
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
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM chart_of_accounts")
    rows = cursor.fetchall()

    conn.close()

    return rows


def get_account_type(account_name):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT account_type
        FROM chart_of_accounts
        WHERE account_name = ?
    """, (account_name,))

    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None
