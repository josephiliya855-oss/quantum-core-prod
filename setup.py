import os

files = {
    "config.py": '''# config.py
from decimal import Decimal
import logging

DB_PATH = "trading_system.db"
DEFAULT_SAFETY_BUFFER = Decimal("0.25")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("System")
''',

    "database.py": '''# database.py
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
''',

    "account.py": '''# account.py
from decimal import Decimal, ROUND_HALF_UP
from config import DEFAULT_SAFETY_BUFFER, logger
import database

class MobileTradingAccount:
    def __init__(self, safety_buffer_pct: Decimal = DEFAULT_SAFETY_BUFFER):
        self.safety_buffer_pct = safety_buffer_pct
        raw_balance, raw_peak = database.load_account_state()
        self.balance = Decimal(raw_balance)
        self.peak_balance = Decimal(raw_peak)

    def deposit(self, amount: str) -> bool:
        try:
            dec_amount = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if dec_amount <= 0:
                return False
            self.balance += dec_amount
            if self.balance > self.peak_balance:
                self.peak_balance = self.balance
            database.save_account_state(str(self.balance), str(self.peak_balance))
            database.log_transaction("DEPOSIT", str(dec_amount), str(self.balance))
            return True
        except Exception:
            return False

    def calculate_optimal_withdrawal(self) -> Decimal:
        required_cushion = (self.peak_balance * self.safety_buffer_pct).quantize(Decimal("0.01"))
        available_surplus = self.balance - required_cushion
        return max(Decimal("0.00"), available_surplus)

    def withdraw_optimized(self) -> Decimal:
        optimal_amount = self.calculate_optimal_withdrawal()
        if optimal_amount <= 0:
            database.log_transaction("WITHDRAW_FAIL", "0.00", str(self.balance))
            return Decimal("0.00")
        self.balance -= optimal_amount
        database.save_account_state(str(self.balance), str(self.peak_balance))
        database.log_transaction("WITHDRAW_SUCCESS", str(optimal_amount), str(self.balance))
        return optimal_amount
''',

    "main.py": '''# main.py
import sys
import database
from account import MobileTradingAccount

def show_menu(account):
    while True:
        print("\\n" + "="*40)
        print("      PREMIUM MOBILE TRADING WALLET     ")
        print("="*40)
        print(f" Current Balance: ${account.balance:,.2f}")
        print(f" Trailing Peak:   ${account.peak_balance:,.2f}")
        print(f" Safe Cushion:    ${(account.peak_balance * account.safety_buffer_pct):,.2f}")
        print("-"*40)
        print(" 1. Make a Deposit")
        print(" 2. Smart Withdrawal (Better Amount)")
        print(" 3. View Statement Ledger")
        print(" 4. Exit System")
        print("="*40)
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == "1":
            amt = input("Enter deposit amount: $").strip()
            if account.deposit(amt):
                print("\\n[SUCCESS] Deposit updated and verified.")
            else:
                print("\\n[ERROR] Invalid numerical amount.")
        elif choice == "2":
            opt_amt = account.calculate_optimal_withdrawal()
            print(f"\\nOptimized Safe Amount Available: ${opt_amt:,.2f}")
            confirm = input("Execute withdrawal? (y/n): ").strip().lower()
            if confirm == 'y':
                withdrawn = account.withdraw_optimized()
                if withdrawn > 0:
                    print(f"[SUCCESS] Safely withdrew optimized amount: ${withdrawn:,.2f}")
                else:
                    print("[BLOCKED] Balance must remain above safety cushion.")
        elif choice == "3":
            history = database.get_ledger_history()
            print("\\n--- LAST 10 TRANSACTIONS ---")
            if not history:
                print("No transactions recorded yet.")
            for tx in history:
                print(f"[{tx[0]}] {tx[1]} | Amt: ${float(tx[2]):.2f} | Bal: ${float(tx[3]):.2f}")
        elif choice == "4":
            print("\\nSystem shutting down securely.")
            sys.exit()
        else:
            print("\\n[INVALID] Selection out of range.")

def main():
    database.initialize_database()
    account = MobileTradingAccount()
    show_menu(account)

if __name__ == "__main__":
    main()
'''
}

print("Generating clean system layers...")
for filename, content in files.items():
    with open(filename, "w") as f:
        f.write(content)
    print(f" -> Created: {filename}")
print("\n[COMPLETE] Run 'python setup.py' to unpack structure.")
