"""Selected icon intent and the boundary between raster artwork and platform assets."""

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING, Final

from logo_helper.asset_models import IconAssetIntent

if TYPE_CHECKING:
    from logo_helper.app_icon_models import AppIconIntent

ARTWORK_LIMITATIONS: Final = (
    "This PNG is app-icon artwork, not an Icon Composer document, a complete adaptive-icon set, "
    "an app build, or evidence of store acceptance. Platform preparation and validation "
    "are separate steps. Preview masks are illustrative and do not alter the original."
)


def app_icon_guide(intent: AppIconIntent | None) -> str:
    """Describe only the selected artifact's intent, preserving Unicode lettering."""
    if intent is None:
        return ""
    asset = intent.asset or IconAssetIntent()
    return (
        "\n## Selected app-icon artwork\n\n"
        f"Preset: {escape(intent.preset)}\n\n"
        f"Subject: {escape(intent.subject)}\n\n"
        f"Placement: {escape(intent.placement)}\n\n"
        f"Exact lettering: {escape(intent.text or 'None')}\n\n"
        f"Asset purpose: {asset.kind}; platform: {asset.platform}; role: {asset.role}.\n\n"
        f"Requested home appearance: {asset.appearance}; "
        f"Icon Composer mode: {asset.composer_mode or 'not specified'}.\n\n"
        "The manifest asset_report records local PNG checks and the remaining platform handoff. "
        "Foreground alpha is allowed for authored layers; native rendering is unverified.\n\n"
        f"{ARTWORK_LIMITATIONS}\n"
    )
