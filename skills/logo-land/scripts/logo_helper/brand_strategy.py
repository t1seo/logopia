"""Optional proposed brand context, separate from authoritative rendering intent."""

from typing import Annotated

from pydantic import Field

from logo_helper.model_base import FrozenModel, Text


class BrandStrategy(FrozenModel):
    """Saved design proposals; these fields do not assert researched market facts."""

    positioning: Text
    audience_need: Text
    brand_promise: Text
    distinctive_principle: Text
    typography: Text
    color_roles: Text
    assumptions: Annotated[tuple[Text, ...], Field(max_length=12)] = ()

    def prompt_context(self) -> str:
        """Bound supporting context without truncating saved source or exact user intent."""
        summary = BrandStrategy(
            positioning=self.positioning.strip()[:320],
            audience_need=self.audience_need.strip()[:320],
            brand_promise=self.brand_promise.strip()[:320],
            distinctive_principle=self.distinctive_principle.strip()[:320],
            typography=self.typography.strip()[:320],
            color_roles=self.color_roles.strip()[:320],
            assumptions=tuple(value.strip()[:160] for value in self.assumptions[:3]),
        )
        return summary.model_dump_json()


def absent_strategy(value: BrandStrategy | None) -> bool:
    return value is None
