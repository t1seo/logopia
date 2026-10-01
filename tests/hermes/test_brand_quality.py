from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal

import pytest
from logopia_studio import registration
from logopia_studio.engine import Studio
from logopia_studio.host import HermesHost
from logopia_studio.host_api import JsonObject
from logopia_studio.models import Strategy, StudioBrief
from logopia_studio.models_base import Prompt
from logopia_studio.models_jobs import Feedback
from logopia_studio.prompts import edit_prompt, image_prompt
from pydantic import TypeAdapter
from tests.hermes.test_core_fixtures import REPO
from tests.hermes.test_host_fakes import (
    FakeContext,
    FakeLlm,
    brief,
    critic_response,
    direction,
    native_receipt,
    planning_responses,
    strategy,
    write_png,
)

if TYPE_CHECKING:
    from pathlib import Path


def strategy_data(prompt: str) -> JsonObject:
    start = '<brand-strategy-data authority="advisory">'
    assert start in prompt, "Saved brand strategy must reach the native image request"
    data = prompt.split(start, 1)[1].split("</brand-strategy-data>", 1)[0]
    return TypeAdapter(JsonObject).validate_json(data)


def visual_strategy(planned: Strategy) -> JsonObject:
    return TypeAdapter(JsonObject).validate_json(planned.model_dump_json(exclude={"assumptions"}))


@pytest.mark.parametrize("logo_type", ["wordmark", "symbol", "combination"])
def test_brand_strategy_reaches_generation_when_saved(
    logo_type: Literal["wordmark", "symbol", "combination"],
) -> None:
    # Given saved brand meaning, typography and color placement separate from a direction.
    request = brief().model_copy(update={"logo_type": logo_type})
    planned = strategy()
    # When generating a brand candidate, then every saved strategy field remains available.
    prompt = image_prompt(request, direction(0), strategy=planned)
    assert strategy_data(prompt) == visual_strategy(planned)


def test_explicit_intent_survives_when_strategy_conflicts() -> None:
    # Given user-supplied text, color and canvas alongside a conflicting advisory proposal.
    request = brief().model_copy(
        update={
            "exact_text": "책 사이",
            "colors": ("#FA683A symbol", "#202630 lettering"),
            "notes": "Use the explicit blue #1555AA exterior canvas; no metallic finish.",
        }
    )
    proposed = strategy().model_copy(
        update={"typography": "Space initials", "color_roles": "Gold letters on beige"}
    )
    # When assembled, then the original user intent is retained separately from advisory data.
    prompt = image_prompt(request, direction(0), strategy=proposed)
    raw = prompt.split("<brief-data>", 1)[1].split("</brief-data>", 1)[0]
    restored = StudioBrief.model_validate_json(raw)
    assert (restored.exact_text, restored.colors, restored.notes) == (
        request.exact_text,
        request.colors,
        request.notes,
    )
    assert strategy_data(prompt) == visual_strategy(proposed)


@pytest.mark.parametrize("mode", ["app_icon", "ip"])
def test_brand_strategy_does_not_change_other_modes(
    mode: Literal["app_icon", "ip"],
) -> None:
    # Given an app or character workflow with a saved strategy.
    request = brief().model_copy(update={"mode": mode, "exact_text": ""})
    # When generation receives that strategy, then its existing mode prompt remains unchanged.
    assert image_prompt(request, direction(0), strategy=strategy()) == image_prompt(
        request, direction(0)
    )


def test_latest_edit_feedback_is_current_when_parent_contains_strategy() -> None:
    # Given a saved parent request with advisory strategy and a later spacing correction.
    request = brief()
    parent = image_prompt(request, direction(0), strategy=strategy())
    keep = ("Exact Hangul lettering", "Teal symbol", "White canvas")
    change = "Increase the gap between the symbol and lettering."
    # When editing, then inherited instructions are historical and scoped feedback is current.
    prompt = edit_prompt(request, parent, keep, change)
    assert '<parent-request authority="historical">' in prompt
    assert direction(0).prompt in prompt
    assert request.exact_text in prompt
    assert "<brand-strategy-data" not in prompt
    feedback_block = '<feedback-data authority="current">'
    assert feedback_block in prompt
    payload = prompt.split(feedback_block, 1)[1].split("</feedback-data>", 1)[0]
    assert Feedback.model_validate_json(payload) == Feedback(
        candidate_id="parent", keep=keep, change=change
    )


