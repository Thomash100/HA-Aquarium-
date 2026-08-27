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
        # Die Kurve rechnet relativ zum Lichtaufgang, damit ein Lichttag ueber
        # Mitternacht dieselbe Form behaelt wie im Python-Profil.
        self.assertIn("const sunsetStart = span - sunsetDuration", source)
        self.assertIn("const elapsed = (((minute - sunrise) % 1440) + 1440) % 1440", source)
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

        self.assertIn("data-rgbw-channel", source)
        self.assertIn('data-phase="${endpoint}"', source)
        self.assertIn('`${phase}_start`', source)
        self.assertIn('`${phase}_end`', source)
        self.assertIn("alc-channel-r", source)
        self.assertIn("alc-channel-w", source)
        self.assertIn('callService("aquarium_led_cockpit", "set_transition_color"', source)
        self.assertIn("Pause: Nacht", source)
        self.assertIn("Pause: Speicher voll", source)
        self.assertIn("Pause: PV-Überschuss", source)

    def test_continuous_moonlight_factors_are_visible(self) -> None:
        source = RESOURCE.read_text(encoding="utf-8")

        self.assertIn("moon_phase_brightness_pct", source)
        self.assertIn("moon_cloud_dimming_pct", source)
        self.assertIn('this.metric("Mondlicht"', source)
        self.assertIn('this.metric("Mond-Wolken"', source)

    def test_light_day_offset_is_adjustable_and_shows_real_time(self) -> None:
        source = RESOURCE.read_text(encoding="utf-8")

        self.assertIn("day_offset_number", source)
        # Dashboards written before the rename keep working.
        self.assertIn("sunrise_offset_number", source)
        self.assertIn("sunrise_actual", source)
        self.assertIn("celestial_sunset", source)
        self.assertIn("Lichttag verschieben", source)
        self.assertIn('data-day-offset=', source)
        self.assertIn("data-day-offset-delta", source)
        self.assertIn('type="number"', source)
        self.assertIn('step="0.25"', source)
        self.assertIn(
            "celestialGeometry(currentTime, sunriseActual, sunsetActual)",
            source,
        )
        self.assertIn("Verschiebt Aufgang und Untergang gemeinsam", source)
        self.assertIn("die echte Sonnenbahn bleibt fest", source)

    def test_two_separate_white_channels_are_adjustable(self) -> None:
        source = RESOURCE.read_text(encoding="utf-8")

        self.assertIn("white_channel_1_number", source)
        self.assertIn("white_channel_2_number", source)
        self.assertIn("white_channel_targets_pct", source)
        self.assertIn("Separate Weiss-LED-Kanaele", source)
        self.assertIn("data-white-channel-level", source)
        self.assertIn("data-white-level-delta", source)

    def test_intensity_curve_is_separate_and_shows_all_effects(self) -> None:
        source = RESOURCE.read_text(encoding="utf-8")

        self.assertIn('viewBox="0 0 720 190"', source)
        self.assertIn("alc-effect-chart", source)
        self.assertIn("buildIntensityProjection", source)
        self.assertIn("Grundprofil", source)
        self.assertIn("Preisfaktor", source)
        self.assertIn("Wolkenfaktor", source)
        self.assertIn("PV-/SOC-Faktor", source)
        self.assertIn("Akku-SOC", source)
        self.assertIn("midday_peak_minute", source)
        self.assertIn("price_response_exponent", source)
        self.assertIn("cloud_simulation_coverage", source)
        self.assertIn("battery_charge_surplus", source)
        self.assertIn("solar_energy_factor", source)
        self.assertIn("solarEnergyFactorAt", source)
        self.assertIn("Lichtausgänge", source)
        self.assertIn("Laden &gt; Entladen", source)
        self.assertIn("alc-effect-noon", source)
        self.assertNotIn("alc-intensity-panel", source)

    def test_transition_durations_are_adjustable_in_the_card(self) -> None:
        source = RESOURCE.read_text(encoding="utf-8")

        self.assertIn("sunrise_duration_number", source)
        self.assertIn("sunset_duration_number", source)
        self.assertIn("data-transition-duration", source)
        self.assertIn('max="240"', source)
        self.assertIn('step="5"', source)
        self.assertIn("data-duration-delta", source)
        self.assertIn('type="number"', source)


if __name__ == "__main__":
    unittest.main()
