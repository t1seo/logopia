from __future__ import annotations

from typing import TYPE_CHECKING, Final

from logo_helper.comparison_models import ComparisonResult
from logo_helper.preference_response import PreferenceRecordResult

if TYPE_CHECKING:
    from pathlib import Path

    from logo_helper.preference_models import PreferenceSelection
    from logo_helper.preference_response import PreferenceResponse
    from tests.conftest import Harness

pytest_plugins: Final = ("tests.test_preference_fixtures",)


def test_real_cli_when_gallery_and_response_are_submitted(
    harness: Harness,
    preference_selection: PreferenceSelection,
    preference_response: PreferenceResponse,
    tmp_path: Path,
) -> None:
    # Given: explicit saved candidates and a declared synthetic user response.
    before = harness.state_path.read_bytes()
    selection = tmp_path / "comparison.json"
    response = tmp_path / "response.json"
    _ = selection.write_text(preference_selection.model_dump_json())
    _ = response.write_text(preference_response.model_dump_json())
    # When: both public CLI commands run through the real entry point.
    gallery = ComparisonResult.model_validate_json(
        harness.ok(
            "preference-gallery", "--selection-file", str(selection), "--output", "cli-blind"
        )
    )
    result = PreferenceRecordResult.model_validate_json(
        harness.ok("preference-record", "--gallery", gallery.path, "--response-file", str(response))
    )
    # Then: portable HTML and a preference sidecar exist without modifying source state.
    assert (harness.workspace / gallery.index_path).is_file()
    assert (harness.workspace / result.path).is_file()
    assert result.status == "user_preference"
    assert harness.state_path.read_bytes() == before


def test_real_cli_when_selection_file_is_missing(harness: Harness, tmp_path: Path) -> None:
    # Given: a missing input file.
    # When: the public command reads the bounded JSON input.
    result = harness.run(
        "preference-gallery", "--selection-file", str(tmp_path / "missing.json"), "--output", "bad"
    )
    # Then: the CLI reports a controlled error without leaving an output folder.
    assert result.returncode == 1
    assert "invalid_file" in result.stderr
    assert not (harness.workspace / "bad").exists()
