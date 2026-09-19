"""Stable public model API consumed by the host, engine and gallery."""

from typing import Annotated, Literal, Self, TypeAlias

from pydantic import Field, model_validator

from .models_base import (
    CRITIQUE_LIMIT,
    EDIT_LIMIT,
    ROLE_COUNT,
    Digest,
    FrozenModel,
    Identifier,
    Note,
    Prompt,
    Revision,
    SchemaVersion,
    StudioError,
    Text,
)
from .models_brief import Direction, PlanResult, Strategy, StudioBrief
from .models_budget import CallBudget
from .models_jobs import Delivery, Feedback, Job, validate_retry_links
from .models_references import DesignSpecification, ReferenceAnalysis, StudioReference
from .models_review import Criterion, Critique, FeedbackEnvelope, GeneratedImage, ReviewInput

__all__ = [
    "Candidate",
    "Criterion",
    "Critique",
    "Delivery",
    "Direction",
    "Feedback",
    "FeedbackEnvelope",
    "GeneratedImage",
    "Job",
    "Phase",
    "PlanResult",
    "ReviewInput",
    "Strategy",
    "StudioBrief",
    "StudioError",
    "Workflow",
]

Phase: TypeAlias = Literal[
    "draft",
    "planning",
    "generating",
    "reviewing",
    "awaiting_choice",
    "revising",
    "ready",
    "delivered",
    "failed",
    "outcome_unknown",
    "cancelled",
]


class Candidate(FrozenModel):
    """One immutable canonical original and its own critique evidence."""

    id: Identifier
    direction_id: Identifier
    candidate_slot: Annotated[int, Field(ge=1, le=3)] = 1
    changed_variables: Annotated[tuple[Text, ...], Field(max_length=6)] = ()
    references: Annotated[tuple[StudioReference, ...], Field(max_length=6)] = ()
    reference_conditioning: Literal["none", "text"] = "none"
    design_spec: DesignSpecification | None = None
    reference_analysis: Annotated[tuple[ReferenceAnalysis, ...], Field(max_length=6)] = ()
    parent_id: Identifier | None
    image_path: Text
    sha256: Digest
    width: Annotated[int, Field(gt=0)]
    height: Annotated[int, Field(gt=0)]
    prompt: Prompt
    provider: Text
    model: Text
    critiques: Annotated[tuple[Critique, ...], Field(max_length=2)] = ()
    keep: Annotated[tuple[Text, ...], Field(max_length=20)] = ()
    change: Note = ""


class Workflow(FrozenModel):
    """Strict sidecar; original helper session schema remains unchanged."""

    schema_version: SchemaVersion = 1
    id: Identifier
    revision: Revision = 0
    brief: StudioBrief
    phase: Phase = "draft"
    strategy: Strategy | None = None
    directions: Annotated[tuple[Direction, ...], Field(max_length=6)] = ()
    candidates: Annotated[tuple[Candidate, ...], Field(max_length=11)] = ()
    selected_id: Identifier | None = None
    jobs: Annotated[tuple[Job, ...], Field(max_length=35)] = ()
    feedback: Annotated[tuple[Feedback, ...], Field(max_length=2)] = ()
    delivery: Delivery | None = None
    last_error: Annotated[str, Field(max_length=64000)] | None = None

    @property
    def call_budget(self) -> CallBudget:
        review_jobs = tuple(job for job in self.jobs if job.kind == "critique")
        return CallBudget(
            initial_images_reserved=sum(job.kind == "generate" for job in self.jobs),
            initial_image_limit=self.brief.effective_count,
            edit_images_reserved=sum(job.kind == "edit" for job in self.jobs),
            edit_image_limit=EDIT_LIMIT,
            planning_llm_calls_reserved=ROLE_COUNT * sum(job.kind == "plan" for job in self.jobs),
            review_llm_calls_reserved=ROLE_COUNT * len(review_jobs),
            review_llm_call_limit=self.brief.effective_review_call_budget,
            explicit_review_recoveries=len(review_jobs)
            - len({job.candidate_id for job in review_jobs}),
        )

    @property
    def reference_analysis(self) -> tuple[ReferenceAnalysis, ...]:
        return next((job.plan.reference_analysis for job in self.jobs if job.plan is not None), ())

    @model_validator(mode="after")
    def consistent_graph(self) -> Self:
        directions = {item.id for item in self.directions}
        if len(directions) != len(self.directions) or (
            self.directions and len(directions) != self.brief.effective_direction_count
        ):
            raise StudioError("invalid_state", "Direction count/identity differs from saved brief")
        seen: set[str] = set()
        original_slots: set[tuple[str, int]] = set()
        for candidate in self.candidates:
            if (
                candidate.id in seen
                or candidate.direction_id not in directions
                or (candidate.parent_id is not None and candidate.parent_id not in seen)
            ):
                raise StudioError("invalid_state", "Invalid candidate lineage")
            expected = f".logo-generator/sessions/{self.id}/artifacts/{candidate.id}.png"
            if candidate.image_path != expected:
                raise StudioError(
                    "invalid_state", "Candidate path differs from its deterministic artifact"
                )
            seen.add(candidate.id)
            if candidate.candidate_slot > self.brief.candidates_per_direction:
                raise StudioError("invalid_state", "Candidate slot exceeds the saved exploration")
            if candidate.parent_id is None:
                slot = (candidate.direction_id, candidate.candidate_slot)
                if slot in original_slots:
                    raise StudioError("invalid_state", "Duplicate original candidate slot")
                original_slots.add(slot)
        if self.selected_id is not None and self.selected_id not in seen:
            raise StudioError("invalid_state", "Selection does not exist")
        if self.delivery is not None and self.delivery.artifact_id != self.selected_id:
            raise StudioError("invalid_state", "Delivery differs from explicit selection")
        return self

    @model_validator(mode="after")
    def bounded_jobs(self) -> Self:
        if self.call_budget.review_llm_calls_reserved > self.brief.effective_review_call_budget:
            raise StudioError("invalid_state", "Review LLM call budget exceeded")
        validate_retry_links(self.jobs, {candidate.id for candidate in self.candidates})
        if len({job.id for job in self.jobs}) != len(self.jobs):
            raise StudioError("invalid_state", "Duplicate job identity")
        if sum(job.kind == "plan" for job in self.jobs) > 1:
            raise StudioError("invalid_state", "Planning attempt budget exceeded")
        if sum(job.kind == "edit" for job in self.jobs) > EDIT_LIMIT:
            raise StudioError("invalid_state", "Edit attempt budget exceeded")
        if sum(job.kind == "generate" for job in self.jobs) > self.brief.effective_count:
            raise StudioError("invalid_state", "Initial image attempt budget exceeded")
        generated_slots = [
            (job.direction_id, job.candidate_slot) for job in self.jobs if job.kind == "generate"
        ]
        if len(set(generated_slots)) != len(generated_slots):
            raise StudioError("invalid_state", "A generation slot cannot be dispatched twice")
        for candidate in self.candidates:
            if (
                sum(
                    job.kind == "critique" and job.candidate_id == candidate.id for job in self.jobs
                )
                > CRITIQUE_LIMIT
            ):
                raise StudioError("invalid_state", "Critique attempt budget exceeded")
        return self
