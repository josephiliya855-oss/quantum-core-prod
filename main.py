import socket
import re

def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    # 1. Pass numeric IPs through instantly
    if host and isinstance(host, str) and re.match(r'^\d+\.\d+\.\d+\.\d+$', host):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (host, int(port)))]
    
    # 2. Total In-Memory DNS Map (Completely bypasses the broken system stack)
    host_str = str(host).lower() if host else ""
    
    if "localhost" in host_str or "127.0.0.1" in host_str:
        target_ip = "127.0.0.1"
    else:
        # Default all external api traffic directly to Coinbase's edge infrastructure
        target_ip = "104.18.27.141"
        
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (target_ip, int(port)))]

# Overwrite completely without any fallbacks to the native hanging call
socket.getaddrinfo = custom_getaddrinfo

import socket
import json
import urllib.request
import ssl



import sqlite3
import os
import time
import sys
import csv
import math
import subprocess

GREEN = '\033[1;32m'
RED = '\033[1;31m'
YELLOW = '\033[1;33m'
CYAN = '\033[1;36m'
RESET = '\033[0m'
BOLD = '\033[1m'
CLEAR_SCREEN = '\033[H\033[2J'

def get_performance_metrics():
    balance, peak, cushion_pct = 0.0, 0.0, 0.25
    win_ratio, profit_factor = 0.0, 1.0
    wins, losses = 0, 0
    total_won, total_lost = 0.0, 0.0
    max_dd_pct = 0.0
    sharpe_ratio = 0.0
    
    try:
        with sqlite3.connect('trading_system.db', timeout=2.0) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance, peak_balance, cushion_pct FROM account_state WHERE id = 1;")
            row = cursor.fetchone()
            if row:
                balance, peak, cushion_pct = float(row[0]), float(row[1]), float(row[2])
            
            cursor.execute("SELECT type, amount, resulting_balance FROM ledger_history ORDER BY id ASC;")
            transactions = cursor.fetchall()
            
            running_peak = 0.0
            returns = []
            prev_bal = None
            
            for tx_type, tx_amt, res_bal in transactions:
                if tx_type == 'GAIN':
                    wins += 1
                    total_won += tx_amt
                elif tx_type == 'LOSS':
                    losses += 1
                    total_lost += tx_amt
                
                if res_bal > running_peak:
                    running_peak = res_bal
                if running_peak > 0:
                    dd = ((running_peak - res_bal) / running_peak) * 100
                    if dd > max_dd_pct:
                        max_dd_pct = dd
                
                if prev_bal is not None and prev_bal > 0:
                    ret = (res_bal - prev_bal) / prev_bal
                    returns.append(ret)
                prev_bal = res_bal
                    
            total_trades = wins + losses
            if total_trades > 0:
                win_ratio = (wins / total_trades) * 100
            if total_lost > 0:
                profit_factor = total_won / total_lost
            else:
                profit_factor = total_won if total_won > 0 else 1.0
                
            if len(returns) > 1:
                avg_ret = sum(returns) / len(returns)
                variance = sum((x - avg_ret) ** 2 for x in returns) / (len(returns) - 1)
                std_dev = math.sqrt(variance)
                if std_dev > 0:
                    sharpe_ratio = (avg_ret / std_dev) * math.sqrt(252)
    except:
        pass
    return balance, peak, cushion_pct, win_ratio, profit_factor, max_dd_pct, sharpe_ratio

def export_ledger_to_csv():
    try:
        with sqlite3.connect('trading_system.db', timeout=5.0) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, type, amount, resulting_balance FROM ledger_history ORDER BY id ASC;")
            rows = cursor.fetchall()
            
            filename = f"trading_report_{int(time.time())}.csv"
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Transaction ID', 'Timestamp', 'Execution Type', 'Delta Amount ($)', 'Resulting Balance ($)'])
                writer.writerows(rows)
            print(f"\n{GREEN}[SUCCESS] Strategy log exported to {filename}{RESET}")
    except Exception as e:
        print(f"\n{RED}[ERROR] Export failed: {e}{RESET}")
    time.sleep(2)

def render_dashboard_frame(balance, peak, cushion, win_ratio, pf, max_dd, sharpe):
    sys.stdout.write(CLEAR_SCREEN)
    print(f"{BOLD}====================================={RESET}")
    print(f"{CYAN}    QUANT PERFORMANCE MATRIX SHELL   {RESET}")
    print(f"{BOLD}====================================={RESET}")
    print(f"Current Balance:  {GREEN}${balance:,.2f}{RESET}")
    print(f"Trailing Peak:    ${peak:,.2f}")
    print(f"Risk Floor:       {YELLOW}${cushion:,.2f}{RESET}")
    print(f"{BOLD}-------------------------------------{RESET}")
    print(f"Win/Loss Ratio:   {GREEN if win_ratio >= 50 else RED}{win_ratio:.1f}%{RESET}")
    print(f"Profit Factor:    {GREEN if pf >= 1.2 else RED}{pf:.2f}{RESET}")
    print(f"Max Peak DD%:     {RED if max_dd > 15 else YELLOW}{max_dd:.2f}%{RESET}")
    print(f"Sharpe Ratio:     {GREEN if sharpe >= 1.5 else CYAN}{sharpe:.2f}{RESET}")
    print(f"{BOLD}====================================={RESET}")
    print("1. Inject Deposit Capital")
    print("2. Safe Capital Withdrawal")
    print("3. Strategy Execution Module Selector")
    print("4. Adjust Safety Floor Parameter")
    print("5. Export History to Excel CSV")
    print("6. Administrative Reset Engine")
    print("7. Terminate Terminal Session")
    print(f"{BOLD}====================================={RESET}")

