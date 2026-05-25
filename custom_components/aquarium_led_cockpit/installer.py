"""File export helpers for Aquarium LED Cockpit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from shutil import copy2
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util import slugify

from .const import DOMAIN

RESOURCE_ROOT = Path(__file__).parent / "resources"
EXPORT_FOLDER = DOMAIN


@dataclass(frozen=True)
class InstallItem:
    """A single file that can be exported into the Home Assistant config path."""

    key: str
    source: Path
    target: Path
    description: str
    replacements: dict[str, str] | None = None


def _dashboard_replacements(aquarium_name: str) -> dict[str, str]:
    """Build entity replacements for one aquarium dashboard export."""
    slug = slugify(aquarium_name or "Aquarium") or "aquarium"
    return {
        "sensor.aquarium_status": f"sensor.{slug}_status",
        "switch.aquarium_steuerung": f"switch.{slug}_steuerung",
        "switch.aquarium_simulation": f"switch.{slug}_simulation",
        "switch.aquarium_zeitraffer": f"switch.{slug}_zeitraffer",
        "number.aquarium_simulationszeit": f"number.{slug}_simulationszeit",
        "number.aquarium_zeitraffer_schritt": f"number.{slug}_zeitraffer_schritt",
        "number.aquarium_taghelligkeit": f"number.{slug}_taghelligkeit",
        "number.aquarium_nachtlicht": f"number.{slug}_nachtlicht",
        "number.aquarium_preisdimmung": f"number.{slug}_preisdimmung",
        "number.aquarium_wolkenstaerke": f"number.{slug}_wolkenstaerke",
    }


def _helper_replacements(aquarium_name: str) -> dict[str, str]:
    """Build helper replacements for one aquarium package export."""
    slug = slugify(aquarium_name or "Aquarium") or "aquarium"
    return {"aquarium_led_": f"{slug}_aquarium_led_"}


def _build_install_plan(
    hass: HomeAssistant,
    *,
    install_blueprint: bool,
    export_dashboard_snippets: bool,
    export_legacy_files: bool,
    aquarium_name: str,
) -> list[InstallItem]:
    config_root = Path(hass.config.path())
    aquarium_slug = slugify(aquarium_name or "Aquarium") or "aquarium"
    dashboard_replacements = _dashboard_replacements(aquarium_name)
    helper_replacements = _helper_replacements(aquarium_name)
    items: list[InstallItem] = [
        InstallItem(
            key="readme",
            source=RESOURCE_ROOT / "README.txt",
            target=config_root / EXPORT_FOLDER / "README.txt",
            description="Installationshinweise",
        )
    ]

    if install_blueprint:
        items.append(
            InstallItem(
                key="blueprint",
                source=(
                    RESOURCE_ROOT
                    / "blueprints"
                    / "automation"
                    / DOMAIN
                    / "aquarium_led_tibber_weather_shelly_rgbw.yaml"
                ),
                target=(
                    config_root
                    / "blueprints"
                    / "automation"
                    / DOMAIN
                    / "aquarium_led_tibber_weather_shelly_rgbw.yaml"
                ),
                description="Aquarium LED Automation-Blueprint",
            )
        )

    if install_blueprint or export_legacy_files:
        items.append(
            InstallItem(
                key="dashboard_controls_package",
                source=RESOURCE_ROOT / "packages" / "aquarium_led_cockpit_controls.yaml",
                target=config_root
                / "packages"
                / f"aquarium_led_cockpit_{aquarium_slug}_controls.yaml",
                description="Aquarium-spezifisches Steuerhelfer-Paket",
                replacements=helper_replacements,
            )
        )

    if export_dashboard_snippets:
        dashboard_root = config_root / EXPORT_FOLDER / "dashboard" / aquarium_slug
        items.extend(
            [
                InstallItem(
                    key="frontend_simulator_card",
                    source=RESOURCE_ROOT / "frontend" / "aquarium-led-simulator-card.js",
                    target=config_root / "www" / EXPORT_FOLDER / "aquarium-led-simulator-card.js",
                    description="Lovelace-Simulator-Karte",
                ),
                InstallItem(
                    key="dashboard_markdown",
                    source=RESOURCE_ROOT / "dashboards" / "aquarium_led_status_sensor.yaml",
                    target=dashboard_root / "aquarium_led_status_sensor.yaml",
                    description="Dashboard-Markdown-Karte",
                    replacements=dashboard_replacements,
                ),
                InstallItem(
                    key="dashboard_cockpit",
                    source=(
                        RESOURCE_ROOT
                        / "dashboards"
                        / "aquarium_led_cockpit_visual_button_card_sensor.yaml"
                    ),
                    target=dashboard_root / "aquarium_led_cockpit_visual_button_card_sensor.yaml",
                    description="Visuelle Cockpit-Dashboard-Karte",
                    replacements=dashboard_replacements,
                ),
                InstallItem(
                    key="dashboard_panel",
                    source=RESOURCE_ROOT / "dashboards" / "aquarium_led_technikpanel_sensor.yaml",
                    target=dashboard_root / "aquarium_led_technikpanel_sensor.yaml",
                    description="Technikpanel-Dashboard-Karte",
                    replacements=dashboard_replacements,
                ),
                InstallItem(
                    key="dashboard_controls",
                    source=RESOURCE_ROOT / "dashboards" / "aquarium_led_controls_panel.yaml",
                    target=dashboard_root / "aquarium_led_controls_panel.yaml",
                    description="Dashboard-Steuerpanel",
                    replacements=dashboard_replacements,
                ),
                InstallItem(
                    key="dashboard_power_price_24h",
                    source=RESOURCE_ROOT / "dashboards" / "aquarium_led_power_price_24h.yaml",
                    target=dashboard_root / "aquarium_led_power_price_24h.yaml",
                    description="24h-Status- und Preisverlauf",
                    replacements=dashboard_replacements,
                ),
                InstallItem(
                    key="dashboard_simulator_card",
                    source=RESOURCE_ROOT / "dashboards" / "aquarium_led_simulator_card.yaml",
                    target=dashboard_root / "aquarium_led_simulator_card.yaml",
                    description="Lovelace-Simulator-Kartenbeispiel",
                    replacements=dashboard_replacements,
                ),
            ]
        )

    if export_legacy_files:
        legacy_root = config_root / EXPORT_FOLDER / "legacy"
        items.extend(
            [
                InstallItem(
                    key="legacy_helper",
                    source=RESOURCE_ROOT / "legacy" / "aquarium_led_dashboard_status_helper.yaml",
                    target=config_root / "packages" / "aquarium_led_dashboard_status_helper.yaml",
                    description="Legacy-input_text-Helferpaket",
                ),
                InstallItem(
                    key="legacy_markdown",
                    source=RESOURCE_ROOT / "legacy" / "aquarium_led_status_markdown_legacy.yaml",
                    target=legacy_root / "aquarium_led_status_markdown_legacy.yaml",
                    description="Legacy-Markdown-Dashboard-Karte",
                ),
                InstallItem(
                    key="legacy_cockpit",
                    source=RESOURCE_ROOT / "legacy" / "aquarium_led_cockpit_visual_button_card_legacy.yaml",
                    target=legacy_root / "aquarium_led_cockpit_visual_button_card_legacy.yaml",
                    description="Legacy-Cockpit-Karte",
                ),
                InstallItem(
                    key="legacy_panel",
                    source=RESOURCE_ROOT / "legacy" / "aquarium_led_technikpanel_legacy.yaml",
                    target=legacy_root / "aquarium_led_technikpanel_legacy.yaml",
                    description="Legacy-Technikpanel-Karte",
                ),
            ]
        )

    return items


def _copy_plan(plan: list[InstallItem], overwrite_existing: bool) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    for item in plan:
        item.target.parent.mkdir(parents=True, exist_ok=True)

        if item.target.exists() and not overwrite_existing:
            results.append(
                {
                    "key": item.key,
                    "description": item.description,
                    "status": "skipped",
                    "target": str(item.target),
                }
            )
            continue

        status = "updated" if item.target.exists() else "created"
        if item.replacements:
            text = item.source.read_text(encoding="utf-8")
            for old, new in item.replacements.items():
                text = text.replace(old, new)
            item.target.write_text(text, encoding="utf-8")
        else:
            copy2(item.source, item.target)
        results.append(
            {
                "key": item.key,
                "description": item.description,
                "status": status,
                "target": str(item.target),
            }
        )

    return results


async def async_install_resources(
    hass: HomeAssistant,
    *,
    install_blueprint: bool,
    export_dashboard_snippets: bool,
    export_legacy_files: bool,
    overwrite_existing: bool,
    aquarium_name: str,
) -> list[dict[str, Any]]:
    """Copy packaged resources into the Home Assistant config directory."""
    plan = _build_install_plan(
        hass,
        install_blueprint=install_blueprint,
        export_dashboard_snippets=export_dashboard_snippets,
        export_legacy_files=export_legacy_files,
        aquarium_name=aquarium_name,
    )
    return await hass.async_add_executor_job(_copy_plan, plan, overwrite_existing)