def test_long_strategy_stays_bounded_without_changing_saved_plan() -> None:
    # Given maximum-length valid strategy fields and assumptions with a normal direction.
    planned = Strategy(
        positioning="Positioning " * 166,
        audience_need="Need " * 400,
        brand_promise="Promise " * 250,
        distinctive_principle="Principle " * 200,
        typography="Typography " * 181,
        color_roles="Color " * 333,
        assumptions=("Assumption " * 181,) * 12,
    )
    saved = planned.model_dump_json()
    # When rendered, then the generation context fits the persisted prompt contract.
    prompt = image_prompt(brief(), direction(0), strategy=planned)
    assert TypeAdapter(Prompt).validate_python(prompt) == prompt
    projected = strategy_data(prompt)
    assert set(projected) == set(visual_strategy(planned))
    assert all(isinstance(value, str) and len(value) <= 321 for value in projected.values())
    assert planned.model_dump_json() == saved


def test_optional_strategy_preserves_a_request_at_the_existing_prompt_limit() -> None:
    # Given a valid request whose brief and direction already fill the saved prompt allowance.
    request = brief()
    chosen = direction(0)
    allowance = 20_000 - len(image_prompt(request, chosen))
    chosen = chosen.model_copy(update={"prompt": chosen.prompt + "x" * allowance})
    original = image_prompt(request, chosen)
    # When optional strategy is supplied, then explicit existing request data is not discarded.
    prompt = image_prompt(request, chosen, strategy=strategy())
    assert TypeAdapter(Prompt).validate_python(prompt) == original


def test_native_start_preserves_strategy_and_helper_intent_when_produced(tmp_path: Path) -> None:
    # Given real native routing with deterministic substitutes only for external model calls.
    image = tmp_path / "native.png"
    _ = write_png(image)
    ctx = FakeContext(
        llm=FakeLlm(responses=[*planning_responses(), *(critic_response() for _ in range(4))]),
        dispatch_results=[native_receipt(image), native_receipt(image)],
    )
    plugin_root = tmp_path / "plugin"
    plugin_root.mkdir()
    _ = (plugin_root / "settings.json").write_text(
        json.dumps({"schema_version": 1, "workspace": str(tmp_path), "helper_repo": str(REPO)}),
        encoding="utf-8",
    )
    registration.register(ctx, plugin_root)
    request: JsonObject = {
        "workflow_id": "brand-quality",
        "brief": TypeAdapter(JsonObject).validate_json(brief().model_dump_json()),
    }
    # When the public start tool produces the agreed candidates and is repeated.
    result = TypeAdapter(JsonObject).validate_json(ctx.handlers["logopia_start"](request))
    helper_brief = tmp_path / ".logo-generator/workflows/brand-quality/requests/brief.json"
    original_intent = helper_brief.read_bytes()
    _ = ctx.handlers["logopia_start"](request)
    # Then saved and dispatched requests include strategy without extra calls or brief mutation.
    assert result["success"] is True
    assert len(ctx.dispatches) == 2
    state = Studio(tmp_path, REPO, HermesHost(ctx)).status("brand-quality")
    assert state.phase == "awaiting_choice"
    assert state.strategy == strategy()
    saved_strategy = state.strategy
    assert saved_strategy is not None
    assert all(
        strategy_data(arguments["prompt"]) == visual_strategy(saved_strategy)
        for _, arguments in ctx.dispatches
    )
    assert all(
        strategy_data(candidate.prompt) == visual_strategy(saved_strategy)
        for candidate in state.candidates
    )
    assert helper_brief.read_bytes() == original_intent
    assert state.brief == brief()
    assert state.call_budget.planning_llm_calls_reserved == 2
    assert state.call_budget.review_llm_calls_reserved == 4
