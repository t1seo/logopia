"""Durable attempt reservations and exact recovery evidence."""

from typing import Annotated, Literal, TypeAlias

from pydantic import Field

from .models_base import Digest, FrozenModel, Identifier, Note, Prompt, Receipt, StudioError, Text
from .models_brief import PlanResult
from .models_references import DesignSpecification, ReferenceAnalysis, StudioReference
from .models_review import Critique, GeneratedImage

JobKind: TypeAlias = Literal["plan", "generate", "edit", "critique", "deliver"]
JobStatus: TypeAlias = Literal["reserved", "returned", "succeeded", "failed", "unknown"]


class Job(FrozenModel):
    """A reservation counts even when its native result is unknown or failed."""

    id: Identifier
    kind: JobKind
    status: JobStatus = "reserved"
    request_sha256: Digest
    candidate_id: Identifier | None = None
    retry_of: Identifier | None = None
    direction_id: Identifier | None = None
    candidate_slot: Annotated[int, Field(ge=1, le=3)] = 1
    changed_variables: Annotated[tuple[Text, ...], Field(max_length=6)] = ()
    references: Annotated[tuple[StudioReference, ...], Field(max_length=6)] = ()
    reference_conditioning: Literal["none", "text"] = "none"
    design_spec: DesignSpecification | None = None
    reference_analysis: Annotated[tuple[ReferenceAnalysis, ...], Field(max_length=6)] = ()
    parent_id: Identifier | None = None
    prompt: Prompt | None = None
    keep: Annotated[tuple[Text, ...], Field(max_length=20)] = ()
    change: Note = ""
    generated: GeneratedImage | None = None
    image_sha256: Digest | None = None
    plan: PlanResult | None = None
    critiques: Annotated[tuple[Critique, ...], Field(max_length=2)] = ()
    raw_reports: Annotated[tuple[Receipt, ...], Field(max_length=2)] = ()
    output_path: Note | None = None
    error: Receipt | None = None


class Delivery(FrozenModel):
    """Verified original/package hashes attached after the helper commit."""

    path: Text
    artifact_id: Identifier
    image_sha256: Digest
    zip_path: Text
    zip_sha256: Digest
    manifest_sha256: Digest


class Feedback(FrozenModel):
    """Exact saved keep/change request for a dispatched edit."""

    candidate_id: Identifier
    keep: Annotated[tuple[Text, ...], Field(max_length=20)]
    change: Note


def validate_retry_links(jobs: tuple[Job, ...], candidate_ids: set[str]) -> None:
    previous: dict[str, Job] = {}
    replaced: set[str] = set()
    for job in jobs:
        if job.retry_of is not None:
            old = previous.get(job.retry_of)
            if (
                job.kind != "critique"
                or old is None
                or old.kind != "critique"
                or old.status != "unknown"
                or old.critiques
                or old.retry_of is not None
                or old.id in replaced
                or job.candidate_id not in candidate_ids
                or job.candidate_id != old.candidate_id
                or job.request_sha256 != old.request_sha256
            ):
                raise StudioError(
                    "invalid_retry", "A retry must reference its exact unknown critique"
                )
            replaced.add(old.id)
        previous[job.id] = job
