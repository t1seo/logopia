"""Saved design intent and structured planning results."""

from typing import Annotated, Literal, Self, assert_never

from pydantic import Field, model_validator

from .models_base import (
    CRITIQUE_LIMIT,
    EDIT_LIMIT,
    INITIAL_IMAGE_LIMIT,
    ROLE_COUNT,
    Background,
    Count,
    FrozenModel,
    Identifier,
    Note,
    Prompt,
    StudioError,
    Text,
)
from .models_icon import StudioIconIntent
from .models_references import (
    CandidateVariation,
    DesignSpecification,
    ReferenceAnalysis,
    StudioReference,
)


class StudioBrief(FrozenModel):
    """Native workflow scope; text and colors are preserved as supplied."""

    name: Text
    exact_text: Note
    product: Text
    audience: Text
    personality: Text
    use_case: Text
    display_width: Annotated[int, Field(ge=16, le=1024)] = 192
    logo_type: Literal[
        "wordmark",
        "lettermark",
        "monogram",
        "symbol",
        "abstract",
        "combination",
        "emblem",
        "mascot",
    ] = "combination"
    mode: Literal["brand", "app_icon", "ip"] = "brand"
    background: Background = "opaque"
    count: Count | None = None
    direction_count: Count | None = None
    candidates_per_direction: Annotated[int, Field(ge=1, le=3)] = 1
    colors: Annotated[tuple[Text, ...], Field(max_length=12)] = ()
    notes: Note = ""
    color_policy: Literal["advisory"] = "advisory"
    references: Annotated[tuple[StudioReference, ...], Field(max_length=6)] = ()
    reference_conditioning: Literal["text", "image"] = "text"
    app_icon: StudioIconIntent | None = None
    review_call_budget: Annotated[int, Field(ge=2, le=44)] | None = None

    @model_validator(mode="after")
    def supported_intent(self) -> Self:
        if self.app_icon is not None and (
            self.mode != "app_icon" or self.exact_text != (self.app_icon.text or "")
        ):
            raise StudioError(
                "intent_conflict", "app_icon metadata requires matching app mode/text"
            )
        if self.mode in {"app_icon", "ip"} and self.background != "opaque":
            raise StudioError("unsupported_intent", "App/IP requires an opaque composite PNG")
        if self.mode == "ip" and self.exact_text != "":
            raise StudioError(
                "unsupported_intent", "IP character portraits require empty exact_text"
            )
        if self.count is not None and self.direction_count is not None:
            raise StudioError("invalid_count", "Use legacy count or direction_count, not both")
        if self.candidates_per_direction != 1 and self.direction_count is None:
            raise StudioError("invalid_count", "Exploration requires explicit direction_count")
        if self.effective_count > INITIAL_IMAGE_LIMIT:
            raise StudioError(
                "image_budget", "At most nine initial images and two edits are supported"
            )
        if self.effective_review_call_budget < ROLE_COUNT * self.effective_count:
            raise StudioError(
                "review_budget", "Budget must cover both initial critics per candidate"
            )
        if len({item.id for item in self.references}) != len(self.references):
            raise StudioError("invalid_reference", "Reference IDs must be unique")
        if self.reference_conditioning == "image":
            raise StudioError(
                "unsupported_conditioning",
                (
                    "Hermes image_generate has one image_url reserved for edits; use text "
                    "conditioning from multimodal reference planning, or the helper input route"
                ),
            )
        return self

    @property
    def effective_count(self) -> int:
        return self.effective_direction_count * self.candidates_per_direction

    @property
    def effective_direction_count(self) -> int:
        if self.direction_count is not None:
            return self.direction_count
        if self.count is not None:
            return self.count
        match self.mode:
            case "brand" | "app_icon":
                return 3
            case "ip":
                return 6
            case _:
                assert_never(self.mode)

    @property
    def effective_review_call_budget(self) -> int:
        return (
            self.review_call_budget
            if self.review_call_budget is not None
            else ROLE_COUNT * CRITIQUE_LIMIT * (self.effective_count + EDIT_LIMIT)
        )


class Strategy(FrozenModel):
    """Design proposals, not claims of researched market facts."""

    positioning: Text
    audience_need: Text
    brand_promise: Text
    distinctive_principle: Text
    typography: Text
    color_roles: Text
    assumptions: Annotated[tuple[Text, ...], Field(max_length=12)]


class Direction(FrozenModel):
    """One independently generated candidate direction."""

    id: Identifier
    title: Text
    motif: Text
    construction: Text
    rationale: Text
    risk: Text
    preserve: Annotated[tuple[Text, ...], Field(max_length=20)]
    prompt: Prompt
    design_spec: DesignSpecification | None = None
    variations: Annotated[tuple[CandidateVariation, ...], Field(max_length=3)] = ()

    @model_validator(mode="after")
    def unique_slots(self) -> Self:
        if len({item.slot for item in self.variations}) != len(self.variations):
            raise StudioError("invalid_plan", "Candidate variation slots must be unique")
        return self


class PlanResult(FrozenModel):
    """Attribution and exact ordered output of a single planning attempt."""

    strategy: Strategy
    directions: Annotated[tuple[Direction, ...], Field(min_length=1, max_length=6)]
    provider: Text
    model: Text
    reference_analysis: Annotated[tuple[ReferenceAnalysis, ...], Field(max_length=6)] = ()

    @model_validator(mode="after")
    def unique_directions(self) -> Self:
        if len({item.id for item in self.directions}) != len(self.directions):
            raise StudioError("invalid_plan", "Direction IDs must be unique")
        return self
