from decimal import Decimal
import random
from dashboard.models import LedgerHistory, AccountState

class ExecutionEngine:
    def __init__(self):
        self.max_drawdown_pct = Decimal('0.15')  # 15% Maximum Risk Envelope

    def evaluate_and_execute(self, current_price, market_regime):
        state = AccountState.objects.get(id=1)
        
        # 1. Check if the system circuit breaker has already tripped
        if state.is_locked:
            print("[⚠️ RISK OVERRIDE] Engine is LOCKED. Order rejected to protect capital.")
            return None

        # 2. Calculate current drawdown from initial peak capital
        drawdown = (state.initial_capital - state.equity) / state.initial_capital
        if drawdown >= self.max_drawdown_pct:
            state.is_locked = True
            state.save()
            print(f"[🚨 CIRCUIT BREAKER TRIPPED] Drawdown reached {drawdown*100:.2f}%. Halting all processes!")
            return None

        current_price = Decimal(str(round(current_price, 2)))
        action = None
        if market_regime == "BULLISH_EXPANSION":
            action = "BUY"
        elif market_regime == "BEARISH_DISTRIBUTION":
            action = "SELL"
            
        if not action:
            return None

        is_win = random.choice([True, False, True]) # Edge simulation
        
        if is_win:
            delta = Decimal(random.uniform(200.00, 1500.00))
        else:
            delta = Decimal(random.uniform(-400.00, -1200.00)) # Realistic risk/reward variance

        delta = round(delta, 2)
        state.balance += delta
        state.equity = state.balance
        state.save()

        ledger_entry = LedgerHistory.objects.create(
            delta=delta,
            resulting_balance=state.balance
        )
        
        print(f"[ORDER EXECUTION] {action} Order Filled | Delta: {'' if delta < 0 else '+'}${delta} | Balance: ${state.balance}")
        return ledger_entry
