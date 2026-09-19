"""Independent PNG asset intent; this contract never represents a native package."""

from typing import Annotated, Final, Literal, Self, assert_never

from pydantic import Field, model_validator

from logo_helper.model_base import Digest, FrozenModel, ProjectError

type IconAssetKind = Literal[
    "concept_artwork", "apple_layered", "android_adaptive", "google_play_listing"
]
type IconPlatform = Literal["unspecified", "apple", "android"]
type IconAssetRole = Literal["composite", "foreground", "background", "monochrome"]
type IconAppearance = Literal[
    "unspecified",
    "default",
    "dark",
    "clear_light",
    "clear_dark",
    "tinted_light",
    "tinted_dark",
    "themed",
]
type ComposerMode = Literal["default", "dark", "mono"]
ANDROID_LAYER_DP: Final = 108
ANDROID_SAFE_DIAMETER_DP: Final = 66
PLAY_SIZE_PX: Final = 512
PLAY_MAX_BYTES: Final = 1024 * 1024


class IconAssetIntent(FrozenModel):
    """A single original PNG's purpose and layer role, separate from style or material."""

    kind: IconAssetKind = "concept_artwork"
    platform: IconPlatform = "unspecified"
    role: IconAssetRole = "composite"
    appearance: IconAppearance = "unspecified"
    composer_mode: ComposerMode | None = None

    @model_validator(mode="after")
    def consistent_asset(self) -> Self:
        match self.kind:
            case "concept_artwork":
                valid = self.role == "composite"
            case "apple_layered":
                valid = self.platform == "apple" and self.role in {"foreground", "background"}
            case "android_adaptive":
                valid = self.platform == "android" and self.role in {
                    "foreground",
                    "background",
                    "monochrome",
                }
            case "google_play_listing":
                valid = (
                    self.platform == "android"
                    and self.role == "composite"
                    and self.appearance in {"unspecified", "default"}
                )
            case _:
                assert_never(self.kind)
        if not valid or (self.composer_mode is not None and self.kind != "apple_layered"):
            raise ProjectError("invalid_asset", "Asset kind, platform, and layer role disagree")
        match self.platform:
            case "apple":
                appearance_valid = self.appearance != "themed"
            case "android":
                appearance_valid = self.appearance in {"unspecified", "default", "dark", "themed"}
            case "unspecified":
                appearance_valid = self.appearance == "unspecified"
            case _:
                assert_never(self.platform)
        if not appearance_valid:
            raise ProjectError("invalid_asset", "Appearance belongs to a different platform")
        return self

    @property
    def allows_alpha(self) -> bool:
        match self.kind:
            case "concept_artwork":
                return False
            case "apple_layered" | "android_adaptive":
                return self.role in {"foreground", "monochrome"}
            case "google_play_listing":
                return True
            case _:
                assert_never(self.kind)


def absent_asset(value: IconAssetIntent | None) -> bool:
    return value is None


class AssetCheck(FrozenModel):
    """One local check, never a visual preference or OS validation result."""

    code: str
    status: Literal["pass", "fail", "warning", "not_checked"]
    detail: str


class SafeZoneEvidence(FrozenModel):
    """A conservative circle in normalized coordinates, not a pixel-to-dp conversion."""

    layer_dp: Literal[108] = 108
    safe_diameter_dp: Literal[66] = 66
    normalized_diameter: float = ANDROID_SAFE_DIAMETER_DP / ANDROID_LAYER_DP
    visible_pixels_outside: Annotated[int, Field(ge=0)]
    measurement: Literal["all nonzero alpha; semantic foreground unknown"] = (
        "all nonzero alpha; semantic foreground unknown"
    )


class AssetReport(FrozenModel):
    """Hash-bound diagnostics and explicit handoff limits for one unmodified PNG."""

    source_sha256: Digest
    intent: IconAssetIntent
    checks: tuple[AssetCheck, ...]
    safe_zone: SafeZoneEvidence | None = None
    handoff: tuple[str, ...]
    platform_validation: Literal["not_run"] = "not_run"
    native_package: Literal[False] = False

    @property
    def passed(self) -> bool:
        return all(check.status != "fail" for check in self.checks)
