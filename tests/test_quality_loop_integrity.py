from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from logo_helper.brief_models import Brief
from logo_helper.model_base import ArtifactId, ProjectError, SessionId
from logo_helper.quality_loop import load_loop, record_critique, request_step, start_loop
from logo_helper.quality_models import CriterionAssessment, Critique
from logo_helper.storage import Store
from logo_helper.workflow import create, import_image
from tests.test_app_icon_compatibility import install_baseline
from tests.test_quality_loop import contract
from tests.test_quality_loop_support import assessment, imported

if TYPE_CHECKING:
    from tests.conftest import Harness


def test_text_free_abstract_is_valid_symbol_only_scope(harness: Harness) -> None:
    store = Store.at(harness.workspace)
    _ = create(
        store,
        SessionId("demo"),
        Brief(
            brand_name="Morrow",
            industry="Design",
            audience="Product teams",
            exact_text="",
            logo_type="abstract",
        ),
    )
    fixed = contract().model_copy(update={"scope": "symbol_only", "fixed_typography": True})

    created = start_loop(store, "craft", fixed)

    assert created.contract.fixed_typography
    assert store.load(SessionId("demo")).brief.logo_type == "abstract"


@pytest.mark.parametrize("version", [1, 2])
def test_legacy_source_bytes_survive_start_request_and_resume(
    harness: Harness, version: int
) -> None:
    original = install_baseline(harness, version)
    store = Store.at(harness.workspace)
    state = start_loop(store, "craft", contract())

    reserved = request_step(store, "craft", state.revision)
    resumed = load_loop(store, "craft")

    assert resumed.requests == reserved.requests
    assert harness.state_path.read_bytes() == original
    assert not harness.state_path.with_name("session.v1.backup.json").exists()


def test_unknown_criterion_cannot_be_marked_ready(harness: Harness) -> None:
    harness.init()
    store = Store.at(harness.workspace)
    state = request_step(store, "craft", start_loop(store, "craft", contract()).revision)
    imported(harness, store, state)
    original = assessment(store, state)
    changed = original.model_copy(
        update={
            "decision": "ready",
            "changes": (),
            "assessments": tuple(
                item.model_copy(update={"status": "not_observed", "evidence_ids": ()})
                if item.criterion == "use_size"
                else item.model_copy(update={"status": "pass"})
                for item in original.assessments
            ),
        }
    )

    with pytest.raises(ProjectError, match="unresolved_quality"):
        _ = record_critique(store, "craft", state.revision, changed)

    assert load_loop(store, "craft").pending is not None


def test_revised_criterion_requires_stable_issue_identifier() -> None:
    with pytest.raises(ProjectError, match="issue_id"):
        _ = CriterionAssessment(
            criterion="optics",
            status="revise",
            observation="Lower gap pinches to a point",
            evidence_ids=("original",),
        )


def test_reframe_request_has_new_structure_and_no_parent(harness: Harness) -> None:
    harness.init()
    store = Store.at(harness.workspace)
    state = request_step(store, "craft", start_loop(store, "craft", contract()).revision)
    imported(harness, store, state)
    reviewed = record_critique(
        store, "craft", state.revision, assessment(store, state, decision="reframe")
    )

    result = request_step(store, "craft", reviewed.revision)

    assert result.requests[-1].direction_id == "two"
    assert result.requests[-1].input.parent_id is None
    assert contract().directions[1].structure in result.requests[-1].input.prompt


@pytest.mark.parametrize("outcome", ["unchanged", "regressed", "not_observed"])
def test_child_without_observed_improvement_cannot_refine(harness: Harness, outcome: str) -> None:
    harness.init()
    store = Store.at(harness.workspace)
    first = request_step(store, "craft", start_loop(store, "craft", contract()).revision)
    imported(harness, store, first)
    reviewed = record_critique(store, "craft", first.revision, assessment(store, first))
    second = request_step(store, "craft", reviewed.revision)
    imported(harness, store, second, "v2")
    report = assessment(store, second, artifact="v2", unresolved="form")
    altered = Critique.model_validate_json(
        report.model_copy(update={"change_result": outcome}).model_dump_json()
    )

    with pytest.raises(ProjectError, match="edit_not_improved"):
        _ = record_critique(store, "craft", second.revision, altered)

    assert load_loop(store, "craft").calls_used == 2


def test_new_optical_issue_does_not_count_as_stalled_old_issue(harness: Harness) -> None:
    harness.init()
    store = Store.at(harness.workspace)
    first = request_step(store, "craft", start_loop(store, "craft", contract()).revision)
    imported(harness, store, first)
    reviewed = record_critique(store, "craft", first.revision, assessment(store, first))
    second = request_step(store, "craft", reviewed.revision)
    imported(harness, store, second, "v2")
    report = assessment(store, second, artifact="v2")
    altered = report.model_copy(
        update={
            "assessments": tuple(
                item.model_copy(update={"issue_id": "new-terminal-weight"})
                if item.status == "revise"
                else item
                for item in report.assessments
            )
        }
    )

    result = record_critique(store, "craft", second.revision, altered)

    assert result.status == "active"


@pytest.mark.parametrize("wrong_prompt", [True, False])
def test_import_must_match_reserved_prompt_and_background(
    harness: Harness, wrong_prompt: bool
) -> None:
    harness.init()
    store = Store.at(harness.workspace)
    state = request_step(store, "craft", start_loop(store, "craft", contract()).revision)
    request = state.requests[-1]
    _ = import_image(
        store,
        state.contract.session_id,
        request.source_revision,
        artifact_id=ArtifactId("v1"),
        image=harness.png,
        parent_id=None,
        prompt="A different native call" if wrong_prompt else request.input.prompt,
        background=request.expected_background if wrong_prompt else "opaque",
    )

    with pytest.raises(ProjectError, match="reserved call"):
        _ = record_critique(store, "craft", state.revision, assessment(store, state))

    assert load_loop(store, "craft").pending is not None


def test_edit_import_cannot_drop_reserved_parent(harness: Harness) -> None:
    harness.init()
    store = Store.at(harness.workspace)
    first = request_step(store, "craft", start_loop(store, "craft", contract()).revision)
    imported(harness, store, first)
    reviewed = record_critique(store, "craft", first.revision, assessment(store, first))
    second = request_step(store, "craft", reviewed.revision)
    request = second.requests[-1]
    _ = import_image(
        store,
        second.contract.session_id,
        request.source_revision,
        artifact_id=ArtifactId("v2"),
        image=harness.png,
        prompt=request.input.prompt,
        parent_id=None,
        background=request.expected_background,
    )

    with pytest.raises(ProjectError, match="reserved call"):
        _ = record_critique(
            store, "craft", second.revision, assessment(store, second, artifact="v2")
        )

    assert load_loop(store, "craft").pending == second.pending


def test_legacy_artifact_without_timezone_returns_typed_error(harness: Harness) -> None:
    harness.init()
    _ = harness.import_image()
    store = Store.at(harness.workspace)
    source = store.load(SessionId("demo"))
    naive_artifact = source.artifacts[0].model_copy(
        update={
            "created_at": source.artifacts[0].created_at.replace(tzinfo=None),
        }
    )
    malformed = source.model_copy(update={"artifacts": (naive_artifact,)})
    _ = harness.state_path.write_text(malformed.model_dump_json(), encoding="utf-8")
    initial = start_loop(store, "craft", contract())

    with pytest.raises(ProjectError, match="timezone"):
        _ = request_step(store, "craft", initial.revision)

    assert load_loop(store, "craft").calls_used == 0
