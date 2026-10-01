"""Atomic, append-only sidecar storage independent of legacy logo session bytes."""

from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from typing import TYPE_CHECKING
from uuid import uuid4

from logo_helper.model_base import ProjectError
from logo_helper.quality_state import QualityLoop
from logo_helper.quality_verify import (
    verify_continuation,
    verify_critique,
    verify_failure,
    verify_request,
)
from logo_helper.storage import read_source, safe_path, validate_id, write_new

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from logo_helper.models import Brief
    from logo_helper.storage import Store


def brief_digest(brief: Brief) -> str:
    """Bind stable serialized intent without changing its source session."""
    data = json.dumps(brief.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _directory(store: Store, identifier: str) -> Path:
    return safe_path(store.root, f".logo-generator/quality-loops/{validate_id(identifier)}")


@contextmanager
def lock_loop(store: Store, identifier: str) -> Generator[None]:
    """Use a distinct cooperative lock and never steal an existing writer's reservation."""
    directory = _directory(store, identifier)
    directory.mkdir(parents=True, exist_ok=True)
    lock = safe_path(directory, "loop.lock")
    try:
        lock.mkdir()
    except FileExistsError as error:
        raise ProjectError("locked", f"Quality loop locked; inspect its writer: {lock}") from error
    try:
        yield
    finally:
        lock.rmdir()


def _verify_events(state: QualityLoop) -> None:
    if state.revision != len(state.requests) + len(state.critiques) + len(state.failures):
        raise ProjectError("invalid_state", "Loop revision must match its append-only event count")
    if state.calls_used > state.contract.call_budget:
        raise ProjectError("invalid_state", "Native call budget has been exceeded")
    critiques = {item.request_number: item for item in state.critiques}
    if len(critiques) != len(state.critiques) or len(
        {item.artifact_id for item in state.critiques}
    ) != len(state.critiques):
        raise ProjectError("invalid_state", "Each request and returned artifact is critiqued once")
    if tuple(critiques) != tuple(sorted(critiques)):
        raise ProjectError("invalid_state", "Critiques must follow reservation order")
    failure_keys = {(item.request_number, item.outcome) for item in state.failures}
    if len(failure_keys) != len(state.failures):
        raise ProjectError("invalid_state", "Failure outcomes cannot be appended repeatedly")
    resolved = {item.request_number for item in state.failures if item.outcome == "failed"}
    if resolved.intersection(critiques):
        raise ProjectError("invalid_state", "Failed requests cannot also have a returned artifact")
    resolved.update(critiques)
    _verify_request_order(state, resolved)
    _verify_failure_order(state)


def _verify_request_order(state: QualityLoop, resolved: set[int]) -> None:
    directions = {item.id for item in state.contract.directions}
    previous_time = state.created_at
    for number, request in enumerate(state.requests, 1):
        if (
            request.number != number
            or request.direction_id not in directions
            or request.created_at.tzinfo is None
            or request.created_at < previous_time
            or (number > 1 and number - 1 not in resolved)
        ):
            raise ProjectError(
                "invalid_state", "Reservation order or pending-call state is invalid"
            )
        verify_continuation(state, request)
        previous_time = request.created_at


def _verify_failure_order(state: QualityLoop) -> None:
    previous_time = state.created_at
    for failure in state.failures:
        if failure.request_number > len(state.requests):
            raise ProjectError("invalid_state", "Failure has no reserved native call")
        request = state.requests[failure.request_number - 1]
        if (
            failure.created_at.tzinfo is None
            or failure.created_at < request.created_at
            or failure.created_at < previous_time
            or (
                failure.request_number < len(state.requests)
                and failure.created_at > state.requests[failure.request_number].created_at
            )
        ):
            raise ProjectError("invalid_state", "Failure predates its reservation")
        if failure.outcome == "unknown" and any(
            item.request_number == failure.request_number
            and item.outcome == "failed"
            and item.created_at <= failure.created_at
            for item in state.failures
        ):
            raise ProjectError("invalid_state", "A resolved failure cannot become unknown")
        previous_time = failure.created_at


def _verify_state(store: Store, state: QualityLoop) -> None:
    source = store.load(state.contract.session_id)
    if state.created_at.tzinfo is None:
        raise ProjectError("invalid_state", "Loop timestamps require an explicit timezone")
    if brief_digest(source.brief) != state.brief_sha256:
        raise ProjectError("brief_changed", "Source brief changed; preserve this loop's intent")
    if state.contract.scope == "symbol_only" and (
        source.brief.logo_type not in {"symbol", "abstract"}
        or source.brief.exact_text != ""
        or source.brief.slogan != ""
        or source.brief.lockup is not None
        or source.brief.app_icon is not None
    ):
        raise ProjectError("scope_conflict", "Symbol-only loops require a symbol-only source brief")
    _verify_events(state)
    for request in state.requests:
        verify_request(store, source, request)
    for failure in state.failures:
        verify_failure(source, state.requests[failure.request_number - 1], failure)
    for critique in state.critiques:
        verify_critique(store, state, critique)


def load_state(store: Store, identifier: str) -> QualityLoop:
    """Verify source bytes, immutable parent intent and every claimed view on resume."""
    path = safe_path(_directory(store, identifier), "loop.json")
    state = QualityLoop.model_validate_json(read_source(path))
    if state.id != identifier:
        raise ProjectError("invalid_state", "Stored loop ID differs from its directory")
    _verify_state(store, state)
    return state


def _verify_append(previous: QualityLoop, current: QualityLoop) -> None:
    if current.revision != previous.revision + 1:
        raise ProjectError("stale_revision", "Quality-loop revision must advance by exactly one")
    if (
        previous.id != current.id
        or previous.created_at != current.created_at
        or previous.contract != current.contract
        or previous.brief_sha256 != current.brief_sha256
    ):
        raise ProjectError("immutable_history", "Loop contract and source identity are immutable")
    for old, new in (
        (previous.requests, current.requests),
        (previous.critiques, current.critiques),
        (previous.failures, current.failures),
    ):
        if new[: len(old)] != old:
            raise ProjectError("immutable_history", "Reservations and reports are append-only")
    additions = (
        len(current.requests) - len(previous.requests),
        len(current.critiques) - len(previous.critiques),
        len(current.failures) - len(previous.failures),
    )
    if sum(additions) != 1:
        raise ProjectError("invalid_state", "Each loop revision appends exactly one event")
    if additions[0] and previous.pending is not None:
        raise ProjectError("invalid_state", "Pending native calls must be reconciled first")
    if additions[1] or additions[2]:
        number = (
            current.critiques[-1].request_number
            if additions[1]
            else current.failures[-1].request_number
        )
        if previous.pending is None or previous.pending.number != number:
            raise ProjectError("invalid_state", "New reports must resolve the pending native call")


def save_state(store: Store, state: QualityLoop) -> None:
    """Commit a fully verified revision atomically; caller holds the sidecar lock."""
    verified = QualityLoop.model_validate_json(state.model_dump_json())
    directory = _directory(store, verified.id)
    path = safe_path(directory, "loop.json")
    if path.exists():
        previous = load_state(store, verified.id)
        _verify_append(previous, verified)
        for critique in verified.critiques[len(previous.critiques) :]:
            verify_critique(store, previous, critique)
    elif verified.revision != 0:
        raise ProjectError("stale_revision", "New quality loops begin at revision zero")
    _verify_state(store, verified)
    directory.mkdir(parents=True, exist_ok=True)
    temporary = safe_path(directory, f".loop-{uuid4().hex}.tmp")
    try:
        write_new(temporary, (verified.model_dump_json(indent=2) + "\n").encode("utf-8"))
        if path.is_symlink():
            raise ProjectError("unsafe_path", "Quality-loop JSON cannot be a symlink")
        _ = temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
