import sqlite3

DB_NAME = "ledger.db"


def initialize_entity_table():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_code TEXT UNIQUE,
            entity_name TEXT
        )
    """)

    conn.commit()
    conn.close()


def seed_default_entity():

    initialize_entity_table()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO entities (entity_code, entity_name)
        VALUES ('ENT001', 'Default Entity')
    """)

    conn.commit()
    conn.close()


def get_entities():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT entity_id, entity_code, entity_name FROM entities")

    rows = cursor.fetchall()
    conn.close()

    return rows
