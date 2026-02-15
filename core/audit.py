import sqlite3
from datetime import datetime

DB_NAME = "ledger.db"


def initialize_audit_table():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            timestamp TEXT,
            action TEXT,
            details TEXT
        )
    """)

    conn.commit()
    conn.close()


def log_action(action, details):

    initialize_audit_table()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO audit_log (timestamp, action, details)
        VALUES (?, ?, ?)
    """, (str(datetime.now()), action, details))

    conn.commit()
    conn.close()


def load_audit_log():

    initialize_audit_table()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, action, details
        FROM audit_log
        ORDER BY timestamp DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows
