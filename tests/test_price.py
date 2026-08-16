"""Tests for electricity-price dimming."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = (
    Path(__file__).parents[1]
    / "custom_components"
    / "aquarium_led_cockpit"
    / "price.py"
)
SPEC = importlib.util.spec_from_file_location("aquarium_led_price", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
PRICE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PRICE)


class PriceAdjustmentTests(unittest.TestCase):
    """Verify the adaptive high-price curve."""

    ATTRIBUTES = {
        "min_price": 0.17,
        "avg_price": 0.31,
        "max_price": 0.41,
        "unit_of_measurement": "EUR/kWh",
    }

    def test_no_dimming_at_or_below_daily_average(self) -> None:
        for price in (0.17, 0.31):
            with self.subTest(price=price):
                result = PRICE.calculate_price_adjustment(price, self.ATTRIBUTES, 72)
                self.assertEqual(result["factor"], 1.0)
                self.assertEqual(result["load"], 0.0)

    def test_dimming_reacts_progressively_above_average(self) -> None:
        result = PRICE.calculate_price_adjustment(0.36, self.ATTRIBUTES, 72)
        self.assertAlmostEqual(result["raw_load"], 0.5)
        self.assertAlmostEqual(result["load"], 0.5 ** PRICE.PRICE_RESPONSE_EXPONENT)
        self.assertAlmostEqual(result["factor"], 0.5411581741650656)
        self.assertLess(result["factor"], 0.64)

    def test_configured_dimming_is_reached_at_daily_maximum(self) -> None:
        result = PRICE.calculate_price_adjustment(0.41, self.ATTRIBUTES, 72)
        self.assertEqual(result["load"], 1.0)
        self.assertEqual(result["raw_load"], 1.0)
        self.assertAlmostEqual(result["factor"], 0.28)

    def test_intraday_ranking_is_used_as_fallback(self) -> None:
        result = PRICE.calculate_price_adjustment(
            0.36,
            {"intraday_price_ranking": 0.75},
            60,
        )
        self.assertEqual(result["strategy"], "intraday_ranking")
        self.assertAlmostEqual(result["raw_load"], 0.5)
        self.assertAlmostEqual(result["load"], 0.5 ** PRICE.PRICE_RESPONSE_EXPONENT)
        self.assertLess(result["factor"], 0.7)

    def test_cent_per_kwh_sensor_uses_scaled_thresholds(self) -> None:
        result = PRICE.calculate_price_adjustment(
            45,
            {"unit_of_measurement": "ct/kWh"},
            80,
        )
        self.assertEqual(result["strategy"], "unit_threshold")
        self.assertEqual(result["load"], 1.0)
        self.assertAlmostEqual(result["factor"], 0.2)

    def test_unavailable_price_does_not_dim(self) -> None:
        result = PRICE.calculate_price_adjustment(None, {}, 90)
        self.assertEqual(result["strategy"], "unavailable")
        self.assertEqual(result["factor"], 1.0)
        self.assertEqual(result["raw_load"], 0.0)

    def test_battery_full_uses_configured_threshold(self) -> None:
        self.assertFalse(PRICE.is_battery_full(94.9, 95))
        self.assertTrue(PRICE.is_battery_full(95, 95))
        self.assertTrue(PRICE.is_battery_full(100, 95))

    def test_unavailable_battery_is_not_full(self) -> None:
        self.assertFalse(PRICE.is_battery_full(None, 95))

    def test_high_battery_adds_daylight_brightness_factor(self) -> None:
        self.assertEqual(1.0, PRICE.calculate_battery_brightness_factor(89.9, 90))
        self.assertEqual(1.15, PRICE.calculate_battery_brightness_factor(90, 90))
        self.assertEqual(1.15, PRICE.calculate_battery_brightness_factor(100, 90))

    def test_battery_boost_is_bounded(self) -> None:
        self.assertEqual(1.5, PRICE.calculate_battery_brightness_factor(90, 90, 80))
        self.assertEqual(90, PRICE.apply_battery_brightness_boost(80, 90, 90, 90))
        self.assertEqual(80.5, PRICE.apply_battery_brightness_boost(70, 90, 90, 90))
        self.assertEqual(70, PRICE.apply_battery_brightness_boost(70, 90, 89.9, 90))


if __name__ == "__main__":
    unittest.main()
