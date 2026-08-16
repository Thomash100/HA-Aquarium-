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

    def test_sunrise_reaches_configured_daylight_after_one_hour(self) -> None:
        midpoint = self.profile(390)
        daylight = self.profile(420)

        self.assertEqual("sunrise", midpoint.phase)
        self.assertAlmostEqual(25.75, midpoint.base_pct)
        self.assertEqual((222, 110, 128, 128), midpoint.rgbw)
        self.assertEqual("day", daylight.phase)
        self.assertEqual(SOLAR.DAYLIGHT_RGBW, daylight.rgbw)
        self.assertAlmostEqual(49.5, daylight.base_pct)

    def test_sunset_starts_ninety_minutes_before_real_sunset(self) -> None:
        start = self.profile(1110)
        midpoint = self.profile(1155)

        self.assertEqual("sunset", start.phase)
        self.assertEqual(SOLAR.DAYLIGHT_RGBW, start.rgbw)
        self.assertAlmostEqual(49.5, start.base_pct)
        self.assertEqual("sunset", midpoint.phase)
        self.assertAlmostEqual(25.75, midpoint.base_pct)
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

    def test_daylight_has_its_unique_maximum_at_noon(self) -> None:
        morning = self.profile(600)
        noon = self.profile(720)
        afternoon = self.profile(840)

        self.assertLess(morning.base_pct, noon.base_pct)
        self.assertEqual(90, noon.base_pct)
        self.assertLess(afternoon.base_pct, noon.base_pct)

    def test_daylight_clouds_have_visible_weather_and_wave_effects(self) -> None:
        weather, calm, effective = SOLAR.calculate_daylight_cloud_factors(
            0.12, 0.45, 0
        )
        _, cloud_peak, _ = SOLAR.calculate_daylight_cloud_factors(
            0.12, 0.45, 1
        )

        self.assertAlmostEqual(0.2325, effective)
        self.assertLess(weather, 0.95)
        self.assertLess(cloud_peak, calm)
        self.assertLess(weather * cloud_peak, 0.88)

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

    def test_all_four_transition_endpoints_are_independently_configurable(self) -> None:
        sunrise_start = (220, 10, 20, 0)
        sunrise_end = (180, 200, 240, 230)
        sunset_start = (210, 180, 120, 160)
        sunset_end = (250, 30, 5, 4)

        profiles = [
            SOLAR.calculate_solar_profile(
                minute,
                360,
                1200,
                90,
                2,
                sunrise_start,
                sunset_end,
                60,
                90,
                sunrise_end,
                sunset_start,
            )
            for minute in (360, 420, 1110, 1199)
        ]

        self.assertEqual(sunrise_start, profiles[0].rgbw)
        self.assertEqual(sunrise_end, profiles[1].rgbw)
        self.assertEqual(sunset_start, profiles[2].rgbw)
        self.assertEqual((250, 32, 6, 6), profiles[3].rgbw)

    def test_rgbw_channels_are_interpolated_linearly(self) -> None:
        midpoint = SOLAR.calculate_solar_profile(
            390,
            360,
            1200,
            90,
            2,
            (10, 20, 30, 40),
            (50, 60, 70, 80),
            60,
            90,
            (110, 120, 130, 140),
            (150, 160, 170, 180),
        )

        self.assertEqual((60, 70, 80, 90), midpoint.rgbw)

    def test_invalid_configured_colour_falls_back_to_deep_red(self) -> None:
        profile = SOLAR.calculate_solar_profile(
            360, 360, 1200, 90, 2, [999, "bad"], None
        )

        self.assertEqual(SOLAR.DAWN_DUSK_RGBW, profile.rgbw)

    def test_sunrise_can_be_shifted_later_by_hours(self) -> None:
        shifted = SOLAR.shift_sunrise_minute(355, 2.5)

        self.assertEqual(505, shifted)

    def test_sunrise_shift_is_limited_and_does_not_wrap_days(self) -> None:
        self.assertEqual(0, SOLAR.shift_sunrise_minute(300, -20))
        self.assertEqual(1439, SOLAR.shift_sunrise_minute(1200, 20))
        self.assertEqual(300, SOLAR.shift_sunrise_minute(300, "invalid"))

    def test_sunrise_and_sunset_durations_are_adjustable(self) -> None:
        sunrise_midpoint = SOLAR.calculate_solar_profile(
            420,
            360,
            1200,
            90,
            2,
            sunrise_duration_minutes=120,
            sunset_duration_minutes=30,
        )
        sunset_midpoint = SOLAR.calculate_solar_profile(
            1185,
            360,
            1200,
            90,
            2,
            sunrise_duration_minutes=120,
            sunset_duration_minutes=30,
        )

        self.assertEqual("sunrise", sunrise_midpoint.phase)
        self.assertAlmostEqual(25.75, sunrise_midpoint.base_pct)
        self.assertEqual("sunset", sunset_midpoint.phase)
        self.assertAlmostEqual(25.75, sunset_midpoint.base_pct)

    def test_transition_duration_is_clipped_to_safe_range(self) -> None:
        self.assertEqual(
            SOLAR.MIN_TRANSITION_DURATION_MINUTES,
            SOLAR.normalize_transition_duration(-20, 60),
        )
        self.assertEqual(
            SOLAR.MAX_TRANSITION_DURATION_MINUTES,
            SOLAR.normalize_transition_duration(999, 90),
        )
        self.assertEqual(60, SOLAR.normalize_transition_duration("invalid", 60))


if __name__ == "__main__":
    unittest.main()
