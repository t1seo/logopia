"""Actual image evidence, independent critiques and copied feedback."""

from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from .models_base import (
    CRITERION_COUNT,
    CriterionKey,
    Digest,
    FrozenModel,
    Identifier,
    Note,
    Receipt,
    Revision,
    Role,
    SchemaVersion,
    StudioError,
    Text,
)
from .models_brief import StudioBrief
from .models_references import DesignSpecification


class GeneratedImage(FrozenModel):
    """An exact native tool return, retained for no-inference recovery."""

    path: Path
    provider: Text
    model: Text
    receipt: Receipt


class Criterion(FrozenModel):
    """One concrete visual observation and required fix."""

    key: CriterionKey
    status: Literal["pass", "needs_revision", "not_observed", "not_applicable"]
    observation: Text
    fix: Note = ""


class Critique(FrozenModel):
    """Host-bound evidence; model prose alone cannot approve an image."""

    role: Role
    provider: Text
    model: Text
    summary: Text
    criteria: Annotated[tuple[Criterion, ...], Field(min_length=5, max_length=5)]
    call_id: Identifier
    image_sha256: Digest
    parent_sha256: Digest | None
    view_sha256: Digest
    view_width: Annotated[int, Field(ge=16, le=1024)]
    parent_view_sha256: Digest | None = None

    @model_validator(mode="after")
    def complete_keys(self) -> Self:
        if len({item.key for item in self.criteria}) != CRITERION_COUNT:
            raise StudioError("invalid_report", "Critique requires five unique criteria")
        return self


class ReviewInput(FrozenModel):
    """Actual original and parent paths for one independent critique pair."""

    brief: StudioBrief
    image_path: Path
    image_sha256: Digest
    parent_path: Path | None
    keep: Annotated[tuple[Text, ...], Field(max_length=20)]
    change: Note
    design_spec: DesignSpecification | None = None
    changed_variables: Annotated[tuple[Text, ...], Field(max_length=6)] = ()


class FeedbackEnvelope(FrozenModel):
    """A draft decision must be explicitly applied against its exact revision."""

    schema_version: SchemaVersion = 1
    workflow_id: Identifier
    expected_revision: Revision
    candidate_id: Identifier
    candidate_sha256: Digest
    action: Literal["choose", "revise"]
    keep: Annotated[tuple[Text, ...], Field(max_length=20)] = ()
    change: Note = ""

    @model_validator(mode="after")
    def action_intent(self) -> Self:
        if (self.action == "choose" and self.change != "") or (
            self.action == "revise" and not self.change.strip()
        ):
            raise StudioError("invalid_feedback", "Choose needs empty change; revise needs change")
        return self