def user_interface_menu():
    while True:
        balance, peak, cushion_pct, win_ratio, pf, max_dd, sharpe = get_performance_metrics()
        cushion = peak * cushion_pct
        render_dashboard_frame(balance, peak, cushion, win_ratio, pf, max_dd, sharpe)
        
        try:
            choice = input("Execute Action Protocol (1-7): ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        
        if choice == "1":
            try:
                amount_str = input(f"\nEnter deposit amount: {GREEN}$").strip()
                val = float(amount_str)
                if val <= 0: raise ValueError
                with sqlite3.connect('trading_system.db', timeout=5.0) as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE account_state SET balance = balance + ?, peak_balance = max(peak_balance, balance + ?) WHERE id = 1;", (val, val))
                    conn.commit()
                print(f"{GREEN}[SUCCESS] Capital balance updated.{RESET}")
                time.sleep(1.2)
            except ValueError:
                print(f"{RED}[REJECTED] Invalid positive numerical input.{RESET}")
                time.sleep(1.5)
        elif choice == "2":
            surplus = balance - cushion
            if surplus > 0:
                print(f"\nMax Free Liquidity: {GREEN}${surplus:,.2f}{RESET}")
                if input("Confirm execution? (y/n): ").strip().lower() == 'y':
                    with sqlite3.connect('trading_system.db', timeout=5.0) as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE account_state SET balance = balance - ? WHERE id = 1;", (surplus,))
                        conn.commit()
                    print(f"{GREEN}[SUCCESS] Liquidity extracted.{RESET}")
            else:
                print(f"\n{RED}[REJECTED] Drawdown containment active.{RESET}")
            time.sleep(1.5)
        elif choice == "3":
            sys.stdout.write(CLEAR_SCREEN)
            print(f"{BOLD}=== STRATEGY EXECUTION SWITCHBOARD ==={RESET}")
            print("1. Run Instant Historical Backtest Sweep")
            print("2. Engage Real-Time Live Stream Simulation")
            mode = input("\nSelect operational mode (1-2): ").strip()
            
            if mode == "1":
                print(f"\n{YELLOW}[SYSTEM] Executing optimized historical calculation...{RESET}")
                subprocess.run(["python", "backtest.py"])
                time.sleep(1.5)
            elif mode == "2":
                print(f"\n{GREEN}[SYSTEM] Launching live background tick daemon...{RESET}")
                subprocess.Popen(["nohup", "python", "simulation.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1)
                try:
                    while True:
                        b, pk, cp, wr, p_f, m_dd, sh = get_performance_metrics()
                        sys.stdout.write(CLEAR_SCREEN)
                        print(f"{BOLD}====================================={RESET}")
                        print(f" LIVE TELEMETRY STREAM | DD: {m_dd:.1f}% | SR: {sh:.2f}")
                        print(f" Bal: {GREEN}${b:,.2f}{RESET} | Floor: {YELLOW}${pk*cp:,.2f}{RESET}")
                        print(f"{BOLD}====================================={RESET}")
                        if os.path.exists("trading.log"):
                            with open("trading.log", "r") as log_file:
                                for line in log_file.readlines()[-13:]:
                                    cleaned = line.strip()
                                    print(f"{YELLOW}⚠️ {cleaned}{RESET}" if "DEFENSIVE" in cleaned else (f"{GREEN}{cleaned}{RESET}" if "GAIN" in cleaned else (f"{RED}{cleaned}{RESET}" if "LOSS" in cleaned else cleaned)))
                        time.sleep(2)
                except KeyboardInterrupt:
                    print(f"\n{YELLOW}[SYSTEM] Detaching console view. Engine remains live in core memory.{RESET}")
                    time.sleep(1.5)
        elif choice == "4":
            try:
                pct_str = input("\nEnter target risk floor percentage (e.g. 20 for 20%): ").strip()
                new_pct = float(pct_str) / 100.0
                if not (0.05 <= new_pct <= 0.50): raise ValueError
                with sqlite3.connect('trading_system.db', timeout=5.0) as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE account_state SET cushion_pct = ? WHERE id = 1;", (new_pct,))
                    conn.commit()
                print(f"{GREEN}[SUCCESS] Safety margin adjusted to {pct_str}%.{RESET}")
            except ValueError:
                print(f"{RED}[REJECTED] Margin bounds must be between 5% and 50%.{RESET}")
            time.sleep(1.5)
        elif choice == "5":
            export_ledger_to_csv()
        elif choice == "6":
            print(f"\n{YELLOW}[SYSTEM] Executing structural reset wipe...{RESET}")
            try:
                with sqlite3.connect('trading_system.db', timeout=5.0) as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE account_state SET balance = 320.75, peak_balance = 320.75, cushion_pct = 0.25 WHERE id = 1;")
                    cursor.execute("DELETE FROM ledger_history;")
                    conn.commit()
                if os.path.exists("trading.log"): 
                    os.remove("trading.log")
                print(f"{GREEN}[RESET SUCCESSFUL] Systems re-calibrated back to baseline.{RESET}")
            except Exception as e:
                print(f"{RED}[ERROR] Reset interrupted: {e}{RESET}")
            time.sleep(2)
        elif choice == "7":
            print(f"\n{CYAN}[SYSTEM] System terminal safe shutdown complete.{RESET}")
            break

if __name__ == "__main__":
    user_interface_menu()