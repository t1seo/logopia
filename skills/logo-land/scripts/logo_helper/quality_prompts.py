"""Translate recorded critique into the exact next native generation or edit prompt."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final, assert_never

from logo_helper.model_base import ArtifactId, ProjectError
from logo_helper.prompts import PromptResult, build_prompt

if TYPE_CHECKING:
    from logo_helper.quality_models import Direction
    from logo_helper.quality_state import QualityLoop
    from logo_helper.session_models import Session
    from logo_helper.storage import Store

PROMPT_CAPACITY: Final = 20000


def resolve_direction(
    state: QualityLoop, requested: str | None
) -> tuple[Direction, ArtifactId | None, str]:
    previous_direction = (
        state.requests[-1].direction_id if state.requests else state.contract.directions[0].id
    )
    identifier = requested or previous_direction
    parent_id: ArtifactId | None = None
    changes = ""
    if state.critiques:
        latest = state.critiques[-1]
        match latest.decision:
            case "refine":
                expected = state.requests[latest.request_number - 1].direction_id
                if requested is not None and requested != expected:
                    raise ProjectError(
                        "action_conflict", "Refine must retain the recorded direction"
                    )
                identifier = expected
                parent_id = latest.artifact_id
                changes = (
                    f"Preserve: {'; '.join(latest.preserve)}. "
                    f"Make only these visible changes: {'; '.join(latest.changes)}. "
                    f"Observed reason: {latest.reason}."
                )
            case "reframe" | "reject":
                expected = latest.next_direction_id
                if expected is None:
                    raise ProjectError("invalid_state", "Missing next direction")
                if requested is not None and requested != expected:
                    raise ProjectError("action_conflict", "Use the direction recorded in critique")
                identifier = expected
            case "ready" | "stop":
                raise ProjectError("loop_terminal", "This loop has no further generation action")
            case _:
                assert_never(latest.decision)
    for direction in state.contract.directions:
        if direction.id == identifier:
            return direction, parent_id, changes
    raise ProjectError(
        "unknown_direction", f"Direction {identifier!r} is not in the fixed contract"
    )


def compile_input(
    store: Store, state: QualityLoop, session: Session, requested: str | None
) -> tuple[str, PromptResult]:
    direction, parent_id, changes = resolve_direction(state, requested)
    concept = (
        f"Idea: {direction.idea}. Structural proposal: {direction.structure}. "
        f"Specific distinction to explore: {direction.distinction}."
    )
    result = build_prompt(store, session, concept=concept, parent_id=parent_id, changes=changes)
    contract = state.contract
    constraints = (
        f"\nFixed production scope: {contract.scope}. "
        f"Fixed decisions: {'; '.join(contract.fixed_decisions)}. "
        f"Brand evidence supplied by the director: {'; '.join(contract.source_evidence)}. "
        f"Success criteria: {'; '.join(contract.success_criteria)}. "
        f"Required use contexts: {'; '.join(contract.use_contexts)}."
    )
    if contract.scope == "symbol_only":
        constraints += (
            " Create or edit only the symbol. No lettering, initials, slogan, font proposal, "
            "wordmark or text lockup. Existing typography is outside this image task."
        )
    if state.critiques and parent_id is not None:
        previous = state.critiques[-1]
        observations = "; ".join(
            f"{item.criterion}: {item.observation}"
            for item in previous.assessments
            if item.status != "pass"
        )
        constraints += f"\nPrior observed weaknesses to resolve, not rationalize: {observations}."
    elif state.critiques:
        constraints += (
            "\nThe director has rejected the previous direction. Explore the current idea and "
            "structural proposal independently; do not carry over the previous subject or "
            "geometry. Preserve the fixed brand decisions and required use contexts."
        )
    prompt = result.prompt + constraints
    if len(prompt) > PROMPT_CAPACITY:
        raise ProjectError("prompt_capacity", "Compiled native prompt exceeds import capacity")
    background = (
        session.artifact(parent_id).effective_background(session.brief)
        if parent_id is not None
        else session.brief.background
    )
    return direction.id, result.model_copy(
        update={"prompt": prompt, "requested_background": background}
    )
