"""Evidence-only reconciliation and explicit, bounded interrupted-critique continuation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final, assert_never

from pydantic import ValidationError

from .checks import candidate_by_id
from .engine_jobs import is_superseded, unresolved_jobs
from .engine_production import apply_plan, attach_critiques, attach_image, critique
from .engine_steps import advance, job_by_id, put_job
from .helper_delivery import verified_delivery
from .models import StudioError
from .models_base import CRITIQUE_LIMIT, ROLE_COUNT

if TYPE_CHECKING:
    from .engine_steps import Steps
    from .models import Job, Workflow

REASON_LIMIT: Final = 2000


def can_resume_critique(state: Workflow) -> bool:
    """Inspect saved eligibility only; the caller must explicitly request continuation."""
    if state.phase != "outcome_unknown" or state.delivery is not None or state.strategy is None:
        return False
    pending = unresolved_jobs(state)
    if len(pending) != 1:
        return False
    job = pending[0]
    if job.kind != "critique" or job.status != "unknown" or job.critiques:
        return False
    originals = tuple(candidate for candidate in state.candidates if candidate.parent_id is None)
    if len(originals) != state.brief.effective_count or {
        (candidate.direction_id, candidate.candidate_slot) for candidate in originals
    } != {
        (direction.id, slot)
        for direction in state.directions
        for slot in range(1, state.brief.candidates_per_direction + 1)
    }:
        return False
    return (
        state.call_budget.review_llm_calls_reserved + ROLE_COUNT
        <= state.brief.effective_review_call_budget
        and any(
            candidate.id == job.candidate_id and not candidate.critiques
            for candidate in state.candidates
        )
        and sum(
            prior.kind == "critique" and prior.candidate_id == job.candidate_id
            for prior in state.jobs
        )
        < CRITIQUE_LIMIT
    )


def resume_critique(steps: Steps, state: Workflow) -> Workflow:
    if not can_resume_critique(state):
        return state
    job = unresolved_jobs(state)[0]
    if job.candidate_id is None:
        raise StudioError("invalid_job", "Interrupted critique has no candidate")
    candidate = candidate_by_id(state, job.candidate_id)
    return critique(steps, state, candidate, retry_of=job.id)


def interrupt(steps: Steps, state: Workflow, reason: str) -> Workflow:
    if not reason.strip() or len(reason) > REASON_LIMIT:
        raise StudioError("invalid_reason", "Interruption requires a bounded nonblank reason")
    if state.phase == "delivered":
        return state
    with steps.store.locked(state.id):
        current = steps.store.expect(state.id, state.revision)
        jobs = tuple(
            job.model_copy(update={"status": "unknown", "error": reason})
            if job.status in {"reserved", "returned"}
            else job
            for job in current.jobs
        )
        interrupted = current.model_copy(update={"jobs": jobs})
        unknown = any(job.status == "unknown" for job in unresolved_jobs(interrupted))
        updated = current.model_copy(
            update={
                "jobs": jobs,
                "phase": "outcome_unknown" if unknown else "cancelled",
                "last_error": reason,
            }
        )
        return steps.store.save(advance(updated))


def _has_evidence(job: Job) -> bool:
    match job.kind:
        case "plan":
            return job.plan is not None
        case "generate" | "edit":
            return job.generated is not None and job.image_sha256 is not None
        case "critique":
            return bool(job.critiques)
        case "deliver":
            return job.output_path is not None
        case _:
            assert_never(job.kind)


def _recover(steps: Steps, state: Workflow, job: Job) -> Workflow:
    match job.kind:
        case "plan":
            return apply_plan(steps, state, job)
        case "generate" | "edit":
            return attach_image(steps, state, job)
        case "critique":
            return attach_critiques(steps, state, job)
        case "deliver":
            if job.output_path is None:
                raise StudioError("invalid_job", "No recorded export destination")
            receipt = verified_delivery(steps.helper, state, job.output_path)
            updated = put_job(state, job.model_copy(update={"status": "succeeded"}))
            return steps.commit(
                updated.model_copy(
                    update={"delivery": receipt, "phase": "delivered", "last_error": None}
                )
            )
        case _:
            assert_never(job.kind)


def reconcile(steps: Steps, state: Workflow, job_id: str) -> Workflow:
    job = job_by_id(state, job_id)
    if job.status == "reserved":
        raise StudioError("busy", "Settle and interrupt the owned runner before reconciliation")
    if is_superseded(state, job.id) or job.status == "succeeded" or not _has_evidence(job):
        return state
    try:
        current = _recover(steps, state, job)
    except (StudioError, OSError, ValidationError) as error:
        return steps.fail(state, job, error)
    if current.delivery is not None:
        return current
    phase = (
        "outcome_unknown"
        if any(item.status == "unknown" for item in unresolved_jobs(current))
        else "awaiting_choice"
        if current.candidates
        else "draft"
    )
    return steps.commit(current.model_copy(update={"phase": phase, "last_error": None}))
