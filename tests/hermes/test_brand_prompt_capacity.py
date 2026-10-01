from __future__ import annotations

import pytest
from logopia_studio.models import Direction, StudioBrief
from logopia_studio.models_base import Prompt
from logopia_studio.prompts import edit_prompt, image_prompt
from pydantic import TypeAdapter
from tests.hermes.test_host_fakes import strategy


def capacity_brief() -> StudioBrief:
    return StudioBrief(
        name="Example",
        exact_text="Example",
        product="Example product",
        audience="Readers",
        personality="Calm",
        use_case="Header",
    )


def capacity_direction(length: int) -> Direction:
    return Direction(
        id="d1",
        title="Plain",
        motif="Type",
        construction="Type",
        rationale="Type",
        risk="Type",
        preserve=("Text",),
        prompt="X" * length,
    )


@pytest.mark.parametrize("direction_length", [19_051, 19_141])
def test_generation_preserves_a_long_direction_accepted_before_quality_guidance(
    direction_length: int,
) -> None:
    # Given an unchanged brief and long direction whose previous request fit the model limit.
    request = capacity_brief()
    chosen = capacity_direction(direction_length)
    # When new quality guidance is applied, then advisory prose cannot reject the same intent.
    prompt = image_prompt(request, chosen)
    assert TypeAdapter(Prompt).validate_python(prompt) == prompt
    previous_prompt_length = 849 + direction_length
    assert len(prompt) <= previous_prompt_length <= 20_000
    assert f"<direction-data>{chosen.prompt}</direction-data>" in prompt


@pytest.mark.parametrize("parent_length", [19_500, 19_620, 19_653])
def test_edit_preserves_a_long_parent_accepted_before_quality_guidance(parent_length: int) -> None:
    # Given an exact saved parent near capacity and a small later spacing correction.
    request = capacity_brief()
    parent = "X" * parent_length
    keep = ("Exact text",)
    change = "Open the gap"
    # When building the edit, then optional framing cannot displace the exact parent or feedback.
    prompt = edit_prompt(request, parent, keep, change)
    assert TypeAdapter(Prompt).validate_python(prompt) == prompt
    previous_prompt_length = 347 + parent_length
    assert len(prompt) <= previous_prompt_length <= 20_000
    assert parent in prompt
    assert change in prompt


def test_first_edit_remains_valid_after_generation_with_strategy() -> None:
    # Given a long otherwise valid direction and a concise full six-field strategy.
    request = capacity_brief()
    chosen = capacity_direction(16_300)
    planned = strategy().model_copy(
        update={
            "positioning": "p" * 320,
            "audience_need": "n" * 320,
            "brand_promise": "b" * 320,
            "distinctive_principle": "d" * 320,
            "typography": "t" * 320,
            "color_roles": "c" * 320,
        }
    )
    parent = image_prompt(request, chosen, strategy=planned)
    assert TypeAdapter(Prompt).validate_python(parent) == parent
    # When its first scoped correction is requested, then original direction and change survive.
    prompt = edit_prompt(request, parent, ("open contour",), "Widen the gap.")
    assert TypeAdapter(Prompt).validate_python(prompt) == prompt
    assert chosen.prompt in prompt
    assert "Widen the gap." in prompt


def test_legacy_parent_with_advice_like_text_is_preserved() -> None:
    # Given an existing parent whose user-authored wording resembles a new advice marker.
    parent = (
        "Keep my exact layout\n<brand-generation-advice>\nUser detail\n</brand-generation-advice>"
    )
    # When editing, then arbitrary historical instructions cannot be classified as new advice.
    prompt = edit_prompt(capacity_brief(), parent, ("user detail",), "Widen the gap.")
    assert parent in prompt
