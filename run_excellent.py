import subprocess
import time
import sys
import os

# Ensure the script exists before trying to run it
target = "simulation.py"
if not os.path.exists(target):
    print(f"[ERROR] {target} not found in {os.getcwd()}")
    sys.exit(1)

print("[SYSTEM] Resilience Watchdog Armed. Launching simulation...")
while True:
    try:
        # Run the simulation
        process = subprocess.Popen([sys.executable, target])
        process.wait()
        
        print("[!] System exited. Restarting in 5 seconds...")
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n[!] Watchdog stopped by user.")
        break
