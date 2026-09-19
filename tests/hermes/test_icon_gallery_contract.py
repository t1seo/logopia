from pathlib import Path

from logopia_studio.gallery import publish_gallery
from tests.hermes.test_gallery_fixture import make_workflow


def test_icon_gallery_displays_equal_sized_diagnostic_context_without_changing_originals(
    tmp_path: Path,
) -> None:
    state = make_workflow(tmp_path)
    state = state.model_copy(update={"brief": state.brief.model_copy(update={"mode": "app_icon"})})
    before = tuple((tmp_path / item.image_path).read_bytes() for item in state.candidates)
    gallery = publish_gallery(tmp_path, state, tmp_path / "gallery")
    html = gallery.read_text(encoding="utf-8")
    assert all(f'data-diagnostic-size="{width}"' in html for width in (32, 48, 64, 128))
    assert 'data-platform-preview="simulation"' in html
    assert 'data-icon-context="48"' in html
    assert tuple((tmp_path / item.image_path).read_bytes() for item in state.candidates) == before
