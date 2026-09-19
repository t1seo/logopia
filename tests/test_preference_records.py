from __future__ import annotations

from hashlib import sha256
from typing import TYPE_CHECKING, Final, Literal

import pytest
from pydantic import ValidationError

from logo_helper.models import ProjectError
from logo_helper.preference_records import record_preference
from logo_helper.preference_response import PreferenceRecord, PreferenceResponse
from logo_helper.storage import Store

if TYPE_CHECKING:
    from logo_helper.models import Session
    from tests.conftest import Harness

pytest_plugins: Final = ("tests.test_preference_fixtures",)


@pytest.mark.parametrize("outcome", ["a", "b", "tie", "neither"])
def test_all_outcomes_are_sidecars_when_user_responds(
    harness: Harness,
    icon_state: Session,
    preference_response: PreferenceResponse,
    outcome: Literal["a", "b", "tie", "neither"],
) -> None:
    # Given: a viewed pair without any production review or selection.
    before = harness.state_path.read_bytes()
    original = (harness.state_path.parent / icon_state.artifacts[0].path).read_bytes()
    decision = preference_response.decisions[0].model_copy(update={"outcome": outcome})
    response = preference_response.model_copy(update={"decisions": (decision,)})
    # When: any supported preference outcome is recorded.
    result = record_preference(Store.at(harness.workspace), "blind", response)
    record = PreferenceRecord.model_validate_json((harness.workspace / result.path).read_bytes())
    # Then: only an immutable preference sidecar is created.
    assert record.status == "user_preference"
    assert record.response.decisions[0].outcome == outcome
    assert record.response_sha256 == sha256(response.model_dump_json().encode()).hexdigest()
    assert result.source_sessions_changed is False
    assert result.recorded_ai_review_calls == 0
    assert harness.state_path.read_bytes() == before
    assert (harness.state_path.parent / icon_state.artifacts[0].path).read_bytes() == original
    state = Store.at(harness.workspace).load(icon_state.id)
    assert state.selected_id is None
    assert state.artifacts[0].review is None
    assert state.exports == ()


def test_ai_budget_is_bounded_when_second_ai_response_is_recorded(
    harness: Harness, preference_response: PreferenceResponse
) -> None:
    # Given: one explicit AI call has exhausted the independent budget.
    store = Store.at(harness.workspace)
    response = preference_response.model_copy(update={"reviewer_kind": "ai", "review_calls": 1})
    first = record_preference(store, "blind", response)
    second = response.model_copy(update={"reviewer": "Another AI observation"})
    # When: another AI call is submitted.
    with pytest.raises(ProjectError, match="review_budget"):
        _ = record_preference(store, "blind", second)
    # Then: AI recommendation remains distinct and no extra response is stored.
    assert first.status == "ai_recommendation"
    assert first.recorded_ai_review_calls == 1
    assert len(list((harness.workspace / "blind/preference-records").glob("*.json"))) == 1


@pytest.mark.parametrize("change", ["manifest", "image", "revision", "labels", "missing_pair"])
def test_stale_or_mismatched_evidence_is_rejected(
    harness: Harness, icon_state: Session, preference_response: PreferenceResponse, change: str
) -> None:
    # Given: one component no longer matches the reviewed immutable snapshot.
    store = Store.at(harness.workspace)
    response = preference_response
    if change == "manifest":
        path = harness.workspace / "blind/manifest.json"
        _ = path.write_bytes(path.read_bytes() + b"\n")
    if change == "image":
        path = harness.workspace / "blind/images/01-a.png"
        _ = path.write_bytes(b"tampered")
    if change == "revision":
        store.save(icon_state.model_copy(update={"revision": 1}))
    if change == "labels":
        decision = response.decisions[0].model_copy(update={"a_sha256": "0" * 64})
        response = response.model_copy(update={"decisions": (decision,)})
    if change == "missing_pair":
        decision = response.decisions[0].model_copy(update={"pair_id": "pair-02"})
        response = response.model_copy(update={"decisions": (decision,)})
    # When: recording is attempted.
    with pytest.raises(
        ProjectError, match=r"stale_comparison|hash_mismatch|stale_revision|invalid_review"
    ):
        _ = record_preference(store, "blind", response)
    # Then: invalid evidence never becomes a recorded observation.
    assert not (harness.workspace / "blind/preference-records").exists()


@pytest.mark.parametrize("missing", ["small_size_32", "peer_context", "craft_detail"])
def test_concrete_observation_is_required_when_response_is_parsed(
    preference_response: PreferenceResponse, missing: str
) -> None:
    # Given: required visible evidence is replaced with empty whitespace.
    data = preference_response.model_dump(mode="json")
    decision = preference_response.decisions[0]
    observations = decision.observations.model_dump()
    observations[missing] = " "
    data["decisions"] = [{**decision.model_dump(), "observations": observations}]
    # When: external response data crosses the JSON boundary.
    with pytest.raises(ValidationError):
        _ = PreferenceResponse.model_validate(data)
    # Then: no subjective number substitutes for concrete image observations.


def test_duplicate_response_is_not_counted_twice(
    harness: Harness, preference_response: PreferenceResponse
) -> None:
    # Given: an exact response has already been saved.
    store = Store.at(harness.workspace)
    _ = record_preference(store, "blind", preference_response)
    # When: the same response is submitted again.
    with pytest.raises(ProjectError, match="conflict"):
        _ = record_preference(store, "blind", preference_response)
    # Then: idempotent re-submission preserves the sole original record.
    assert len(list((harness.workspace / "blind/preference-records").glob("*.json"))) == 1


def test_existing_record_integrity_when_another_response_is_added(
    harness: Harness, preference_response: PreferenceResponse
) -> None:
    # Given: a prior record's claimed content hash no longer matches its response.
    store = Store.at(harness.workspace)
    result = record_preference(store, "blind", preference_response)
    path = harness.workspace / result.path
    record = PreferenceRecord.model_validate_json(path.read_bytes())
    invalid = record.model_copy(update={"response_sha256": "0" * 64})
    _ = path.write_text(invalid.model_dump_json())
    response = preference_response.model_copy(update={"reviewer": "Second fixture observer"})
    # When: another record would use the previous records as budget evidence.
    with pytest.raises(ProjectError, match="invalid_record"):
        _ = record_preference(store, "blind", response)
    # Then: corrupted records cannot silently participate in budget accounting.
    assert len(list(path.parent.glob("*.json"))) == 1
