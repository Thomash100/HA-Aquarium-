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
        self.assertGreater(midpoint.rgbw[0], midpoint.rgbw[1])
        self.assertGreater(midpoint.rgbw[1], midpoint.rgbw[2])
        self.assertLess(midpoint.rgbw[3], 30)
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
        self.assertEqual(self.profile(390).rgbw, midpoint.rgbw)

    def test_real_sunset_switches_to_dim_moonlight(self) -> None:
        before = self.profile(1199)
        night = self.profile(1200)

        self.assertEqual("sunset", before.phase)
        self.assertGreater(before.rgbw[0], before.rgbw[2])
        self.assertEqual("night", night.phase)
        self.assertEqual(SOLAR.MOONLIGHT_RGBW, night.rgbw)
        self.assertEqual(0, night.rgbw[0])
        self.assertGreater(night.rgbw[2], night.rgbw[1])
        self.assertEqual(0, night.rgbw[3])
        self.assertEqual(2, night.base_pct)

    def test_moon_phase_controls_continuous_night_brightness(self) -> None:
        new_moon, new_factor, _ = SOLAR.calculate_moonlight_target(
            7, "new_moon", 0, 1, 1
        )
        full_moon, full_factor, _ = SOLAR.calculate_moonlight_target(
            7, "full_moon", 0, 1, 1
        )

        self.assertEqual(0.25, new_factor)
        self.assertEqual(1.0, full_factor)
        self.assertGreaterEqual(new_moon, SOLAR.MIN_MOONLIGHT_BRIGHTNESS_PCT)
        self.assertGreater(full_moon, new_moon)

    def test_clouds_dim_moonlight_without_switching_it_off(self) -> None:
        clear, _, clear_factor = SOLAR.calculate_moonlight_target(
            7, "full_moon", 0, 1, 1
        )
        cloudy, _, cloudy_factor = SOLAR.calculate_moonlight_target(
            7, "full_moon", 1, 1, 1
        )
        new_moon_cloudy, _, _ = SOLAR.calculate_moonlight_target(
            1, "new_moon", 1, 1, 1
        )

        self.assertEqual(1.0, clear_factor)
        self.assertLess(cloudy_factor, clear_factor)
        self.assertLess(cloudy, clear)
        self.assertEqual(SOLAR.MIN_MOONLIGHT_BRIGHTNESS_PCT, new_moon_cloudy)

    def test_colour_stops_pass_through_orange_gold_and_warm_white(self) -> None:
        self.assertEqual(
            SOLAR.ORANGE_RGBW,
            SOLAR._interpolate_rgbw_stops(SOLAR.SUNRISE_RGBW_STOPS, 0.22),
        )
        self.assertEqual(
            SOLAR.GOLD_RGBW,
            SOLAR._interpolate_rgbw_stops(SOLAR.SUNRISE_RGBW_STOPS, 0.55),
        )
        self.assertEqual(
            SOLAR.WARM_WHITE_RGBW,
            SOLAR._interpolate_rgbw_stops(SOLAR.SUNRISE_RGBW_STOPS, 0.82),
        )

    def test_sunrise_and_sunset_endpoints_are_independently_configurable(self) -> None:
        sunrise_color = (210, 20, 80, 15)
        sunset_color = (255, 80, 0, 25)

        sunrise = SOLAR.calculate_solar_profile(
            360, 360, 1200, 90, 2, sunrise_color, sunset_color
        )
        sunset_stops = SOLAR.build_transition_stops(sunset_color, reverse=True)

        self.assertEqual(sunrise_color, sunrise.rgbw)
        self.assertEqual(sunset_color, sunset_stops[-1][1])
        self.assertNotEqual(sunrise.rgbw, sunset_stops[-1][1])

    def test_invalid_configured_colour_falls_back_to_deep_red(self) -> None:
        profile = SOLAR.calculate_solar_profile(
            360, 360, 1200, 90, 2, [999, "bad"], None
        )

        self.assertEqual(SOLAR.DAWN_DUSK_RGBW, profile.rgbw)


if __name__ == "__main__":
    unittest.main()
