import time
import threading
import sqlite3
import random
from decimal import Decimal

# Global lock to manage resource sharing safely
db_lock = threading.Lock()

def init_db_concurrency():
    """Configures the database file safely for parallel read/write loops on mobile storage."""
    try:
        conn = sqlite3.connect('trading_system.db', timeout=15.0)
        cursor = conn.cursor()
        # Enable Write-Ahead Logging to allow multi-threaded reads while writing
        cursor.execute("PRAGMA journal_mode=WAL;")
        # Give operations a relaxed breathing window to resolve transactions cleanly
        cursor.execute("PRAGMA busy_timeout = 15000;")
        conn.commit()
        conn.close()
    except:
        pass

def background_trading_loop():
    """Continuous simulation loop running safely with resource locking."""
    time.sleep(2)
    while True:
        try:
            with db_lock:
                # Use higher timeout parameters to absorb execution lag
                conn = sqlite3.connect('trading_system.db', timeout=15.0)
                cursor = conn.cursor()
                cursor.execute("SELECT balance, peak_balance FROM account_state WHERE id = 1;")
                row = cursor.fetchone()
                
                if row:
                    current_balance = Decimal(str(row[0]))
                    peak_balance = Decimal(str(row[1]))
                    
                    if random.choice([True, False]):
                        gain = Decimal(str(random.randint(15, 80)))
                        new_balance = current_balance + gain
                        new_peak = max(peak_balance, new_balance)
                        
                        cursor.execute("UPDATE account_state SET balance = ?, peak_balance = ? WHERE id = 1;", (str(new_balance), str(new_peak)))
                        cursor.execute("INSERT INTO transactions (timestamp, type, amount, balance) VALUES (datetime('now','localtime'), 'MARKET_GAIN', ?, ?);", (str(gain), str(new_balance)))
                    else:
                        loss = Decimal(str(random.randint(10, 70)))
                        new_balance = max(Decimal("0.00"), current_balance - loss)
                        
                        cursor.execute("UPDATE account_state SET balance = ? WHERE id = 1;", (str(new_balance),))
                        cursor.execute("INSERT INTO transactions (timestamp, type, amount, balance) VALUES (datetime('now','localtime'), 'MARKET_LOSS', ?, ?);", (str(-loss), str(new_balance)))
                    
                    conn.commit()
                conn.close()
        except Exception as e:
            pass
            
        time.sleep(10)

def user_interface_menu():
    """Interactive command console dashboard running with thread safety."""
    while True:
        with db_lock:
            try:
                conn = sqlite3.connect('trading_system.db', timeout=15.0)
                cursor = conn.cursor()
                cursor.execute("SELECT balance, peak_balance FROM account_state WHERE id = 1;")
                row = cursor.fetchone()
                conn.close()
                balance = float(row[0]) if row else 0.0
                peak = float(row[1]) if row else 0.0
                cushion = peak * 0.25
            except:
                balance, peak, cushion = 0.0, 0.0, 0.0

        print("\n=====================================")
        print("    PREMIUM MOBILE TRADING WALLET    ")
        print("=====================================")
        print(f"Current Balance: ${balance:,.2f}")
        print(f"Trailing Peak:   ${peak:,.2f}")
        print(f"Safe Cushion:    ${cushion:,.2f}")
        print("=====================================")
        print("1. Make a Deposit")
        print("2. Smart Withdrawal")
        print("3. View Statement Ledger")
        print("4. Exit System")
        print("=====================================")
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == "1":
            amount = input("\nEnter deposit amount: $").strip()
            try:
                val = float(amount)
                with db_lock:
                    conn = sqlite3.connect('trading_system.db', timeout=15.0)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE account_state SET balance = balance + ?, peak_balance = max(peak_balance, balance + ?) WHERE id = 1;", (val, val))
                    cursor.execute("INSERT INTO transactions (timestamp, type, amount, balance) VALUES (datetime('now','localtime'), 'DEPOSIT', ?, (SELECT balance FROM account_state WHERE id=1));", (val,))
                    conn.commit()
                    conn.close()
                print(f"[SUCCESS] Deposited ${val:,.2f}")
            except:
                print("[ERROR] Invalid numeric input.")
                
        elif choice == "2":
            surplus = balance - cushion
            if surplus > 0:
                print(f"\nOptimized Safe Amount Available: ${surplus:,.2f}")
                confirm = input("Execute withdrawal? (y/n): ").strip().lower()
                if confirm == 'y':
                    with db_lock:
                        conn = sqlite3.connect('trading_system.db', timeout=15.0)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE account_state SET balance = balance - ? WHERE id = 1;", (surplus,))
                        cursor.execute("INSERT INTO transactions (timestamp, type, amount, balance) VALUES (datetime('now','localtime'), 'WITHDRAW_SUCCESS', ?, (SELECT balance FROM account_state WHERE id=1));", (-surplus,))
                        conn.commit()
                        conn.close()
                    print(f"[SUCCESS] Safely withdrew optimized amount: ${surplus:,.2f}")
            else:
                print("\n[BLOCKED] Current balance is below safety cushion limit.")
                
        elif choice == "3":
            print("\n--- LAST 10 TRANSACTIONS ---")
            with db_lock:
                try:
                    conn = sqlite3.connect('trading_system.db', timeout=15.0)
                    cursor = conn.cursor()
                    cursor.execute("SELECT timestamp, type, amount, balance FROM transactions ORDER BY timestamp DESC LIMIT 10;")
                    rows = cursor.fetchall()
                    conn.close()
                    for r in rows:
                        print(f"[{r[0]}] {r[1]} | Amt: ${float(r[2]):,.2f} | Bal: ${float(r[3]):,.2f}")
                except Exception as e:
                    print(f"[ERROR] Ledger access failed: {e}")
                
        elif choice == "4":
            print("System shutting down securely.")
            break
        else:
            print("[INVALID] Selection out of range.")

if __name__ == "__main__":
    # Optimize storage settings before spawning parallel workloads
    init_db_concurrency()
    
    bot_thread = threading.Thread(target=background_trading_loop, daemon=True)
    bot_thread.start()
    user_interface_menu()
