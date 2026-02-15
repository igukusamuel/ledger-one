import sqlite3
from datetime import datetime

DB_NAME = "ledger.db"

def log_action(action, details):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            timestamp TEXT,
            action TEXT,
            details TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO audit_log VALUES (?, ?, ?)
    """, (str(datetime.now()), action, details))

    conn.commit()
    conn.close()


def load_audit_log():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM audit_log
        ORDER BY timestamp DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows
