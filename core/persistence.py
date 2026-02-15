import sqlite3
import json
import os

DB_NAME = "data/ledger.db"
INVENTORY_FILE = "data/inventory.json"


# -------------------------
# Journals (SQLite)
# -------------------------

def initialize_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journals (
            entity_id TEXT,
            entry_date TEXT,
            debit_account TEXT,
            credit_account TEXT,
            amount REAL,
            description TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_journals(journal_entries):
    initialize_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for j in journal_entries:
        cursor.execute("""
            INSERT INTO journals VALUES (?, ?, ?, ?, ?, ?)
        """, (
            j.entity_id,
            j.entry_date,
            j.debit_account,
            j.credit_account,
            j.amount,
            j.description
        ))

    conn.commit()
    conn.close()


def load_journals(JournalEntry):
    initialize_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM journals")
    rows = cursor.fetchall()
    conn.close()

    return [JournalEntry(*row) for row in rows]


# -------------------------
# Inventory (JSON)
# -------------------------

def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        return {}

    with open(INVENTORY_FILE, "r") as f:
        return json.load(f)


def save_inventory(data):
    os.makedirs("data", exist_ok=True)
    with open(INVENTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)
