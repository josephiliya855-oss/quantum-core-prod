import sqlite3
from flask import Flask, render_template_string

app = Flask(__name__)

def get_dashboard_data():
    conn = sqlite3.connect('trading_system.db')
    cursor = conn.cursor()
    
    # 1. Fetch current account state parameters
    cursor.execute("SELECT balance, peak_balance, cushion_pct FROM account_state WHERE id=1")
    account = cursor.fetchone()
    
    # 2. Fetch the 10 most recent trades from history
    cursor.execute("SELECT timestamp, type, amount, resulting_balance FROM ledger_history ORDER BY rowid DESC LIMIT 10")
    trades = cursor.fetchall()
    
    conn.close()
    
    # Handle initial empty state gracefully
    if not account:
        account = ("0.00", "0.00", "0.10")
        
    # Determine the system's operational posture based on the last recorded trade state
    current_posture = "INITIALIZING"
    if trades:
        last_trade_type = trades[0][1] # Looks like 'LIVE_NORMAL BUY' or 'LIVE_DEFENSIVE BUY'
        if "DEFENSIVE" in last_trade_type:
            current_posture = "LIVE_DEFENSIVE (Shield Active)"
        else:
            current_posture = "LIVE_NORMAL"
            
    return {
        "balance": float(account[0]),
        "peak_balance": float(account[1]),
        "cushion_pct": float(account[2]) * 100,
        "posture": current_posture,
        "trades": trades
    }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Core Context Trading Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-gray-100 font-sans minimum-h-screen">

    <nav class="bg-gray-800 border-b border-gray-700 px-6 py-4 flex justify-between items-center">
        <h1 class="text-xl font-bold tracking-wider text-emerald-400">EXCELLENT ENGINE V1.0</h1>
        <div class="px-3 py-1 rounded text-xs font-semibold tracking-wide {% if 'DEFENSIVE' in data.posture %}bg-amber-500/20 text-amber-400 border border-amber-500/30{% else %}bg-emerald-500/20 text-emerald-400 border border-emerald-500/30{% endif %}">
            System State: {{ data.posture }}
        </div>
    </nav>

    <div class="max-w-7xl mx-auto p-6 space-y-6">
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg shadow-sm">
                <p class="text-xs font-semibold uppercase tracking-wider text-gray-400">Simulated Account Balance</p>
                <p class="text-3xl font-bold text-white mt-2">${{ "{:,.2f}".format(data.balance) }}</p>
            </div>
            <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg shadow-sm">
                <p class="text-xs font-semibold uppercase tracking-wider text-gray-400">Peak Balance Registered</p>
                <p class="text-3xl font-bold text-gray-300 mt-2">${{ "{:,.2f}".format(data.peak_balance) }}</p>
            </div>
            <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg shadow-sm">
                <p class="text-xs font-semibold uppercase tracking-wider text-gray-400">Risk Cushion Allocation</p>
                <p class="text-3xl font-bold text-cyan-400 mt-2">{{ data.cushion_pct }}%</p>
            </div>
        </div>

        <div class="bg-gray-800 border border-gray-700 rounded-lg shadow-sm overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-700 flex justify-between items-center">
                <h2 class="text-md font-semibold text-white uppercase tracking-wider">Live Execution Stream</h2>
                <a href="/" class="text-xs bg-gray-700 hover:bg-gray-600 px-3 py-1.5 rounded transition font-medium">Refresh Data</a>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm">
                    <thead class="bg-gray-800/50 text-gray-400 uppercase text-xs tracking-wider border-b border-gray-700">
                        <tr>
                            <th class="px-6 py-3">Timestamp</th>
                            <th class="px-6 py-3">Execution State</th>
                            <th class="px-6 py-3">Delta Impact</th>
                            <th class="px-6 py-3 text-right">Resulting Balance</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-700/50">
                        {% for trade in data.trades %}
                        <tr class="hover:bg-gray-700/30 transition">
                            <td class="px-6 py-4 font-mono text-gray-400 text-xs">{{ trade[0] }}</td>
                            <td class="px-6 py-4">
                                <span class="px-2 py-0.5 rounded text-xs font-semibold {% if 'STOP' in trade[1] or 'LOSS' in trade[1] %}bg-red-500/10 text-red-400{% elif 'DEFENSIVE' in trade[1] %}bg-amber-500/10 text-amber-400{% else %}bg-emerald-500/10 text-emerald-400{% endif %}">
                                    {{ trade[1] }}
                                </span>
                            </td>
                            <td class="px-6 py-4 font-semibold {% if trade[2] < 0 %}text-red-400{% else %}text-emerald-400{% endif %}">
                                {% if trade[2] >= 0 %}+{% endif %}${{ "{:,.2f}".format(trade[2]) }}
                            </td>
                            <td class="px-6 py-4 font-mono text-right text-gray-300">${{ "{:,.2f}".format(trade[3]) }}</td>
                        </tr>
                        {% endfor dict %}
                        {% if not data.trades %}
                        <tr>
                            <td colspan="4" class="px-6 py-10 text-center text-gray-500 italic">No trades recorded in ledger history yet.</td>
                        </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

</body>
</html>
"""

@app.route("/")
def index():
    data = get_dashboard_data()
    return render_template_string(HTML_TEMPLATE, data=data)

if __name__ == "__main__":
    # Running locally inside your environment
    app.run(host="127.0.0.1", port=8080, debug=True)
