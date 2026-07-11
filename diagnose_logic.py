import sqlite3

def run_diagnostic():
    conn = sqlite3.connect('trading_system.db')
    cursor = conn.cursor()
    
    print("\n--- LOGIC STATE CORRELATION ---")
    # Join ledger data with state to see how often each state leads to loss vs gain
    query = """
    SELECT type, COUNT(*) as frequency 
    FROM ledger_history 
    GROUP BY type
    ORDER BY frequency DESC
    """
    cursor.execute(query)
    results = cursor.fetchall()
    
    for trade_type, count in results:
        print(f"State outcome '{trade_type}' occurred {count} times.")
    
    print("\n[Diagnostic Note]: If LOSS frequency is high, check simulation.py 'risk_floor' logic.")
    conn.close()

if __name__ == "__main__":
    run_diagnostic()
