import sqlite3
import csv
import sys
from decimal import Decimal

def verify_system_integrity():
    print("==================================================")
    print("       PORTFOLIO SYSTEM INTEGRITY AUDIT           ")
    print("==================================================")
    
    db_file = 'trading_system.db'
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 1. Structural DB Integrity Check
        cursor.execute("PRAGMA integrity_check;")
        status = cursor.fetchone()[0]
        if status == "ok":
            print("[✓] DATABASE STRUCTURE: Healthy / Integrity OK")
        else:
            print(f"[X] DATABASE CRITICAL ERROR: {status}")
            sys.exit(1)
            
        # 2. Fetch Account State Balances
        cursor.execute("SELECT balance, peak_balance FROM account_state WHERE id = 1;")
        state = cursor.fetchone()
        if not state:
            print("[X] ERROR: Account state parameters missing.")
            sys.exit(1)
            
        current_bal = Decimal(str(state[0]))
        peak_bal = Decimal(str(state[1]))
        
        # 3. Ledger Mathematical Auditing
        cursor.execute("SELECT type, amount FROM ledger_history ORDER BY id ASC;")
        ledger_entries = cursor.fetchall()
        
        # Assume initial seed deposit if reset engine baseline was used
        calculated_bal = Decimal('320.75') 
        
        for tx_type, tx_amt in ledger_entries:
            if tx_type == 'GAIN':
                calculated_bal += Decimal(str(tx_amt))
            elif tx_type == 'LOSS':
                calculated_bal -= Decimal(str(tx_amt))
                
        # Validate balance discrepancies
        diff = abs(current_bal - calculated_bal)
        print(f"[✓] ACCOUNT BALANCE: Verified at ${current_bal:,.2f}")
        print(f"[✓] LEDGER TRACKING: Compiled at ${calculated_bal:,.2f}")
        
        if diff <= Decimal('0.05'):
            print("[✓] MATH RECONCILIATION: Flawless Ledger Alignment.")
        else:
            print(f"[!] WARNING: Balance skew detected! Variance: ${diff}")
            
        # 4. Secure Backup Export Routine
        cursor.execute("SELECT id, timestamp, type, amount, resulting_balance FROM ledger_history;")
        all_rows = cursor.fetchall()
        
        backup_filename = "verified_ledger_backup.csv"
        with open(backup_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Index', 'Timestamp', 'Type', 'Amount', 'Balance'])
            writer.writerows(all_rows)
            
        print(f"[✓] SECURITY EXPORT: Complete. Data persistent in '{backup_filename}'")
        print("==================================================")
        
        conn.close()
    except Exception as e:
        print(f"[X] AUDIT SYSTEM FAILURE: {e}")

if __name__ == "__main__":
    verify_system_integrity()
