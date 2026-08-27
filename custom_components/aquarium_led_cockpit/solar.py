"""Pure solar lighting profile calculations."""
from __future__ import annotations

from dataclasses import dataclass
from math import pi, sin


SUNRISE_DURATION_MINUTES = 60
SUNSET_DURATION_MINUTES = 90
MIN_TRANSITION_DURATION_MINUTES = 10
MAX_TRANSITION_DURATION_MINUTES = 240
MIN_DAY_OFFSET_HOURS = -6.0
MAX_DAY_OFFSET_HOURS = 6.0
MINUTES_PER_DAY = 1440
MIN_DAYLIGHT_MINUTES = 10

DAWN_DUSK_RGBW = (255, 0, 0, 0)
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
MIDDAY_PEAK_MINUTE = 12 * 60
DAY_EDGE_BRIGHTNESS_FACTOR = 0.55
DAY_CLOUD_SIMULATION_COVERAGE = 0.25
DAY_CLOUD_WEATHER_WEIGHT = 0.30
DAY_CLOUD_WAVE_STRENGTH = 0.60
SOLAR_ENERGY_MIN_FACTOR = 0.30
SOLAR_ENERGY_SOC_FLOOR = 20.0
SOLAR_ENERGY_SOC_TARGET = 90.0
DEFAULT_WHITE_CHANNEL_LEVEL = 100.0


@dataclass(frozen=True)
class SolarProfile:
    """Calculated solar phase, brightness and RGBW colour."""

    phase: str
    progress: float
    base_pct: float
    rgbw: tuple[int, int, int, int]


@dataclass(frozen=True)
class SolarEnergyAdjustment:
    """Daylight factor derived from current PV coverage and battery SOC."""

    available: bool
    factor: float
    pv_coverage: float
    soc_support: float
    support: float


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def normalize_white_channel_level(value: object) -> float:
    """Return a valid per-channel share of the RGBW white component."""
    try:
        level = float(value)
    except (TypeError, ValueError):
        level = DEFAULT_WHITE_CHANNEL_LEVEL
    return _clamp(level, 0, 100)


def calculate_white_channel_targets(
    white_pct: float,
    levels_pct: list[object] | tuple[object, ...],
    channel_count: int,
) -> tuple[int, ...]:
    """Scale the RGBW white component independently for each white output."""
    base = _clamp(float(white_pct), 0, 100)
    targets: list[int] = []
    for index in range(max(0, int(channel_count))):
        level = normalize_white_channel_level(
            levels_pct[index]
            if index < len(levels_pct)
            else DEFAULT_WHITE_CHANNEL_LEVEL
        )
        targets.append(int(round(base * (level / 100))))
    return tuple(targets)


def calculate_solar_energy_adjustment(
    solar_power: float | None,
    output_power: float | None,
    battery_soc: float | None,
) -> SolarEnergyAdjustment:
    """Scale daylight from 30-100% using PV/output coverage and battery SOC.

    PV coverage and stored energy have equal weight. A missing input fails open
    at 100 percent so a temporarily unavailable sensor cannot darken the tank.
    """
    if solar_power is None or output_power is None or battery_soc is None:
        return SolarEnergyAdjustment(
            available=False,
            factor=1.0,
            pv_coverage=1.0,
            soc_support=1.0,
            support=1.0,
        )

    solar = max(0.0, float(solar_power))
    output = max(0.0, float(output_power))
    soc = _clamp(float(battery_soc), 0, 100)
    pv_coverage = _clamp(solar / output, 0, 1) if output > 0 and solar > 0 else 0.0
    soc_support = _clamp(
        (soc - SOLAR_ENERGY_SOC_FLOOR)
        / (SOLAR_ENERGY_SOC_TARGET - SOLAR_ENERGY_SOC_FLOOR),
        0,
        1,
    )
    support = (pv_coverage + soc_support) / 2
    factor = SOLAR_ENERGY_MIN_FACTOR + (
        (1 - SOLAR_ENERGY_MIN_FACTOR) * support
    )
    return SolarEnergyAdjustment(
        available=True,
        factor=factor,
        pv_coverage=pv_coverage,
        soc_support=soc_support,
        support=support,
    )


def normalize_day_offset(value: object) -> float:
    """Return a valid user-selectable light-day shift in hours."""
    try:
        offset = float(value)
    except (TypeError, ValueError):
        offset = 0.0
    return _clamp(offset, MIN_DAY_OFFSET_HOURS, MAX_DAY_OFFSET_HOURS)


