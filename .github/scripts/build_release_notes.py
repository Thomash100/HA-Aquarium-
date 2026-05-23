"""Build GitHub release notes from CHANGELOG.md."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _manifest_version() -> str:
    manifest = json.loads((ROOT / "custom_components/aquarium_led_cockpit/manifest.json").read_text())
    return str(manifest["version"])


def _extract_changelog(tag: str) -> str:
    changelog_path = ROOT / "CHANGELOG.md"
    if not changelog_path.exists():
        return ""

    text = changelog_path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"^##\s+{re.escape(tag)}\s*$\n(?P<body>.*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        return ""
    return match.group("body").strip()


def main() -> int:
    tag = sys.argv[1]
    version = _manifest_version()
    body = _extract_changelog(tag)
    title = f"{tag} - Aquarium LED Cockpit"

    print(f"# {title}")
    print()
    print(f"Home Assistant manifest version: `{version}`")
    print()
    if body:
        print(body)
        print()
    else:
        print("Automated release for Aquarium LED Cockpit.")
        print()
    print("Install or update through HACS, then restart Home Assistant.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
