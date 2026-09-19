"""Python 3.11 projection of optional helper icon intent; no native package claim."""

from typing import Annotated, Final, Literal, Self, assert_never
from unicodedata import category

from pydantic import Field, model_validator

from .models_base import FrozenModel, StudioError

MAX_MONOGRAM_LENGTH: Final = 8


class IconAssetIntent(FrozenModel):
    """Platform asset vocabulary is independent of drawing style and placement."""

    kind: Literal["concept_artwork", "apple_layered", "android_adaptive", "google_play_listing"] = (
        "concept_artwork"
    )
    platform: Literal["unspecified", "apple", "android"] = "unspecified"
    role: Literal["composite", "foreground", "background", "monochrome"] = "composite"
    appearance: Literal[
        "unspecified",
        "default",
        "dark",
        "clear_light",
        "clear_dark",
        "tinted_light",
        "tinted_dark",
        "themed",
    ] = "unspecified"
    composer_mode: Literal["default", "dark", "mono"] | None = None


class StudioIconIntent(FrozenModel):
    """Explicit optional metadata; older workflow/helper sessions retain absent intent."""

    preset: Literal["ip_mascot", "pictogram", "abstract", "monogram", "soft_3d", "pixel_art"]
    subject: Annotated[str, Field(min_length=1, max_length=500, pattern=r"\S")]
    placement: Literal["center", "lower_left", "lower_right"]
    text: str | None = None
    asset: IconAssetIntent | None = None

    @model_validator(mode="after")
    def lettering_contract(self) -> Self:
        match self.preset:
            case "monogram":
                if (
                    self.text is None
                    or not 1 <= len(self.text) <= MAX_MONOGRAM_LENGTH
                    or any(
                        char.isspace() or category(char) in {"Cc", "Cf", "Cs"} for char in self.text
                    )
                ):
                    raise StudioError(
                        "invalid_app_icon",
                        (
                            "Monogram text needs 1-8 Unicode code points "
                            "without whitespace or controls"
                        ),
                    )
            case "ip_mascot" | "pictogram" | "abstract" | "soft_3d" | "pixel_art":
                if self.text is not None:
                    raise StudioError("invalid_app_icon", "Only a monogram may request text")
            case _:
                assert_never(self.preset)
        return self

    @model_validator(mode="after")
    def supported_asset(self) -> Self:
        if self.asset is not None and (
            self.asset.kind != "concept_artwork" or self.asset.role != "composite"
        ):
            raise StudioError(
                "unsupported_asset",
                (
                    "Hermes produces flat concept PNGs. Use the helper's real-layer validation "
                    "and platform handoff for native layers or a size-verified store listing."
                ),
            )
        if self.asset is not None:
            if self.asset.composer_mode is not None:
                raise StudioError("invalid_asset", "Composer mode requires a real Apple layer")
            match self.asset.platform:
                case "apple":
                    valid = self.asset.appearance != "themed"
                case "android":
                    valid = self.asset.appearance in {"unspecified", "default", "dark", "themed"}
                case "unspecified":
                    valid = self.asset.appearance == "unspecified"
                case _:
                    assert_never(self.asset.platform)
            if not valid:
                raise StudioError("invalid_asset", "Appearance belongs to a different platform")
        return self
