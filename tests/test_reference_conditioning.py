from __future__ import annotations

import json
from hashlib import sha256
from typing import TYPE_CHECKING

import pytest
from PIL import Image

from logo_helper import color_workflow, workflow
from logo_helper.conditioning import condition_prompt
from logo_helper.conditioning_models import ReferencePlan
from logo_helper.models import ArtifactId, Brief, ProjectError, ReferenceId, SessionId
from logo_helper.prompts import PromptResult, build_prompt
from logo_helper.storage import Store

if TYPE_CHECKING:
    from pathlib import Path


def setup_reference(tmp_path: Path) -> Store:
    with Image.new("RGB", (64, 64), "navy") as image:
        image.save(tmp_path / "reference.png")
    store = Store.at(tmp_path)
    brief = Brief(brand_name="SEAM", exact_text="", industry="writing", audience="writers")
    _ = workflow.create(store, SessionId("test"), brief)
    _ = color_workflow.add_reference(
        store,
        SessionId("test"),
        0,
        reference_id=ReferenceId("r1"),
        image=tmp_path / "reference.png",
        roi=None,
    )
    return store


def plan(
    store: Store, *, role: str = "positive", capability: str = "codex_native"
) -> ReferencePlan:
    reference = store.load(SessionId("test")).reference(ReferenceId("r1"))
    return ReferencePlan.model_validate_json(
        json.dumps(
            {
                "mode": "image",
                "capability": capability,
                "references": [
                    {
                        "reference_id": "r1",
                        "image_sha256": reference.sha256,
                        "role": role,
                        "observations": ["Broad filled field"],
                        "transfer": ["Clear silhouette"],
                        "avoid": ["Copying the actual contour"],
                        "inspected_by": "test fixture",
                        "inspected_on": "2026-09-19",
                    }
                ],
            }
        )
    )


def base_prompt(store: Store, parent: ArtifactId | None = None) -> PromptResult:
    return build_prompt(
        store,
        store.load(SessionId("test")),
        concept="Two folded slips",
        parent_id=parent,
        changes="Open the gap" if parent else "",
    )


def test_real_reference_path_and_prompt_reach_native_arguments(tmp_path: Path) -> None:
    store = setup_reference(tmp_path)
    original = base_prompt(store)
    result = condition_prompt(store, store.load(SessionId("test")), original, plan(store))
    assert result.input_plan is not None
    assert result.input_plan.arguments.prompt == result.prompt
    assert result.input_plan.arguments.referenced_image_paths == (
        str(store.session_dir(SessionId("test")) / "references/r1.png"),
    )
    assert result.input_plan.conditioning == "image"
    assert "Clear silhouette" in result.prompt
    assert result.input_plan.request_sha256 != sha256(original.prompt.encode()).hexdigest()


def test_negative_reference_never_becomes_positive_image_input(tmp_path: Path) -> None:
    store = setup_reference(tmp_path)
    result = condition_prompt(
        store, store.load(SessionId("test")), base_prompt(store), plan(store, role="negative")
    )
    assert result.input_plan is not None
    assert result.input_plan.arguments.referenced_image_paths == ()
    assert result.input_plan.conditioning == "analysis_text"
    assert "Copying the actual contour" in result.prompt


def test_parent_is_first_and_separate_from_positive_reference(tmp_path: Path) -> None:
    store = setup_reference(tmp_path)
    _ = workflow.import_image(
        store,
        SessionId("test"),
        1,
        artifact_id=ArtifactId("a"),
        image=tmp_path / "reference.png",
        prompt="Original",
        parent_id=None,
    )
    result = condition_prompt(
        store, store.load(SessionId("test")), base_prompt(store, ArtifactId("a")), plan(store)
    )
    assert result.input_plan is not None
    paths = result.input_plan.arguments.referenced_image_paths
    assert len(paths) == 2
    assert paths[0] == result.parent_image_path
    assert paths[1].endswith("references/r1.png")
    assert result.input_plan.parent_sha256 is not None


def test_unsupported_conditioning_fails_explicitly(tmp_path: Path) -> None:
    store = setup_reference(tmp_path)
    with pytest.raises(ProjectError, match="unsupported_conditioning"):
        _ = condition_prompt(
            store,
            store.load(SessionId("test")),
            base_prompt(store),
            plan(store, capability="text_only"),
        )


@pytest.mark.parametrize("failure", ["missing", "changed", "corrupt"])
def test_invalid_reference_never_produces_model_request(tmp_path: Path, failure: str) -> None:
    store = setup_reference(tmp_path)
    state = store.load(SessionId("test"))
    prompt, selected = base_prompt(store), plan(store)
    path = store.session_dir(state.id) / state.references[0].path
    if failure == "missing":
        path.unlink()
    else:
        _ = path.write_bytes(b"invalid PNG" if failure == "corrupt" else b"changed")
    with pytest.raises(ProjectError):
        _ = condition_prompt(store, state, prompt, selected)


def test_uninspected_or_stale_analysis_cannot_condition(tmp_path: Path) -> None:
    store = setup_reference(tmp_path)
    selected = plan(store)
    wrong = selected.references[0].model_copy(update={"image_sha256": "0" * 64})
    with pytest.raises(ProjectError, match="analysis_mismatch"):
        _ = condition_prompt(
            store,
            store.load(SessionId("test")),
            base_prompt(store),
            selected.model_copy(update={"references": (wrong,)}),
        )


def test_no_reference_prompt_retains_legacy_contract(tmp_path: Path) -> None:
    store = setup_reference(tmp_path)
    result = base_prompt(store)
    assert "input_plan" not in result.model_dump()
    assert result.parent_image_path is None
