"""Typed conversational choices; explicit placement is always respected."""

from typing import Final

from logo_helper.app_icon_models import AppIconPlacement, AppIconPreset
from logo_helper.model_base import FrozenModel


class AppIconPresetChoice(FrozenModel):
    """A discoverable style and its conversational starting placement."""

    id: AppIconPreset
    label: str
    description: str
    default_placement: AppIconPlacement


APP_ICON_PRESETS: Final[tuple[AppIconPresetChoice, ...]] = (
    AppIconPresetChoice(
        id="ip_mascot",
        label="IP mascot",
        description=(
            "A personified character with deliberate expression, proportions and silhouette "
            "suited to the product and requested colors."
        ),
        default_placement="lower_left",
    ),
    AppIconPresetChoice(
        id="pictogram",
        label="Pictogram",
        description="One immediately recognizable silhouette with clean flat shapes.",
        default_placement="center",
    ),
    AppIconPresetChoice(
        id="abstract",
        label="Abstract",
        description="A coherent nonliteral gesture with deliberate contour and negative space.",
        default_placement="center",
    ),
    AppIconPresetChoice(
        id="monogram",
        label="Monogram",
        description="One to eight exact Unicode characters shaped as readable lettering.",
        default_placement="center",
    ),
    AppIconPresetChoice(
        id="soft_3d",
        label="Soft 3D",
        description="One tactile object with a chosen material, readable silhouette and depth.",
        default_placement="center",
    ),
    AppIconPresetChoice(
        id="pixel_art",
        label="Pixel art",
        description="Deliberate block geometry on a consistent pixel grid.",
        default_placement="center",
    ),
)
