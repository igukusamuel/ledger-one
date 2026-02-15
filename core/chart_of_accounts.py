import pandas as pd
import sqlite3
from core.persistence import initialize_db, DB_NAME


def get_accounts():

    initialize_db()

    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query(
        """
        SELECT account_code, account_name, account_type
        FROM chart_of_accounts
        ORDER BY account_code
        """,
        conn
    )

    conn.close()

    return df


def add_account(account_code, account_name, account_type):

    initialize_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO chart_of_accounts
        VALUES (?, ?, ?)
    """, (account_code, account_name, account_type))

    conn.commit()
    conn.close()
