from django.apps import AppConfig
import threading
import time
from datetime import datetime
from decimal import Decimal
import random
import requests

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN') == 'true':
            threading.Thread(target=self.start_market_clock, daemon=True).start()

    def start_market_clock(self):
        time.sleep(2)
        print("[⚡] Connecting Quantum//Core to Live Market Feed...")
        
        from dashboard.models import XauUsdCandle, AccountState
        from engine.analysis import MarketAnalyzer
        from engine.execution import ExecutionEngine

        analyzer = MarketAnalyzer()
        executor = ExecutionEngine()
        
        # Change this when you have your unique twelve data or polygon key
        API_KEY = "YOUR_API_KEY_HERE"
        API_URL = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={API_KEY}"

        while True:
            time.sleep(5)
            try:
                state, _ = AccountState.objects.get_or_create(id=1, defaults={'balance': Decimal('100000.00'), 'equity': Decimal('100000.00'), 'initial_capital': Decimal('100000.00')})
                last_candle = XauUsdCandle.objects.order_by('-timestamp').first()
                base_price = float(last_candle.close_price) if last_candle else 2380.00
                
                live_price = None
                
                # Try reaching external live servers if a real key looks present
                if API_KEY != "YOUR_API_KEY_HERE":
                    try:
                        response = requests.get(API_URL, timeout=3)
                        if response.status_code == 200:
                            data = response.json()
                            if "price" in data:
                                live_price = float(data["price"])
                    except Exception:
                        pass
                
                # Failover Fallback: Generate simulation price tracking if API is unavailable/unauthorized
                if live_price is None:
                    change = random.uniform(-1.80, 1.95)
                    live_price = base_price + change

                new_time = datetime.now()
                open_p = base_price
                close_p = live_price
                high_p = max(open_p, close_p) + random.uniform(0.05, 0.25)
                low_p = min(open_p, close_p) - random.uniform(0.05, 0.25)

                XauUsdCandle.objects.create(
                    timestamp=new_time,
                    open_price=round(Decimal(open_p), 2),
                    high_price=round(Decimal(high_p), 2),
                    low_price=round(Decimal(low_p), 2),
                    close_price=round(Decimal(close_p), 2),
                    volume=random.randint(150, 450)
                )

                if XauUsdCandle.objects.count() > 100:
                    oldest = XauUsdCandle.objects.order_by('timestamp').first()
                    oldest.delete()

                db_candles = XauUsdCandle.objects.order_by('timestamp')
                candle_history = [
                    {"high": float(c.high_price), "low": float(c.low_price), "close": float(c.close_price)}
                    for c in db_candles
                ]
                
                regime = analyzer.analyze_regime_structure(candle_history)
                executor.evaluate_and_execute(close_p, regime)

            except Exception as e:
                print(f"[Core Clock Error]: {str(e)}")
