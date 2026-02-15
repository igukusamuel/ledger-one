import pandas as pd
import sqlite3
from core.persistence import initialize_db, DB_NAME


# =========================================================
# LOAD FULL CHART
# =========================================================

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


# =========================================================
# ADD / UPDATE ACCOUNT
# =========================================================

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


# =========================================================
# GET ACCOUNT TYPE (Needed by GL)
# =========================================================

def get_account_type(account_code):

    initialize_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT account_type
        FROM chart_of_accounts
        WHERE account_code = ?
    """, (account_code,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None
