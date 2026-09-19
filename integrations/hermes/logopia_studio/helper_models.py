"""Strict projections of the existing CLI wire schema, with no helper imports."""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field, JsonValue, ValidationError

from .models import StudioBrief, StudioError
from .models_base import Background, Digest, FrozenModel, Identifier, Revision
from .models_icon import StudioIconIntent


class HelperBrief(FrozenModel):
    """Exact legacy brief wire shape used by this additive integration."""

    brand_name: str
    exact_text: str
    industry: str
    audience: str
    slogan: str = ""
    logo_type: str = "combination"
    styles: tuple[str, ...] = ()
    palette: tuple[str, ...] = ()
    forbidden: tuple[str, ...] = ()
    use_cases: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    lockup: None = None
    background: Background = "opaque"
    concept_count: Annotated[int, Field(ge=1, le=6)] = 3
    app_icon: StudioIconIntent | None = None

    @classmethod
    def from_brief(cls, brief: StudioBrief) -> "HelperBrief":
        return cls(
            brand_name=brief.name,
            exact_text=brief.exact_text,
            industry=brief.product,
            audience=brief.audience,
            logo_type=brief.logo_type,
            styles=(brief.personality,),
            palette=brief.colors,
            use_cases=(brief.use_case,),
            assumptions=(brief.notes,) if brief.notes else (),
            background=brief.background,
            concept_count=brief.effective_direction_count,
            app_icon=brief.app_icon,
        )


class HelperReview(FrozenModel):
    """Explicit helper booleans derived only from both passing pixel critics."""

    reviewer: str
    notes: str
    text_correct: bool
    composition_ok: bool
    small_size_ok: bool
    preservation_ok: bool
    background_checked: bool


class ImageFacts(FrozenModel):
    """Decoded PNG facts returned by the authoritative helper."""

    format: Literal["PNG"] = "PNG"
    width: Annotated[int, Field(gt=0)]
    height: Annotated[int, Field(gt=0)]
    alpha_min: Annotated[int, Field(ge=0, le=255)]
    alpha_max: Annotated[int, Field(gt=0, le=255)]
    transparent_pixels: Annotated[int, Field(ge=0)]
    visible_pixels: Annotated[int, Field(gt=0)]


class HelperArtifact(FrozenModel):
    """Exact helper artifact provenance needed for reconciliation."""

    id: Identifier
    path: str
    sha256: Digest
    image: ImageFacts
    prompt: str
    parent_id: Identifier | None = None
    created_at: datetime
    requested_background: Background | None = None
    palette_id: None = None
    lockup: None = None
    app_icon: StudioIconIntent | None = None
    review: HelperReview | None = None
    reviewed_at: datetime | None = None


class HelperExport(FrozenModel):
    """Committed helper export identity, destination and timestamp."""

    path: str
    artifact_id: Identifier
    created_at: datetime


class HelperSession(FrozenModel):
    """Opaque color evidence is validated by the authoritative CLI, never persisted here."""

    schema_version: Literal[2]
    id: Identifier
    revision: Revision
    created_at: datetime
    updated_at: datetime
    brief: HelperBrief
    artifacts: tuple[HelperArtifact, ...] = ()
    selected_id: Identifier | None = None
    failures: tuple[JsonValue, ...] = ()
    exports: tuple[HelperExport, ...] = ()
    palettes: tuple[JsonValue, ...] = ()
    active_palette_id: None = None
    references: tuple[JsonValue, ...] = ()
    color_reports: tuple[JsonValue, ...] = ()


class HelperManifest(FrozenModel):
    """Published manifest fields verified against the committed helper session."""

    schema_version: Literal[2]
    session_id: Identifier
    revision: Revision
    exported_at: datetime
    image_file: Literal["logo.png"]
    source: HelperArtifact
    brief: HelperBrief
    media_kind: Literal["raster"]
    requested_background: Background
    transparency_verified: bool
    intended_palette: None
    color_report: JsonValue
    color_policy: JsonValue
    warnings: tuple[str, ...]
    color_method: str
    color_limits: tuple[str, ...]
    lockup_intent: None
    font_reference_usage: Literal["appearance-reference-only"]
    app_icon: StudioIconIntent | None
    artwork_limitations: str | None
    asset_report: JsonValue = None


def parse_session(raw: str) -> HelperSession:
    try:
        return HelperSession.model_validate_json(raw)
    except ValidationError as error:
        raise StudioError("invalid_helper", str(error)) from error
