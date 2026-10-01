"""Bind host-written critiques to immutable artifacts and inspected view files."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, assert_never

from logo_helper.images import inspect_png
from logo_helper.model_base import ArtifactId, ProjectError
from logo_helper.storage import read_source, safe_path

if TYPE_CHECKING:
    from logo_helper.models import Artifact, Session
    from logo_helper.quality_models import Critique, ViewEvidence
    from logo_helper.quality_state import QualityLoop, StepFailure, StepRequest
    from logo_helper.storage import Store


def verify_request(store: Store, source: Session, request: StepRequest) -> None:
    """Check a historical reservation without replacing its captured palette intent."""
    planned = request.input
    if any(item.created_at.tzinfo is None for item in source.artifacts):
        raise ProjectError(
            "invalid_state", "Source artifact timestamps require an explicit timezone"
        )
    snapshot = tuple(item.id for item in source.artifacts if item.created_at <= request.created_at)
    if (
        planned.session_id != source.id
        or planned.revision != request.source_revision
        or request.source_revision > source.revision
        or request.source_artifact_ids != snapshot
        or len(set(snapshot)) != len(request.source_artifact_ids)
        or not planned.prompt.strip()
    ):
        raise ProjectError("invalid_request", "Reservation source snapshot does not match")
    if any(
        item.created_at > request.created_at
        for item in source.artifacts[: len(request.source_artifact_ids)]
    ):
        raise ProjectError("invalid_request", "Reservation includes an artifact from its future")
    if (planned.palette_id is None) != (planned.palette_digest is None) or (
        planned.palette_id is not None
        and source.palette(planned.palette_id).digest != planned.palette_digest
    ):
        raise ProjectError("invalid_request", "Reservation palette ID and digest must match")
    if planned.requested_background not in (None, request.expected_background):
        raise ProjectError("invalid_request", "Reservation background intent differs")
    if planned.parent_id is None:
        if (
            planned.mode != "generation"
            or planned.parent_image_path is not None
            or planned.parent_requested_background is not None
            or request.parent_sha256 is not None
            or request.expected_background != source.brief.background
            or planned.lockup != source.brief.lockup
            or planned.app_icon != source.brief.app_icon
        ):
            raise ProjectError("invalid_request", "Generation reservation has edit-only intent")
        return
    parent = source.artifact(planned.parent_id)
    expected_path = str(safe_path(store.session_dir(source.id), parent.path))
    background = parent.effective_background(source.brief)
    if (
        planned.mode != "edit"
        or parent.id not in request.source_artifact_ids
        or planned.parent_image_path != expected_path
        or request.parent_sha256 != parent.sha256
        or planned.parent_requested_background != background
        or request.expected_background != background
        or planned.palette_id != parent.palette_id
        or planned.lockup != parent.lockup
        or planned.app_icon != parent.app_icon
    ):
        raise ProjectError(
            "invalid_request", "Edit reservation does not preserve its parent intent"
        )


def _verify_view(store: Store, source: Session, artifact: Artifact, evidence: ViewEvidence) -> None:
    path = safe_path(store.root, evidence.path)
    data = read_source(path)
    if (
        hashlib.sha256(data).hexdigest() != evidence.sha256
        or evidence.source_artifact_sha256 != artifact.sha256
    ):
        raise ProjectError("hash_mismatch", "Review evidence no longer matches its bound bytes")
    facts = inspect_png(data)
    if evidence.kind == "original":
        original = safe_path(store.session_dir(source.id), artifact.path)
        if path != original or evidence.sha256 != artifact.sha256:
            raise ProjectError("invalid_evidence", "Original evidence must reference the artifact")
    if evidence.kind == "target_size" and (
        evidence.target_width is None
        or evidence.target_width != facts.width
        or facts.width >= artifact.image.width
    ):
        raise ProjectError("invalid_evidence", "Target-size view requires a smaller decoded width")


def _verify_observations(critique: Critique) -> None:
    evidence = {item.id: item for item in critique.evidence}
    if not any(item.kind == "original" for item in critique.evidence):
        raise ProjectError("invalid_evidence", "Critique must include the original artifact view")
    for assessment in critique.assessments:
        if assessment.status == "not_observed":
            continue
        kinds = {evidence[item].kind for item in assessment.evidence_ids}
        if not kinds:
            raise ProjectError("invalid_evidence", "Observed criteria require an inspected view")
        if assessment.criterion == "use_size" and assessment.status == "pass":
            if "target_size" not in kinds:
                raise ProjectError("invalid_evidence", "Use-size pass needs a target-size view")
        elif assessment.criterion == "versatility" and assessment.status == "pass":
            if not kinds.intersection({"context", "one_color", "inverse"}):
                raise ProjectError("invalid_evidence", "Versatility pass needs an application view")
        elif not kinds.intersection({"original", "target_size", "context", "one_color", "inverse"}):
            raise ProjectError(
                "invalid_evidence", "Criterion requires an appropriate inspected view"
            )


def verify_critique(store: Store, state: QualityLoop, critique: Critique) -> None:
    """Verify provenance, never claim a hash proves a view was inspected or rendered correctly."""
    verified = type(critique).model_validate_json(critique.model_dump_json())
    source = store.load(state.contract.session_id)
    if verified.request_number > len(state.requests):
        raise ProjectError("invalid_critique", "Critique has no reserved native call")
    request = state.requests[verified.request_number - 1]
    verify_request(store, source, request)
    artifact = source.artifact(ArtifactId(verified.artifact_id))
    if verified not in state.critiques and source.revision != request.source_revision + 1:
        raise ProjectError(
            "stale_revision", "Critique requires exactly the reserved import mutation"
        )
    position = len(request.source_artifact_ids)
    planned = request.input
    if (
        artifact.id in request.source_artifact_ids
        or position >= len(source.artifacts)
        or source.artifacts[position].id != artifact.id
        or artifact.created_at < request.created_at
        or source.revision <= request.source_revision
        or artifact.sha256 != verified.artifact_sha256
        or artifact.prompt != planned.prompt
        or artifact.parent_id != planned.parent_id
        or artifact.effective_background(source.brief) != request.expected_background
        or artifact.palette_id != planned.palette_id
        or artifact.lockup != planned.lockup
        or artifact.app_icon != planned.app_icon
    ):
        raise ProjectError("invalid_critique", "Returned artifact does not match the reserved call")
    if verified.next_direction_id is not None:
        directions = {item.id for item in state.contract.directions}
        if (
            verified.next_direction_id not in directions
            or verified.next_direction_id == request.direction_id
        ):
            raise ProjectError(
                "invalid_critique", "Reframe/reject requires another known direction"
            )
    for evidence in verified.evidence:
        _verify_view(store, source, artifact, evidence)
    _verify_observations(verified)
    verify_action(state, verified)


def verify_action(state: QualityLoop, critique: Critique) -> None:
    """Replay decisions against their historical request, not the latest session candidate."""
    request = state.requests[critique.request_number - 1]
    edited = request.input.parent_id is not None
    if edited == (critique.change_result == "initial"):
        raise ProjectError(
            "invalid_critique", "Change result must distinguish initial and edited artifacts"
        )
    if (
        edited
        and critique.decision in {"refine", "ready"}
        and (critique.change_result != "improved" or critique.preservation_result != "pass")
    ):
        raise ProjectError(
            "edit_not_improved",
            "Further refinement or readiness requires observed improvement and preserved intent",
        )
    if critique.next_direction_id is not None and critique.next_direction_id in {
        item.direction_id for item in state.requests[: critique.request_number]
    }:
        raise ProjectError("repeated_direction", "Reframe/reject must choose an unused direction")
    if critique.decision == "refine":
        prior = next(
            (
                item
                for item in state.critiques
                if item.artifact_id == request.input.parent_id
                and item.request_number < critique.request_number
            ),
            None,
        )
        if prior is not None:
            unresolved = {
                (item.criterion, item.issue_id)
                for item in critique.assessments
                if item.status == "revise"
            }
            repeated = unresolved & {
                (item.criterion, item.issue_id)
                for item in prior.assessments
                if item.status == "revise"
            }
            if repeated:
                raise ProjectError(
                    "stalled_refinement", "Repeated unresolved criteria require reframe or stop"
                )


def verify_continuation(state: QualityLoop, request: StepRequest) -> None:
    """Require each persisted request to implement its preceding recorded decision."""
    prior = next(
        (item for item in reversed(state.critiques) if item.request_number < request.number), None
    )
    parent_id = None
    direction_id = request.direction_id
    if prior is not None:
        match prior.decision:
            case "refine":
                parent_id = prior.artifact_id
                direction_id = state.requests[prior.request_number - 1].direction_id
            case "reframe" | "reject":
                direction_id = prior.next_direction_id
            case "ready" | "stop":
                raise ProjectError("invalid_state", "A terminal critique cannot start another call")
            case _:
                assert_never(prior.decision)
    if request.input.parent_id != parent_id or request.direction_id != direction_id:
        raise ProjectError("invalid_request", "Reservation contradicts its preceding critique")


def verify_failure(source: Session, request: StepRequest, failure: StepFailure) -> None:
    position = len(request.source_artifact_ids)
    if failure.outcome != "failed" or position >= len(source.artifacts):
        return
    candidate = source.artifacts[position]
    if (
        request.created_at <= candidate.created_at <= failure.created_at
        and candidate.prompt == request.input.prompt
        and candidate.parent_id == request.input.parent_id
    ):
        raise ProjectError(
            "returned_result", "An imported result requires critique, not a failed-call label"
        )
