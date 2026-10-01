from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from logo_helper.model_base import ProjectError
from logo_helper.quality_loop import (
    load_loop,
    record_critique,
    record_failure,
    request_step,
    start_loop,
)
from logo_helper.storage import Store
from tests.test_quality_loop import contract
from tests.test_quality_loop_support import assessment, imported

if TYPE_CHECKING:
    from tests.conftest import Harness


def test_refine_compiles_changes_and_preserves_real_parent(harness: Harness) -> None:
    harness.init()
    store = Store.at(harness.workspace)
    initial = start_loop(store, "craft", contract())
    reserved = request_step(store, "craft", initial.revision)
    imported(harness, store, reserved)
    report = assessment(store, reserved)
    recorded = record_critique(store, "craft", reserved.revision, report)

    result = request_step(store, "craft", recorded.revision)

    native = result.requests[-1].input
    assert native.parent_id == report.artifact_id
    assert native.parent_image_path == str(
        store.session_dir(initial.contract.session_id) / "artifacts/v1.png"
    )
    assert all(change in native.prompt for change in report.changes)
    assert all(preserve in native.prompt for preserve in report.preserve)
    assert native.requested_background == "transparent"


def test_unknown_call_stays_pending_and_charged_until_explicit_failure(harness: Harness) -> None:
    harness.init()
    store = Store.at(harness.workspace)
    initial = start_loop(store, "craft", contract().model_copy(update={"call_budget": 1}))
    reserved = request_step(store, "craft", initial.revision)
    unknown = record_failure(
        store,
        "craft",
        reserved.revision,
        request_number=1,
        outcome="unknown",
        reason="Host connection ended without a result",
    )

    resumed = load_loop(store, "craft")

    assert resumed.status == "pending"
    assert resumed.calls_used == 1
    assert resumed.pending == reserved.pending
    failed = record_failure(
        store,
        "craft",
        unknown.revision,
        request_number=1,
        outcome="failed",
        reason="Host confirmed no artifact was returned",
    )
    assert failed.status == "exhausted"
    with pytest.raises(ProjectError, match="exhausted"):
        _ = request_step(store, "craft", failed.revision)


def test_exhaustion_keeps_unresolved_critique_without_promoting_candidate(harness: Harness) -> None:
    harness.init()
    store = Store.at(harness.workspace)
    initial = start_loop(store, "craft", contract().model_copy(update={"call_budget": 1}))
    reserved = request_step(store, "craft", initial.revision)
    imported(harness, store, reserved)

    result = record_critique(store, "craft", reserved.revision, assessment(store, reserved))

    assert result.status == "exhausted"
    assert store.load(initial.contract.session_id).selected_id is None
    assert store.load(initial.contract.session_id).artifacts[0].review is None


def test_repeated_unresolved_parent_child_criterion_blocks_blind_refine(harness: Harness) -> None:
    harness.init()
    store = Store.at(harness.workspace)
    state = start_loop(store, "craft", contract())
    first = request_step(store, "craft", state.revision)
    imported(harness, store, first)
    recorded = record_critique(store, "craft", first.revision, assessment(store, first))
    second = request_step(store, "craft", recorded.revision)
    imported(harness, store, second, "v2")

    with pytest.raises(ProjectError, match="stalled_refinement"):
        _ = record_critique(
            store, "craft", second.revision, assessment(store, second, artifact="v2")
        )

    assert load_loop(store, "craft").pending == second.pending


def test_ready_is_user_review_only_and_preserves_source_session_bytes(harness: Harness) -> None:
    harness.init()
    store = Store.at(harness.workspace)
    initial = start_loop(store, "craft", contract())
    reserved = request_step(store, "craft", initial.revision)
    imported(harness, store, reserved)
    original = harness.state_path.read_bytes()

    result = record_critique(
        store,
        "craft",
        reserved.revision,
        assessment(store, reserved, decision="ready", unresolved=None),
    )

    assert result.status == "ready_for_user_review"
    assert harness.state_path.read_bytes() == original
    with pytest.raises(ProjectError, match="ready_for_user_review"):
        _ = request_step(store, "craft", result.revision)
