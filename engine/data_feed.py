import time
import random
import logging

logger = logging.getLogger(__name__)

class MarketDataEngine:
    def __init__(self, symbol="XAUUSD"):
        self.symbol = symbol
        self.current_spread = 0.15 # Institutional tight spread target ($0.15 on Gold)
        self.base_price = 2385.50

    def fetch_live_tick(self):
        """
        Simulates an institutional ultra-low latency WebSocket/REST tick update.
        In production, this replaces with your broker API stream (e.g., MetaTrader5 or OANDA).
        """
        # Introduce continuous micro-tick asset variance
        price_change = random.uniform(-1.25, 1.30)
        self.base_price = round(self.base_price + price_change, 2)
        
        # Micro-fluctuations in broker liquidity spreads
        self.current_spread = round(random.uniform(0.12, 0.22), 2)
        
        tick_data = {
            "symbol": self.symbol,
            "bid": round(self.base_price, 2),
            "ask": round(self.base_price + self.current_spread, 2),
            "spread": self.current_spread,
            "timestamp": time.time()
        }
        return tick_data

    def calculate_atr(self, high_array, low_array, close_array, period=14):
        """
        Calculates Average True Range (ATR) to measure volatility metrics for position sizing rules.
        """
        if len(close_array) < 2:
            return 1.50 # Fallback default volatility buffer
            
        ranges = []
        for i in range(1, len(close_array)):
            tr1 = high_array[i] - low_array[i]
            tr2 = abs(high_array[i] - close_array[i-1])
            tr3 = abs(low_array[i] - close_array[i-1])
            ranges.append(max(tr1, tr2, tr3))
            
        return sum(ranges[-period:]) / min(len(ranges), period)
