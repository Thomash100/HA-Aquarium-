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

    def test_time_lapse_duration_is_adjustable_in_the_card(self) -> None:
        source = RESOURCE.read_text(encoding="utf-8")

        self.assertIn("time_lapse_duration_number", source)
        self.assertIn("24-Stunden-Dauer", source)
        self.assertIn('max="10"', source)
        self.assertIn('callService("number", "set_value"', source)

    def test_physical_preview_requires_confirmation(self) -> None:
        source = RESOURCE.read_text(encoding="utf-8")

        self.assertIn("aquarium_preview_switch", source)
        self.assertIn("Am Aquarium zeigen", source)
        self.assertIn("window.confirm", source)
        self.assertIn("stellt den vorherigen Lichtzustand wieder her", source)

    def test_day_band_uses_sun_arc_and_home_assistant_moon_phase(self) -> None:
        source = RESOURCE.read_text(encoding="utf-8")

        self.assertIn("celestialGeometry", source)
        self.assertIn("alc-sun-arc", source)
        self.assertIn("alc-moon-arc", source)
        self.assertIn("moon_phase_label", source)

    def test_transition_colours_are_editable_as_rgbw(self) -> None:
        source = RESOURCE.read_text(encoding="utf-8")

        self.assertIn('type="color"', source)
        self.assertIn("data-white-picker", source)
        self.assertIn('callService("aquarium_led_cockpit", "set_transition_color"', source)
        self.assertIn("Pause: Nacht", source)
        self.assertIn("Pause: Speicher voll", source)

    def test_continuous_moonlight_factors_are_visible(self) -> None:
        source = RESOURCE.read_text(encoding="utf-8")

        self.assertIn("moon_phase_brightness_pct", source)
        self.assertIn("moon_cloud_dimming_pct", source)
        self.assertIn('this.metric("Mondlicht"', source)
        self.assertIn('this.metric("Mond-Wolken"', source)


if __name__ == "__main__":
    unittest.main()
