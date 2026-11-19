import unittest

from quant_crypto_sniper.risk import position_notional_krw
from quant_crypto_sniper.strategy import Candle, trend_signal


class StrategyTests(unittest.TestCase):
    def test_long_requires_daily_trend_and_four_hour_breakout(self):
        daily = [Candle(i, i + 1, i - 1, i) for i in range(100, 205)]
        four_hour = [Candle(i, i + 1, i - 1, i) for i in range(100, 131)]
        four_hour[-1] = Candle(132, 135, 131, 134)
        signal = trend_signal(daily, four_hour)
        self.assertEqual(signal.state, "long")
        self.assertLess(signal.stop_price, signal.entry_price)

    def test_falling_daily_market_stays_in_cash(self):
        daily = [Candle(i, i + 1, i - 1, i) for i in range(205, 100, -1)]
        four_hour = [Candle(i, i + 1, i - 1, i) for i in range(100, 131)]
        four_hour[-1] = Candle(132, 135, 131, 134)
        self.assertEqual(trend_signal(daily, four_hour).state, "cash")

    def test_position_size_obeys_allocation_and_risk(self):
        self.assertEqual(
            position_notional_krw(100_000, 100_000, 100, 97),
            15_000,
        )
        self.assertEqual(
            position_notional_krw(20_000, 20_000, 100, 90),
            0,
        )


if __name__ == "__main__":
    unittest.main()
