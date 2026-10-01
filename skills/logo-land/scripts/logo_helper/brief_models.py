"""Brand intent with exact lettering and optional requested lockup."""

from typing import Annotated, Self

from pydantic import Field, model_validator

from logo_helper.app_icon_models import AppIconIntent, omit_absent
from logo_helper.asset_models import IconAssetIntent
from logo_helper.brand_strategy import BrandStrategy, absent_strategy
from logo_helper.lockup_models import LockupIntent
from logo_helper.model_base import Background, FrozenModel, LogoType, ProjectError, Text


class Brief(FrozenModel):
    """Brand intent; exact_text and slogan are preserved verbatim."""

    brand_name: Text
    exact_text: Annotated[str, Field(max_length=2000)]
    industry: Text
    audience: Text
    slogan: str = ""
    logo_type: LogoType = "combination"
    styles: tuple[Text, ...] = ()
    palette: tuple[Text, ...] = ()
    forbidden: tuple[Text, ...] = ()
    use_cases: tuple[Text, ...] = ()
    assumptions: tuple[Text, ...] = ()
    lockup: LockupIntent | None = None
    background: Background = "opaque"
    concept_count: Annotated[int, Field(ge=1)] = 3
    app_icon: AppIconIntent | None = Field(default=None, exclude_if=omit_absent)
    brand_strategy: BrandStrategy | None = Field(default=None, exclude_if=absent_strategy)

    @model_validator(mode="after")
    def consistent_icon_brief(self) -> Self:
        if self.app_icon is not None and (
            (
                self.background != "opaque"
                and not (self.app_icon.asset or IconAssetIntent()).allows_alpha
            )
            or self.slogan != ""
            or self.lockup is not None
            or self.exact_text != (self.app_icon.text or "")
        ):
            raise ProjectError(
                "intent_conflict",
                (
                    "An icon brief requires an asset-compatible background, no slogan or lockup, "
                    "and exact_text matching its monogram text or empty"
                ),
            )
        return self
