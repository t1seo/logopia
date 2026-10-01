"""Bounded host-native production: reserve, import, observe, direct, and resume."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Literal

from logo_helper.model_base import ProjectError
from logo_helper.quality_models import Critique, LoopContract
from logo_helper.quality_prompts import compile_input
from logo_helper.quality_state import QualityLoop, StepFailure, StepRequest
from logo_helper.quality_storage import brief_digest, load_state, lock_loop, save_state
from logo_helper.quality_verify import verify_critique

if TYPE_CHECKING:
    from logo_helper.storage import Store


def load_loop(store: Store, identifier: str) -> QualityLoop:
    """Resume after rechecking original bytes and every recorded evidence binding."""
    return load_state(store, identifier)


def start_loop(store: Store, identifier: str, contract: LoopContract) -> QualityLoop:
    """Create a sidecar without writing or migrating the source session."""
    checked = LoopContract.model_validate_json(contract.model_dump_json())
    with lock_loop(store, identifier), store.locked(checked.session_id):
        source = store.load(checked.session_id)
        state = QualityLoop(
            id=identifier,
            created_at=datetime.now(UTC),
            contract=checked,
            brief_sha256=brief_digest(source.brief),
        )
        save_state(store, state)
    return load_loop(store, identifier)


def _expect(store: Store, identifier: str, revision: int) -> QualityLoop:
    state = load_state(store, identifier)
    if state.revision != revision:
        raise ProjectError(
            "stale_revision", f"Expected loop revision {revision}; current is {state.revision}"
        )
    return state


def request_step(
    store: Store, identifier: str, revision: int, *, direction_id: str | None = None
) -> QualityLoop:
    """Charge one call durably before the host can submit its exact native input."""
    with lock_loop(store, identifier):
        state = _expect(store, identifier, revision)
        if state.pending is not None:
            raise ProjectError(
                "pending_request", "Reconcile the pending request before reserving another"
            )
        if state.status != "active":
            raise ProjectError("loop_terminal", f"No further calls: {state.status}")
        with store.locked(state.contract.session_id):
            source = store.load(state.contract.session_id)
            direction, native_input = compile_input(store, state, source, direction_id)
            parent = (
                source.artifact(native_input.parent_id)
                if native_input.parent_id is not None
                else None
            )
            background = (
                parent.effective_background(source.brief)
                if parent is not None
                else source.brief.background
            )
            request = StepRequest(
                number=state.calls_used + 1,
                direction_id=direction,
                created_at=datetime.now(UTC),
                source_revision=source.revision,
                source_artifact_ids=tuple(item.id for item in source.artifacts),
                input=native_input,
                parent_sha256=parent.sha256 if parent is not None else None,
                expected_background=background,
            )
            updated = state.model_copy(
                update={
                    "revision": state.revision + 1,
                    "requests": (*state.requests, request),
                }
            )
            save_state(store, updated)
    return updated


def record_critique(
    store: Store, identifier: str, revision: int, critique: Critique
) -> QualityLoop:
    """Bind observations to imported bytes; never select, approve, review, or export."""
    checked = Critique.model_validate_json(critique.model_dump_json())
    with lock_loop(store, identifier):
        state = _expect(store, identifier, revision)
        pending = state.pending
        if pending is None or pending.number != checked.request_number:
            raise ProjectError("request_mismatch", "Critique must resolve the pending request")
        with store.locked(state.contract.session_id):
            verify_critique(store, state, checked)
            updated = state.model_copy(
                update={
                    "revision": state.revision + 1,
                    "critiques": (*state.critiques, checked),
                }
            )
            save_state(store, updated)
    return updated


def record_failure(
    store: Store,
    identifier: str,
    revision: int,
    *,
    request_number: int,
    outcome: Literal["failed", "unknown"],
    reason: str,
) -> QualityLoop:
    """Record a failed or uncertain host outcome without refunding its reservation."""
    with lock_loop(store, identifier):
        state = _expect(store, identifier, revision)
        pending = state.pending
        if pending is None or pending.number != request_number:
            raise ProjectError("request_mismatch", "Failure must describe the pending request")
        if any(
            item.request_number == request_number and item.outcome == outcome
            for item in state.failures
        ):
            raise ProjectError("duplicate_outcome", "This outcome is already recorded")
        with store.locked(state.contract.session_id):
            failure = StepFailure(
                request_number=request_number,
                outcome=outcome,
                reason=reason,
                created_at=datetime.now(UTC),
            )
            updated = state.model_copy(
                update={
                    "revision": state.revision + 1,
                    "failures": (*state.failures, failure),
                }
            )
            save_state(store, updated)
    return updated
