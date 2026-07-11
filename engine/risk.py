import logging

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self, max_daily_loss_pct=2.0, max_drawdown_pct=5.0, risk_per_trade_pct=1.0, pip_value_gold=10.0):
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_drawdown_pct = max_drawdown_pct
        self.risk_per_trade_pct = risk_per_trade_pct
        self.pip_value_gold = pip_value_gold  # Standard value per lot per pip for XAUUSD

    def check_safety_guards(self, current_balance, current_equity, starting_daily_balance):
        """
        Enforces a hard circuit breaker if daily or total drawdown caps are breached.
        """
        daily_loss = starting_daily_balance - current_equity
        max_daily_loss_allowed = starting_daily_balance * (self.max_daily_loss_pct / 100.0)
        
        # Check daily loss limit
        if daily_loss >= max_daily_loss_allowed:
            logger.critical(f"EMERGENCY: Daily loss limit breached! Loss: {daily_loss} | Allowed: {max_daily_loss_allowed}")
            return {"status": "KILL_SWITCH", "reason": "Daily drawdown threshold exceeded."}
            
        # Check maximum absolute peak-to-trough drawdown
        total_drawdown = (current_balance - current_equity) / current_balance * 100.0
        if total_drawdown >= self.max_drawdown_pct:
            logger.critical(f"EMERGENCY: Max total drawdown breached! Drawdown: {total_drawdown}%")
            return {"status": "KILL_SWITCH", "reason": "Max total drawdown threshold exceeded."}

        return {"status": "NOMINAL", "reason": "Risk parameters within safe boundaries."}

    def calculate_position_size(self, balance, stop_loss_pips):
        """
        Dynamically adjusts lot sizing based on total stop loss distance in pips.
        """
        if stop_loss_pips <= 0:
            return 0.0
            
        cash_risk = balance * (self.risk_per_trade_pct / 100.0)
        raw_lot_size = cash_risk / (stop_loss_pips * self.pip_value_gold)
        
        # Round down to standard institutional lot step sizing (2 decimal places)
        return round(raw_lot_size, 2)
