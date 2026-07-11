import math

class MarketAnalyzer:
    def __init__(self):
        pass

    def calculate_ema(self, prices, period):
        """Calculates the Exponential Moving Average for a given period."""
        if len(prices) < period:
            return None
        
        # Start with simple moving average for the first data point
        sma = sum(prices[:period]) / period
        multiplier = 2 / (period + 1)
        
        ema = sma
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        return ema

    def calculate_atr(self, candle_history, period=14):
        """Calculates the Average True Range to measure market volatility."""
        if len(candle_history) < period + 1:
            return 1.50  # Stable default volatility buffer if history is short

        true_ranges = []
        for i in range(1, len(candle_history)):
            high = candle_history[i]['high']
            low = candle_history[i]['low']
            prev_close = candle_history[i-1]['close']
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)

        # Return the simple average of the true ranges for the period
        return sum(true_ranges[-period:]) / period

    def analyze_regime_structure(self, candle_history):
        """
        Processes history to return a structural market regime:
        'BULLISH_TREND', 'BEARISH_TREND', or 'RANGING'
        """
        if len(candle_history) < 20:
            return "RANGING"

        closes = [c['close'] for c in candle_history]
        
        # Calculate standard institutional cross trends (9 EMA vs 21 EMA)
        ema_fast = self.calculate_ema(closes, 9)
        ema_slow = self.calculate_ema(closes, 21)
        
        if not ema_fast or not ema_slow:
            return "RANGING"

        atr = self.calculate_atr(candle_history, period=14)
        
        # Filter: If ATR is squeezing super low, classify as low-volatility RANGING
        if atr < 0.30:
            return "RANGING"

        # Crossover verification rules
        if ema_fast > ema_slow:
            return "BULLISH_TREND"
        elif ema_fast < ema_slow:
            return "BEARISH_TREND"
        
        return "RANGING"
