"""Lighting calculation helpers for Aquarium LED Cockpit."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import sin, tau
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import (
    CONF_BATTERY_FULL_THRESHOLD,
    CONF_BATTERY_SOC_ENTITY,
    CONF_PRICE_ENTITY,
    CONF_SOLAR_POWER_ENTITY,
    CONF_SUN_ENTITY,
    CONF_WEATHER_ENTITY,
    CONTROL_AQUARIUM_PREVIEW,
    CONTROL_CLOUD_STRENGTH,
    CONTROL_DAY_BRIGHTNESS,
    CONTROL_NIGHT_BRIGHTNESS,
    CONTROL_PRICE_DIMMING,
    CONTROL_SIMULATION,
    CONTROL_SIMULATION_TIME,
    CONTROL_TIME_LAPSE_DURATION,
    CONTROL_TIME_LAPSE,
    DEFAULT_CLOUD_STRENGTH,
    DEFAULT_BATTERY_FULL_THRESHOLD,
    DEFAULT_DAY_BRIGHTNESS,
    DEFAULT_NIGHT_BRIGHTNESS,
    DEFAULT_PRICE_DIMMING,
    DEFAULT_SIMULATION_TIME,
    DEFAULT_SUN_ENTITY,
)
from .price import calculate_price_adjustment, is_battery_full
from .solar import (
    SUNRISE_DURATION_MINUTES,
    SUNSET_DURATION_MINUTES,
    calculate_solar_profile,
)
from .time_lapse import MINUTES_PER_DAY, normalize_time_lapse_duration


@dataclass(frozen=True)
class AquariumLightTarget:
    """Calculated light target."""

    status: dict[str, Any]
    brightness_pct: int
    rgbw: tuple[int, int, int, int]


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _parse_minutes(value: Any, default: int) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _minutes_to_clock(minutes: int) -> str:
    wrapped = minutes % 1440
    return f"{wrapped // 60:02d}:{wrapped % 60:02d}"


def _price_state(hass: HomeAssistant, entity_id: str | None) -> tuple[float | None, dict[str, Any]]:
    if not entity_id:
        return None, {}
    state = hass.states.get(entity_id)
    if state is None:
        return None, {}
    try:
        return float(state.state), dict(state.attributes)
    except (TypeError, ValueError):
        return None, dict(state.attributes)


def _number_state(hass: HomeAssistant, entity_id: str | None) -> float | None:
    if not entity_id:
        return None
    state = hass.states.get(entity_id)
    if state is None:
        return None
    try:
        return float(state.state)
    except (TypeError, ValueError):
        return None


def _regional_sun(hass: HomeAssistant, entity_id: str | None) -> bool:
    if not entity_id:
        return False
    state = hass.states.get(entity_id)
    return state is not None and str(state.state).lower() in {"sunny", "partlycloudy"}


def _weather_cloudiness(hass: HomeAssistant, entity_id: str | None) -> float:
    if not entity_id:
        return 0.2
    state = hass.states.get(entity_id)
    if state is None:
        return 0.2

    coverage = state.attributes.get("cloud_coverage")
    try:
        return _clamp(float(coverage) / 100, 0, 1)
    except (TypeError, ValueError):
        pass

    state_name = str(state.state).lower()
    if state_name in {"sunny", "clear-night"}:
        return 0
    if state_name in {"partlycloudy", "windy", "windy-variant"}:
        return 0.35
    if state_name in {"cloudy", "fog", "hail"}:
        return 0.65
    if state_name in {"rainy", "pouring", "snowy", "snowy-rainy", "lightning", "lightning-rainy"}:
        return 0.85
    return 0.2


def _sun_window(hass: HomeAssistant, entity_id: str, today: datetime) -> tuple[int, int]:
    state = hass.states.get(entity_id)
    if state is None:
        return 360, 1080

    def attr_minutes(name: str, fallback: int) -> int:
        value = state.attributes.get(name)
        if value is None:
            return fallback
        if isinstance(value, str):
            parsed = dt_util.parse_datetime(value)
            if parsed is None:
                return fallback
            value_dt = dt_util.as_local(parsed)
        else:
            value_dt = dt_util.as_local(value)
        if value_dt.date() > today.date():
            value_dt = value_dt - timedelta(days=1)
        return value_dt.hour * 60 + value_dt.minute

    sunrise = attr_minutes("next_rising", 360)
    sunset = attr_minutes("next_setting", 1080)
    return sunrise, sunset


def calculate_target(
    hass: HomeAssistant,
    settings: dict[str, Any],
    controls: dict[str, Any],
    *,
    now: datetime | None = None,
) -> AquariumLightTarget:
    """Calculate the current aquarium light target."""
    now = now or dt_util.now()
    time_lapse = bool(controls.get(CONTROL_TIME_LAPSE, False))
    simulation = bool(controls.get(CONTROL_SIMULATION, False) or time_lapse)
    time_lapse_duration = normalize_time_lapse_duration(
        controls.get(CONTROL_TIME_LAPSE_DURATION)
    )
    minute = (
        _parse_minutes(controls.get(CONTROL_SIMULATION_TIME), DEFAULT_SIMULATION_TIME) % 1440
        if time_lapse
        else now.hour * 60 + now.minute
    )

    sunrise_start, sunset_event = _sun_window(
        hass,
        str(settings.get(CONF_SUN_ENTITY) or DEFAULT_SUN_ENTITY),
        now,
    )
    day = _clamp(float(controls.get(CONTROL_DAY_BRIGHTNESS, DEFAULT_DAY_BRIGHTNESS)), 1, 100)
    night = _clamp(float(controls.get(CONTROL_NIGHT_BRIGHTNESS, DEFAULT_NIGHT_BRIGHTNESS)), 0, 30)
    solar_profile = calculate_solar_profile(
        minute,
        sunrise_start,
        sunset_event,
        day,
        night,
    )
    phase = solar_profile.phase
    base_pct = solar_profile.base_pct

    price_value, price_attributes = _price_state(hass, settings.get(CONF_PRICE_ENTITY))
    price_adjustment = calculate_price_adjustment(
        price_value,
        price_attributes,
        float(controls.get(CONTROL_PRICE_DIMMING, DEFAULT_PRICE_DIMMING)),
    )
    battery_soc = _number_state(hass, settings.get(CONF_BATTERY_SOC_ENTITY))
    battery_full_threshold = float(
        settings.get(CONF_BATTERY_FULL_THRESHOLD, DEFAULT_BATTERY_FULL_THRESHOLD)
    )
    battery_full = is_battery_full(battery_soc, battery_full_threshold)
    price_ignored = phase == "night" or battery_full
    price_factor = 1.0 if price_ignored else price_adjustment["factor"]
    price_strategy = "battery_full_override" if battery_full else price_adjustment["strategy"]
    solar_power = _number_state(hass, settings.get(CONF_SOLAR_POWER_ENTITY))
    regional_sun = _regional_sun(hass, settings.get(CONF_WEATHER_ENTITY))

    cloudiness = _weather_cloudiness(hass, settings.get(CONF_WEATHER_ENTITY))
    cloud_strength = _clamp(float(controls.get(CONTROL_CLOUD_STRENGTH, DEFAULT_CLOUD_STRENGTH)) / 100, 0, 1)
    weather_factor = 1 if phase == "night" else _clamp(1 - (cloudiness * 0.2), 0.5, 1)
    wave = (sin((minute / 1440) * tau * 8) + 1) / 2
    cloud_factor = 1 if phase == "night" else _clamp(1 - (cloudiness * cloud_strength * wave * 0.25), 0.4, 1)

    brightness = int(round(_clamp(base_pct * price_factor * weather_factor * cloud_factor, 0, 100)))
    rgbw = solar_profile.rgbw

    status = {
        "phase": phase,
        "time": _minutes_to_clock(minute),
        "time_lapse": time_lapse,
        "simulation": simulation,
        "aquarium_preview": bool(controls.get(CONTROL_AQUARIUM_PREVIEW, False)),
        "time_lapse_duration_minutes": time_lapse_duration,
        "time_lapse_speed_minutes_per_second": round(
            MINUTES_PER_DAY / (time_lapse_duration * 60),
            2,
        ),
        "sunrise": _minutes_to_clock(sunrise_start),
        "sunrise_duration_minutes": SUNRISE_DURATION_MINUTES,
        "sunrise_end": _minutes_to_clock(sunrise_start + SUNRISE_DURATION_MINUTES),
        "sunset": _minutes_to_clock(sunset_event),
        "sunset_duration_minutes": SUNSET_DURATION_MINUTES,
        "sunset_phase_start": _minutes_to_clock(sunset_event - SUNSET_DURATION_MINUTES),
        "light_mode": "moonlight" if phase == "night" else phase,
        "color_control": "rgbw",
        "day_brightness_pct": round(day, 1),
        "night_brightness_pct": round(night, 1),
        "base_pct": round(base_pct, 1),
        "target_pct": brightness,
        "white_pct": int(round(brightness * (rgbw[3] / 255))),
        "rgbw": list(rgbw),
        "price": price_value if price_value is not None else "-",
        "price_entity": settings.get(CONF_PRICE_ENTITY) or "",
        "price_factor": round(price_factor, 3),
        "price_load_pct": int(round(price_adjustment["load"] * 100)),
        "price_dimming_pct": int(round((1 - price_factor) * 100)),
        "price_reference": price_adjustment["reference"] if price_adjustment["reference"] is not None else "-",
        "price_ceiling": price_adjustment["ceiling"] if price_adjustment["ceiling"] is not None else "-",
        "price_strategy": price_strategy,
        "price_ignored": price_ignored,
        "price_ignored_reason": "battery_full" if battery_full else ("night" if phase == "night" else "-"),
        "battery_soc": battery_soc if battery_soc is not None else "-",
        "battery_soc_entity": settings.get(CONF_BATTERY_SOC_ENTITY) or "",
        "battery_full_threshold": round(battery_full_threshold, 1),
        "battery_full": battery_full,
        "solar_power": solar_power if solar_power is not None else "-",
        "solar_power_entity": settings.get(CONF_SOLAR_POWER_ENTITY) or "",
        "regional_sun": regional_sun,
        "weather": hass.states.get(settings.get(CONF_WEATHER_ENTITY)).state
        if settings.get(CONF_WEATHER_ENTITY) and hass.states.get(settings.get(CONF_WEATHER_ENTITY))
        else "-",
        "cloudiness_pct": int(round(cloudiness * 100)),
        "weather_factor": round(weather_factor, 3),
        "cloud_factor": round(cloud_factor, 3),
        "updated": now.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return AquariumLightTarget(status=status, brightness_pct=brightness, rgbw=rgbw)
