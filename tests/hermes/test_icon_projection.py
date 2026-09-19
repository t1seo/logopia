from pathlib import Path

import pytest
from logopia_studio.engine import Studio
from logopia_studio.helper_models import HelperBrief
from logopia_studio.host_api import JsonObject
from logopia_studio.models import StudioBrief
from logopia_studio.models_icon import StudioIconIntent
from logopia_studio.registration import register
from pydantic import TypeAdapter, ValidationError
from tests.hermes.test_core_fixtures import REPO, FixtureHost, brief
from tests.hermes.test_host_fakes import FakeContext


def test_legacy_icon_intent_stays_absent() -> None:
    request = brief().model_copy(update={"mode": "app_icon"})
    assert HelperBrief.from_brief(request).app_icon is None


def test_explicit_icon_intent_survives_real_helper_round_trip(tmp_path: Path) -> None:
    request = StudioBrief.model_validate_json(
        brief().model_copy(update={"mode": "app_icon"}).model_dump_json()[:-1]
        + (
            ',"app_icon":{"preset":"abstract","subject":"A folded contour",'
            '"placement":"lower_left","asset":{"kind":"concept_artwork",'
            '"platform":"apple","appearance":"dark"}}}'
        )
    )
    studio = Studio(tmp_path, REPO, FixtureHost(tmp_path))
    state = studio.create("icon", request)
    assert studio.steps.helper.show(state).brief.app_icon == request.app_icon


@pytest.mark.parametrize("kind", ["apple_layered", "android_adaptive", "google_play_listing"])
def test_native_platform_deliverable_is_rejected_before_inference(kind: str) -> None:
    raw = (
        brief().model_copy(update={"mode": "app_icon"}).model_dump_json()[:-1]
        + (
            ',"app_icon":{"preset":"abstract","subject":"Fold","placement":"center",'
            '"asset":{"kind":"'
        )
        + kind
        + '"}}}'
    )
    with pytest.raises(ValidationError, match="unsupported_asset"):
        _ = StudioBrief.model_validate_json(raw)


@pytest.mark.parametrize(
    "intent",
    [
        '{"preset":"abstract","text":"A"}',
        '{"preset":"abstract","text":""}',
        '{"preset":"monogram","text":null}',
        '{"preset":"monogram","text":""}',
        '{"preset":"monogram","text":"A B"}',
        '{"preset":"monogram","text":"A\\u200b"}',
        '{"preset":"monogram","text":"123456789"}',
        '{"preset":"abstract","asset":{"appearance":"dark"}}',
        '{"preset":"abstract","asset":{"platform":"apple","appearance":"themed"}}',
        '{"preset":"abstract","asset":{"platform":"android","appearance":"clear_light"}}',
        '{"preset":"abstract","asset":{"composer_mode":"default"}}',
    ],
)
def test_icon_metadata_rejects_helper_incompatible_intent_at_boundary(
    tmp_path: Path, intent: str
) -> None:
    # Given invalid text or platform metadata that the helper would reject after persistence.
    raw = intent[:-1] + ',"subject":"Fold","placement":"center"}'
    metadata = TypeAdapter(JsonObject).validate_json(raw)
    raw_brief = TypeAdapter(JsonObject).validate_json(brief().model_dump_json())
    raw_brief.update(mode="app_icon", app_icon=metadata, exact_text=metadata.get("text") or "")
    ctx = FakeContext()
    register(ctx, tmp_path)
    # When the native boundary parses it, then invalid intent cannot reach workflow creation.
    result = TypeAdapter(JsonObject).validate_json(
        ctx.handlers["logopia_start"]({"workflow_id": "invalid", "brief": raw_brief})
    )
    assert result["error"] == "invalid_request"
    assert not ctx.dispatches
    assert not ctx.llm.calls
    assert not tuple(tmp_path.iterdir())


def test_exact_hangul_monogram_and_apple_appearance_remain_supported() -> None:
    # Given an explicit one-syllable mark and valid concept appearance.
    raw = (
        '{"preset":"monogram","subject":"Open counter","placement":"center",'
        '"text":"틈","asset":{"platform":"apple","appearance":"clear_dark"}}'
    )
    # When parsed, then Unicode content and its platform intent survive unchanged.
    intent = StudioIconIntent.model_validate_json(raw)
    assert intent.text == "틈"
    assert intent.asset is not None
    assert intent.asset.appearance == "clear_dark"
