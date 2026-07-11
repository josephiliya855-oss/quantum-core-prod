import sqlite3
conn = sqlite3.connect('trading_system.db')
cursor = conn.cursor()

print("\n--- PERFORMANCE SUMMARY ---")
cursor.execute("SELECT COUNT(*), type FROM ledger_history GROUP BY type")
results = cursor.fetchall()
for count, trade_type in results:
    print(f"Total {trade_type}s: {count}")

cursor.execute("SELECT balance FROM account_state WHERE id=1")
bal = cursor.fetchone()[0]
print(f"Current Balance: ${bal}")
print("---------------------------\n")
conn.close()
