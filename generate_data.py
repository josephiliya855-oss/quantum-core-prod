import csv
import random

# Generate 500 data points mimicking historical price action
price = 150.0
with open('historical_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'price'])
    for i in range(500):
        price += random.uniform(-2.5, 2.7)
        writer.writerow([f"2026-07-01 {i//60:02d}:{i%60:02d}:00", round(price, 2)])
print("[SUCCESS] historical_data.csv generated with 500 price bars.")
