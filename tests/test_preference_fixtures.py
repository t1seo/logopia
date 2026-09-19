from __future__ import annotations

from hashlib import sha256
from typing import TYPE_CHECKING, Final

import pytest

from logo_helper.preference_gallery import render_preference_gallery
from logo_helper.preference_models import (
    PreferenceManifest,
    PreferencePairInput,
    PreferenceSelection,
    PreferenceSource,
)
from logo_helper.preference_response import (
    PreferenceContext,
    PreferenceDecision,
    PreferenceEvidence,
    PreferenceResponse,
)
from logo_helper.storage import Store

if TYPE_CHECKING:
    from logo_helper.models import Session
    from tests.conftest import Harness

pytest_plugins: Final = ("tests.test_app_icon_gallery",)


@pytest.fixture
def preference_selection(icon_state: Session) -> PreferenceSelection:
    first, second = icon_state.artifacts[:2]
    return PreferenceSelection(
        shared_brief="Fixture only: an app for clear daily notes. No required text.",
        pairs=(
            PreferencePairInput(
                first=PreferenceSource(
                    session=icon_state.id, revision=icon_state.revision, artifact=first.id
                ),
                second=PreferenceSource(
                    session=icon_state.id, revision=icon_state.revision, artifact=second.id
                ),
            ),
        ),
        seed=20260919,
        ai_review_budget=1,
    )


@pytest.fixture
def preference_response(
    harness: Harness, preference_selection: PreferenceSelection
) -> PreferenceResponse:
    result = render_preference_gallery(Store.at(harness.workspace), preference_selection, "blind")
    raw = (harness.workspace / result.path / "manifest.json").read_bytes()
    manifest = PreferenceManifest.model_validate_json(raw)
    pair = manifest.pairs[0]
    return PreferenceResponse(
        manifest_sha256=sha256(raw).hexdigest(),
        reviewer="Synthetic fixture observer",
        reviewer_kind="user",
        review_calls=0,
        context=PreferenceContext(mask="circle", peer_context=True),
        decisions=(
            PreferenceDecision(
                pair_id=pair.id,
                a_sha256=pair.a.sha256,
                b_sha256=pair.b.sha256,
                outcome="tie",
                observations=PreferenceEvidence(
                    brief_reference_fit="Fixture only; both have a flat green field.",
                    shape_background="The central yellow pixel differs from the background.",
                    craft_detail="No designed curve or lettering exists in this fixture.",
                    effects_material="No object depth is present.",
                    distinctiveness="A and B share identical synthetic bytes.",
                    small_size_32="At 32 px the center point disappears.",
                    peer_context="The two identical rectangles have no differentiating feature.",
                ),
            ),
        ),
    )
