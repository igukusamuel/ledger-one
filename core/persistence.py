import sqlite3
import json
import os
from datetime import datetime

# =========================================================
# CONFIGURATION
# =========================================================

DATA_DIR = "data"
DB_NAME = os.path.join(DATA_DIR, "ledger.db")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_db():

    os.makedirs(DATA_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # -------------------------
    # Journals
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id TEXT,
            entry_date TEXT,
            debit_account TEXT,
            credit_account TEXT,
            amount REAL,
            description TEXT
        )
    """)

    # -------------------------
    # Chart of Accounts
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chart_of_accounts (
            account_code TEXT PRIMARY KEY,
            account_name TEXT,
            account_type TEXT
        )
    """)

    # -------------------------
    # Entities
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            entity_id TEXT PRIMARY KEY,
            entity_name TEXT
        )
    """)

    # -------------------------
    # Audit Log
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            timestamp TEXT,
            action TEXT,
            details TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# JOURNAL PERSISTENCE
# =========================================================

def save_journals(journal_entries):

    initialize_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for j in journal_entries:
        cursor.execute("""
            INSERT INTO journals (
                entity_id,
                entry_date,
                debit_account,
                credit_account,
                amount,
                description
            )
            VALUES (?, ?, ?, ?, ?, ?)
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

    cursor.execute("""
        SELECT entity_id, entry_date, debit_account,
               credit_account, amount, description
        FROM journals
    """)

    rows = cursor.fetchall()
    conn.close()

    return [JournalEntry(*row) for row in rows]


# =========================================================
# CHART OF ACCOUNTS
# =========================================================

def save_account(account_code, account_name, account_type):

    initialize_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO chart_of_accounts
        VALUES (?, ?, ?)
    """, (account_code, account_name, account_type))

    conn.commit()
    conn.close()


def load_chart_of_accounts():

    initialize_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT account_code, account_name, account_type
        FROM chart_of_accounts
        ORDER BY account_code
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


# =========================================================
# ENTITY MANAGEMENT
# =========================================================

def save_entity(entity_id, entity_name):

    initialize_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO entities
        VALUES (?, ?)
    """, (entity_id, entity_name))

    conn.commit()
    conn.close()


def load_entities():

    initialize_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT entity_id, entity_name FROM entities
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


# =========================================================
# INVENTORY (JSON)
# =========================================================

def load_inventory():

    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(INVENTORY_FILE):
        return {}

    with open(INVENTORY_FILE, "r") as f:
        return json.load(f)


def save_inventory(data):

    os.makedirs(DATA_DIR, exist_ok=True)

    with open(INVENTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


# =========================================================
# AUDIT LOG
# =========================================================

def log_action(action, details):

    initialize_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO audit_log
        VALUES (?, ?, ?)
    """, (str(datetime.now()), action, details))

    conn.commit()
    conn.close()


def load_audit_log():

    initialize_db()

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
