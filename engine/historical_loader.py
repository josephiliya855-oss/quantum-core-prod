import os
import sys
import django
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_platform.settings')
django.setup()

from dashboard.models import XauUsdCandle
from django.db import transaction

def load_historical_fixtures():
    print("[*] Generating dynamic trend-cycling dataset...")
    
    base_price = 2350.00
    current_time = datetime.now() - timedelta(hours=12)
    candles_to_create = []
    
    for i in range(60):
        bar_time = current_time + timedelta(minutes=i)
        
        # Phase 1: Strong Bullish Accumulation (Bars 0-25) -> Forces a BUY signal
        if i < 25:
            change = 2.40  
        # Phase 2: Ranging Peak Distribution (Bars 25-40) -> Slows momentum
        elif i < 40:
            change = 0.20 if i % 2 == 0 else -0.30
        # Phase 3: Aggressive Bearish Capitulation (Bars 40-60) -> Forces a SELL/LIQ
        else:
            change = -3.10
            
        open_p = base_price
        close_p = open_p + change
        high_p = max(open_p, close_p) + 0.50
        low_p = min(open_p, close_p) - 0.50
        
        candle = XauUsdCandle(
            timestamp=bar_time,
            open_price=round(open_p, 2),
            high_price=round(high_p, 2),
            low_price=round(low_p, 2),
            close_price=round(close_p, 2),
            volume=450
        )
        candles_to_create.append(candle)
        base_price = close_p

    try:
        with transaction.atomic():
            XauUsdCandle.objects.all().delete()
            XauUsdCandle.objects.bulk_create(candles_to_create)
        print(f"[✓] Injected {len(candles_to_create)} high-volatility trend bars.")
    except Exception as error:
        print(f"[❌] Failed: {str(error)}")

if __name__ == '__main__':
    load_historical_fixtures()
