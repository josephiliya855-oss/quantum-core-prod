from decimal import Decimal, ROUND_HALF_UP
import random
from dashboard.models import LedgerHistory, AccountState

class ExecutionEngine:
    def __init__(self):
        self.max_drawdown_pct = Decimal('0.15')  # 15% Maximum Risk Envelope

    def _rand_decimal(self, low, high):
        # Return a Decimal rounded to 2 places safely
        value = Decimal(str(random.uniform(float(low), float(high))))
        return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def evaluate_and_execute(self, current_price, market_regime):
        # Ensure AccountState exists
        state, _ = AccountState.objects.get_or_create(
            id=1,
            defaults={'balance': Decimal('100000.00'), 'equity': Decimal('100000.00'), 'initial_capital': Decimal('100000.00')}
        )

        # 1. Check if the system circuit breaker has already tripped
        if state.is_locked:
            print("[⚠️ RISK OVERRIDE] Engine is LOCKED. Order rejected to protect capital.")
            return None

        # 2. Calculate current drawdown from initial peak capital
        try:
            drawdown = (state.initial_capital - state.equity) / state.initial_capital
        except Exception:
            drawdown = Decimal('0.0')

        if drawdown >= self.max_drawdown_pct:
            state.is_locked = True
            state.save()
            print(f"[🚨 CIRCUIT BREAKER TRIPPED] Drawdown reached {drawdown * 100:.2f}%. Halting all processes!")
            return None

        action = None
        if market_regime == "BULLISH_EXPANSION":
            action = "BUY"
        elif market_regime == "BEARISH_DISTRIBUTION":
            action = "SELL"

        if not action:
            return None

        is_win = random.choice([True, False, True])  # Edge simulation

        if is_win:
            delta = self._rand_decimal(200.00, 1500.00)
        else:
            delta = self._rand_decimal(-1200.00, -400.00)

        # Apply results
        state.balance = (state.balance or Decimal('0.0')) + delta
        state.equity = state.balance
        state.save()

        ledger_entry = LedgerHistory.objects.create(
            action=action,
            delta=delta,
            resulting_balance=state.balance
        )

        sign = '+' if delta >= 0 else ''
        print(f"[ORDER EXECUTION] {action} Order Filled | Delta: {sign}${delta} | Balance: ${state.balance}")
        return ledger_entry
