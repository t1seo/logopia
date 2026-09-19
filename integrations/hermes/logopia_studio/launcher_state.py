"""Preflight and verify durable state instead of trusting Hermes prose."""

from __future__ import annotations

from typing import TYPE_CHECKING, assert_never

from .engine_jobs import unresolved_jobs
from .engine_recovery import can_resume_critique
from .host_requests import (
    ContinueRequest,
    DeliverRequest,
    ReconcileRequest,
    StartRequest,
    StatusRequest,
)
from .launcher_process import LaunchError
from .models import FeedbackEnvelope, StudioError

if TYPE_CHECKING:
    from pathlib import Path

    from .engine import Studio
    from .launcher_requests import Request
    from .models import Critique, GeneratedImage, PlanResult, ReviewInput, StudioBrief, Workflow


class NoInferenceHost:
    """The CLI's status/interrupt instance cannot dispatch a model or an image."""

    def plan(self, brief: StudioBrief) -> PlanResult:
        del brief
        raise LaunchError("inference_forbidden", "This local operation cannot plan")

    def generate(self, prompt: str, parent: Path | None, background: str) -> GeneratedImage:
        del prompt, parent, background
        raise LaunchError("inference_forbidden", "This local operation cannot generate")

    def critique(self, request: ReviewInput) -> tuple[Critique, ...]:
        del request
        raise LaunchError("inference_forbidden", "This local operation cannot critique")


def existing_state(studio: Studio, workflow_id: str) -> Workflow | None:
    try:
        return studio.status(workflow_id)
    except StudioError as error:
        if error.code != "not_found":
            raise
        return None


def _idle(state: Workflow) -> None:
    if state.phase in {"cancelled", "outcome_unknown"}:
        raise LaunchError(state.phase, "Inspect saved state; do not resubmit an unresolved request")
    pending = unresolved_jobs(state)
    if any(job.status == "unknown" for job in pending):
        raise LaunchError("outcome_unknown", "A saved job needs explicit reconciliation")
    if any(job.status in {"reserved", "returned"} for job in pending):
        raise LaunchError("workflow_busy", "A saved job is active or awaits reconciliation")


def preflight(studio: Studio, request: Request) -> Workflow | None:
    state = existing_state(studio, request.workflow_id)
    match request:
        case StartRequest():
            if state is not None:
                if state.brief != request.brief:
                    raise LaunchError("conflict", "Workflow ID already has a different brief")
                _idle(state)
            return state
        case StatusRequest():
            if state is None:
                raise LaunchError("workflow_missing", "No saved workflow exists for this ID")
            return state
        case ContinueRequest() | DeliverRequest() | ReconcileRequest() | FeedbackEnvelope():
            if state is None:
                raise LaunchError("workflow_missing", "No saved workflow exists for this ID")
            if state.revision != request.expected_revision:
                raise LaunchError(
                    "stale_revision",
                    f"Expected {request.expected_revision}; saved {state.revision}",
                )
            _preflight_action(request, state)
            return state
        case _:
            assert_never(request)


def _preflight_action(
    request: ContinueRequest | DeliverRequest | ReconcileRequest | FeedbackEnvelope,
    state: Workflow,
) -> None:
    match request:
        case FeedbackEnvelope():
            candidate = next((c for c in state.candidates if c.id == request.candidate_id), None)
            if candidate is None or candidate.sha256 != request.candidate_sha256:
                raise LaunchError("stale_candidate", "Candidate ID/hash differs from saved state")
            _idle(state)
        case ReconcileRequest():
            if not any(job.id == request.job_id for job in state.jobs):
                raise LaunchError("unknown_job", "Reconciliation must name an exact saved job")
        case ContinueRequest():
            if not can_resume_critique(state):
                _idle(state)
        case DeliverRequest():
            _idle(state)
        case _:
            assert_never(request)


def _produced(state: Workflow) -> bool:
    originals = tuple(c for c in state.candidates if c.parent_id is None)
    return (
        state.phase in {"awaiting_choice", "ready", "delivered"}
        and state.strategy is not None
        and len(state.directions) == state.brief.effective_direction_count
        and len(originals) == state.brief.effective_count
        and {(c.direction_id, c.candidate_slot) for c in originals}
        == {
            (d.id, slot)
            for d in state.directions
            for slot in range(1, state.brief.candidates_per_direction + 1)
        }
        and all(
            {review.role for review in c.critiques} == {"design", "production"} for c in originals
        )
    )


def _postcondition(request: Request, before: Workflow | None, state: Workflow) -> bool:
    changed = before is not None and state.revision > before.revision
    prior_selection = before.selected_id if before is not None else None
    match request:
        case StartRequest():
            valid = (
                state.brief == request.brief
                and _produced(state)
                and state.selected_id == prior_selection
            )
        case ContinueRequest():
            valid = _produced(state) and state.selected_id == prior_selection
        case StatusRequest():
            valid = True
        case FeedbackEnvelope():
            valid = _feedback_result(request, before, state)
        case DeliverRequest():
            valid = (
                state.phase == "delivered"
                and state.delivery is not None
                and before is not None
                and state.delivery.artifact_id == before.selected_id
                and (changed or state.delivery == before.delivery)
            )
        case ReconcileRequest():
            valid = any(
                job.id == request.job_id and job.status == "succeeded" for job in state.jobs
            )
        case _:
            assert_never(request)
    return valid


def _feedback_result(request: FeedbackEnvelope, before: Workflow | None, state: Workflow) -> bool:
    if before is None:
        return False
    changed = state.revision > before.revision
    match request.action:
        case "choose":
            return state.selected_id == request.candidate_id and (
                changed or (before.delivery == state.delivery and state.phase == "delivered")
            )
        case "revise":
            previous_ids = {c.id for c in before.candidates}
            children = tuple(c for c in state.candidates if c.id not in previous_ids)
            return (
                changed
                and len(children) == 1
                and children[0].parent_id == request.candidate_id
                and children[0].keep == request.keep
                and children[0].change == request.change
                and {r.role for r in children[0].critiques} == {"design", "production"}
                and state.selected_id == before.selected_id
            )
        case _:
            assert_never(request.action)


def verify_result(request: Request, before: Workflow | None, state: Workflow) -> None:
    if state.id != request.workflow_id:
        raise LaunchError("postcondition_failed", "Saved workflow ID differs from the request")
    if before is not None and (state.brief != before.brief or state.revision < before.revision):
        raise LaunchError("postcondition_failed", "Saved intent/revision regressed")
    if state.phase in {"failed", "outcome_unknown", "cancelled"}:
        raise LaunchError(state.phase, (state.last_error or "Workflow did not complete")[:1000])
    if not _postcondition(request, before, state):
        raise LaunchError(
            "postcondition_failed", "Hermes exited without the requested saved result"
        )
