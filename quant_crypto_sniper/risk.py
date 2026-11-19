"""Position sizing shared by backtests and eventual live execution."""

from .config import (
    MAX_EXPOSURE_PER_ASSET_PCT,
    MAX_RISK_PER_TRADE_PCT,
    MIN_ORDER_KRW,
)


def position_notional_krw(
    equity_krw: float,
    available_krw: float,
    entry_price: float,
    stop_price: float,
) -> float:
    if min(equity_krw, available_krw, entry_price, stop_price) <= 0:
        return 0.0
    stop_pct = (entry_price - stop_price) / entry_price
    if stop_pct <= 0:
        return 0.0
    allocation_cap = equity_krw * MAX_EXPOSURE_PER_ASSET_PCT
    risk_cap = equity_krw * MAX_RISK_PER_TRADE_PCT / stop_pct
    notional = min(available_krw, allocation_cap, risk_cap)
    return notional if notional >= MIN_ORDER_KRW else 0.0
