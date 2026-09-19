from pathlib import Path

import pytest
from logopia_studio.engine import Studio
from logopia_studio.models import StudioBrief, StudioError
from pydantic import ValidationError
from tests.hermes.test_core_fixtures import REPO, FixtureHost, brief


def test_review_budget_blocks_edit_before_generating_an_unreviewable_image(tmp_path: Path) -> None:
    host = FixtureHost(tmp_path)
    studio = Studio(tmp_path, REPO, host)
    request = brief().model_copy(update={"review_call_budget": 2})
    created = studio.create("budget", request)
    state = studio.produce(created.id, created.revision)
    with pytest.raises(StudioError, match="review_limit"):
        _ = studio.revise(created.id, state.revision, "c1", (), "Widen gap")
    assert len(host.calls) == 1
    assert len(host.reviews) == 1
    assert studio.status(created.id) == state


def test_review_budget_must_cover_two_roles_for_each_initial_candidate() -> None:
    request = brief(count=3).model_copy(update={"review_call_budget": 4})
    with pytest.raises(ValidationError, match="review_budget"):
        _ = StudioBrief.model_validate_json(request.model_dump_json())
