"""Electricity-price adjustment helpers."""
from __future__ import annotations

from typing import Any, Mapping, TypedDict


class PriceAdjustment(TypedDict):
    """Normalized result of the electricity-price calculation."""

    factor: float
    load: float
    raw_load: float
    reference: float | None
    ceiling: float | None
    strategy: str


class BatteryPriority(TypedDict):
    """Normalized battery-priority decision."""

    active: bool
    charge_surplus: bool
    charging_power: float | None
    discharging_power: float | None
    full: bool
    net_charging_power: float | None


PRICE_RESPONSE_EXPONENT = 0.65
BATTERY_BRIGHTNESS_BOOST_PCT = 15.0


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_number(attributes: Mapping[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = _as_float(attributes.get(key))
        if value is not None:
            return value
    return None


def _generic_price_window(unit: str) -> tuple[float, float]:
    """Return conservative high-price thresholds for sensors without statistics."""
    normalized = unit.casefold().replace(" ", "")
    if "mwh" in normalized:
        return 250.0, 450.0
    if "ct/" in normalized or "cent/" in normalized:
        return 25.0, 45.0
    return 0.25, 0.45


def calculate_price_adjustment(
    price: float | None,
    attributes: Mapping[str, Any],
    dimming_pct: float,
) -> PriceAdjustment:
    """Calculate dimming only for prices in the expensive part of the day.

    Daily average and maximum attributes are preferred because they adapt to
    the configured tariff and currency. The configured dimming percentage is
    reached at the daily maximum. Ranking and unit-aware fixed thresholds keep
    generic price sensors useful when daily statistics are unavailable.
    """
    if price is None:
        return {
            "factor": 1.0,
            "load": 0.0,
            "raw_load": 0.0,
            "reference": None,
            "ceiling": None,
            "strategy": "unavailable",
        }

    dim_strength = _clamp(float(dimming_pct) / 100, 0, 0.9)
    average = _first_number(attributes, "avg_price", "average_price", "average", "mean")
    maximum = _first_number(attributes, "max_price", "maximum_price", "maximum", "max")
    minimum = _first_number(attributes, "min_price", "minimum_price", "minimum", "min")
    ranking = _first_number(attributes, "intraday_price_ranking", "price_ranking", "ranking")

    reference: float
    ceiling: float
    strategy: str
    if average is not None and maximum is not None and maximum > average:
        reference = average
        ceiling = maximum
        strategy = "daily_average_to_maximum"
        raw_load = _clamp((price - reference) / (ceiling - reference), 0, 1)
    elif minimum is not None and maximum is not None and maximum > minimum:
        reference = minimum + ((maximum - minimum) / 2)
        ceiling = maximum
        strategy = "daily_midpoint_to_maximum"
        raw_load = _clamp((price - reference) / (ceiling - reference), 0, 1)
    elif ranking is not None:
        reference = 0.5
        ceiling = 1.0
        strategy = "intraday_ranking"
        raw_load = _clamp((ranking - reference) / (ceiling - reference), 0, 1)
    else:
        reference, ceiling = _generic_price_window(str(attributes.get("unit_of_measurement") or ""))
        strategy = "unit_threshold"
        raw_load = _clamp((price - reference) / (ceiling - reference), 0, 1)

    # Values just above the daily average must already be visible. The curve
    # stays continuous and still reaches the configured maximum at the daily
    # high, but reacts more strongly than the previous linear response.
    load = raw_load ** PRICE_RESPONSE_EXPONENT

    return {
        "factor": _clamp(1 - (load * dim_strength), 0.1, 1),
        "load": load,
        "raw_load": raw_load,
        "reference": reference,
        "ceiling": ceiling,
        "strategy": strategy,
    }


def is_battery_full(soc: float | None, threshold: float) -> bool:
    """Return whether a storage battery has reached its full threshold."""
    if soc is None:
        return False
    return soc >= _clamp(float(threshold), 50, 100)


def calculate_battery_priority(
    soc: float | None,
    threshold: float,
    charging_power: float | None,
    discharging_power: float | None,
) -> BatteryPriority:
    """Enable battery priority only while PV charging exceeds discharging."""
    charge = _as_float(charging_power)
    discharge = _as_float(discharging_power)
    charge_surplus = (
        charge is not None
        and discharge is not None
        and charge > discharge
    )
    full = is_battery_full(soc, threshold)
    return {
        "active": full and charge_surplus,
        "charge_surplus": charge_surplus,
        "charging_power": charge,
        "discharging_power": discharge,
        "full": full,
        "net_charging_power": (
            charge - discharge
            if charge is not None and discharge is not None
            else None
        ),
    }


def calculate_battery_brightness_factor(
    priority_active: bool,
    boost_pct: float = BATTERY_BRIGHTNESS_BOOST_PCT,
) -> float:
    """Return the daylight brightness multiplier for a high battery SOC."""
    if not priority_active:
        return 1.0
    return 1.0 + (_clamp(float(boost_pct), 0, 50) / 100)


def apply_battery_brightness_boost(
    brightness_pct: float,
    maximum_pct: float,
    priority_active: bool,
    boost_pct: float = BATTERY_BRIGHTNESS_BOOST_PCT,
) -> float:
    """Apply the high-SOC bonus without exceeding the configured day maximum."""
    factor = calculate_battery_brightness_factor(priority_active, boost_pct)
    return _clamp(float(brightness_pct) * factor, 0, float(maximum_pct))
