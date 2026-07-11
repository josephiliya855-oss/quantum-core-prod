# database.py
import sqlite3
from datetime import datetime
from config import DB_PATH

def initialize_database():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS account_state (
                id INTEGER PRIMARY KEY,
                balance TEXT NOT NULL,
                peak_balance TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                amount TEXT NOT NULL,
                resulting_balance TEXT NOT NULL
            )
        """)
        cursor = conn.execute("SELECT COUNT(*) FROM account_state")
        if cursor.fetchone()[0] == 0:
            conn.execute("INSERT INTO account_state (id, balance, peak_balance) VALUES (1, '0.00', '0.00')")
        conn.commit()

def load_account_state():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT balance, peak_balance FROM account_state WHERE id = 1")
        return cursor.fetchone()

def save_account_state(balance: str, peak_balance: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE account_state SET balance = ?, peak_balance = ? WHERE id = 1", (balance, peak_balance))
        conn.commit()

def log_transaction(tx_type: str, amount: str, current_balance: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO ledger (timestamp, type, amount, resulting_balance) VALUES (?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tx_type, amount, current_balance)
        )
        conn.commit()

def get_ledger_history():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT timestamp, type, amount, resulting_balance FROM ledger ORDER BY id DESC LIMIT 10")
        return cursor.fetchall()
