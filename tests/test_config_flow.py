"""Compatibility tests for the Home Assistant options flow."""

from __future__ import annotations

import ast
from pathlib import Path
import unittest


CONFIG_FLOW = (
    Path(__file__).parents[1]
    / "custom_components"
    / "aquarium_led_cockpit"
    / "config_flow.py"
)


class OptionsFlowCompatibilityTests(unittest.TestCase):
    """Protect compatibility with Home Assistant's read-only property."""

    def test_config_entry_property_is_not_assigned(self) -> None:
        """The HA 2026.8 OptionsFlow config_entry property has no setter."""
        tree = ast.parse(CONFIG_FLOW.read_text(encoding="utf-8"))
        assigned_attributes = {
            target.attr
            for node in ast.walk(tree)
            if isinstance(node, (ast.Assign, ast.AnnAssign))
            for target in (
                node.targets if isinstance(node, ast.Assign) else [node.target]
            )
            if isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == "self"
        }

        self.assertNotIn("config_entry", assigned_attributes)
        self.assertIn("_config_entry", assigned_attributes)

    def test_battery_power_balance_entities_are_configurable(self) -> None:
        source = CONFIG_FLOW.read_text(encoding="utf-8")

        self.assertIn("CONF_BATTERY_CHARGING_POWER_ENTITY", source)
        self.assertIn("CONF_BATTERY_DISCHARGE_POWER_ENTITY", source)


if __name__ == "__main__":
    unittest.main()
