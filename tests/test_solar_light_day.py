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

    def test_late_shift_runs_past_midnight(self) -> None:
        """+6 h must be applied in full, even though sunset lands next day."""
        sunrise, sunset, applied = solar.shift_light_day(SUNRISE, SUNSET, 6)

        self.assertEqual(applied, 6)
        self.assertEqual(sunrise, SUNRISE + 360)
        self.assertEqual(sunset, (SUNSET + 360) % 1440)
        self.assertLess(sunset, sunrise)
        self.assertEqual(solar.light_day_span(sunrise, sunset), SUNSET - SUNRISE)

    def test_early_shift_runs_past_midnight(self) -> None:
        sunrise, sunset, applied = solar.shift_light_day(120, 1000, -6)

        self.assertEqual(applied, -6)
        self.assertEqual(sunrise, 1440 + 120 - 360)
        self.assertEqual(sunset, 1000 - 360)
        self.assertEqual(solar.light_day_span(sunrise, sunset), 880)

    def test_span_survives_every_offset(self) -> None:
        for offset in (-6, -4.25, -1, 0, 1, 3.5, 6):
            with self.subTest(offset=offset):
                sunrise, sunset, _ = solar.shift_light_day(SUNRISE, SUNSET, offset)
                self.assertEqual(
                    solar.light_day_span(sunrise, sunset),
                    SUNSET - SUNRISE,
                )

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

    def test_peak_keeps_its_place_in_a_shifted_day(self) -> None:
        """The peak must sit as far into the light day as solar noon does."""
        noon_offset = (solar.MIDDAY_PEAK_MINUTE - SUNRISE) % 1440
        sunrise_end, sunset_start = 160, (SUNSET - SUNRISE) - 165

        brightest = max(
            range(sunrise_end, sunset_start),
            key=lambda elapsed: solar.calculate_daylight_brightness(
                elapsed,
                sunrise_end,
                sunset_start,
                90,
                noon_offset,
            ),
        )
        self.assertEqual(brightest, noon_offset)

    def test_a_light_day_past_midnight_runs_through_every_phase(self) -> None:
        """The whole point of the shift: light after midnight, not clipped."""
        sunrise, sunset, _ = solar.shift_light_day(SUNRISE, SUNSET, 6)
        span = solar.light_day_span(sunrise, sunset)
        seen = []
        for elapsed in range(0, 1440):
            profile = solar.calculate_solar_profile(
                (sunrise + elapsed) % 1440,
                sunrise,
                sunset,
                90,
                3,
                sunrise_duration_minutes=160,
                sunset_duration_minutes=165,
            )
            if not seen or seen[-1][0] != profile.phase:
                seen.append((profile.phase, elapsed))

        self.assertEqual([entry[0] for entry in seen], ["sunrise", "day", "sunset", "night"])
        self.assertEqual(seen[1][1], 160)
        self.assertEqual(seen[2][1], span - 165)
        self.assertEqual(seen[3][1], span)

    def test_shifted_day_matches_the_unshifted_one_minute_for_minute(self) -> None:
        """A shift may move the day on the clock, never reshape it."""
        sunrise, sunset, _ = solar.shift_light_day(SUNRISE, SUNSET, 6)
        noon_offset = (solar.MIDDAY_PEAK_MINUTE - SUNRISE) % 1440

        for elapsed in range(0, 1440, 7):
            with self.subTest(elapsed=elapsed):
                shifted = solar.calculate_solar_profile(
                    (sunrise + elapsed) % 1440,
                    sunrise,
                    sunset,
                    90,
                    3,
                    sunrise_duration_minutes=160,
                    sunset_duration_minutes=165,
                    midday_peak_minute=(sunrise + noon_offset) % 1440,
                )
                plain = solar.calculate_solar_profile(
                    (SUNRISE + elapsed) % 1440,
                    SUNRISE,
                    SUNSET,
                    90,
                    3,
                    sunrise_duration_minutes=160,
                    sunset_duration_minutes=165,
                )
                self.assertEqual(shifted.phase, plain.phase)
                self.assertAlmostEqual(shifted.base_pct, plain.base_pct, places=6)
                self.assertEqual(shifted.rgbw, plain.rgbw)


if __name__ == "__main__":
    unittest.main()
