"""Pure, look-ahead-safe trend signal functions."""

from dataclasses import dataclass
from typing import Sequence

from .config import (
    ATR_PERIOD,
    ATR_STOP_MULTIPLIER,
    DAILY_MA_PERIOD,
    DAILY_SLOPE_DAYS,
    FOUR_HOUR_BREAKOUT_PERIOD,
)


@dataclass(frozen=True)
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass(frozen=True)
class Signal:
    state: str
    entry_price: float | None
    stop_price: float | None
    reason: str


def _sma(values: Sequence[float], period: int) -> float:
    if len(values) < period:
        raise ValueError(f"at least {period} values are required")
    return sum(values[-period:]) / period


def atr(candles: Sequence[Candle], period: int = ATR_PERIOD) -> float:
    if len(candles) < period + 1:
        raise ValueError(f"at least {period + 1} candles are required")
    ranges = []
    for previous, current in zip(candles[-period-1:-1], candles[-period:]):
        ranges.append(max(
            current.high - current.low,
            abs(current.high - previous.close),
            abs(current.low - previous.close),
        ))
    return sum(ranges) / period


def trend_signal(
    completed_daily: Sequence[Candle],
    completed_four_hour: Sequence[Candle],
) -> Signal:
    """Return long/cash using completed candles only; callers exclude live candles."""
    daily_needed = DAILY_MA_PERIOD + DAILY_SLOPE_DAYS
    four_hour_needed = max(FOUR_HOUR_BREAKOUT_PERIOD + 1, ATR_PERIOD + 1)
    if len(completed_daily) < daily_needed or len(completed_four_hour) < four_hour_needed:
        return Signal("cash", None, None, "insufficient completed candles")

    daily_closes = [candle.close for candle in completed_daily]
    current_ma = _sma(daily_closes, DAILY_MA_PERIOD)
    prior_ma = _sma(daily_closes[:-DAILY_SLOPE_DAYS], DAILY_MA_PERIOD)
    daily_uptrend = daily_closes[-1] > current_ma and current_ma > prior_ma

    current = completed_four_hour[-1]
    prior_high = max(
        candle.high
        for candle in completed_four_hour[-FOUR_HOUR_BREAKOUT_PERIOD-1:-1]
    )
    if not daily_uptrend:
        return Signal("cash", None, None, "daily trend filter is not positive")
    if current.close <= prior_high:
        return Signal("cash", None, None, "four-hour breakout not confirmed")

    stop = current.close - atr(completed_four_hour) * ATR_STOP_MULTIPLIER
    if stop <= 0 or stop >= current.close:
        return Signal("cash", None, None, "invalid volatility stop")
    return Signal("long", current.close, stop, "daily uptrend and four-hour breakout")
