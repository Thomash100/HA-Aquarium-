"""File export helpers for Aquarium LED Cockpit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from shutil import copy2
from typing import Any

from homeassistant.core import HomeAssistant

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


def _build_install_plan(
    hass: HomeAssistant,
    *,
    install_blueprint: bool,
    export_dashboard_snippets: bool,
    export_legacy_files: bool,
) -> list[InstallItem]:
    config_root = Path(hass.config.path())
    items: list[InstallItem] = [
        InstallItem(
            key="readme",
            source=RESOURCE_ROOT / "README.txt",
            target=config_root / EXPORT_FOLDER / "README.txt",
            description="Installation notes",
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
                description="Aquarium LED automation blueprint",
            )
        )

    if install_blueprint or export_dashboard_snippets:
        items.append(
            InstallItem(
                key="dashboard_controls_package",
                source=RESOURCE_ROOT / "packages" / "aquarium_led_cockpit_controls.yaml",
                target=config_root / "packages" / "aquarium_led_cockpit_controls.yaml",
                description="Dashboard control helper package",
            )
        )

    if export_dashboard_snippets:
        dashboard_root = config_root / EXPORT_FOLDER / "dashboard"
        items.extend(
            [
                InstallItem(
                    key="dashboard_markdown",
                    source=RESOURCE_ROOT / "dashboards" / "aquarium_led_status_sensor.yaml",
                    target=dashboard_root / "aquarium_led_status_sensor.yaml",
                    description="Dashboard markdown card",
                ),
                InstallItem(
                    key="dashboard_cockpit",
                    source=(
                        RESOURCE_ROOT
                        / "dashboards"
                        / "aquarium_led_cockpit_visual_button_card_sensor.yaml"
                    ),
                    target=dashboard_root / "aquarium_led_cockpit_visual_button_card_sensor.yaml",
                    description="Visual cockpit dashboard card",
                ),
                InstallItem(
                    key="dashboard_panel",
                    source=RESOURCE_ROOT / "dashboards" / "aquarium_led_technikpanel_sensor.yaml",
                    target=dashboard_root / "aquarium_led_technikpanel_sensor.yaml",
                    description="Technical panel dashboard card",
                ),
                InstallItem(
                    key="dashboard_controls",
                    source=RESOURCE_ROOT / "dashboards" / "aquarium_led_controls_panel.yaml",
                    target=dashboard_root / "aquarium_led_controls_panel.yaml",
                    description="Dashboard controls panel",
                ),
                InstallItem(
                    key="dashboard_power_price_24h",
                    source=RESOURCE_ROOT / "dashboards" / "aquarium_led_power_price_24h.yaml",
                    target=dashboard_root / "aquarium_led_power_price_24h.yaml",
                    description="24h power and Tibber price chart",
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
                    description="Legacy input_text helper package",
                ),
                InstallItem(
                    key="legacy_markdown",
                    source=RESOURCE_ROOT / "legacy" / "aquarium_led_status_markdown_legacy.yaml",
                    target=legacy_root / "aquarium_led_status_markdown_legacy.yaml",
                    description="Legacy markdown dashboard card",
                ),
                InstallItem(
                    key="legacy_cockpit",
                    source=RESOURCE_ROOT / "legacy" / "aquarium_led_cockpit_visual_button_card_legacy.yaml",
                    target=legacy_root / "aquarium_led_cockpit_visual_button_card_legacy.yaml",
                    description="Legacy visual cockpit card",
                ),
                InstallItem(
                    key="legacy_panel",
                    source=RESOURCE_ROOT / "legacy" / "aquarium_led_technikpanel_legacy.yaml",
                    target=legacy_root / "aquarium_led_technikpanel_legacy.yaml",
                    description="Legacy technical panel card",
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
) -> list[dict[str, Any]]:
    """Copy packaged resources into the Home Assistant config directory."""
    plan = _build_install_plan(
        hass,
        install_blueprint=install_blueprint,
        export_dashboard_snippets=export_dashboard_snippets,
        export_legacy_files=export_legacy_files,
    )
    return await hass.async_add_executor_job(_copy_plan, plan, overwrite_existing)
