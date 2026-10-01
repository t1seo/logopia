from __future__ import annotations

import json
from typing import TYPE_CHECKING, Final, TypedDict

import pytest
from pydantic import ValidationError

from logo_helper.app_icon_models import AppIconIntent
from logo_helper.app_icon_prompts import build_app_icon_prompt
from logo_helper.models import Brief, Session
from logo_helper.prompts import PromptResult, build_prompt
from logo_helper.storage import Store
from tests.test_app_icon_compatibility import install_baseline
from tests.test_color_models import session

if TYPE_CHECKING:
    from tests.conftest import Harness


class StrategyPayload(TypedDict):
    positioning: str
    audience_need: str
    brand_promise: str
    distinctive_principle: str
    typography: str
    color_roles: str
    assumptions: list[str]


STRATEGY: Final[StrategyPayload] = {
    "positioning": "A quiet reading companion, not enterprise infrastructure",
    "audience_need": "Readers need an inviting place to keep a thought",
    "brand_promise": "Keep one worthwhile idea close",
    "distinctive_principle": "One open fold represents a saved thought",
    "typography": "A wide serif proposed by the strategist",
    "color_roles": "Proposed warm amber for attention",
    "assumptions": ["Personal reading is the primary use"],
}


def strategy_brief() -> Brief:
    return Brief.model_validate_json(
        json.dumps(session().brief.model_dump(mode="json") | {"brand_strategy": STRATEGY})
    )


@pytest.mark.parametrize("version", [1, 2])
def test_absent_strategy_does_not_rewrite_existing_sessions(harness: Harness, version: int) -> None:
    # Given: actual pre-strategy persisted state.
    before = install_baseline(harness, version)
    # When: the public CLI reads it and builds a prompt.
    shown = Session.model_validate_json(harness.ok("show", "--session", "demo"))
    _ = harness.ok("prompt", "--session", "demo")
    # Then: absence stays absent and the source bytes remain untouched.
    assert shown.brief.brand_strategy is None
    assert "brand_strategy" not in shown.brief.model_dump()
    assert harness.state_path.read_bytes() == before


def test_strategy_roundtrips_through_init_and_prompt_without_mutation(harness: Harness) -> None:
    # Given: a brief with proposed strategy and exact user text.
    brief = strategy_brief()
    _ = harness.brief.write_text(brief.model_dump_json(), encoding="utf-8")
    harness.init()
    before = harness.state_path.read_bytes()
    # When: the user asks for a concept through the real CLI.
    result = PromptResult.model_validate_json(
        harness.ok("prompt", "--session", "demo", "--concept", "An open folded page")
    )
    # Then: saved strategy survives and the generation receives its useful context.
    restored = Session.model_validate_json(harness.state_path.read_bytes())
    assert restored.brief == brief
    assert STRATEGY["distinctive_principle"] in result.prompt
    assert repr(brief.exact_text) in result.prompt
    assert harness.state_path.read_bytes() == before


def test_strategy_is_frozen_typed_input() -> None:
    # Given: a valid strategy parsed at the external boundary.
    strategy = strategy_brief().brand_strategy
    assert strategy is not None
    # When: a caller tries to mutate this saved intent.
    with pytest.raises(ValidationError, match="frozen_instance"):
        strategy.typography = "Changed"


@pytest.mark.parametrize("invalid", [("unknown", "invented"), ("positioning", 5)])
def test_invalid_strategy_rejected_before_initialization(
    harness: Harness, invalid: tuple[str, str | int]
) -> None:
    # Given: malformed strategy supplied by a caller.
    _ = harness.brief.write_text(
        json.dumps(
            session().brief.model_dump(mode="json")
            | {"brand_strategy": STRATEGY | {invalid[0]: invalid[1]}}
        ),
        encoding="utf-8",
    )
    # When: it crosses the CLI boundary.
    result = harness.run("init", "--session", "demo", "--brief", str(harness.brief))
    # Then: no session is created from untyped or unknown strategy data.
    assert result.returncode != 0
    assert not harness.state_path.exists()


def test_parent_edit_does_not_receive_historical_strategy(harness: Harness) -> None:
    # Given: an existing candidate originating from a strategic brief.
    _ = harness.brief.write_text(strategy_brief().model_dump_json(), encoding="utf-8")
    harness.init()
    _ = harness.import_image()
    before = harness.state_path.read_bytes()
    # When: the user edits only its spacing.
    result = PromptResult.model_validate_json(
        harness.ok("prompt", "--session", "demo", "--parent", "v1", "--changes", "Open the gap")
    )
    # Then: strategy cannot restore an old appearance over the parent's actual design.
    assert "Open the gap" in result.prompt
    assert STRATEGY["distinctive_principle"] not in result.prompt
    assert STRATEGY["typography"] not in result.prompt
    assert harness.state_path.read_bytes() == before


def test_app_icon_override_keeps_its_existing_prompt(harness: Harness) -> None:
    # Given: a brand strategy and an explicit icon request.
    brief = strategy_brief()
    state = session().model_copy(update={"brief": brief})
    icon = AppIconIntent(preset="soft_3d", subject="Open fold", placement="center")
    # When: that override routes the prompt to the icon workflow.
    result = build_prompt(
        Store.at(harness.workspace), state, concept="", parent_id=None, changes="", app_icon=icon
    )
    # Then: new brand rendering rules and strategy never alter the icon path.
    assert result.prompt == build_app_icon_prompt(icon, brief, None, "", "", has_parent=False)
    assert STRATEGY["positioning"] not in result.prompt


def test_supporting_context_is_bounded_without_changing_long_saved_strategy() -> None:
    # Given: valid strategy with leading whitespace and a long rationale.
    long_positioning = " " * 350 + "Positioning detail " * 1000
    brief = Brief.model_validate_json(
        json.dumps(
            session().brief.model_dump(mode="json")
            | {"brand_strategy": STRATEGY | {"positioning": long_positioning}}
        )
    )
    strategy = brief.brand_strategy
    assert strategy is not None
    # When: the proposed context is prepared for generation.
    rendered = strategy.prompt_context()
    # Then: the render is concise, while the stored value remains byte-for-byte intact.
    assert len(rendered) < 3000
    assert "Positioning detail" in rendered
    assert strategy.positioning == long_positioning
