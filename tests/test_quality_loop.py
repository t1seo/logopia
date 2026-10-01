from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from logo_helper.model_base import ProjectError, SessionId
from logo_helper.quality_loop import load_loop, request_step, start_loop
from logo_helper.quality_models import Direction, LoopContract
from logo_helper.storage import Store

if TYPE_CHECKING:
    from tests.conftest import Harness


def contract() -> LoopContract:
    return LoopContract(
        session_id=SessionId("demo"),
        scope="full_logo",
        fixed_decisions=("Use the existing lettering exactly",),
        source_evidence=("Brand owner supplied the brief",),
        success_criteria=("A specific memorable relationship of shapes",),
        use_contexts=("Product header at 32 pixels",),
        directions=(
            Direction(
                id="one",
                idea="A shared path",
                structure="Open continuous gesture",
                distinction="Unusual terminal relationship",
            ),
            Direction(
                id="two",
                idea="An unexpected meeting",
                structure="Separate interacting masses",
                distinction="Specific asymmetric space",
            ),
        ),
    )


def test_start_keeps_existing_session_bytes_when_creating_sidecar(harness: Harness) -> None:
    # Given an existing session whose serialized form must remain untouched.
    harness.init()
    original = harness.state_path.read_bytes()
    # When a quality loop is created.
    result = start_loop(Store.at(harness.workspace), "craft", contract())
    # Then the sidecar owns the budget while the session is byte-identical.
    assert result.calls_used == 0
    assert harness.state_path.read_bytes() == original


def test_pending_reservation_cannot_be_repeated_after_resume(harness: Harness) -> None:
    # Given a reserved native call.
    harness.init()
    store = Store.at(harness.workspace)
    initial = start_loop(store, "craft", contract())
    reserved = request_step(store, "craft", initial.revision)
    # When a second reservation is attempted against the resumed revision.
    with pytest.raises(ProjectError, match="pending"):
        _ = request_step(store, "craft", reserved.revision)
    # Then the original exact native input and single charge survive.
    resumed = load_loop(store, "craft")
    assert resumed.calls_used == 1
    assert resumed.requests == reserved.requests


def test_fixed_typography_rejects_full_logo_contract(harness: Harness) -> None:
    # Given typography is already fixed by the user.
    harness.init()
    # When full-logo generation is requested.
    with pytest.raises(ProjectError, match="symbol_only"):
        _ = start_loop(
            Store.at(harness.workspace),
            "craft",
            contract().model_copy(update={"fixed_typography": True}),
        )
