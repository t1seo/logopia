"""Local per-asset PNG checks and truthful handoff evidence, never native validation."""

from hashlib import sha256
from typing import Final, assert_never

from logo_helper.asset_geometry import android_safe_zone
from logo_helper.asset_models import (
    PLAY_MAX_BYTES,
    PLAY_SIZE_PX,
    AssetCheck,
    AssetReport,
    IconAssetIntent,
    SafeZoneEvidence,
)
from logo_helper.images import inspect_png

PNG_RGBA8_IHDR: Final = b"\x08\x06"
COMMON_HANDOFF: Final = (
    "Only the original PNG is supplied; no layers were inferred or extracted.",
    "Mask, grayscale, and home-screen previews are diagnostic simulations, not OS renders.",
    "Local checks do not establish app build success, store acceptance, or visual preference.",
)


def check_icon_asset(data: bytes, intent: IconAssetIntent) -> AssetReport:
    """Decode the actual source and bind every result to its exact bytes."""
    facts = inspect_png(data)
    checks = [
        AssetCheck(code="png_integrity", status="pass", detail="Complete, static PNG decoded.")
    ]
    safe_zone: SafeZoneEvidence | None = None
    handoff = COMMON_HANDOFF
    if not intent.allows_alpha:
        checks.append(
            AssetCheck(
                code="background_opacity",
                status="fail" if facts.has_transparency else "pass",
                detail=("This role requires an opaque background; foreground alpha is separate."),
            )
        )
    match intent.kind:
        case "concept_artwork":
            handoff += (
                "Flattened concept artwork; choose an explicit platform asset role before handoff.",
            )
        case "apple_layered":
            checks.append(
                AssetCheck(
                    code="apple_layer_role",
                    status="pass",
                    detail=f"Single {intent.role} PNG. Foreground alpha is allowed.",
                )
            )
            handoff += (
                "Supply authored foreground and full-bleed opaque background to Icon Composer.",
                (
                    "Review baked highlights, refraction, and shadows against system effects. "
                    "Do not pre-mask the outer tile."
                ),
                (
                    "Icon Composer modes: Default, Dark, Mono. Home appearances: default/dark/"
                    "clear/tinted, with clear/tinted light and dark variants."
                ),
                "Keep the core shape across appearances; verify in Icon Composer and Xcode.",
            )
        case "android_adaptive":
            checks.append(
                AssetCheck(
                    code="android_square_canvas",
                    status="pass" if facts.width == facts.height else "fail",
                    detail="Map square layers to 108 x 108 dp; PNG pixels are not dp units.",
                )
            )
            if intent.role in {"foreground", "monochrome"}:
                safe_zone = android_safe_zone(data)
                checks.append(
                    AssetCheck(
                        code="android_safe_zone",
                        status="warning" if safe_zone.visible_pixels_outside else "pass",
                        detail=(
                            f"{safe_zone.visible_pixels_outside} nonzero-alpha pixels outside "
                            "the centered 66/108 diameter circle. Decorations may extend beyond "
                            "it; manually identify the essential shape."
                        ),
                    )
                )
            handoff += (
                "Provide real foreground/background and authored monochrome for themed rendering.",
                "Assemble Android adaptive-icon resources; test OEM masks and launcher motion.",
                (
                    "Keep the essential logo inside the centered 66 dp circle on a 108 dp layer. "
                    "Decorative overflow is a warning, not an aesthetic failure."
                ),
                (
                    "Do not bake the outer mask or outer shadow into layers. "
                    "Inspect internal object shading separately."
                ),
            )
        case "google_play_listing":
            checks.extend(
                (
                    AssetCheck(
                        code="play_dimensions",
                        status="pass" if facts.width == facts.height == PLAY_SIZE_PX else "fail",
                        detail="Listing icon: 512 x 512 px. Launcher dp rules do not apply.",
                    ),
                    AssetCheck(
                        code="play_32bit_png",
                        status="pass" if data[24:26] == PNG_RGBA8_IHDR else "fail",
                        detail="Source PNG must encode 8-bit RGBA. No conversion performed.",
                    ),
                    AssetCheck(
                        code="play_file_size",
                        status="pass" if len(data) <= PLAY_MAX_BYTES else "fail",
                        detail=f"{len(data)} bytes; limit {PLAY_MAX_BYTES} bytes (1024 KiB).",
                    ),
                    AssetCheck(
                        code="play_transparency",
                        status="warning" if facts.has_transparency else "pass",
                        detail=(
                            "Transparency is permitted but shows the Play UI background. "
                            "Inspect both light and dark surroundings."
                        ),
                    ),
                    AssetCheck(
                        code="play_srgb",
                        status="not_checked",
                        detail=(
                            "Confirm sRGB using a color-managed export tool. "
                            "This check does not prove or convert the color profile."
                        ),
                    ),
                )
            )
            handoff += (
                "Deliver a full-square 512 px, 32-bit sRGB PNG up to 1024 KB for the listing.",
                (
                    "Play applies outer rounding and shadow. Internal artwork shadow and lighting "
                    "remain valid design choices."
                ),
                "Inspect transparent areas against the store UI; validate the Play Console upload.",
            )
        case _:
            assert_never(intent.kind)
    checks.extend(
        (
            AssetCheck(
                code="outer_mask_and_shadow",
                status="not_checked",
                detail=(
                    "Inspect for pre-rounded corners, nested tiles, or baked outer shadow. "
                    "Pixel alpha alone cannot identify them."
                ),
            ),
            AssetCheck(
                code="appearance_identity",
                status="not_checked",
                detail="One PNG cannot prove identity across actual platform appearances.",
            ),
        )
    )
    return AssetReport(
        source_sha256=sha256(data).hexdigest(),
        intent=intent,
        checks=tuple(checks),
        safe_zone=safe_zone,
        handoff=handoff,
    )
