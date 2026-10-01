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


def test_confirmed_failed_edit_preserves_parent_and_visible_changes_on_retry(
    harness: Harness,
) -> None:
    harness.init()
    store = Store.at(harness.workspace)
    first = request_step(store, "craft", start_loop(store, "craft", contract()).revision)
    imported(harness, store, first)
    report = assessment(store, first)
    reviewed = record_critique(store, "craft", first.revision, report)
    edit = request_step(store, "craft", reviewed.revision)
    failed = record_failure(
        store,
        "craft",
        edit.revision,
        request_number=2,
        outcome="failed",
        reason="The host confirmed no output",
    )

    retried = request_step(store, "craft", failed.revision)

    assert retried.requests[-1].input.mode == "edit"
    assert retried.requests[-1].input.parent_id == report.artifact_id
    assert retried.requests[-1].input.prompt == edit.requests[-1].input.prompt
    assert retried.calls_used == 3


def test_confirmed_failed_reframe_does_not_return_to_rejected_direction(harness: Harness) -> None:
    harness.init()
    store = Store.at(harness.workspace)
    first = request_step(store, "craft", start_loop(store, "craft", contract()).revision)
    imported(harness, store, first)
    report = assessment(store, first, decision="reframe")
    reviewed = record_critique(store, "craft", first.revision, report)
    reframe = request_step(store, "craft", reviewed.revision)
    failed = record_failure(
        store,
        "craft",
        reframe.revision,
        request_number=2,
        outcome="failed",
        reason="The host confirmed no output",
    )

    retried = request_step(store, "craft", failed.revision)

    assert retried.requests[-1].direction_id == "two"
    assert retried.requests[-1].input.parent_id is None
    assert retried.requests[-1].input.prompt == reframe.requests[-1].input.prompt
    assert retried.calls_used == 3


def test_known_imported_result_cannot_bypass_critique_as_failed(harness: Harness) -> None:
    harness.init()
    store = Store.at(harness.workspace)
    first = request_step(store, "craft", start_loop(store, "craft", contract()).revision)
    imported(harness, store, first)

    with pytest.raises(ProjectError, match="returned_result"):
        _ = record_failure(
            store,
            "craft",
            first.revision,
            request_number=1,
            outcome="failed",
            reason="The logo is weak",
        )

    assert load_loop(store, "craft").pending == first.pending


def test_reframing_does_not_instruct_new_subject_to_fix_rejected_geometry(harness: Harness) -> None:
    harness.init()
    store = Store.at(harness.workspace)
    first = request_step(store, "craft", start_loop(store, "craft", contract()).revision)
    imported(harness, store, first)
    original = assessment(store, first, decision="reframe")
    report = original.model_copy(
        update={
            "assessments": tuple(
                item.model_copy(
                    update={"observation": "The old finger junction pinches into a palm"}
                )
                if item.status == "revise"
                else item
                for item in original.assessments
            )
        }
    )
    reviewed = record_critique(store, "craft", first.revision, report)

    result = request_step(store, "craft", reviewed.revision)

    assert "finger junction" not in result.requests[-1].input.prompt
    assert contract().directions[1].idea in result.requests[-1].input.prompt
    assert result.critiques[0] == report
