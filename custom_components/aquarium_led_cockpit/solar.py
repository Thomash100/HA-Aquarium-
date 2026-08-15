"""Pure solar lighting profile calculations."""
from __future__ import annotations

from dataclasses import dataclass


SUNRISE_DURATION_MINUTES = 60
SUNSET_DURATION_MINUTES = 90

DAWN_DUSK_RGBW = (255, 0, 0, 0)
ORANGE_RGBW = (255, 45, 0, 0)
GOLD_RGBW = (255, 135, 20, 10)
WARM_WHITE_RGBW = (255, 190, 100, 140)
DAYLIGHT_RGBW = (190, 220, 255, 255)
MOONLIGHT_RGBW = (0, 10, 90, 0)

SUNRISE_RGBW_STOPS = (
    (0.00, DAWN_DUSK_RGBW),
    (0.22, ORANGE_RGBW),
    (0.55, GOLD_RGBW),
    (0.82, WARM_WHITE_RGBW),
    (1.00, DAYLIGHT_RGBW),
)
SUNSET_RGBW_STOPS = tuple(
    (round(1 - progress, 2), color)
    for progress, color in reversed(SUNRISE_RGBW_STOPS)
)


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


def _interpolate_rgbw_stops(
    stops: tuple[tuple[float, tuple[int, int, int, int]], ...],
    progress: float,
) -> tuple[int, int, int, int]:
    """Interpolate a colour on a multi-stop RGBW palette."""
    progress = _clamp(progress, 0, 1)
    for index in range(1, len(stops)):
        start_progress, start_color = stops[index - 1]
        end_progress, end_color = stops[index]
        if progress <= end_progress:
            segment = (progress - start_progress) / (end_progress - start_progress)
            return _interpolate_rgbw(start_color, end_color, segment)
    return stops[-1][1]


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
        rgbw = _interpolate_rgbw_stops(SUNRISE_RGBW_STOPS, progress)
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
        rgbw = _interpolate_rgbw_stops(SUNSET_RGBW_STOPS, progress)
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
