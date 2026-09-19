"""Explicit visual evidence and native input capability, separate from edit ancestry."""

from datetime import date
from typing import Annotated, Literal

from pydantic import Field

from logo_helper.model_base import Digest, FrozenModel, ReferenceId, Text
from logo_helper.reference_models import RegionOfInterest


class VisualReference(FrozenModel):
    """An observer's claims bound to imported bytes; never inferred by the helper."""

    reference_id: ReferenceId
    image_sha256: Digest
    role: Literal["positive", "negative"]
    observations: Annotated[tuple[Text, ...], Field(min_length=1, max_length=6)]
    transfer: Annotated[tuple[Text, ...], Field(max_length=6)] = ()
    avoid: Annotated[tuple[Text, ...], Field(max_length=6)] = ()
    inspected_by: Text
    inspected_on: date
    roi: RegionOfInterest | None = None
    source_url: str | None = None
    selection_origin: Literal["user", "automatic"] = "automatic"
    rights_status: Literal["unknown", "user_owned", "permission_recorded"] = "unknown"


class ReferencePlan(FrozenModel):
    """Only selected relevant references; image fallback is never silent."""

    mode: Literal["text", "image"] = "text"
    capability: Literal["codex_native", "text_only"] = "codex_native"
    references: Annotated[tuple[VisualReference, ...], Field(min_length=1, max_length=6)]


def no_paths(value: tuple[str, ...]) -> bool:
    return not value


class NativeImageArguments(FrozenModel):
    """Only parameters present in the observed Codex imagegen schema."""

    prompt: str
    referenced_image_paths: tuple[str, ...] = Field(default=(), exclude_if=no_paths)


class InputPlan(FrozenModel):
    """Inspectable exact tool arguments and evidence for the external native call."""

    tool: Literal["image_gen__imagegen"] = "image_gen__imagegen"
    conditioning: Literal["analysis_text", "image"]
    arguments: NativeImageArguments
    references: tuple[VisualReference, ...]
    parent_sha256: Digest | None
    request_sha256: Digest
    limitations: tuple[str, ...] = ()


def no_input_plan(value: InputPlan | None) -> bool:
    return value is None
