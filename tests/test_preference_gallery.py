from __future__ import annotations

from hashlib import sha256
from typing import TYPE_CHECKING, Final

import pytest
from pydantic import HttpUrl, ValidationError

from logo_helper.models import ProjectError
from logo_helper.preference_gallery import render_preference_gallery
from logo_helper.preference_models import (
    PreferenceManifest,
    PreferencePairInput,
    PreferenceReference,
    PreferenceSelection,
    PreferenceSource,
)
from logo_helper.storage import Store

if TYPE_CHECKING:
    from logo_helper.models import Session
    from tests.conftest import Harness

pytest_plugins: Final = ("tests.test_preference_fixtures",)


def test_blind_interface_when_sources_have_creator_metadata(
    harness: Harness, preference_selection: PreferenceSelection
) -> None:
    # Given: source artifacts include named styles, IDs and saved creator prompts.
    before = harness.state_path.read_bytes()
    # When: a blind gallery is rendered.
    result = render_preference_gallery(Store.at(harness.workspace), preference_selection, "blind")
    markup = (harness.workspace / result.index_path).read_text()
    manifest = PreferenceManifest.model_validate_json(
        (harness.workspace / result.path / "manifest.json").read_bytes()
    )
    # Then: only neutral A/B labels, a common brief, and the same diagnostic sizes are exposed.
    assert all(value not in markup for value in ("v1", "v2", "Exact prompt", "ip_mascot"))
    assert preference_selection.shared_brief in markup
    for size in (32, 48, 64, 128):
        assert f'width="{size}" height="{size}"' in markup
    assert 'class="home light"' in markup
    assert 'class="home dark"' in markup
    for pair in manifest.pairs:
        for candidate in (pair.a, pair.b):
            data = (harness.workspace / result.path / candidate.image_file).read_bytes()
            assert sha256(data).hexdigest() == candidate.sha256
            assert candidate.source.artifact not in candidate.image_file
    assert harness.state_path.read_bytes() == before


def test_seed_is_repeatable_and_sides_are_balanced(
    harness: Harness, icon_state: Session, preference_selection: PreferenceSelection
) -> None:
    # Given: three distinct pairs, including a legacy non-icon candidate.
    sources = tuple(
        PreferenceSource(session=icon_state.id, revision=0, artifact=item.id)
        for item in icon_state.artifacts
    )
    pairs = tuple(
        PreferencePairInput(first=sources[left], second=sources[right])
        for left, right in ((0, 1), (0, 2), (1, 2))
    )
    selection = preference_selection.model_copy(update={"pairs": pairs})
    store = Store.at(harness.workspace)
    # When: the same seeded comparison is rendered into separate new directories.
    results = tuple(render_preference_gallery(store, selection, name) for name in ("one", "two"))
    manifests = tuple(
        PreferenceManifest.model_validate_json(
            (harness.workspace / result.path / "manifest.json").read_bytes()
        )
        for result in results
    )
    # Then: source order repeats and input-group position counts differ by at most one.
    assert manifests[0] == manifests[1]
    first_on_left = sum(
        any(pair.a.source == item.first and pair.b.source == item.second for item in pairs)
        for pair in manifests[0].pairs
    )
    assert first_on_left in {1, 2}


@pytest.mark.parametrize(
    "output", ["../escape", "/escape", "a/../b", ".git/x", ".logo-generator/x"]
)
def test_bad_output_path_when_blind_gallery_is_requested(
    harness: Harness, preference_selection: PreferenceSelection, output: str
) -> None:
    # Given: a path outside the ordinary gallery output namespace.
    # When: publication is requested.
    with pytest.raises(ProjectError, match=r"unsafe_path|reserved_output"):
        _ = render_preference_gallery(Store.at(harness.workspace), preference_selection, output)
    # Then: no managed source is changed.
    assert not list(harness.workspace.glob(".preference-gallery-*"))


@pytest.mark.parametrize("bad", ["missing", "corrupt", "hash", "escape"])
def test_reference_is_verified_when_local_copy_is_requested(
    harness: Harness, preference_selection: PreferenceSelection, bad: str
) -> None:
    # Given: a local reference with one invalid input property.
    data = harness.png.read_bytes()
    path = harness.workspace / "reference.png"
    if bad != "missing":
        _ = path.write_bytes(b"not an image" if bad == "corrupt" else data)
    reference = PreferenceReference(
        label="Fixture reference",
        source_url=HttpUrl("https://example.com/reference"),
        role="positive",
        observations="Synthetic green field only.",
        verification="image_observed",
        image_path="../reference.png" if bad == "escape" else "reference.png",
        image_sha256=sha256(b"not an image" if bad == "corrupt" else data).hexdigest()
        if bad != "hash"
        else "0" * 64,
    )
    selection = preference_selection.model_copy(update={"references": (reference,)})
    # When: the reference is included in the rendered comparison.
    with pytest.raises(
        ProjectError, match=r"invalid_file|invalid_reference|hash_mismatch|unsafe_path"
    ):
        _ = render_preference_gallery(Store.at(harness.workspace), selection, "blind")
    # Then: no partial gallery or ambiguous reference is published.
    assert not (harness.workspace / "blind").exists()


def test_bounded_input_when_too_many_pairs_are_submitted(
    preference_selection: PreferenceSelection,
) -> None:
    # Given: the explicit 12-pair comparison ceiling is exceeded.
    payload = preference_selection.model_copy(update={"pairs": preference_selection.pairs * 13})
    # When: a submitted selection crosses the JSON boundary.
    with pytest.raises(ValidationError):
        _ = PreferenceSelection.model_validate_json(payload.model_dump_json())
    # Then: the extra work cannot be scheduled by this API.


def test_reference_copy_and_escaping_when_verified_input_is_supplied(
    harness: Harness, preference_selection: PreferenceSelection
) -> None:
    # Given: a verified private PNG and hostile-looking text are explicit review inputs.
    data = harness.png.read_bytes()
    _ = (harness.workspace / "reference.png").write_bytes(data)
    reference = PreferenceReference(
        label="Local fixture",
        source_url=HttpUrl("https://example.com/reference"),
        role="negative",
        observations='<script>alert("not executable")</script>',
        verification="image_observed",
        image_sha256=sha256(data).hexdigest(),
        image_path="reference.png",
    )
    selection = preference_selection.model_copy(update={"references": (reference,)})
    # When: the read-only comparison is rendered.
    result = render_preference_gallery(Store.at(harness.workspace), selection, "blind")
    markup = (harness.workspace / result.index_path).read_text()
    # Then: the image remains byte-identical and observations are escaped, role-labeled data.
    assert (harness.workspace / result.path / "images/reference-01.png").read_bytes() == data
    assert "Local fixture · negative" in markup
    assert "&lt;script&gt;" in markup
    assert '<script>alert("not executable")</script>' not in markup
