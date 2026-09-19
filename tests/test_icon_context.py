from __future__ import annotations

from typing import TYPE_CHECKING, Final

from logo_helper.app_icon_gallery import render_app_icon_gallery
from logo_helper.models import ArtifactId
from logo_helper.storage import Store

if TYPE_CHECKING:
    from logo_helper.models import Session
    from tests.conftest import Harness

pytest_plugins: Final = ("tests.test_app_icon_gallery",)


def test_actual_size_and_balanced_context_when_gallery_is_rendered(
    harness: Harness, icon_state: Session
) -> None:
    # Given: two explicit originals, without visual approval.
    before = harness.state_path.read_bytes()
    # When: the ordinary gallery renders diagnostic surroundings.
    result = render_app_icon_gallery(
        Store.at(harness.workspace), icon_state, (ArtifactId("v1"), ArtifactId("v2")), "icons"
    )
    markup = (harness.workspace / result.index_path).read_text()
    # Then: every peer uses real candidate bytes and equal-size simulation controls.
    assert 'id="size-48"' in markup
    assert 'class="context-home"' in markup
    assert 'class="context-list"' in markup
    assert "Simulation" in markup
    assert "official platform sizes" in markup
    assert "candidate peers" in markup
    assert markup.count('src="images/v1.png"') == markup.count('src="images/v2.png"')
    assert harness.state_path.read_bytes() == before
