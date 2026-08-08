import sqlite3
from pathlib import Path


DATA_FOLDER = Path("data")
DATABASE_FILE = DATA_FOLDER / "finora.db"


def get_connection():
    DATA_FOLDER.mkdir(exist_ok=True)

    return sqlite3.connect(DATABASE_FILE)


def create_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    connection.commit()
    connection.close()



# Transactions


def add_transaction(
    amount,
    transaction_type,
    category,
    transaction_date,
    description
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (amount, transaction_type, category, date, description)
        VALUES (?, ?, ?, ?, ?)
    """, (
        amount,
        transaction_type,
        category,
        transaction_date,
        description
    ))

    connection.commit()
    connection.close()


def update_transaction(
    transaction_id,
    amount,
    transaction_type,
    category,
    transaction_date,
    description
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE transactions
        SET amount = ?,
            transaction_type = ?,
            category = ?,
            date = ?,
            description = ?
        WHERE id = ?
    """, (
        amount,
        transaction_type,
        category,
        transaction_date,
        description,
        transaction_id
    ))

    connection.commit()
    connection.close()


def delete_transaction(transaction_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    connection.commit()
    connection.close()


def get_transaction(transaction_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, amount, transaction_type, category, date, description
        FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    transaction = cursor.fetchone()

    connection.close()

    return transaction


def get_transactions_for_month(year, month):
    connection = get_connection()
    cursor = connection.cursor()

    month_string = f"{year:04d}-{month:02d}"

    cursor.execute("""
        SELECT id, amount, transaction_type, category, date, description
        FROM transactions
        WHERE date LIKE ?
        ORDER BY date DESC, id DESC
    """, (f"{month_string}-%",))

    transactions = cursor.fetchall()

    connection.close()

    return transactions



# Settings


def get_setting(key):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT value
        FROM settings
        WHERE key = ?
    """, (key,))

    result = cursor.fetchone()

    connection.close()

    if result:
        return result[0]

    return None


def save_setting(key, value):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO settings (key, value)
        VALUES (?, ?)
    """, (key, value))

    connection.commit()
    connection.close()