import json
from hashlib import sha256
from pathlib import Path

import pytest
from logopia_studio.engine import Studio
from logopia_studio.host import HermesHost
from logopia_studio.host_api import JsonObject
from logopia_studio.models import PlanResult, StudioError
from logopia_studio.models_references import ReferenceAnalysis, StudioReference
from logopia_studio.prompts import image_prompt
from pydantic import TypeAdapter
from tests.hermes.test_core_fixtures import REPO, FixtureHost, brief
from tests.hermes.test_host_fakes import (
    FakeCompletion,
    FakeContext,
    FakeLlm,
    critic_response,
    direction,
    native_receipt,
    strategy,
    write_png,
)


def test_reference_analysis_reaches_generation_and_edit_keeps_actual_parent(tmp_path: Path) -> None:
    reference_path = tmp_path / "reference.png"
    reference_bytes = write_png(reference_path)
    reference = StudioReference(
        id="open-counter",
        path=reference_path,
        sha256=sha256(reference_bytes).hexdigest(),
        transfer_traits=("Open counter",),
        selected_by="automatic",
    )
    request = brief(2).model_copy(update={"references": (reference,)})
    analysis = ReferenceAnalysis(
        reference_id=reference.id,
        observations=("A wide counter is visible in the center",),
        interpretation="It may read clearly at small size",
        transfer_traits=("Wide counter",),
    )
    report: JsonObject = {
        "directions": [
            TypeAdapter(JsonObject).validate_json(direction(i).model_dump_json()) for i in range(2)
        ],
        "reference_analysis": [TypeAdapter(JsonObject).validate_json(analysis.model_dump_json())],
    }
    outputs = tuple(tmp_path / f"native-{index}.png" for index in range(3))
    for output in outputs:
        _ = write_png(output, "#fafafa")
    context = FakeContext(
        llm=FakeLlm(
            responses=[
                FakeCompletion(strategy().model_dump_json()),
                FakeCompletion(json.dumps(report)),
                *(critic_response() for _ in range(6)),
            ]
        ),
        dispatch_results=[native_receipt(output) for output in outputs],
    )
    studio = Studio(tmp_path, REPO, HermesHost(context))
    created = studio.create("references", request)
    produced = studio.produce(created.id, created.revision)
    parent = produced.candidates[0]
    edited = studio.revise(created.id, produced.revision, parent.id, ("counter",), "Widen counter")
    assert len(context.dispatches) == 3
    assert "image_url" not in context.dispatches[0][1]
    edit_args = context.dispatches[-1][1]
    assert "image_url" in edit_args
    assert edit_args["image_url"] == str(tmp_path / parent.image_path)
    assert edit_args["image_url"] != str(reference_path)
    child = edited.candidates[-1]
    assert child.references == (reference,)
    assert child.reference_conditioning == "text"
    assert child.reference_analysis[0].reference_sha256 == reference.sha256
    assert "Wide counter" in child.prompt
    assert reference.sha256 in child.prompt
    assert edited.selected_id is None
    assert edited.candidates[0] == parent
    assert reference_path.read_bytes() == reference_bytes


def test_reference_changed_after_planning_blocks_image_call(tmp_path: Path) -> None:
    reference_path = tmp_path / "reference.png"
    data = write_png(reference_path)
    reference = StudioReference(id="ref", path=reference_path, sha256=sha256(data).hexdigest())
    request = brief().model_copy(update={"references": (reference,)})
    host = FixtureHost(tmp_path)
    studio = Studio(tmp_path, REPO, host)
    created = studio.create("changed-ref", request)
    _ = write_png(reference_path, "#552244")
    with pytest.raises(StudioError, match="reference_changed"):
        _ = studio.produce(created.id, created.revision)
    assert not host.calls
    assert not studio.status(created.id).candidates


def test_old_reference_free_plan_still_builds_original_prompt() -> None:
    plan = PlanResult(
        strategy=strategy(), directions=(direction(1),), provider="fixture", model="fixture"
    )
    prompt = image_prompt(brief(), plan.directions[0])
    assert plan.reference_analysis == ()
    assert "reference-" not in prompt.split("<reference-traits", maxsplit=1)[0]
    assert "Pure white solid background" in prompt
