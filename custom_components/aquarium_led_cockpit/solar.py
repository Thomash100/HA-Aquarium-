"""Pure solar lighting profile calculations."""
from __future__ import annotations

from dataclasses import dataclass


SUNRISE_DURATION_MINUTES = 60
SUNSET_DURATION_MINUTES = 90
MIN_SUNRISE_OFFSET_HOURS = -6.0
MAX_SUNRISE_OFFSET_HOURS = 6.0

DAWN_DUSK_RGBW = (255, 0, 0, 0)
ORANGE_RGBW = (255, 45, 0, 0)
GOLD_RGBW = (255, 135, 20, 10)
WARM_WHITE_RGBW = (255, 190, 100, 140)
DAYLIGHT_RGBW = (190, 220, 255, 255)
MOONLIGHT_RGBW = (0, 10, 90, 0)
MIN_MOONLIGHT_BRIGHTNESS_PCT = 1.0
MOON_PHASE_LIGHT_FACTORS = {
    "new_moon": 0.25,
    "waxing_crescent": 0.45,
    "first_quarter": 0.65,
    "waxing_gibbous": 0.85,
    "full_moon": 1.0,
    "waning_gibbous": 0.85,
    "last_quarter": 0.65,
    "waning_crescent": 0.45,
}
DEFAULT_MOON_PHASE_LIGHT_FACTOR = 0.6


@dataclass(frozen=True)
class SolarProfile:
    """Calculated solar phase, brightness and RGBW colour."""

    phase: str
    progress: float
    base_pct: float
    rgbw: tuple[int, int, int, int]


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def normalize_sunrise_offset(value: object) -> float:
    """Return a valid user-selectable sunrise shift in hours."""
    try:
        offset = float(value)
    except (TypeError, ValueError):
        offset = 0.0
    return _clamp(offset, MIN_SUNRISE_OFFSET_HOURS, MAX_SUNRISE_OFFSET_HOURS)


def shift_sunrise_minute(sunrise_minute: int, offset_hours: object) -> int:
    """Shift sunrise without wrapping into the previous or following day."""
    shifted = int(
        round(
            int(sunrise_minute)
            + (normalize_sunrise_offset(offset_hours) * 60)
        )
    )
    return int(_clamp(shifted, 0, 1439))


def _interpolate_rgbw(
    color_from: tuple[int, int, int, int],
    color_to: tuple[int, int, int, int],
    progress: float,
) -> tuple[int, int, int, int]:
    return tuple(
        int(round(color_from[index] + ((color_to[index] - color_from[index]) * progress)))
        for index in range(4)
    )


def normalize_rgbw(
    value: object,
    fallback: tuple[int, int, int, int] = DAWN_DUSK_RGBW,
) -> tuple[int, int, int, int]:
    """Return a validated RGBW tuple with channels clipped to 0-255."""
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return fallback
    try:
        return tuple(int(round(_clamp(float(channel), 0, 255))) for channel in value)
    except (TypeError, ValueError):
        return fallback


def moon_phase_light_factor(moon_phase: object) -> float:
    """Return the visible moonlight share for a Home Assistant moon phase."""
    return MOON_PHASE_LIGHT_FACTORS.get(
        str(moon_phase),
        DEFAULT_MOON_PHASE_LIGHT_FACTOR,
    )


def calculate_moonlight_target(
    night_brightness_pct: float,
    moon_phase: object,
    cloudiness: float,
    cloud_strength: float,
    cloud_wave: float,
) -> tuple[float, float, float]:
    """Return continuous moonlight brightness plus moon and cloud factors.

    The configured night brightness is the full-moon ceiling. Clouds reduce
    it smoothly, while the one-percent floor keeps the RGBW moonlight on for
    the whole night, including new moon and dense cloud cover.
    """
    configured = _clamp(float(night_brightness_pct), 1, 30)
    phase_factor = moon_phase_light_factor(moon_phase)
    cloud_amount = _clamp(float(cloudiness), 0, 1)
    strength = _clamp(float(cloud_strength), 0, 1)
    wave = _clamp(float(cloud_wave), 0, 1)
    cloud_factor = _clamp(
        1 - (cloud_amount * strength * (0.25 + (0.75 * wave)) * 0.55),
        0.35,
        1,
    )
    target = max(
        MIN_MOONLIGHT_BRIGHTNESS_PCT,
        configured * phase_factor * cloud_factor,
    )
    return target, phase_factor, cloud_factor


def _tinted_color(
    base: tuple[int, int, int, int],
    endpoint: tuple[int, int, int, int],
    influence: float,
) -> tuple[int, int, int, int]:
    """Tint a warm palette colour towards a configurable endpoint."""
    return tuple(
        int(round(_clamp(base[index] + ((endpoint[index] - DAWN_DUSK_RGBW[index]) * influence), 0, 255)))
        for index in range(4)
    )


def build_transition_stops(
    endpoint: object,
    *,
    reverse: bool = False,
) -> tuple[tuple[float, tuple[int, int, int, int]], ...]:
    """Build the warm RGBW path for one configurable dawn/dusk endpoint."""
    endpoint_rgbw = normalize_rgbw(endpoint)
    sunrise_stops = (
        (0.00, endpoint_rgbw),
        (0.22, _tinted_color(ORANGE_RGBW, endpoint_rgbw, 0.55)),
        (0.55, _tinted_color(GOLD_RGBW, endpoint_rgbw, 0.25)),
        (0.82, _tinted_color(WARM_WHITE_RGBW, endpoint_rgbw, 0.10)),
        (1.00, DAYLIGHT_RGBW),
    )
    if not reverse:
        return sunrise_stops
    return tuple(
        (round(1 - progress, 2), color)
        for progress, color in reversed(sunrise_stops)
    )


SUNRISE_RGBW_STOPS = build_transition_stops(DAWN_DUSK_RGBW)
SUNSET_RGBW_STOPS = build_transition_stops(DAWN_DUSK_RGBW, reverse=True)


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
    sunrise_rgbw: object = DAWN_DUSK_RGBW,
    sunset_rgbw: object = DAWN_DUSK_RGBW,
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
        rgbw = _interpolate_rgbw_stops(
            build_transition_stops(sunrise_rgbw),
            progress,
        )
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
        rgbw = _interpolate_rgbw_stops(
            build_transition_stops(sunset_rgbw, reverse=True),
            progress,
        )
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
