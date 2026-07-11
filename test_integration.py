import sys
import logging

# Configure testing logger output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ValidationSuite")

def run_system_validation_check():
    logger.info("==================================================")
    logger.info("   LAUNCHING INTER-MODULE INTEGRATION TESTING     ")
    logger.info("==================================================")

    # 1. VERIFY ALL MODULES IMPORT CORRECTLY
    try:
        from engine.risk import RiskManager
        from engine.analysis import MarketAnalyzer
        logger.info("[✓] MILESTONE 1 PASSED: Engine modules imported with zero compilation errors.")
    except ImportError as e:
        logger.critical(f"[X] MILESTONE 1 FAILED: Import error detected: {e}")
        sys.exit(1)

    # Initialize engines with institutional parameters
    risk_engine = RiskManager(max_daily_loss_pct=2.0, max_drawdown_pct=5.0, risk_per_trade_pct=1.0)
    analysis_engine = MarketAnalyzer()

    # 2. TEST WITH MOCK DATA (Simulating an institutional XAUUSD liquidity expansion)
    logger.info("\n[→] Generating synthetic high-volatility XAUUSD candle data matrix...")
    mock_candles = [
        {"high": 2350.0, "low": 2340.0, "close": 2345.0},  # Candle 0: Consolidation baseline
        {"high": 2385.0, "low": 2346.0, "close": 2380.0},  # Candle 1: High-volume expansion bar
        {"high": 2410.0, "low": 2390.0, "close": 2400.0},  # Candle 2: Continuation (Low > Candle 0 High)
        {"high": 2405.0, "low": 2395.0, "close": 2402.0},  # Candle 3
        {"high": 2420.0, "low": 2400.0, "close": 2415.0},  # Candle 4
    ]

    # Execute technical market structures parsing
    regime = analysis_engine.analyze_regime_structure(mock_candles)
    fvgs = analysis_engine.detect_fair_value_gaps(mock_candles)

    logger.info(f"[✓] Market Regime Detected: {regime}")
    if fvgs:
        for gap in fvgs:
            logger.info(f"[✓] Structural Imbalance Discovered: {gap['type']} | Zone: {gap['bottom']} to {gap['top']} (Size: ${gap['gap_size']:.2f})")
    else:
        logger.warning("[!] No Fair Value Gaps identified within the current data array.")

    # 3. RUN RISK ENGINE INTERACTION TESTS
    logger.info("\n[→] Simulating automated position sizing and capital guardrails...")
    
    # Test typical account parameters
    account_balance = 100000.00
    account_equity = 99500.00
    starting_daily_balance = 100000.00
    stop_loss_distance_pips = 45.0  # $4.50 Gold move

    safety_report = risk_engine.check_safety_guards(account_balance, account_equity, starting_daily_balance)
    allocated_lot_size = risk_engine.calculate_position_size(account_balance, stop_loss_distance_pips)

    logger.info(f"[✓] Risk Safeguard Status: {safety_report['status']} ({safety_report['reason']})")
    logger.info(f"[✓] Dynamic Sizing Calculation: For a {stop_loss_distance_pips} pip SL, authorized volume = {allocated_lot_size} Lots.")

    # 4. PERFORM INTEGRATION PROTECTION STRESS-TEST (Forcing a Bug/Kill-Switch Breach)
    logger.info("\n[→] Stress-testing circuit breaker under extreme drawdown scenarios...")
    compromised_equity = 97500.00  # $2,500 floating loss (2.5% drawdown breach)
    
    breach_report = risk_engine.check_safety_guards(account_balance, compromised_equity, starting_daily_balance)
    logger.info(f"[✓] Circuit Breaker Response: {breach_report['status']} | Core Action: {breach_report['reason']}")

    if breach_report['status'] == "KILL_SWITCH":
        logger.info("\n==================================================")
        logger.info("   INTEGRATION TESTING COMPLETION: SUCCESSFUL     ")
        logger.info("==================================================")
    else:
        logger.error("[X] INTEGRATION ERROR: The circuit breaker failed to trip during a margin exception.")
        sys.exit(1)

if __name__ == "__main__":
    run_system_validation_check()
