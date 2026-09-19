from __future__ import annotations

import json
from hashlib import sha256
from typing import TYPE_CHECKING

import pytest
from logopia_studio.host import HermesHost
from logopia_studio.host_api import JsonObject
from logopia_studio.models import StudioBrief, StudioError
from logopia_studio.prompts import image_prompt
from pydantic import TypeAdapter, ValidationError
from tests.hermes.test_core_fixtures import brief
from tests.hermes.test_host_fakes import (
    FakeCompletion,
    FakeContext,
    FakeLlm,
    direction,
    planning_responses,
    write_png,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_explicit_exploration_separates_directions_from_images() -> None:
    # Given an opt-in three-direction, three-candidate brief.
    raw = TypeAdapter(JsonObject).validate_json(brief().model_dump_json())
    _ = raw.pop("count")
    raw.update(direction_count=3, candidates_per_direction=3)
    # When parsed, then nine images are budgeted without nine independent directions.
    request = StudioBrief.model_validate_json(json.dumps(raw))
    assert request.effective_direction_count == 3
    assert request.effective_count == 9
    assert request.candidates_per_direction == 3


@pytest.mark.parametrize(
    "options",
    [
        {"count": 3, "direction_count": 3},
        {"count": None, "direction_count": 4, "candidates_per_direction": 3},
        {"count": None, "candidates_per_direction": 3},
    ],
)
def test_ambiguous_or_excessive_exploration_is_rejected(options: dict[str, int | None]) -> None:
    # Given ambiguous legacy count or an over-budget exploration.
    raw = TypeAdapter(JsonObject).validate_json(brief().model_dump_json())
    raw.update(options)
    # When parsed, then no inference can begin under an unclear budget.
    with pytest.raises(ValidationError):
        _ = StudioBrief.model_validate_json(json.dumps(raw))


def test_app_icon_preserves_exact_short_text_without_forced_pictogram() -> None:
    # Given a requested Hangul mark, rather than an inferred initial.
    raw = TypeAdapter(JsonObject).validate_json(brief().model_dump_json())
    raw.update(mode="app_icon", exact_text="틈", logo_type="lettermark")
    request = StudioBrief.model_validate_json(json.dumps(raw))
    # When assembled, then exact text survives without contradictory style defaults.
    prompt = image_prompt(request, direction(1))
    assert '"exact_text":"틈"' in prompt
    assert "Centered simple pictogram" not in prompt
    assert "no lettering" not in prompt


def test_reference_pixels_reach_both_planning_calls(tmp_path: Path) -> None:
    # Given positive and negative local references with independently identified pixels.
    first = tmp_path / "positive.png"
    second = tmp_path / "negative.png"
    pixels = (write_png(first), write_png(second, "#992233"))
    raw = TypeAdapter(JsonObject).validate_json(brief(count=2).model_dump_json())
    raw["references"] = [
        {
            "id": f"reference-{index}",
            "path": str(path),
            "sha256": sha256(data).hexdigest(),
            "role": role,
            "observations": ["A wide open counter"],
            "transfer_traits": ["Counter remains open at small size"] if role == "positive" else [],
            "avoid_traits": ["Exterior shine hides contour"] if role == "negative" else [],
        }
        for index, (path, data, role) in enumerate(
            zip((first, second), pixels, ("positive", "negative"), strict=True)
        )
    ]
    request = StudioBrief.model_validate_json(json.dumps(raw))
    responses = planning_responses()
    report = {
        "directions": [
            TypeAdapter(JsonObject).validate_json(direction(index).model_dump_json())
            for index in range(2)
        ],
        "reference_analysis": [
            {
                "reference_id": f"reference-{index}",
                "observations": ["Open contour on a solid field"],
                "interpretation": "Open space may remain legible",
                "transfer_traits": ["Open counter"] if index == 0 else [],
                "avoid_traits": ["Distracting gloss"] if index == 1 else [],
            }
            for index in range(2)
        ],
    }
    responses[1] = FakeCompletion(json.dumps(report))
    ctx = FakeContext(llm=FakeLlm(responses=responses))
    # When planning, then both calls inspect actual labeled images without image generation.
    plan = HermesHost(ctx).plan(request)
    assert len(ctx.llm.calls) == 2
    for call in ctx.llm.calls:
        assert tuple(item["data"] for item in call["input"] if item["type"] == "image") == pixels
        labels = " ".join(item["text"] for item in call["input"] if item["type"] == "text")
        assert "negative" in labels
        assert "reference-0" in labels
    assert not ctx.dispatches
    assert tuple(item.reference_sha256 for item in plan.reference_analysis) == tuple(
        sha256(data).hexdigest() for data in pixels
    )


@pytest.mark.parametrize("failure", ["missing", "corrupt", "hash", "unsupported"])
def test_invalid_reference_never_dispatches_a_model(tmp_path: Path, failure: str) -> None:
    # Given invalid or unsupported reference conditioning.
    path = tmp_path / "reference.png"
    if failure != "missing":
        _ = path.write_bytes(b"invalid") if failure == "corrupt" else write_png(path)
    raw = TypeAdapter(JsonObject).validate_json(brief(count=2).model_dump_json())
    raw["references"] = [{"id": "ref", "path": str(path), "sha256": "a" * 64}]
    if failure == "unsupported":
        raw["reference_conditioning"] = "image"
    ctx = FakeContext(llm=FakeLlm(responses=planning_responses()))
    # When the public boundary is used, then malformed inputs fail before a paid call.
    with pytest.raises((StudioError, ValidationError)):
        _ = HermesHost(ctx).plan(StudioBrief.model_validate_json(json.dumps(raw)))
    assert not ctx.llm.calls
    assert not ctx.dispatches
