import sqlite3

def run_deep_diagnostic():
    conn = sqlite3.connect('trading_system.db')
    cursor = conn.cursor()
    
    print("\n--- DEEP LOGIC CORRELATION ---")
    # This query groups outcomes by both the type (GAIN/LOSS) AND the state (LIVE_NORMAL/LIVE_DEFENSIVE)
    query = """
    SELECT type, win_state, COUNT(*) as frequency 
    FROM ledger_history 
    GROUP BY type, win_state
    ORDER BY type DESC
    """
    cursor.execute(query)
    results = cursor.fetchall()
    
    for trade_type, state, count in results:
        print(f"Outcome '{trade_type}' in state '{state}': {count} occurrences.")
    
    conn.close()

if __name__ == "__main__":
    run_deep_diagnostic()
