"""External contracts for bounded logo production and evidence-based critique."""

from __future__ import annotations

from typing import Annotated, Final, Literal, Self, assert_never

from pydantic import Field, model_validator

from logo_helper.model_base import (
    ArtifactId,
    Digest,
    FrozenModel,
    Identifier,
    ProjectError,
    SessionId,
    Text,
)

type Criterion = Literal[
    "appropriateness", "distinctiveness", "form", "optics", "use_size", "versatility", "scope"
]
CRITERION_COUNT: Final = 7


class Direction(FrozenModel):
    """A proposed idea with an explicit structural difference, not a quality score."""

    id: Identifier
    idea: Text
    structure: Text
    distinction: Text


class LoopContract(FrozenModel):
    """Fixed user intent and a finite native-call allocation for one source session."""

    session_id: SessionId
    scope: Literal["symbol_only", "full_logo"]
    fixed_typography: bool = False
    fixed_decisions: Annotated[tuple[Text, ...], Field(min_length=1, max_length=20)]
    source_evidence: Annotated[tuple[Text, ...], Field(min_length=1, max_length=20)]
    success_criteria: Annotated[tuple[Text, ...], Field(min_length=1, max_length=20)]
    use_contexts: Annotated[tuple[Text, ...], Field(min_length=1, max_length=20)]
    directions: Annotated[tuple[Direction, ...], Field(min_length=2, max_length=6)]
    call_budget: Annotated[int, Field(ge=1, le=12)] = 6

    @model_validator(mode="after")
    def consistent_scope(self) -> Self:
        if self.fixed_typography and self.scope != "symbol_only":
            raise ProjectError("scope_conflict", "Fixed typography requires symbol_only scope")
        if len({item.id for item in self.directions}) != len(self.directions):
            raise ProjectError("invalid_contract", "Direction IDs must be unique")
        if len({item.structure.casefold().strip() for item in self.directions}) != len(
            self.directions
        ):
            raise ProjectError("invalid_contract", "Directions need different structural proposals")
        return self


class ViewEvidence(FrozenModel):
    """A reviewer's claimed view bound to a real PNG; hashes do not prove inspection."""

    id: Identifier
    path: Text
    sha256: Digest
    source_artifact_sha256: Digest
    kind: Literal["original", "target_size", "one_color", "inverse", "context"]
    description: Text
    target_width: Annotated[int, Field(ge=1, le=4096)] | None = None


class CriterionAssessment(FrozenModel):
    """Observed form and its consequence, with unknowns kept separate from passes."""

    criterion: Criterion
    status: Literal["pass", "revise", "not_observed"]
    observation: Text
    evidence_ids: tuple[Identifier, ...] = ()
    issue_id: Identifier | None = None

    @model_validator(mode="after")
    def identified_issue(self) -> Self:
        if self.status == "revise" and self.issue_id is None:
            raise ProjectError("invalid_critique", "A revise assessment requires a stable issue_id")
        return self


class Critique(FrozenModel):
    """An explicit host assessment of one returned artifact and its next visible action."""

    request_number: Annotated[int, Field(ge=1)]
    artifact_id: ArtifactId
    artifact_sha256: Digest
    reviewer: Text
    evidence: Annotated[tuple[ViewEvidence, ...], Field(min_length=1, max_length=20)]
    assessments: Annotated[tuple[CriterionAssessment, ...], Field(min_length=7, max_length=7)]
    decision: Literal["refine", "reframe", "reject", "ready", "stop"]
    reason: Text
    preserve: tuple[Text, ...] = ()
    changes: Annotated[tuple[Text, ...], Field(max_length=2)] = ()
    next_direction_id: Identifier | None = None
    unresolved: tuple[Text, ...] = ()
    change_result: Literal["initial", "improved", "unchanged", "regressed", "not_observed"] = (
        "initial"
    )
    preservation_result: Literal["pass", "revise", "not_observed"] = "not_observed"

    @model_validator(mode="after")
    def complete_critique(self) -> Self:
        if len({item.criterion for item in self.assessments}) != CRITERION_COUNT:
            raise ProjectError("invalid_critique", "Every creative criterion must occur once")
        evidence = {item.id: item for item in self.evidence}
        if len(evidence) != len(self.evidence):
            raise ProjectError("invalid_critique", "Evidence IDs must be unique")
        for assessment in self.assessments:
            if any(identifier not in evidence for identifier in assessment.evidence_ids):
                raise ProjectError("invalid_critique", "Assessment references missing evidence")
            if assessment.status != "not_observed" and not assessment.evidence_ids:
                raise ProjectError("invalid_critique", "Observed criteria require image evidence")
        return self

    @model_validator(mode="after")
    def consistent_action(self) -> Self:
        match self.decision:
            case "refine":
                if not self.preserve or not self.changes or self.next_direction_id is not None:
                    raise ProjectError(
                        "invalid_critique", "Refine requires preserve and 1-2 changes"
                    )
            case "reframe" | "reject":
                if self.next_direction_id is None or self.changes:
                    raise ProjectError(
                        "invalid_critique", "Reframe/reject requires a new direction"
                    )
            case "ready":
                if self.unresolved or any(item.status != "pass" for item in self.assessments):
                    raise ProjectError("unresolved_quality", "Ready requires all observed passes")
                if self.changes or self.next_direction_id is not None:
                    raise ProjectError("invalid_critique", "Ready cannot request more generation")
            case "stop":
                if self.changes or self.next_direction_id is not None:
                    raise ProjectError("invalid_critique", "Stop cannot request more generation")
            case _:
                assert_never(self.decision)
        return self
