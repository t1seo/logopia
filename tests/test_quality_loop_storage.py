from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from logo_helper.models import ArtifactId, Brief, ProjectError, SessionId
from logo_helper.prompts import build_prompt
from logo_helper.quality_models import (
    CriterionAssessment,
    Critique,
    Direction,
    LoopContract,
    ViewEvidence,
)
from logo_helper.quality_state import QualityLoop, StepFailure, StepRequest
from logo_helper.quality_storage import brief_digest, load_state, lock_loop, save_state
from logo_helper.quality_verify import verify_critique
from logo_helper.storage import Store
from logo_helper.workflow import create, import_image, select

if TYPE_CHECKING:
    from tests.conftest import Harness


def prepared(harness: Harness) -> tuple[Store, QualityLoop]:
    store = Store.at(harness.workspace)
    brief = Brief(
        brand_name="Fixture",
        exact_text="",
        industry="design",
        audience="makers",
        logo_type="symbol",
    )
    source = create(store, SessionId("quality-source"), brief)
    contract = LoopContract(
        session_id=source.id,
        scope="symbol_only",
        fixed_typography=True,
        fixed_decisions=("Symbol only",),
        source_evidence=("Existing brand brief",),
        success_criteria=("Distinguishable silhouette",),
        use_contexts=("Product header",),
        directions=(
            Direction(id="a", idea="Open", structure="Open curve", distinction="Open contour"),
            Direction(id="b", idea="Join", structure="Paired planes", distinction="Shared gap"),
        ),
    )
    state = QualityLoop(
        id="loop", created_at=datetime.now(UTC), contract=contract, brief_sha256=brief_digest(brief)
    )
    save_state(store, state)
    request = StepRequest(
        number=1,
        direction_id="a",
        created_at=datetime.now(UTC),
        source_revision=0,
        source_artifact_ids=(),
        input=build_prompt(store, source, concept="Open", parent_id=None, changes=""),
        parent_sha256=None,
        expected_background="opaque",
    )
    state = state.model_copy(update={"revision": 1, "requests": (request,)})
    save_state(store, state)
    return store, state


def imported(harness: Harness) -> tuple[Store, QualityLoop, Critique]:
    store, state = prepared(harness)
    request = state.requests[0]
    source = import_image(
        store,
        state.contract.session_id,
        0,
        artifact_id=ArtifactId("returned"),
        image=harness.png,
        prompt=request.input.prompt,
        parent_id=None,
    )
    artifact = source.artifacts[0]
    evidence = ViewEvidence(
        id="original",
        path=f".logo-generator/sessions/{source.id}/{artifact.path}",
        sha256=artifact.sha256,
        source_artifact_sha256=artifact.sha256,
        kind="original",
        description="Actual imported PNG",
    )
    assessments = tuple(
        CriterionAssessment(
            criterion=criterion,
            status="revise",
            observation="Fixture observation",
            evidence_ids=("original",),
            issue_id="gap-too-narrow",
        )
        for criterion in (
            "appropriateness",
            "distinctiveness",
            "form",
            "optics",
            "use_size",
            "versatility",
            "scope",
        )
    )
    critique = Critique(
        request_number=1,
        artifact_id=artifact.id,
        artifact_sha256=artifact.sha256,
        reviewer="Fixture reviewer",
        evidence=(evidence,),
        assessments=assessments,
        decision="refine",
        reason="A visible issue remains",
        preserve=("Silhouette",),
        changes=("Widen gap",),
    )
    return store, state, critique


def test_sidecar_resume_preserves_session_bytes(harness: Harness) -> None:
    store, state, critique = imported(harness)
    path = store.session_dir(state.contract.session_id) / "session.json"
    original = path.read_bytes()
    updated = state.model_copy(update={"revision": 2, "critiques": (critique,)})
    save_state(store, updated)
    assert load_state(store, "loop") == updated
    assert path.read_bytes() == original


def test_changed_reservation_is_not_silently_overwritten(harness: Harness) -> None:
    store, state = prepared(harness)
    request = state.requests[0].model_copy(update={"direction_id": "b"})
    with pytest.raises(ProjectError, match="immutable_history"):
        save_state(store, state.model_copy(update={"revision": 2, "requests": (request,)}))


