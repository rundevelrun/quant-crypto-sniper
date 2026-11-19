import unittest

from quant_crypto_sniper.dashboard import public_state, render_dashboard
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

    def test_public_dashboard_omits_sensitive_account_values(self):
        state = {
            "status": "running",
            "total_exposure_pct": "15.0%",
            "total_assets_krw": 100_000,
            "krw_balance": 85_000,
            "api_secret": "never-publish",
            "markets": [{
                "market": "KRW-BTC", "signal": "현금",
                "coin_quantity": 0.123, "position_exposure_pct": "0.0%",
            }],
        }
        safe = public_state(state)
        markdown = render_dashboard(state)
        self.assertNotIn("total_assets_krw", safe)
        self.assertNotIn("coin_quantity", safe["markets"][0])
        self.assertNotIn("never-publish", markdown)
        self.assertIn("금액 비공개", markdown)


if __name__ == "__main__":
    unittest.main()
