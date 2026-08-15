"""Tests for the real sun and moonlight profile."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


MODULE_PATH = (
    Path(__file__).parents[1]
    / "custom_components"
    / "aquarium_led_cockpit"
    / "solar.py"
)
SPEC = importlib.util.spec_from_file_location("aquarium_led_solar", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
SOLAR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SOLAR
SPEC.loader.exec_module(SOLAR)


class SolarProfileTests(unittest.TestCase):
    """Verify the real event boundaries and colour transitions."""

    def profile(self, minute: int):
        return SOLAR.calculate_solar_profile(minute, 360, 1200, 90, 2)

    def test_sunrise_starts_red_at_real_sunrise(self) -> None:
        profile = self.profile(360)

        self.assertEqual("sunrise", profile.phase)
        self.assertEqual(SOLAR.DAWN_DUSK_RGBW, profile.rgbw)
        self.assertEqual(2, profile.base_pct)

    def test_sunrise_reaches_white_after_one_hour(self) -> None:
        midpoint = self.profile(390)
        daylight = self.profile(420)

        self.assertEqual("sunrise", midpoint.phase)
        self.assertAlmostEqual(46, midpoint.base_pct)
        self.assertEqual("day", daylight.phase)
        self.assertEqual(SOLAR.DAYLIGHT_RGBW, daylight.rgbw)
        self.assertEqual(90, daylight.base_pct)

    def test_sunset_starts_ninety_minutes_before_real_sunset(self) -> None:
        start = self.profile(1110)
        midpoint = self.profile(1155)

        self.assertEqual("sunset", start.phase)
        self.assertEqual(SOLAR.DAYLIGHT_RGBW, start.rgbw)
        self.assertEqual(90, start.base_pct)
        self.assertEqual("sunset", midpoint.phase)
        self.assertAlmostEqual(46, midpoint.base_pct)

    def test_real_sunset_switches_to_dim_moonlight(self) -> None:
        before = self.profile(1199)
        night = self.profile(1200)

        self.assertEqual("sunset", before.phase)
        self.assertGreater(before.rgbw[0], before.rgbw[2])
        self.assertEqual("night", night.phase)
        self.assertEqual(SOLAR.MOONLIGHT_RGBW, night.rgbw)
        self.assertGreater(night.rgbw[3], 0)
        self.assertLess(night.rgbw[3], SOLAR.DAYLIGHT_RGBW[3])
        self.assertEqual(2, night.base_pct)


if __name__ == "__main__":
    unittest.main()
