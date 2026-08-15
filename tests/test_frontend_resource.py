"""Regression tests for the Lovelace simulator resource."""

from __future__ import annotations

from pathlib import Path
import unittest


RESOURCE = (
    Path(__file__).parents[1]
    / "custom_components"
    / "aquarium_led_cockpit"
    / "resources"
    / "frontend"
    / "aquarium-led-simulator-card.js"
)


class FrontendResourceTests(unittest.TestCase):
    """Protect the real history and forecast data sources."""

    def test_energy_timelines_use_home_assistant_sources(self) -> None:
        source = RESOURCE.read_text(encoding="utf-8")

        self.assertIn('type: "history/history_during_period"', source)
        self.assertIn('service: "get_prices"', source)
        self.assertIn('domain: "tibber"', source)
        self.assertIn("Batterieverlauf", source)
        self.assertIn("Tibber-Vorschau", source)

    def test_light_curve_uses_real_event_windows(self) -> None:
        source = RESOURCE.read_text(encoding="utf-8")

        self.assertIn("sunrise_duration_minutes ?? 60", source)
        self.assertIn("sunset_duration_minutes ?? 90", source)
        self.assertIn("const sunsetStart = sunset - sunsetDuration", source)
        self.assertIn('night: "Mondlicht"', source)


if __name__ == "__main__":
    unittest.main()
