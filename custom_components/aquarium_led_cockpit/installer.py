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
    export_frontend_resources: bool,
) -> list[InstallItem]:
    config_root = Path(hass.config.path())
    items: list[InstallItem] = [
        InstallItem(
            key="readme",
            source=RESOURCE_ROOT / "README.txt",
            target=config_root / EXPORT_FOLDER / "README.txt",
            description="Installationshinweise",
        )
    ]

    if export_frontend_resources:
        items.append(
            InstallItem(
                key="frontend_simulator_card",
                source=RESOURCE_ROOT / "frontend" / "aquarium-led-simulator-card.js",
                target=config_root / "www" / EXPORT_FOLDER / "aquarium-led-simulator-card.js",
                description="Lovelace-Simulator-Karte",
            )
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
    export_frontend_resources: bool,
    overwrite_existing: bool,
) -> list[dict[str, Any]]:
    """Copy packaged resources into the Home Assistant config directory."""
    plan = _build_install_plan(
        hass,
        export_frontend_resources=export_frontend_resources,
    )
    return await hass.async_add_executor_job(_copy_plan, plan, overwrite_existing)
