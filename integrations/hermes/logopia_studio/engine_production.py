"""Finite plan/image/critique steps with no automatic unknown-call retries."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

from pydantic import ValidationError

from .checks import candidate_by_id, review_input, verify_critiques
from .engine_jobs import is_superseded
from .engine_steps import digest, is_paused, job_by_id, put_job
from .host_references import reference_inputs
from .models import Candidate, Critique, Job, StudioError
from .models_base import CRITIQUE_LIMIT, ROLE_COUNT
from .store_files import read_file, safe_path

if TYPE_CHECKING:
    from .engine_steps import Steps
    from .models import Workflow


def apply_plan(steps: Steps, state: Workflow, job: Job) -> Workflow:
    if job.plan is None or len(job.plan.directions) != state.brief.effective_direction_count:
        raise StudioError("invalid_plan", "Planning direction count differs from agreed count")
    if state.brief.candidates_per_direction > 1 and any(
        {variant.slot for variant in direction.variations}
        != set(range(1, state.brief.candidates_per_direction + 1))
        for direction in job.plan.directions
    ):
        raise StudioError("invalid_plan", "Exploration requires explicit variables for every slot")
    updated = put_job(state, job.model_copy(update={"status": "succeeded"}))
    updated = updated.model_copy(
        update={"strategy": job.plan.strategy, "directions": job.plan.directions}
    )
    return steps.commit(updated)


def plan_once(steps: Steps, state: Workflow) -> Workflow:
    job = Job(
        id=f"j{len(state.jobs) + 1}",
        kind="plan",
        references=state.brief.references,
        reference_conditioning="text" if state.brief.references else "none",
        request_sha256=digest(state.brief.model_dump_json()),
    )
    reserved = steps.reserve(state, job, "planning")
    try:
        plan = steps.host.plan(reserved.brief)
        returned = job.model_copy(update={"status": "returned", "plan": plan})
        recorded = steps.record(reserved, returned)
        if is_paused(recorded):
            return recorded
        return apply_plan(steps, recorded, returned)
    except (StudioError, TimeoutError, OSError, ValidationError) as error:
        return steps.fail(reserved, job_by_id(steps.store.load(state.id), job.id), error)


def attach_image(steps: Steps, state: Workflow, job: Job) -> Workflow:
    candidate = steps.helper.import_job(state, job)
    existing = tuple(item for item in state.candidates if item.id == candidate.id)
    if existing and existing[0].model_copy(update={"critiques": ()}) != candidate:
        raise StudioError("helper_conflict", "Recovered import conflicts with saved candidate")
    updated = put_job(state, job.model_copy(update={"status": "succeeded"}))
    if not existing:
        updated = updated.model_copy(update={"candidates": (*updated.candidates, candidate)})
    return steps.commit(updated)


def generate(steps: Steps, state: Workflow, job: Job) -> Workflow:
    _ = reference_inputs(job.references)
    reserved = steps.reserve(state, job, "revising" if job.parent_id else "generating")
    if job.prompt is None:
        raise StudioError("invalid_job", "Generation requires an exact saved prompt")
    parent = candidate_by_id(state, job.parent_id) if job.parent_id else None
    path = safe_path(steps.store.root, parent.image_path) if parent else None
    try:
        result = steps.host.generate(job.prompt, path, state.brief.background)
        returned = job.model_copy(update={"status": "returned", "generated": result})
        recorded = steps.record(reserved, returned)

        image_sha = hashlib.sha256(read_file(result.path)).hexdigest()
        returned = returned.model_copy(update={"image_sha256": image_sha})
        recorded = steps.record(recorded, returned)
        if is_paused(recorded):
            return recorded
        return attach_image(steps, recorded, returned)
    except (StudioError, TimeoutError, OSError, ValidationError) as error:
        return steps.fail(reserved, job_by_id(steps.store.load(state.id), job.id), error)


def attach_critiques(steps: Steps, state: Workflow, job: Job) -> Workflow:
    if is_superseded(state, job.id):
        return state
    if job.candidate_id is None:
        raise StudioError("invalid_job", "Critique requires exact candidate")
    candidate = candidate_by_id(state, job.candidate_id)
    verify_critiques(review_input(steps.store.root, state, candidate), job.critiques)
    prior_calls = {
        report.call_id for prior in state.jobs if prior.id != job.id for report in prior.critiques
    }
    if any(report.call_id in prior_calls for report in job.critiques):
        raise StudioError("invalid_report", "Critique call identity was already used")
    reviewed = candidate.model_copy(update={"critiques": job.critiques})
    updated = put_job(state, job.model_copy(update={"status": "succeeded"}))
    return steps.commit(
        updated.model_copy(
            update={
                "candidates": tuple(
                    reviewed if item.id == reviewed.id else item for item in state.candidates
                )
            }
        )
    )


def critique(
    steps: Steps, state: Workflow, candidate: Candidate, *, retry_of: str | None = None
) -> Workflow:
    if (
        sum(job.kind == "critique" and job.candidate_id == candidate.id for job in state.jobs)
        >= CRITIQUE_LIMIT
    ):
        return state
    request = review_input(steps.store.root, state, candidate)
    job = Job(
        id=f"j{len(state.jobs) + 1}",
        kind="critique",
        candidate_id=candidate.id,
        retry_of=retry_of,
        request_sha256=(
            job_by_id(state, retry_of).request_sha256
            if retry_of is not None
            else digest(request.model_dump_json())
        ),
    )
    reserved = steps.reserve(state, job, "reviewing")
    try:
        reports = steps.host.critique(request)
        returned = returned_critiques(job, reports)
        recorded = steps.record(reserved, returned)
        if is_paused(recorded) or is_superseded(recorded, job.id):
            return recorded
        return attach_critiques(steps, recorded, returned)
    except (StudioError, TimeoutError, OSError, ValidationError) as error:
        return steps.fail(reserved, job_by_id(steps.store.load(state.id), job.id), error)


def returned_critiques(job: Job, reports: tuple[Critique, ...]) -> Job:
    raw = tuple(report.model_dump_json() for report in reports)
    if len(reports) != ROLE_COUNT:
        raise StudioError("invalid_report", "Expected exactly two role reports", ("\n".join(raw),))
    return job.model_copy(update={"status": "returned", "critiques": reports, "raw_reports": raw})