def light_day_span(sunrise_minute: int, sunset_minute: int) -> int:
    """Return the length of the light day, valid across midnight.

    A light day that ends on the following calendar day is a normal case
    once the whole day is shifted, so the distance is measured forward from
    sunrise instead of subtracting clock values. Sunrise equal to sunset is
    read as a sun that never sets.
    """
    span = (int(sunset_minute) - int(sunrise_minute)) % MINUTES_PER_DAY
    return span or MINUTES_PER_DAY


def shift_light_day(
    sunrise_minute: int,
    sunset_minute: int,
    offset_hours: object,
) -> tuple[int, int, float]:
    """Move sunrise and sunset together, across midnight where needed.

    Both ends keep their distance, so the shift never changes the length of
    the light day. The applied shift is returned in hours; it always equals
    the requested one, because the phase logic works on a time axis relative
    to sunrise and therefore does not care where the day sits on the clock.
    """
    applied = int(round(normalize_day_offset(offset_hours) * 60))
    sunrise = (int(sunrise_minute) + applied) % MINUTES_PER_DAY
    sunset = (int(sunset_minute) + applied) % MINUTES_PER_DAY
    return sunrise, sunset, applied / 60


def fit_transition_durations(
    sunrise_minute: int,
    sunset_minute: int,
    sunrise_duration: int,
    sunset_duration: int,
) -> tuple[int, int]:
    """Shrink dawn and dusk proportionally so daylight always survives.

    Without this the dusk ramp can start before the dawn ramp has finished
    on a short light day, which drops the day phase entirely and jumps the
    tank from dawn straight into a part-finished sunset.
    """
    sunrise = int(sunrise_duration)
    sunset = int(sunset_duration)
    span = light_day_span(sunrise_minute, sunset_minute)
    total = sunrise + sunset
    if total <= 0:
        return sunrise, sunset

    budget = span - MIN_DAYLIGHT_MINUTES
    if total <= budget:
        return sunrise, sunset
    if budget < 2:
        half = max(1, span // 2)
        return half, max(1, span - half)

    fitted_sunrise = max(1, int(round(budget * sunrise / total)))
    fitted_sunset = max(1, budget - fitted_sunrise)
    return fitted_sunrise, fitted_sunset


def normalize_transition_duration(value: object, default: int) -> int:
    """Return a valid user-selectable dawn or dusk duration in minutes."""
    try:
        duration = int(round(float(value)))
    except (TypeError, ValueError):
        duration = int(default)
    return int(
        _clamp(
            duration,
            MIN_TRANSITION_DURATION_MINUTES,
            MAX_TRANSITION_DURATION_MINUTES,
        )
    )


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


def calculate_daylight_brightness(
    minute: int,
    sunrise_end: int,
    sunset_start: int,
    day_brightness_pct: float,
    midday_peak_minute: int = MIDDAY_PEAK_MINUTE,
) -> float:
    """Return a smooth daytime arc peaking at the light day's midday.

    All four minute values must share one frame. calculate_solar_profile
    passes minutes elapsed since sunrise, which keeps the comparisons
    ordered even when the light day runs past midnight; the 12:00 default
    belongs to the plain clock frame.
    """
    maximum = _clamp(float(day_brightness_pct), 1, 100)
    edge = maximum * DAY_EDGE_BRIGHTNESS_FACTOR
    if sunset_start <= sunrise_end:
        return maximum

    peak = int(_clamp(midday_peak_minute, sunrise_end, sunset_start))
    if minute <= peak:
        span = max(1, peak - sunrise_end)
        progress = _clamp((minute - sunrise_end) / span, 0, 1)
    else:
        span = max(1, sunset_start - peak)
        progress = _clamp((sunset_start - minute) / span, 0, 1)
    shaped = sin(progress * pi / 2)
    return edge + ((maximum - edge) * shaped)


def calculate_daylight_cloud_factors(
    cloudiness: float,
    cloud_strength: float,
    cloud_wave: float,
) -> tuple[float, float, float]:
    """Return stronger weather, cloud-wave, and effective cloud factors."""
    actual = _clamp(float(cloudiness), 0, 1)
    strength = _clamp(float(cloud_strength), 0, 1)
    wave = _clamp(float(cloud_wave), 0, 1)
    effective_cloudiness = _clamp(
        actual + (strength * DAY_CLOUD_SIMULATION_COVERAGE),
        0,
        1,
    )
    weather_factor = _clamp(
        1 - (effective_cloudiness * DAY_CLOUD_WEATHER_WEIGHT),
        0.5,
        1,
    )
    cloud_factor = _clamp(
        1
        - (
            effective_cloudiness
            * strength
            * (0.25 + (0.75 * wave))
            * DAY_CLOUD_WAVE_STRENGTH
        ),
        0.35,
        1,
    )
    return weather_factor, cloud_factor, effective_cloudiness


def calculate_solar_profile(
    minute: int,
    sunrise_minute: int,
    sunset_minute: int,
    day_brightness_pct: float,
    night_brightness_pct: float,
    sunrise_rgbw: object = DAWN_DUSK_RGBW,
    sunset_rgbw: object = DAWN_DUSK_RGBW,
    sunrise_duration_minutes: object = SUNRISE_DURATION_MINUTES,
    sunset_duration_minutes: object = SUNSET_DURATION_MINUTES,
    sunrise_end_rgbw: object = DAYLIGHT_RGBW,
    sunset_start_rgbw: object = DAYLIGHT_RGBW,
    midday_peak_minute: int = MIDDAY_PEAK_MINUTE,
) -> SolarProfile:
    """Return the profile for the given sunrise and sunset event minutes.

    Everything is measured forward from sunrise rather than against the
    clock, so a light day that runs past midnight is an ordinary case and
    needs no special handling.

    Each transition interpolates every RGBW channel linearly between its two
    configurable endpoints. The daytime colour moves smoothly from the end of
    sunrise to the start of sunset. The following night uses cool moonlight.
    """
    minute %= MINUTES_PER_DAY
    sunrise_minute %= MINUTES_PER_DAY
    sunset_minute %= MINUTES_PER_DAY
    sunrise_duration = normalize_transition_duration(
        sunrise_duration_minutes,
        SUNRISE_DURATION_MINUTES,
    )
    sunset_duration = normalize_transition_duration(
        sunset_duration_minutes,
        SUNSET_DURATION_MINUTES,
    )
    sunrise_duration, sunset_duration = fit_transition_durations(
        sunrise_minute,
        sunset_minute,
        sunrise_duration,
        sunset_duration,
    )
    # Zeitachse relativ zum Lichtaufgang: 0 ist der Aufgang, span das Ende.
    span = light_day_span(sunrise_minute, sunset_minute)
    elapsed = (minute - sunrise_minute) % MINUTES_PER_DAY
    peak_elapsed = (midday_peak_minute - sunrise_minute) % MINUTES_PER_DAY
    sunrise_end = sunrise_duration
    sunset_start = span - sunset_duration
    sunrise_start_color = normalize_rgbw(sunrise_rgbw)
    sunrise_end_color = normalize_rgbw(sunrise_end_rgbw, DAYLIGHT_RGBW)
    sunset_start_color = normalize_rgbw(sunset_start_rgbw, DAYLIGHT_RGBW)
    sunset_end_color = normalize_rgbw(sunset_rgbw)
    day_edge_pct = float(day_brightness_pct) * DAY_EDGE_BRIGHTNESS_FACTOR

    if elapsed < sunrise_end:
        phase = "sunrise"
        progress = _clamp(
            elapsed / sunrise_duration,
            0,
            1,
        )
        base_pct = night_brightness_pct + (
            (day_edge_pct - night_brightness_pct) * progress
        )
        rgbw = _interpolate_rgbw(
            sunrise_start_color,
            sunrise_end_color,
            progress,
        )
    elif elapsed < sunset_start:
        phase = "day"
        progress = _clamp(
            (elapsed - sunrise_end) / max(1, sunset_start - sunrise_end),
            0,
            1,
        )
        base_pct = calculate_daylight_brightness(
            elapsed,
            sunrise_end,
            sunset_start,
            day_brightness_pct,
            peak_elapsed,
        )
        rgbw = _interpolate_rgbw(
            sunrise_end_color,
            sunset_start_color,
            progress,
        )
    elif elapsed < span:
        phase = "sunset"
        progress = _clamp(
            (elapsed - sunset_start) / sunset_duration,
            0,
            1,
        )
        base_pct = day_edge_pct + (
            (night_brightness_pct - day_edge_pct) * progress
        )
        rgbw = _interpolate_rgbw(
            sunset_start_color,
            sunset_end_color,
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
