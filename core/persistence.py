import sqlite3
import json
from datetime import date

DB_NAME = "ledger.db"

INVENTORY_FILE = "data/inventory.json"

def load_inventory():
    try:
        with open(INVENTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_inventory(data):
    with open(INVENTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ------------------------------------------
# Database Connection
# ------------------------------------------

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


# ------------------------------------------
# Initialize Tables
# ------------------------------------------

def initialize_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            trade_id TEXT PRIMARY KEY,
            trade_data TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS journals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            journal_data TEXT
        )
    """)

    conn.commit()
    conn.close()


# ------------------------------------------
# Trade Persistence
# ------------------------------------------

def save_trades(trades):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM trades")

    for trade in trades:
        cur.execute(
            "INSERT INTO trades (trade_id, trade_data) VALUES (?, ?)",
            (trade["trade_id"], json.dumps(trade, default=str))
        )

    conn.commit()
    conn.close()


def load_trades():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT trade_data FROM trades")
    rows = cur.fetchall()

    conn.close()

    return [json.loads(row[0]) for row in rows]


# ------------------------------------------
# Journal Persistence
# ------------------------------------------

def save_journals(journals):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM journals")

    for j in journals:
        cur.execute(
            "INSERT INTO journals (journal_data) VALUES (?)",
            (json.dumps(j.__dict__, default=str),)
        )

    conn.commit()
    conn.close()


def load_journals(JournalEntryClass):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT journal_data FROM journals")
    rows = cur.fetchall()

    conn.close()

    journals = []

    for row in rows:
        data = json.loads(row[0])
        journals.append(
            JournalEntryClass(**data)
        )

    return journals
