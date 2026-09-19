from pathlib import Path

import pytest
from logopia_studio.engine import Studio
from logopia_studio.host_requests import StartRequest
from logopia_studio.launcher_state import verify_result
from logopia_studio.models import StudioBrief, StudioError, Workflow
from tests.hermes.test_core_fixtures import REPO, FixtureHost, brief


def exploration() -> StudioBrief:
    return StudioBrief.model_validate_json(
        brief()
        .model_copy(update={"count": None, "direction_count": 3, "candidates_per_direction": 3})
        .model_dump_json()
    )


def test_exploration_runs_nine_slots_once_and_keeps_two_edit_budget(tmp_path: Path) -> None:
    # Given three structural directions with three controlled candidates per direction.
    host = FixtureHost(tmp_path)
    studio = Studio(tmp_path, REPO, host)
    created = studio.create("explore", exploration())
    # When produced, repeated and explicitly edited twice.
    state = studio.produce("explore", created.revision)
    repeated = studio.produce("explore", state.revision)
    verify_result(StartRequest(workflow_id="explore", brief=created.brief), created, state)
    first_edit = studio.revise("explore", repeated.revision, "c1", ("contour",), "Open counter")
    second_edit = studio.revise("explore", first_edit.revision, "e1", ("contour",), "Widen gap")
    # Then exact slots survive, no duplicate image is emitted, and the third edit is blocked.
    assert state == repeated
    assert state.call_budget.initial_images_reserved == 9
    assert state.call_budget.review_llm_calls_reserved == 18
    assert state.call_budget.planning_llm_calls_reserved == 2
    assert len(host.calls) == 11
    assert len(state.directions) == 3
    assert {(c.direction_id, c.candidate_slot) for c in state.candidates} == {
        (f"d{direction}", slot) for direction in range(1, 4) for slot in range(1, 4)
    }
    assert all(candidate.changed_variables for candidate in state.candidates)
    assert second_edit.candidates[-1].parent_id == "e1"
    assert second_edit.selected_id is None
    assert second_edit.call_budget.edit_images_reserved == 2
    assert second_edit.call_budget.review_llm_calls_reserved == 22
    assert Workflow.model_validate_json(second_edit.model_dump_json()) == second_edit
    with pytest.raises(StudioError, match="edit_limit"):
        _ = studio.revise("explore", second_edit.revision, "e2", (), "Another change")


def test_exploration_unknown_image_is_not_resent(tmp_path: Path) -> None:
    # Given a provider that returns an uncertain image outcome.
    host = FixtureHost(tmp_path, mode="unknown")
    studio = Studio(tmp_path, REPO, host)
    created = studio.create("explore", exploration())
    # When continued after that uncertainty, then the reserved slot remains unresolved.
    state = studio.produce("explore", created.revision)
    again = studio.produce("explore", state.revision)
    assert state.phase == "outcome_unknown"
    assert state == again
    assert len(host.calls) == 1


def test_fifth_interrupted_slot_reconciles_exact_return_before_remaining_slots(
    tmp_path: Path,
) -> None:
    def interrupt_fifth() -> None:
        if len(host.calls) == 5:
            current = studio.status("explore")
            _ = studio.interrupt(
                "explore", current.revision, "Fixture runner settled during slot five"
            )

    host = FixtureHost(tmp_path, on_generate=interrupt_fifth)
    studio = Studio(tmp_path, REPO, host)
    created = studio.create("explore", exploration())
    interrupted = studio.produce(created.id, created.revision)
    assert interrupted.phase == "outcome_unknown"
    assert len(interrupted.candidates) == 4
    assert len(host.calls) == 5
    assert studio.produce(created.id, interrupted.revision) == interrupted
    job = next(item for item in interrupted.jobs if item.candidate_id == "c5")
    assert job.generated is not None
    recovered = studio.reconcile(created.id, interrupted.revision, job.id)
    assert len(recovered.candidates) == 5
    assert len(host.calls) == 5
    completed = studio.produce(created.id, recovered.revision)
    assert len(completed.candidates) == 9
    assert len(host.calls) == 9
    assert completed.phase == "awaiting_choice"
    assert tuple(candidate.sha256 for candidate in completed.candidates[:4]) == tuple(
        candidate.sha256 for candidate in interrupted.candidates
    )
    assert (
        len(
            {
                (candidate.direction_id, candidate.candidate_slot)
                for candidate in completed.candidates
            }
        )
        == 9
    )
