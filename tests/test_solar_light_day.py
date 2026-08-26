"""Tests for the shared light-day shift and the transition fit."""

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

# Loaded straight from the file so the pure maths stays testable without a
# Home Assistant install; dataclasses need the module registered first.
_spec = importlib.util.spec_from_file_location("aquarium_solar", MODULE_PATH)
solar = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = solar
_spec.loader.exec_module(solar)


# Real Berlin sun window for late August: 06:10 and 20:07.
SUNRISE = 370
SUNSET = 1207


class ShiftLightDayTests(unittest.TestCase):
    """Both ends of the light day move together."""

    def test_shift_keeps_the_day_length(self) -> None:
        sunrise, sunset, applied = solar.shift_light_day(SUNRISE, SUNSET, 2)

        self.assertEqual(sunrise, SUNRISE + 120)
        self.assertEqual(sunset, SUNSET + 120)
        self.assertEqual(sunset - sunrise, SUNSET - SUNRISE)
        self.assertEqual(applied, 2)

    def test_negative_shift_moves_both_ends_earlier(self) -> None:
        sunrise, sunset, applied = solar.shift_light_day(SUNRISE, SUNSET, -1.5)

        self.assertEqual(sunrise, SUNRISE - 90)
        self.assertEqual(sunset, SUNSET - 90)
        self.assertEqual(applied, -1.5)

    def test_zero_offset_is_the_untouched_sun_window(self) -> None:
        self.assertEqual(
            solar.shift_light_day(SUNRISE, SUNSET, 0),
            (SUNRISE, SUNSET, 0),
        )

    def test_late_shift_stops_at_midnight_without_wrapping(self) -> None:
        sunrise, sunset, applied = solar.shift_light_day(SUNRISE, SUNSET, 6)

        self.assertEqual(sunset, 1439)
        self.assertEqual(sunset - sunrise, SUNSET - SUNRISE)
        self.assertLess(applied, 6)
        self.assertAlmostEqual(applied, (1439 - SUNSET) / 60)

    def test_early_shift_stops_at_midnight_without_wrapping(self) -> None:
        sunrise, sunset, applied = solar.shift_light_day(120, 1000, -6)

        self.assertEqual(sunrise, 0)
        self.assertEqual(sunset, 1000 - 120)
        self.assertAlmostEqual(applied, -2)

    def test_offset_outside_the_slider_range_is_normalised(self) -> None:
        self.assertEqual(
            solar.shift_light_day(600, 700, 99),
            solar.shift_light_day(600, 700, solar.MAX_DAY_OFFSET_HOURS),
        )

    def test_unreadable_offset_falls_back_to_no_shift(self) -> None:
        self.assertEqual(
            solar.shift_light_day(SUNRISE, SUNSET, "spaeter"),
            (SUNRISE, SUNSET, 0),
        )


class FitTransitionDurationsTests(unittest.TestCase):
    """Dawn and dusk never eat the whole light day."""

    def test_a_long_day_keeps_the_configured_durations(self) -> None:
        self.assertEqual(
            solar.fit_transition_durations(SUNRISE, SUNSET, 160, 165),
            (160, 165),
        )

    def test_overlapping_ramps_are_compressed_proportionally(self) -> None:
        sunrise_duration, sunset_duration = solar.fit_transition_durations(
            600,
            700,
            160,
            165,
        )

        span = 700 - 600
        self.assertLessEqual(
            sunrise_duration + sunset_duration,
            span - solar.MIN_DAYLIGHT_MINUTES,
        )
        self.assertGreater(sunrise_duration, 0)
        self.assertGreater(sunset_duration, 0)
        # The dusk ramp stays the longer one, as configured.
        self.assertGreater(sunset_duration, sunrise_duration)

    def test_daylight_survives_a_short_winter_day(self) -> None:
        # 08:15 to 16:15 with both ramps at their 240 minute maximum.
        sunrise_minute, sunset_minute = 495, 975
        sunrise_duration, sunset_duration = solar.fit_transition_durations(
            sunrise_minute,
            sunset_minute,
            240,
            240,
        )

        self.assertLess(
            sunrise_minute + sunrise_duration,
            sunset_minute - sunset_duration,
        )


class SolarProfileDaylightTests(unittest.TestCase):
    """The day phase survives every reachable slider combination."""

    def test_day_phase_exists_on_a_heavily_ramped_short_day(self) -> None:
        sunrise_minute, sunset_minute = 600, 700
        phases = {
            solar.calculate_solar_profile(
                minute,
                sunrise_minute,
                sunset_minute,
                90,
                3,
                sunrise_duration_minutes=160,
                sunset_duration_minutes=165,
            ).phase
            for minute in range(sunrise_minute, sunset_minute)
        }

        self.assertIn("day", phases)
        self.assertIn("sunrise", phases)
        self.assertIn("sunset", phases)

    def test_shifted_day_is_the_unshifted_day_moved_in_time(self) -> None:
        """A shifted light day must reproduce the original curve exactly."""
        sunrise, sunset, applied = solar.shift_light_day(SUNRISE, SUNSET, 2)
        shifted_peak = solar.MIDDAY_PEAK_MINUTE + int(round(applied * 60))

        for offset_minute in (5, 200, 600, 830):
            with self.subTest(offset_minute=offset_minute):
                shifted = solar.calculate_solar_profile(
                    sunrise + offset_minute,
                    sunrise,
                    sunset,
                    90,
                    3,
                    sunrise_duration_minutes=160,
                    sunset_duration_minutes=165,
                    midday_peak_minute=shifted_peak,
                )
                plain = solar.calculate_solar_profile(
                    SUNRISE + offset_minute,
                    SUNRISE,
                    SUNSET,
                    90,
                    3,
                    sunrise_duration_minutes=160,
                    sunset_duration_minutes=165,
                )
                self.assertEqual(shifted.phase, plain.phase)
                self.assertAlmostEqual(shifted.base_pct, plain.base_pct, places=6)

    def test_peak_stays_inside_a_shifted_window(self) -> None:
        """A fixed 12:00 peak would fall outside a strongly shifted day."""
        sunrise, sunset, applied = solar.shift_light_day(SUNRISE, SUNSET, 6)
        shifted_peak = solar.MIDDAY_PEAK_MINUTE + int(round(applied * 60))
        sunrise_end = sunrise + 160
        sunset_start = sunset - 165

        self.assertLess(solar.MIDDAY_PEAK_MINUTE, sunrise_end)
        self.assertGreaterEqual(shifted_peak, sunrise_end)
        self.assertLessEqual(shifted_peak, sunset_start)

        brightest = max(
            range(sunrise_end, sunset_start),
            key=lambda minute: solar.calculate_daylight_brightness(
                minute,
                sunrise_end,
                sunset_start,
                90,
                shifted_peak,
            ),
        )
        self.assertEqual(brightest, shifted_peak)


if __name__ == "__main__":
    unittest.main()
