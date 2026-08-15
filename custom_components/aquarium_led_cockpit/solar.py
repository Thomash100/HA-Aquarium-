"""Pure solar lighting profile calculations."""
from __future__ import annotations

from dataclasses import dataclass


SUNRISE_DURATION_MINUTES = 60
SUNSET_DURATION_MINUTES = 90

DAWN_DUSK_RGBW = (255, 42, 12, 0)
DAYLIGHT_RGBW = (190, 220, 255, 255)
MOONLIGHT_RGBW = (15, 30, 90, 70)


@dataclass(frozen=True)
class SolarProfile:
    """Calculated solar phase, brightness and RGBW colour."""

    phase: str
    progress: float
    base_pct: float
    rgbw: tuple[int, int, int, int]


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _interpolate_rgbw(
    color_from: tuple[int, int, int, int],
    color_to: tuple[int, int, int, int],
    progress: float,
) -> tuple[int, int, int, int]:
    return tuple(
        int(round(color_from[index] + ((color_to[index] - color_from[index]) * progress)))
        for index in range(4)
    )


def calculate_solar_profile(
    minute: int,
    sunrise_minute: int,
    sunset_minute: int,
    day_brightness_pct: float,
    night_brightness_pct: float,
) -> SolarProfile:
    """Return the profile for real sunrise and sunset event minutes.

    Sunrise begins at the actual event and reaches daylight after one hour.
    Sunset begins 90 minutes before the actual event and reaches deep red at
    the event. The following night uses a greatly reduced cool moonlight.
    """
    minute %= 1440
    sunrise_minute %= 1440
    sunset_minute %= 1440
    sunrise_end = sunrise_minute + SUNRISE_DURATION_MINUTES
    sunset_start = sunset_minute - SUNSET_DURATION_MINUTES

    if sunrise_minute <= minute < sunrise_end:
        phase = "sunrise"
        progress = _clamp(
            (minute - sunrise_minute) / SUNRISE_DURATION_MINUTES,
            0,
            1,
        )
        base_pct = night_brightness_pct + (
            (day_brightness_pct - night_brightness_pct) * progress
        )
        rgbw = _interpolate_rgbw(DAWN_DUSK_RGBW, DAYLIGHT_RGBW, progress)
    elif sunrise_end <= minute < sunset_start:
        phase = "day"
        progress = 1
        base_pct = day_brightness_pct
        rgbw = DAYLIGHT_RGBW
    elif sunset_start <= minute < sunset_minute:
        phase = "sunset"
        progress = _clamp(
            (minute - sunset_start) / SUNSET_DURATION_MINUTES,
            0,
            1,
        )
        base_pct = day_brightness_pct + (
            (night_brightness_pct - day_brightness_pct) * progress
        )
        rgbw = _interpolate_rgbw(DAYLIGHT_RGBW, DAWN_DUSK_RGBW, progress)
    else:
        phase = "night"
        progress = 0
        base_pct = night_brightness_pct
        rgbw = MOONLIGHT_RGBW

    return SolarProfile(
        phase=phase,
        progress=progress,
        base_pct=base_pct,
        rgbw=rgbw,
    )
