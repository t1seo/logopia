"""Request a single authored raster asset without claiming native packaging."""

from typing import assert_never

from logo_helper.app_icon_models import AppIconIntent
from logo_helper.model_base import Background


def artwork_direction(icon: AppIconIntent, background: Background) -> str:
    asset = icon.asset
    if asset is None or asset.kind == "concept_artwork":
        return (
            "Produce one full-bleed square raster PNG, approximately 1536 by 1536 pixels, "
            "with square outer corners and a complete solid background covering the entire canvas. "
        )
    match asset.kind:
        case "google_play_listing":
            return (
                "Produce one 512 by 512 pixel Google Play listing PNG in sRGB, 32-bit RGBA. "
                f"Honor the requested {background} background. Keep square outer corners; "
                "For an edit, an explicit compatible background change takes precedence; "
                "otherwise preserve this background intent. "
                "do not pre-mask or add an outer tile shadow. Requested internal object shading "
                "is allowed. This is a store image, not Android adaptive layers. "
            )
        case "apple_layered" | "android_adaptive":
            layer = (
                "Authored foreground layer only: transparent empty pixels; no backing tile. "
                if asset.role in {"foreground", "monochrome"}
                else "Authored background layer only: fully opaque full-bleed background. "
            )
            platform = (
                (
                    "Use a 1024 by 1024 pixel square. System effects are added in Icon Composer; "
                    "avoid duplicating highlights, bevels or outer shadows. "
                )
                if asset.platform == "apple"
                else (
                    "Use a square canvas representing 108 by 108 dp; dp is not output pixels. "
                    "Keep the identifying foreground inside the central circle of diameter 66/108 "
                    "of the canvas. Allow background bleed beyond that zone. "
                )
            )
            monochrome = (
                "Use one foreground color with alpha defining the themed silhouette. "
                if asset.role == "monochrome"
                else ""
            )
            return (
                f"{layer}{platform}{monochrome}Preserve the core silhouette across appearances. "
                f"Appearance intent: {asset.appearance}; Composer editing mode: "
                f"{asset.composer_mode or 'unspecified'}. "
                "One authored layer is not a native package or extracted editable layers. "
            )
        case _:
            assert_never(asset.kind)
