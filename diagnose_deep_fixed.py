import sqlite3

def run_reconstructed_diagnostic():
    conn = sqlite3.connect('trading_system.db')
    cursor = conn.cursor()
    
    # Fetch all trades in the exact order they happened
    cursor.execute("SELECT type FROM ledger_history ORDER BY timestamp ASC")
    rows = cursor.fetchall()
    
    recent_trades = []
    matrix = {
        'LIVE_NORMAL': {'GAIN': 0, 'LOSS': 0},
        'LIVE_DEFENSIVE': {'GAIN': 0, 'LOSS': 0}
    }
    
    for (log_type,) in rows:
        # Replicate the exact logic from simulation.py
        losses_count = recent_trades.count('LOSS')
        current_state = 'LIVE_DEFENSIVE' if losses_count >= 2 else 'LIVE_NORMAL'
        
        # Track the outcome
        if log_type in matrix[current_state]:
            matrix[current_state][log_type] += 1
            
        # Maintain the rolling memory window of 5 trades
        recent_trades.append(log_type)
        if len(recent_trades) > 5:
            recent_trades.pop(0)
            
    print("\n--- RECONSTRUCTED DEEP LOGIC CORRELATION ---")
    for state in ['LIVE_NORMAL', 'LIVE_DEFENSIVE']:
        gains = matrix[state]['GAIN']
        losses = matrix[state]['LOSS']
        total = gains + losses
        win_rate = (gains / total * 100) if total > 0 else 0
        print(f"State '{state}':")
        print(f"  -> GAINs: {gains} | LOSSs: {losses}")
        print(f"  -> Total Trades: {total} | Win Rate: {win_rate:.2f}%")
        print("-" * 45)
        
    conn.close()

if __name__ == "__main__":
    run_reconstructed_diagnostic()
