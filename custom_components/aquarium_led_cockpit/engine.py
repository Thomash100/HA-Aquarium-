"""Lighting calculation helpers for Aquarium LED Cockpit."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import sin, tau
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import (
    CONF_BATTERY_CHARGING_POWER_ENTITY,
    CONF_BATTERY_DISCHARGE_POWER_ENTITY,
    CONF_BATTERY_FULL_THRESHOLD,
    CONF_BATTERY_SOC_ENTITY,
    CONF_MOON_ENTITY,
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
    CONTROL_SUNRISE_DURATION,
    CONTROL_SUNRISE_END_RGBW,
    CONTROL_SUNRISE_OFFSET,
    CONTROL_SUNRISE_RGBW,
    CONTROL_SUNSET_START_RGBW,
    CONTROL_SUNSET_RGBW,
    CONTROL_SUNSET_DURATION,
    CONTROL_TIME_LAPSE_DURATION,
    CONTROL_TIME_LAPSE,
    DEFAULT_CLOUD_STRENGTH,
    DEFAULT_BATTERY_FULL_THRESHOLD,
    DEFAULT_DAY_BRIGHTNESS,
    DEFAULT_NIGHT_BRIGHTNESS,
    DEFAULT_MOON_ENTITY,
    DEFAULT_PRICE_DIMMING,
    DEFAULT_SIMULATION_TIME,
    DEFAULT_SUNRISE_DURATION_MINUTES,
    DEFAULT_SUNRISE_OFFSET_HOURS,
    DEFAULT_SUNSET_DURATION_MINUTES,
    DEFAULT_SUN_ENTITY,
)
from .price import (
    BATTERY_BRIGHTNESS_BOOST_PCT,
    PRICE_RESPONSE_EXPONENT,
    apply_battery_brightness_boost,
    calculate_battery_brightness_factor,
    calculate_battery_priority,
    calculate_price_adjustment,
)
from .solar import (
    DAWN_DUSK_RGBW,
    DAY_CLOUD_SIMULATION_COVERAGE,
    DAY_CLOUD_WAVE_STRENGTH,
    DAY_CLOUD_WEATHER_WEIGHT,
    DAY_EDGE_BRIGHTNESS_FACTOR,
    DAYLIGHT_RGBW,
    MIDDAY_PEAK_MINUTE,
    MIN_MOONLIGHT_BRIGHTNESS_PCT,
    calculate_moonlight_target,
    calculate_daylight_cloud_factors,
    calculate_solar_profile,
    normalize_rgbw,
    normalize_sunrise_offset,
    normalize_transition_duration,
    shift_sunrise_minute,
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


MOON_PHASES = {
    "new_moon": ("Neumond", "🌑"),
    "waxing_crescent": ("Zunehmende Sichel", "🌒"),
    "first_quarter": ("Erstes Viertel", "🌓"),
    "waxing_gibbous": ("Zunehmender Mond", "🌔"),
    "full_moon": ("Vollmond", "🌕"),
    "waning_gibbous": ("Abnehmender Mond", "🌖"),
    "last_quarter": ("Letztes Viertel", "🌗"),
    "waning_crescent": ("Abnehmende Sichel", "🌘"),
}


def _moon_phase(hass: HomeAssistant, entity_id: str | None) -> tuple[str, str, str]:
    """Return raw phase, German label, and symbol from Home Assistant."""
    state = hass.states.get(entity_id) if entity_id else None
    raw = str(state.state) if state is not None else "unknown"
    label, icon = MOON_PHASES.get(raw, ("Mondphase unbekannt", "🌙"))
    return raw, label, icon


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

    sunrise_actual, sunset_event = _sun_window(
        hass,
        str(settings.get(CONF_SUN_ENTITY) or DEFAULT_SUN_ENTITY),
        now,
    )
    sunrise_offset_hours = normalize_sunrise_offset(
        controls.get(CONTROL_SUNRISE_OFFSET, DEFAULT_SUNRISE_OFFSET_HOURS)
    )
    sunrise_start = shift_sunrise_minute(sunrise_actual, sunrise_offset_hours)
    sunrise_duration = normalize_transition_duration(
        controls.get(CONTROL_SUNRISE_DURATION),
        DEFAULT_SUNRISE_DURATION_MINUTES,
    )
    sunset_duration = normalize_transition_duration(
        controls.get(CONTROL_SUNSET_DURATION),
        DEFAULT_SUNSET_DURATION_MINUTES,
    )
    day = _clamp(float(controls.get(CONTROL_DAY_BRIGHTNESS, DEFAULT_DAY_BRIGHTNESS)), 1, 100)
    night = _clamp(float(controls.get(CONTROL_NIGHT_BRIGHTNESS, DEFAULT_NIGHT_BRIGHTNESS)), 1, 30)
    solar_profile = calculate_solar_profile(
        minute,
        sunrise_start,
        sunset_event,
        day,
        night,
        controls.get(CONTROL_SUNRISE_RGBW, DAWN_DUSK_RGBW),
        controls.get(CONTROL_SUNSET_RGBW, DAWN_DUSK_RGBW),
        sunrise_duration,
        sunset_duration,
        controls.get(CONTROL_SUNRISE_END_RGBW, DAYLIGHT_RGBW),
        controls.get(CONTROL_SUNSET_START_RGBW, DAYLIGHT_RGBW),
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
    battery_charging_power = _number_state(
        hass,
        settings.get(CONF_BATTERY_CHARGING_POWER_ENTITY),
    )
    battery_discharge_power = _number_state(
        hass,
        settings.get(CONF_BATTERY_DISCHARGE_POWER_ENTITY),
    )
    battery_priority = calculate_battery_priority(
        battery_soc,
        battery_full_threshold,
        battery_charging_power,
        battery_discharge_power,
    )
    battery_full = battery_priority["full"]
    battery_priority_active = phase != "night" and battery_priority["active"]
    battery_brightness_factor = calculate_battery_brightness_factor(
        battery_priority_active,
    )
    battery_boost_active = battery_priority_active
    price_ignored = phase == "night" or battery_priority_active
    price_factor = 1.0 if price_ignored else price_adjustment["factor"]
    price_strategy = (
        "battery_pv_surplus_override"
        if battery_priority_active
        else price_adjustment["strategy"]
    )
    solar_power = _number_state(hass, settings.get(CONF_SOLAR_POWER_ENTITY))
    regional_sun = _regional_sun(hass, settings.get(CONF_WEATHER_ENTITY))
    moon_phase, moon_phase_label, moon_phase_icon = _moon_phase(
        hass,
        str(settings.get(CONF_MOON_ENTITY) or DEFAULT_MOON_ENTITY),
    )

    cloudiness = _weather_cloudiness(hass, settings.get(CONF_WEATHER_ENTITY))
    cloud_strength = _clamp(float(controls.get(CONTROL_CLOUD_STRENGTH, DEFAULT_CLOUD_STRENGTH)) / 100, 0, 1)
    wave = (sin((minute / 1440) * tau * 8) + 1) / 2
    moonlight_target, moon_phase_factor, moon_cloud_factor = calculate_moonlight_target(
        night,
        moon_phase,
        cloudiness,
        cloud_strength,
        wave,
    )
    if phase == "night":
        weather_factor = 1
        cloud_factor = moon_cloud_factor
        brightness = max(
            int(MIN_MOONLIGHT_BRIGHTNESS_PCT),
            int(round(moonlight_target)),
        )
    else:
        weather_factor, cloud_factor, effective_cloudiness = (
            calculate_daylight_cloud_factors(
                cloudiness,
                cloud_strength,
                wave,
            )
        )
        brightness_without_boost = _clamp(
            base_pct * price_factor * weather_factor * cloud_factor,
            0,
            day,
        )
        brightness = int(
            round(
                apply_battery_brightness_boost(
                    brightness_without_boost,
                    day,
                    battery_priority_active,
                )
            )
        )
    if phase == "night":
        effective_cloudiness = cloudiness
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
        "sunrise_actual": _minutes_to_clock(sunrise_actual),
        "sunrise_offset_hours": sunrise_offset_hours,
        "sunrise_duration_minutes": sunrise_duration,
        "sunrise_end": _minutes_to_clock(sunrise_start + sunrise_duration),
        "sunset": _minutes_to_clock(sunset_event),
        "sunset_duration_minutes": sunset_duration,
        "sunset_phase_start": _minutes_to_clock(sunset_event - sunset_duration),
        "moonlight_start": _minutes_to_clock(sunset_event),
        "moonlight_end": _minutes_to_clock(sunrise_start),
        "light_mode": "moonlight" if phase == "night" else phase,
        "color_control": "rgbw",
        # The legacy names remain available to existing dashboard consumers.
        "sunrise_rgbw": list(normalize_rgbw(controls.get(CONTROL_SUNRISE_RGBW))),
        "sunrise_start_rgbw": list(normalize_rgbw(controls.get(CONTROL_SUNRISE_RGBW))),
        "sunrise_end_rgbw": list(
            normalize_rgbw(
                controls.get(CONTROL_SUNRISE_END_RGBW),
                DAYLIGHT_RGBW,
            )
        ),
        "sunset_start_rgbw": list(
            normalize_rgbw(
                controls.get(CONTROL_SUNSET_START_RGBW),
                DAYLIGHT_RGBW,
            )
        ),
        "sunset_rgbw": list(normalize_rgbw(controls.get(CONTROL_SUNSET_RGBW))),
        "sunset_end_rgbw": list(normalize_rgbw(controls.get(CONTROL_SUNSET_RGBW))),
        "moon_phase": moon_phase,
        "moon_phase_label": moon_phase_label,
        "moon_phase_icon": moon_phase_icon,
        "moon_phase_factor": round(moon_phase_factor, 3),
        "moon_phase_brightness_pct": int(round(moon_phase_factor * 100)),
        "moon_cloud_factor": round(moon_cloud_factor, 3),
        "moon_cloud_dimming_pct": int(round((1 - moon_cloud_factor) * 100)),
        "moonlight_target_pct": brightness if phase == "night" else "-",
        "moonlight_continuous": True,
        "day_brightness_pct": round(day, 1),
        "day_edge_brightness_factor": DAY_EDGE_BRIGHTNESS_FACTOR,
        "midday_peak_minute": MIDDAY_PEAK_MINUTE,
        "midday_peak_time": _minutes_to_clock(MIDDAY_PEAK_MINUTE),
        "night_brightness_pct": round(night, 1),
        "base_pct": round(base_pct, 1),
        "target_pct": brightness,
        "white_pct": int(round(brightness * (rgbw[3] / 255))),
        "rgbw": list(rgbw),
        "price": price_value if price_value is not None else "-",
        "price_entity": settings.get(CONF_PRICE_ENTITY) or "",
        "price_factor": round(price_factor, 3),
        "price_load_pct": int(round(price_adjustment["load"] * 100)),
        "price_raw_load_pct": int(round(price_adjustment["raw_load"] * 100)),
        "price_response_exponent": PRICE_RESPONSE_EXPONENT,
        "price_dimming_pct": int(round((1 - price_factor) * 100)),
        "price_dimming_max_pct": round(
            float(controls.get(CONTROL_PRICE_DIMMING, DEFAULT_PRICE_DIMMING)),
            1,
        ),
        "price_reference": price_adjustment["reference"] if price_adjustment["reference"] is not None else "-",
        "price_ceiling": price_adjustment["ceiling"] if price_adjustment["ceiling"] is not None else "-",
        "price_strategy": price_strategy,
        "price_ignored": price_ignored,
        "price_ignored_reason": (
            "battery_pv_surplus"
            if battery_priority_active
            else ("night" if phase == "night" else "-")
        ),
        "price_rule": (
            "pause_battery_pv_surplus"
            if battery_priority_active
            else ("pause_night" if phase == "night" else "active")
        ),
        "battery_soc": battery_soc if battery_soc is not None else "-",
        "battery_soc_entity": settings.get(CONF_BATTERY_SOC_ENTITY) or "",
        "battery_full_threshold": round(battery_full_threshold, 1),
        "battery_full": battery_full,
        "battery_charging_power": (
            battery_priority["charging_power"]
            if battery_priority["charging_power"] is not None
            else "-"
        ),
        "battery_charging_power_entity": (
            settings.get(CONF_BATTERY_CHARGING_POWER_ENTITY) or ""
        ),
        "battery_discharge_power": (
            battery_priority["discharging_power"]
            if battery_priority["discharging_power"] is not None
            else "-"
        ),
        "battery_discharge_power_entity": (
            settings.get(CONF_BATTERY_DISCHARGE_POWER_ENTITY) or ""
        ),
        "battery_net_charging_power": (
            round(battery_priority["net_charging_power"], 1)
            if battery_priority["net_charging_power"] is not None
            else "-"
        ),
        "battery_charge_surplus": battery_priority["charge_surplus"],
        "battery_priority_active": battery_priority_active,
        "battery_priority_blocked_reason": (
            "night"
            if phase == "night"
            else (
                "soc_below_threshold"
                if not battery_full
                else (
                    "power_unavailable"
                    if battery_priority["charging_power"] is None
                    or battery_priority["discharging_power"] is None
                    else (
                        "charging_not_greater_than_discharging"
                        if not battery_priority["charge_surplus"]
                        else "-"
                    )
                )
            )
        ),
        "battery_boost_active": battery_boost_active,
        "battery_brightness_boost_pct": BATTERY_BRIGHTNESS_BOOST_PCT,
        "battery_brightness_factor": round(
            battery_brightness_factor if battery_boost_active else 1.0,
            3,
        ),
        "battery_boost_added_pct": (
            max(0, brightness - int(round(brightness_without_boost)))
            if phase != "night"
            else 0
        ),
        "solar_power": solar_power if solar_power is not None else "-",
        "solar_power_entity": settings.get(CONF_SOLAR_POWER_ENTITY) or "",
        "regional_sun": regional_sun,
        "weather": hass.states.get(settings.get(CONF_WEATHER_ENTITY)).state
        if settings.get(CONF_WEATHER_ENTITY) and hass.states.get(settings.get(CONF_WEATHER_ENTITY))
        else "-",
        "cloudiness_pct": int(round(cloudiness * 100)),
        "effective_cloudiness_pct": int(round(effective_cloudiness * 100)),
        "cloud_strength_pct": int(round(cloud_strength * 100)),
        "cloud_simulation_coverage": DAY_CLOUD_SIMULATION_COVERAGE,
        "cloud_weather_weight": DAY_CLOUD_WEATHER_WEIGHT,
        "cloud_wave_strength": DAY_CLOUD_WAVE_STRENGTH,
        "weather_factor": round(weather_factor, 3),
        "cloud_factor": round(cloud_factor, 3),
        "updated": now.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return AquariumLightTarget(status=status, brightness_pct=brightness, rgbw=rgbw)
