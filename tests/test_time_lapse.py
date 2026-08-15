"""Tests for the configurable one-to-ten-minute day simulation."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


MODULE_PATH = (
    Path(__file__).parents[1]
    / "custom_components"
    / "aquarium_led_cockpit"
    / "time_lapse.py"
)
SPEC = importlib.util.spec_from_file_location("aquarium_led_time_lapse", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
TIME_LAPSE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = TIME_LAPSE
SPEC.loader.exec_module(TIME_LAPSE)


class TimeLapseTests(unittest.TestCase):
    """Verify full-day timing and duration limits."""

    def test_one_minute_cycle_advances_twenty_four_minutes_per_second(self) -> None:
        position = TIME_LAPSE.advance_time_lapse_position(0, 1, 1)

        self.assertEqual(24, position)

    def test_ten_minute_cycle_completes_after_six_hundred_seconds(self) -> None:
        halfway = TIME_LAPSE.advance_time_lapse_position(0, 300, 10)
        complete = TIME_LAPSE.advance_time_lapse_position(0, 600, 10)

        self.assertEqual(720, halfway)
        self.assertEqual(0, complete)

    def test_duration_is_limited_to_one_through_ten_minutes(self) -> None:
        self.assertEqual(1, TIME_LAPSE.normalize_time_lapse_duration(-4))
        self.assertEqual(8, TIME_LAPSE.normalize_time_lapse_duration(8))
        self.assertEqual(10, TIME_LAPSE.normalize_time_lapse_duration(120))
        self.assertEqual(1, TIME_LAPSE.normalize_time_lapse_duration("invalid"))

    def test_cycle_wraps_from_the_selected_simulation_time(self) -> None:
        position = TIME_LAPSE.advance_time_lapse_position(1430, 1, 1)

        self.assertEqual(14, position)


if __name__ == "__main__":
    unittest.main()
