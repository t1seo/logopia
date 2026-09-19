"""Evidence-bound preference responses, separate from production QA and selection."""

from datetime import datetime
from hashlib import sha256
from typing import Annotated, Literal, Self, assert_never

from pydantic import Field, model_validator

from logo_helper.model_base import Digest, FrozenModel, ProjectError
from logo_helper.preference_models import EvidenceText


class PreferenceEvidence(FrozenModel):
    """Concrete observations are required for every criterion, including actual 32 px detail."""

    brief_reference_fit: EvidenceText
    shape_background: EvidenceText
    craft_detail: EvidenceText
    effects_material: EvidenceText
    distinctiveness: EvidenceText
    small_size_32: EvidenceText
    peer_context: EvidenceText


class PreferenceDecision(FrozenModel):
    """A displayed-label outcome remains bound to both original image hashes."""

    pair_id: Annotated[str, Field(pattern=r"^pair-[0-9]{2}$")]
    a_sha256: Digest
    b_sha256: Digest
    outcome: Literal["a", "b", "tie", "neither"]
    observations: PreferenceEvidence


class PreferenceContext(FrozenModel):
    """Only diagnostic contexts actually available in the local comparison page."""

    kind: Literal["simulation"] = "simulation"
    sizes: tuple[Literal[32], Literal[48], Literal[64], Literal[128]] = (32, 48, 64, 128)
    surfaces: tuple[Literal["light"], Literal["dark"]] = ("light", "dark")
    mask: Literal["square", "rounded", "circle"]
    peer_context: Literal[True]


class PreferenceResponse(FrozenModel):
    """User opinion and AI recommendation are explicitly different response sources."""

    schema_version: Literal[1] = 1
    manifest_sha256: Digest
    reviewer: EvidenceText
    reviewer_kind: Literal["user", "ai"]
    review_calls: Annotated[int, Field(ge=0, le=12)]
    context: PreferenceContext
    decisions: Annotated[tuple[PreferenceDecision, ...], Field(min_length=1, max_length=12)]

    @model_validator(mode="after")
    def consistent_review_calls(self) -> Self:
        match self.reviewer_kind:
            case "user":
                if self.review_calls != 0:
                    raise ProjectError("invalid_review", "User responses require zero AI calls")
            case "ai":
                if self.review_calls < 1:
                    raise ProjectError("invalid_review", "AI responses must report actual calls")
            case _:
                assert_never(self.reviewer_kind)
        if len({decision.pair_id for decision in self.decisions}) != len(self.decisions):
            raise ProjectError("invalid_review", "Do not repeat a pair in one response")
        return self

    @property
    def status(self) -> Literal["user_preference", "ai_recommendation"]:
        match self.reviewer_kind:
            case "user":
                return "user_preference"
            case "ai":
                return "ai_recommendation"
            case _:
                assert_never(self.reviewer_kind)


class PreferenceRecord(FrozenModel):
    """Immutable sidecar with provenance; contains no QA, export or selection mutation."""

    kind: Literal["preference_record"] = "preference_record"
    response_sha256: Digest
    recorded_at: datetime
    status: Literal["user_preference", "ai_recommendation"]
    response: PreferenceResponse

    @model_validator(mode="after")
    def consistent_record(self) -> Self:
        digest = sha256(self.response.model_dump_json().encode("utf-8")).hexdigest()
        if digest != self.response_sha256 or self.status != self.response.status:
            raise ProjectError("invalid_record", "Record hash or reviewer status was changed")
        return self


class PreferenceRecordResult(FrozenModel):
    """Exact record location and budget usage after an exclusive successful write."""

    path: str
    status: Literal["user_preference", "ai_recommendation"]
    recorded_ai_review_calls: int
    source_sessions_changed: Literal[False] = False
