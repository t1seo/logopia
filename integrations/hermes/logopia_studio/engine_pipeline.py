"""Explicit continuation through agreed directions and bounded critique attempts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError

from .engine_jobs import is_superseded
from .engine_production import attach_image, critique, generate, plan_once
from .engine_recovery import can_resume_critique, resume_critique
from .engine_steps import digest, is_paused
from .models import Job, StudioError
from .prompts import image_prompt

if TYPE_CHECKING:
    from .engine_steps import Steps
    from .models import Direction, Workflow


def _produce_direction(steps: Steps, state: Workflow, direction: Direction, slot: int) -> Workflow:
    if any(
        item.direction_id == direction.id and item.candidate_slot == slot and item.parent_id is None
        for item in state.candidates
    ):
        return state
    jobs = tuple(
        item
        for item in state.jobs
        if item.kind == "generate"
        and item.direction_id == direction.id
        and item.candidate_slot == slot
    )
    if jobs:
        job = jobs[0]
        if job.generated is None or job.image_sha256 is None:
            return state
        try:
            return attach_image(steps, state, job)
        except (StudioError, OSError, ValidationError) as error:
            return steps.fail(state, job, error)
    variation = next((item for item in direction.variations if item.slot == slot), None)
    prompt = image_prompt(
        state.brief, direction, variation, state.reference_analysis, strategy=state.strategy
    )
    job = Job(
        id=f"j{len(state.jobs) + 1}",
        kind="generate",
        candidate_id=f"c{len(state.candidates) + 1}",
        direction_id=direction.id,
        candidate_slot=slot,
        changed_variables=variation.changed_variables if variation is not None else (),
        references=state.brief.references,
        reference_conditioning="text" if state.brief.references else "none",
        design_spec=direction.design_spec,
        reference_analysis=state.reference_analysis,
        prompt=prompt,
        request_sha256=digest(prompt + state.brief.model_dump_json()),
    )
    return generate(steps, state, job)


def produce(steps: Steps, state: Workflow) -> Workflow:
    if can_resume_critique(state):
        resumed = resume_critique(steps, state)
        if resumed.phase in {"failed", "outcome_unknown", "cancelled", "ready", "delivered"}:
            return resumed
        return _review_sequence(steps, resumed)
    if is_paused(state) or state.phase in {"ready", "delivered"}:
        return state
    if any(job.status in {"reserved", "returned"} for job in state.jobs):
        raise StudioError("busy", "An in-flight operation requires explicit reconciliation")
    _ = steps.helper.ensure(state)
    current = state
    if current.strategy is None:
        if any(job.kind == "plan" for job in current.jobs):
            return current
        current = plan_once(steps, current)
        if current.strategy is None or is_paused(current):
            return current
    return _planned_sequence(steps, current)


def _planned_sequence(steps: Steps, state: Workflow) -> Workflow:
    current = state
    for direction in current.directions:
        for slot in range(1, current.brief.candidates_per_direction + 1):
            if any(
                item.direction_id == direction.id
                and item.candidate_slot == slot
                and item.parent_id is None
                for item in current.candidates
            ):
                continue
            current = _produce_direction(steps, current, direction, slot)
            if current.phase in {"failed", "outcome_unknown", "cancelled"}:
                return current
    return _review_sequence(steps, current)


def _review_sequence(steps: Steps, state: Workflow) -> Workflow:
    current = state
    for candidate in current.candidates:
        if not candidate.critiques:
            attempt_id = f"j{len(current.jobs) + 1}"
            current = critique(steps, current, candidate)
            if is_superseded(current, attempt_id) or current.phase in {
                "failed",
                "outcome_unknown",
                "cancelled",
                "ready",
                "delivered",
            }:
                return current
    if current.phase == "awaiting_choice":
        return current
    return steps.commit(current.model_copy(update={"phase": "awaiting_choice", "last_error": None}))
