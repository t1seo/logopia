from __future__ import annotations

import json

import pytest

from logo_helper.app_icon_models import AppIconIntent
from logo_helper.brief_models import Brief
from logo_helper.model_base import ProjectError


def test_apple_foreground_accepts_alpha_intent_without_confusing_appearance() -> None:
    # Given: a real foreground PNG is intended for Icon Composer's Mono editing mode.
    raw = json.dumps(
        {
            "preset": "abstract",
            "subject": "folded ribbon",
            "placement": "center",
            "asset": {
                "kind": "apple_layered",
                "platform": "apple",
                "role": "foreground",
                "appearance": "clear_dark",
                "composer_mode": "mono",
            },
        }
    )
    # When: the actual brief boundary parses a transparent foreground request.
    brief = Brief(
        brand_name="Fold",
        exact_text="",
        industry="notes",
        audience="writers",
        background="transparent",
        app_icon=AppIconIntent.model_validate_json(raw),
    )
    # Then: independently declared rendering and home-screen intents survive a round trip.
    restored = Brief.model_validate_json(brief.model_dump_json())
    assert restored == brief
    assert restored.app_icon is not None
    assert restored.app_icon.asset is not None
    assert restored.app_icon.asset.composer_mode == "mono"
    assert restored.app_icon.asset.appearance == "clear_dark"


@pytest.mark.parametrize(
    "asset",
    [
        {"kind": "apple_layered", "platform": "android", "role": "foreground"},
        {"kind": "apple_layered", "platform": "apple", "role": "composite"},
        {"kind": "android_adaptive", "platform": "android", "role": "composite"},
        {"kind": "google_play_listing", "platform": "android", "role": "foreground"},
        {"kind": "google_play_listing", "platform": "android", "appearance": "themed"},
        {"kind": "concept_artwork", "composer_mode": "mono"},
        {
            "kind": "android_adaptive",
            "platform": "android",
            "role": "foreground",
            "appearance": "clear_dark",
        },
    ],
)
def test_invalid_asset_role_or_platform_rejected_at_boundary(asset: dict[str, str]) -> None:
    # Given: independent fields cannot describe a contradictory platform deliverable.
    raw = json.dumps(
        {"preset": "abstract", "subject": "fold", "placement": "center", "asset": asset}
    )
    # When / Then: an inconsistent typed asset never reaches import or generation.
    with pytest.raises(ProjectError, match="invalid_asset"):
        _ = AppIconIntent.model_validate_json(raw)


def test_legacy_icon_without_asset_keeps_existing_json_shape() -> None:
    # Given: a saved v2 icon intent from before asset-specific policies.
    raw = '{"preset":"pictogram","subject":"map","placement":"center","text":null}'
    # When: it passes through the new model.
    intent = AppIconIntent.model_validate_json(raw)
    # Then: no invented platform intent enters the original snapshot.
    assert intent.asset is None
    assert "asset" not in intent.model_dump()