def test_lock_is_distinct_and_never_stolen(harness: Harness) -> None:
    store, _ = prepared(harness)
    with (
        store.locked(SessionId("loop")),
        lock_loop(store, "loop"),
        pytest.raises(ProjectError, match="locked"),
        lock_loop(store, "loop"),
    ):
        pytest.fail("Second lock must not be acquired")


def test_original_evidence_cannot_be_substituted(harness: Harness) -> None:
    store, state, critique = imported(harness)
    alternate = harness.workspace / "copied.png"
    _ = alternate.write_bytes(harness.png.read_bytes())
    evidence = critique.evidence[0].model_copy(update={"path": "copied.png"})
    with pytest.raises(ProjectError, match="invalid_evidence"):
        verify_critique(store, state, critique.model_copy(update={"evidence": (evidence,)}))


def test_original_only_does_not_prove_small_size_pass(harness: Harness) -> None:
    store, state, critique = imported(harness)
    assessments = tuple(
        item.model_copy(update={"status": "pass"}) if item.criterion == "use_size" else item
        for item in critique.assessments
    )
    with pytest.raises(ProjectError, match="invalid_evidence"):
        verify_critique(store, state, critique.model_copy(update={"assessments": assessments}))


def test_evidence_hash_change_is_rejected(harness: Harness) -> None:
    store, state, critique = imported(harness)
    evidence = critique.evidence[0].model_copy(
        update={"sha256": hashlib.sha256(b"other").hexdigest()}
    )
    with pytest.raises(ProjectError, match="hash_mismatch"):
        verify_critique(store, state, critique.model_copy(update={"evidence": (evidence,)}))


def test_intervening_session_mutation_prevents_new_critique(harness: Harness) -> None:
    store, state, critique = imported(harness)
    _ = select(store, state.contract.session_id, 1, critique.artifact_id)
    with pytest.raises(ProjectError, match="stale_revision"):
        save_state(store, state.model_copy(update={"revision": 2, "critiques": (critique,)}))
    assert load_state(store, "loop") == state


def test_historical_critique_survives_later_session_mutation(harness: Harness) -> None:
    store, state, critique = imported(harness)
    updated = state.model_copy(update={"revision": 2, "critiques": (critique,)})
    save_state(store, updated)
    _ = select(store, state.contract.session_id, 1, critique.artifact_id)
    assert load_state(store, "loop") == updated


def test_original_dimensions_cannot_be_claimed_as_target_size(harness: Harness) -> None:
    store, state, critique = imported(harness)
    evidence = critique.evidence[0].model_copy(update={"kind": "target_size", "target_width": 16})
    with pytest.raises(ProjectError, match="invalid_evidence"):
        verify_critique(store, state, critique.model_copy(update={"evidence": (evidence,)}))


def test_evidence_cannot_escape_workspace(harness: Harness) -> None:
    store, state, critique = imported(harness)
    evidence = critique.evidence[0].model_copy(update={"path": "../synthetic-fixture.png"})
    with pytest.raises(ProjectError, match="unsafe_path"):
        verify_critique(store, state, critique.model_copy(update={"evidence": (evidence,)}))


def test_unknown_call_cannot_be_retried_without_resolution(harness: Harness) -> None:
    store, state = prepared(harness)
    failure = StepFailure(
        request_number=1, outcome="unknown", reason="Connection ended", created_at=datetime.now(UTC)
    )
    unknown = state.model_copy(update={"revision": 2, "failures": (failure,)})
    save_state(store, unknown)
    next_request = state.requests[0].model_copy(
        update={"number": 2, "created_at": datetime.now(UTC)}
    )
    with pytest.raises(ProjectError, match="invalid_state"):
        save_state(
            store,
            unknown.model_copy(
                update={"revision": 3, "requests": (*unknown.requests, next_request)}
            ),
        )
    assert load_state(store, "loop").calls_used == 1


def test_unknown_call_can_resolve_to_returned_artifact(harness: Harness) -> None:
    store, state, critique = imported(harness)
    failure = StepFailure(
        request_number=1,
        outcome="unknown",
        reason="Host receipt arrived late",
        created_at=datetime.now(UTC),
    )
    unknown = state.model_copy(update={"revision": 2, "failures": (failure,)})
    save_state(store, unknown)
    resolved = unknown.model_copy(update={"revision": 3, "critiques": (critique,)})
    save_state(store, resolved)
    assert load_state(store, "loop").pending is None
    assert load_state(store, "loop").calls_used == 1
