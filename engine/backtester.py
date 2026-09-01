import os
import sys
from decimal import Decimal, ROUND_HALF_UP
import django
import math

# Set up Django environment if this script is run standalone
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_platform.settings')
django.setup()

from dashboard.models import XauUsdCandle, LedgerHistory, AccountState
from engine.analysis import MarketAnalyzer


def _to_decimal(v):
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def execute_historical_backtest():
    print("====================================================")
    print("🚀 INITIALIZING ADVANCED RISK & PERFORMANCE BACKTEST")
    print("====================================================")

    LedgerHistory.objects.all().delete()

    starting_capital = Decimal("100000.00")
    current_balance = starting_capital
    position_active = False
    entry_price = Decimal("0.00")

    trades_executed = 0
    winning_trades = 0
    total_gains = Decimal("0.00")
    total_losses = Decimal("0.00")
    equity_peak = starting_capital
    max_drawdown = Decimal("0.00")

    analyzer = MarketAnalyzer()
    historical_candles = list(XauUsdCandle.objects.order_by('timestamp'))
    total_records = len(historical_candles)

    if total_records < 15:
        print("[❌] Insufficient data array depth for statistical context.")
        return

    for i in range(14, total_records):
        visible_window = historical_candles[i-14:i+1]
        formatted_history = [
            {"high": float(c.high_price), "low": float(c.low_price), "close": float(c.close_price)}
            for c in visible_window
        ]

        current_candle = historical_candles[i]
        current_close = _to_decimal(current_candle.close_price)
        regime = analyzer.analyze_regime_structure(formatted_history)

        if not position_active:
            if regime == "BULLISH_EXPANSION":
                entry_price = current_close
                position_active = True
                print(f"[+] BUY ORDER | Time: {current_candle.timestamp.strftime('%H:%M')} | Price: ${entry_price}")
        else:
            if regime in ("BEARISH_DISTRIBUTION", "CONSOLIDATION_COMPRESSION"):
                exit_price = current_close
                profit_loss = (exit_price - entry_price) * Decimal("50.0")
                profit_loss = profit_loss.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                current_balance += profit_loss
                position_active = False
                trades_executed += 1

                if profit_loss >= 0:
                    winning_trades += 1
                    total_gains += profit_loss
                else:
                    total_losses += abs(profit_loss)

                if current_balance > equity_peak:
                    equity_peak = current_balance
                else:
                    drawdown = ((equity_peak - current_balance) / equity_peak) * Decimal("100.0")
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown

                LedgerHistory.objects.create(
                    action="SELL" if profit_loss >= 0 else "LIQ",
                    delta=profit_loss,
                    resulting_balance=current_balance
                )
                print(f"[-] EXIT ORDER | Time: {current_candle.timestamp.strftime('%H:%M')} | PnL: ${profit_loss:,.2f} | Bal: ${current_balance:,.2f}")

    win_rate = (winning_trades / trades_executed * 100) if trades_executed > 0 else 0.0
    profit_factor = (total_gains / total_losses) if total_losses > 0 else (total_gains if total_gains > 0 else Decimal("1.0"))

    state, _ = AccountState.objects.get_or_create(id=1)
    state.balance = current_balance
    state.equity = current_balance
    state.save()

    print("\n====================================================")
    print("📊 PERFORMANCE AUDIT REPORT")
    print("====================================================")
    print(f" Ending Balance:      ${current_balance:,.2f}")
    print(f" Net Return:           {((current_balance/starting_capital)-1)*100:+.2f}%")
    print(f" Total Executed:       {trades_executed} trades")
    print(f" Strategy Win Rate:    {win_rate:.1f}%")
    print(f" Profit Factor:        {profit_factor:.2f}x")
    print(f" Maximum Drawdown:     {max_drawdown:.2f}%")
    print("====================================================")


if __name__ == '__main__':
    execute_historical_backtest()
