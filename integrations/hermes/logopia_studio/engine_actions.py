"""Explicit edits, choices and gated existing-helper delivery."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError

from .checks import candidate_by_id, unmet_criteria
from .engine_jobs import is_superseded, unresolved_jobs
from .engine_production import critique, generate
from .engine_steps import digest, is_paused, job_by_id, put_job
from .helper_delivery import export_job, verified_delivery
from .models import Job, StudioError
from .models_base import EDIT_LIMIT, ROLE_COUNT
from .prompts import edit_prompt

if TYPE_CHECKING:
    from .engine_steps import Steps
    from .models import Workflow


def require_idle(state: Workflow) -> None:
    if unresolved_jobs(state):
        raise StudioError("busy", "An operation is active or has an unresolved outcome")
    if state.phase == "cancelled":
        raise StudioError("cancelled", "Workflow was explicitly interrupted")


def revise(
    steps: Steps, state: Workflow, candidate_id: str, keep: tuple[str, ...], change: str
) -> Workflow:
    require_idle(state)
    if state.delivery is not None:
        raise StudioError("already_delivered", "Start a separate workflow after delivery")
    parent = candidate_by_id(state, candidate_id)
    if not change.strip():
        raise StudioError("invalid_feedback", "Revision requires nonblank change")
    attempts = sum(job.kind == "edit" for job in state.jobs)
    if attempts >= EDIT_LIMIT:
        raise StudioError("edit_limit", "Two dispatched edit calls have already been consumed")
    if (
        state.call_budget.review_llm_calls_reserved + ROLE_COUNT
        > state.brief.effective_review_call_budget
    ):
        raise StudioError("review_limit", "No two-call critique budget remains for a new edit")
    prompt = edit_prompt(state.brief, parent.prompt, keep, change)
    job = Job(
        id=f"j{len(state.jobs) + 1}",
        kind="edit",
        candidate_id=f"e{attempts + 1}",
        direction_id=parent.direction_id,
        candidate_slot=parent.candidate_slot,
        changed_variables=(change,),
        references=parent.references,
        reference_conditioning=parent.reference_conditioning,
        design_spec=parent.design_spec,
        reference_analysis=parent.reference_analysis,
        parent_id=parent.id,
        prompt=prompt,
        keep=keep,
        change=change,
        request_sha256=digest(prompt + parent.sha256 + state.brief.model_dump_json()),
    )
    current = generate(steps, state, job)
    if current.phase in {"failed", "outcome_unknown", "cancelled"}:
        return current
    child = candidate_by_id(current, f"e{attempts + 1}")
    attempt_id = f"j{len(current.jobs) + 1}"
    current = critique(steps, current, child)
    if is_superseded(current, attempt_id) or current.phase in {
        "failed",
        "outcome_unknown",
        "cancelled",
        "ready",
        "delivered",
    }:
        return current
    return steps.commit(current.model_copy(update={"phase": "awaiting_choice", "last_error": None}))


def choose(steps: Steps, state: Workflow, candidate_id: str) -> Workflow:
    require_idle(state)
    candidate = candidate_by_id(state, candidate_id)
    if state.delivery is not None:
        if candidate.id == state.selected_id:
            return state
        raise StudioError("already_delivered", "Delivered selection is immutable")
    unmet = unmet_criteria(state, candidate)
    return steps.commit(
        state.model_copy(
            update={
                "selected_id": candidate.id,
                "phase": "awaiting_choice" if unmet else "ready",
                "last_error": "; ".join(unmet) if unmet else None,
            }
        )
    )


def deliver(steps: Steps, state: Workflow) -> Workflow:
    if state.selected_id is None:
        raise StudioError("selection_required", "An explicit candidate choice is required")
    unmet = unmet_criteria(state, candidate_by_id(state, state.selected_id))
    if unmet:
        raise StudioError("review_required", "; ".join(unmet))
    if state.delivery is not None:
        if verified_delivery(steps.helper, state, state.delivery.path) != state.delivery:
            raise StudioError("invalid_delivery", "Recorded package hashes differ")
        return state
    recovered = _previous_delivery(steps, state)
    if recovered is not None:
        return recovered
    require_idle(state)
    candidate = candidate_by_id(state, state.selected_id)
    job = Job(
        id=f"j{len(state.jobs) + 1}",
        kind="deliver",
        candidate_id=candidate.id,
        request_sha256=digest(candidate.model_dump_json()),
        output_path=f"output/logopia/{state.id}",
    )
    reserved = steps.reserve(state, job, "ready")
    try:
        receipt = export_job(steps.helper, reserved, job)
        current = steps.store.load(state.id)
        if is_paused(current):
            return current
        updated = put_job(current, job.model_copy(update={"status": "succeeded"}))
        return steps.commit(
            updated.model_copy(
                update={"delivery": receipt, "phase": "delivered", "last_error": None}
            )
        )
    except (StudioError, OSError, ValidationError) as error:
        return steps.fail(reserved, job_by_id(steps.store.load(state.id), job.id), error)


def _previous_delivery(steps: Steps, state: Workflow) -> Workflow | None:
    jobs = tuple(
        job for job in state.jobs if job.kind == "deliver" and job.candidate_id == state.selected_id
    )
    if jobs:
        job = jobs[-1]
        if job.status == "reserved":
            raise StudioError(
                "busy", "Delivery is active; interrupt settled runner before recovery"
            )
        if job.output_path is None:
            raise StudioError("invalid_job", "Delivery has no reserved destination")
        try:
            receipt = verified_delivery(steps.helper, state, job.output_path)
        except StudioError:
            require_idle(state)
        else:
            updated = put_job(state, job.model_copy(update={"status": "succeeded"}))
            return steps.commit(
                updated.model_copy(
                    update={"delivery": receipt, "phase": "delivered", "last_error": None}
                )
            )
    return None
