
# account.py
from decimal import Decimal, ROUND_HALF_UP
from config import DEFAULT_SAFETY_BUFFER, logger
import database

class MobileTradingAccount:
    def __init__(self, safety_buffer_pct: Decimal = DEFAULT_SAFETY_BUFFER):
        self.safety_buffer_pct = safety_buffer_pct
        raw_balance, raw_peak = database.load_account_state()


        self.balance = Decimal(raw_balance)
        self.peak_balance = Decimal(raw_peak)

    def deposit(self, amount: str) -> bool:
        try:
            dec_amount = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if dec_amount <= 0:
                return False
            self.balance += dec_amount
            if self.balance > self.peak_balance:
                self.peak_balance = self.balance
            database.save_account_state(str(self.balance), str(self.peak_balance))
            database.log_transaction("DEPOSIT", str(dec_amount), str(self.balance))
            return True
        except Exception:
            return False

    def calculate_optimal_withdrawal(self) -> Decimal:
        required_cushion = (self.peak_balance * self.safety_buffer_pct).quantize(Decimal("0.01"))
        available_surplus = self.balance - required_cushion
        return max(Decimal("0.00"), available_surplus)

    def withdraw_optimized(self) -> Decimal:
        optimal_amount = self.calculate_optimal_withdrawal()
        if optimal_amount <= 0:
            database.log_transaction("WITHDRAW_FAIL", "0.00", str(self.balance))
            return Decimal("0.00")
        self.balance -= optimal_amount
        database.save_account_state(str(self.balance), str(self.peak_balance))
        database.log_transaction("WITHDRAW_SUCCESS", str(optimal_amount), str(self.balance))
        return optimal_amount
