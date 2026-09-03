from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum
from dashboard.models import XauUsdCandle, LedgerHistory, AccountState
from engine.analysis import MarketAnalyzer
from decimal import Decimal

def index(request):
    # Safe retrieval
    db_candles = list(XauUsdCandle.objects.order_by('timestamp'))
    ledger_items = LedgerHistory.objects.order_by('-id')[:10]
    
    state, created = AccountState.objects.get_or_create(id=1, defaults={
        'balance': Decimal('100000.00'),
        'equity': Decimal('100000.00')
    })
    
    candle_history = [
        {"high": float(c.high_price), "low": float(c.low_price), "close": float(c.close_price)}
        for c in db_candles
    ]
    
    analyzer = MarketAnalyzer()
    market_regime = analyzer.analyze_regime_structure(candle_history) if len(candle_history) >= 5 else "NEUTRAL_ACCUMULATION"
    
    total_trades = LedgerHistory.objects.count()
    winning_trades = LedgerHistory.objects.filter(delta__gt=0).count()
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
    
    # Safe slice with fallbacks for empty lists
    chart_candles = db_candles[-15:] if len(db_candles) >= 15 else db_candles
    
    if chart_candles:
        chart_labels = [c.timestamp.strftime("%H:%M") for c in chart_candles]
        chart_data = [float(c.close_price) for c in chart_candles]
    else:
        # Prevent layout breakdown on completely empty database
        chart_labels = ["00:00"]
        chart_data = [0.0]
    
    if request.GET.get('format') == 'json':
        data_payload = {
            "balance": float(state.balance),
            "equity": float(state.equity),
            "market_regime": market_regime,
            "win_rate": f"{win_rate:.1f}%",
            "total_trades": total_trades,
            "chart_labels": chart_labels,
            "chart_data": chart_data,
            "guard_status": {"status": "HEALTHY"},
            "table_rows": [
                {
                    "timestamp_str": item.id,
                    "delta": float(item.delta),
                    "resulting_balance": float(item.resulting_balance)
                } for item in ledger_items
            ]
        }
        return JsonResponse(data_payload)
        
    context = {
        "state": {
            "balance": state.balance,
            "equity": state.equity,
            "cushion_pct": "100.00" if state.balance == 0 else f"{(state.equity / state.balance) * 100:.2f}%"
        },
        "market_regime": market_regime,
        "win_rate": f"{win_rate:.1f}%",
        "total_trades": total_trades,
        "history": ledger_items,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "guard_status": {"status": "HEALTHY"}
    }
    return render(request, "dashboard/index.html", context)

from django.http import HttpResponseRedirect
from django.urls import reverse
from decimal import Decimal
from .models import LedgerHistory, XauUsdCandle, AccountState

def reset_system_state(request):
    """
    Resets account balances, wipes historical logs, and releases risk locks.
    """
    if request.method == "POST":
        # Clear out execution history
        LedgerHistory.objects.all().delete()
        XauUsdCandle.objects.all().delete()
        
        # Re-initialize baseline capital structures
        state = AccountState.objects.get(id=1)
        state.balance = Decimal('100000.00')
        state.equity = Decimal('100000.00')
        state.initial_capital = Decimal('100000.00')
        state.is_locked = False
        state.save()
        
        print("[🔄 SYSTEM RESET] Core metrics cleared and re-initialized.")
    return HttpResponseRedirect(reverse('index'))


def summary(request):
    """Project-wide data summary: account, performance, market data, and recent ledger."""
    state, _ = AccountState.objects.get_or_create(id=1, defaults={
        'balance': Decimal('100000.00'),
        'equity': Decimal('100000.00')
    })

    # --- Market data ---
    candles = list(XauUsdCandle.objects.order_by('timestamp'))
    candle_count = len(candles)
    latest_candle = candles[-1] if candles else None
    latest_price = float(latest_candle.close_price) if latest_candle else 0.0
    price_high = max((float(c.high_price) for c in candles), default=0.0)
    price_low = min((float(c.low_price) for c in candles), default=0.0)

    candle_history = [
        {"high": float(c.high_price), "low": float(c.low_price), "close": float(c.close_price)}
        for c in candles
    ]
    analyzer = MarketAnalyzer()
    market_regime = analyzer.analyze_regime_structure(candle_history) if len(candle_history) >= 5 else "INSUFFICIENT_DATA"

    # --- Performance / ledger ---
    total_trades = LedgerHistory.objects.count()
    winning = LedgerHistory.objects.filter(delta__gt=0)
    winning_count = winning.count()
    losing_count = LedgerHistory.objects.filter(delta__lt=0).count()
    win_rate = (winning_count / total_trades * 100) if total_trades > 0 else 0.0

    total_pnl = LedgerHistory.objects.aggregate(t=Sum('delta'))['t'] or Decimal('0')
    gross_profit = winning.aggregate(t=Sum('delta'))['t'] or Decimal('0')
    gross_loss = abs(LedgerHistory.objects.filter(delta__lt=0).aggregate(t=Sum('delta'))['t'] or Decimal('0'))
    profit_factor = float(gross_profit / gross_loss) if gross_loss > 0 else 0.0

    # Peak-to-trough drawdown across the ledger
    max_dd_pct = 0.0
    running_peak = 0.0
    for tx in LedgerHistory.objects.order_by('id').values_list('resulting_balance', flat=True):
        bal = float(tx)
        if bal > running_peak:
            running_peak = bal
        if running_peak > 0:
            dd = ((running_peak - bal) / running_peak) * 100
            if dd > max_dd_pct:
                max_dd_pct = dd

    pnl_pct = (float(total_pnl) / float(state.initial_capital) * 100) if state.initial_capital else 0.0
    recent_ledger = LedgerHistory.objects.order_by('-id')[:15]

    context = {
        "state": state,
        "total_pnl": total_pnl,
        "pnl_pct": pnl_pct,
        "total_trades": total_trades,
        "winning_count": winning_count,
        "losing_count": losing_count,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "max_dd_pct": max_dd_pct,
        "candle_count": candle_count,
        "latest_price": latest_price,
        "price_high": price_high,
        "price_low": price_low,
        "market_regime": market_regime,
        "recent_ledger": recent_ledger,
    }
    return render(request, "dashboard/summary.html", context)
