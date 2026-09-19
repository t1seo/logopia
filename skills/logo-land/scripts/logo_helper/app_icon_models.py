"""Explicit square artwork intent at JSON and persisted snapshot boundaries."""

from typing import Annotated, Final, Literal, Self, assert_never
from unicodedata import category

from pydantic import Field, model_validator

from logo_helper.asset_models import IconAssetIntent, absent_asset
from logo_helper.model_base import Background, FrozenModel, ProjectError

type AppIconPreset = Literal[
    "ip_mascot", "pictogram", "abstract", "monogram", "soft_3d", "pixel_art"
]
type AppIconPlacement = Literal["center", "lower_left", "lower_right"]
MAX_MONOGRAM_LENGTH: Final = 8


class AppIconIntent(FrozenModel):
    """Complete rendering intent; conversation defaults never fill missing fields here."""

    preset: AppIconPreset
    subject: Annotated[str, Field(min_length=1, max_length=500, pattern=r"\S")]
    placement: AppIconPlacement
    text: str | None = None
    asset: IconAssetIntent | None = Field(default=None, exclude_if=absent_asset)

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
                    raise ProjectError(
                        "invalid_app_icon",
                        (
                            "Monogram text needs 1-8 Unicode code points "
                            "without whitespace or control characters"
                        ),
                    )
            case "ip_mascot" | "pictogram" | "abstract" | "soft_3d" | "pixel_art":
                if self.text is not None:
                    raise ProjectError("invalid_app_icon", "Only a monogram may request text")
            case _:
                assert_never(self.preset)
        return self


def omit_absent(value: AppIconIntent | Background | None) -> bool:
    return value is None
