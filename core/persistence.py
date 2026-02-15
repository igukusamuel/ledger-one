import sqlite3
import json
import os
from datetime import datetime

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

    # ---------------- Journals ----------------
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

    # ---------------- Trades ----------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id TEXT,
            trade_date TEXT,
            instrument_type TEXT,
            face_value REAL,
            coupon_rate REAL,
            maturity_date TEXT,
            price REAL
        )
    """)

    # ---------------- Chart of Accounts ----------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chart_of_accounts (
            account_code TEXT PRIMARY KEY,
            account_name TEXT,
            account_type TEXT
        )
    """)

    # ---------------- Entities ----------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            entity_id TEXT PRIMARY KEY,
            entity_name TEXT
        )
    """)

    # ---------------- Audit ----------------
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
# TRADE CAPTURE
# =========================================================

def save_trade(entity_id, trade_date, instrument_type,
               face_value, coupon_rate, maturity_date, price):

    initialize_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO trades (
            entity_id,
            trade_date,
            instrument_type,
            face_value,
            coupon_rate,
            maturity_date,
            price
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        entity_id,
        trade_date,
        instrument_type,
        face_value,
        coupon_rate,
        maturity_date,
        price
    ))

    conn.commit()
    conn.close()


def load_trades():

    initialize_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT entity_id, trade_date, instrument_type,
               face_value, coupon_rate, maturity_date, price
        FROM trades
        ORDER BY trade_date DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


# =========================================================
# JOURNALS
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
# INVENTORY (JSON)
# =========================================================

def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        return {}

    with open(INVENTORY_FILE, "r") as f:
        return json.load(f)


def save_inventory(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(INVENTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)
