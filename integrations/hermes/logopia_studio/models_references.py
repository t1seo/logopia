"""Reference identity and transfer evidence, separate from user preference."""

from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from .models_base import Digest, FrozenModel, Identifier, Note, StudioError, Text


class StudioReference(FrozenModel):
    """Local input pixels are immutable by hash; provenance never grants usage rights."""

    id: Identifier
    path: Path
    sha256: Digest
    role: Literal["positive", "negative"] = "positive"
    observations: Annotated[tuple[Text, ...], Field(max_length=8)] = ()
    transfer_traits: Annotated[tuple[Text, ...], Field(max_length=8)] = ()
    avoid_traits: Annotated[tuple[Text, ...], Field(max_length=8)] = ()
    source_url: Note = ""
    verified_on: Note = "unknown"
    announced_on: Note = "unknown"
    platform: Note = "unknown"
    appearance: Note = "unknown"
    release_status: Literal["released", "concept", "unknown"] = "unknown"
    usage_rights: Literal["unverified", "restricted", "confirmed"] = "unverified"
    selected_by: Literal["user", "automatic"] = "user"

    @model_validator(mode="after")
    def supported_role(self) -> Self:
        if not self.path.is_absolute():
            raise StudioError("invalid_reference", "Reference PNG paths must be absolute")
        if self.role == "negative" and self.transfer_traits:
            raise StudioError(
                "invalid_reference", "Negative references cannot supply transfer traits"
            )
        return self


class DesignSpecification(FrozenModel):
    """Authored intent is distinct from the later pixel critic's observations."""

    primary_form: Text
    construction: Text
    color_roles: Text
    material: Text
    reference_traits: Annotated[tuple[Text, ...], Field(max_length=8)] = ()
    excluded_reference_features: Annotated[tuple[Text, ...], Field(max_length=8)] = ()
    small_size_invariant: Text
    structural_difference: Text
    failure_risk: Text


class CandidateVariation(FrozenModel):
    """A controlled shape change within one direction, never an automatic reroll."""

    slot: Annotated[int, Field(ge=1, le=3)]
    changed_variables: Annotated[tuple[Text, ...], Field(min_length=1, max_length=6)]
    instruction: Text


class ReferenceAnalysis(FrozenModel):
    """Model observations are bound by the host to the reference pixels it inspected."""

    reference_id: Identifier
    reference_sha256: Digest | None = None
    observations: Annotated[tuple[Text, ...], Field(min_length=1, max_length=6)]
    interpretation: Note = ""
    transfer_traits: Annotated[tuple[Text, ...], Field(max_length=6)] = ()
    avoid_traits: Annotated[tuple[Text, ...], Field(max_length=6)] = ()
