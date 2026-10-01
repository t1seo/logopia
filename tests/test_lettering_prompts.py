from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from logo_helper.app_icon_models import AppIconIntent
from logo_helper.app_icon_prompts import build_app_icon_prompt
from logo_helper.color_models import (
    ColorConstraints,
    PaletteContent,
    PaletteVersion,
    palette_digest,
)
from logo_helper.models import (
    ArtifactId,
    Brief,
    LockupIntent,
    LogoType,
    PaletteId,
    Session,
    SessionId,
)
from logo_helper.prompts import PromptResult, build_prompt
from logo_helper.storage import Store
from tests.test_brand_quality import palette_instruction
from tests.test_color_models import palette, session

if TYPE_CHECKING:
    from tests.conftest import Harness


def lettering_brief(logo_type: LogoType = "wordmark", text: str = "너울  Lab") -> Brief:
    return Brief(
        brand_name="Historical brand context",
        exact_text=text,
        industry="creative tools",
        audience="independent makers",
        logo_type=logo_type,
        styles=("playful", "sculpted", "forward-slanted"),
        palette=("user-chosen multicolor",),
        background="transparent",
        use_cases=("a readable 160px-wide header",),
    )


@pytest.mark.parametrize(
    ("logo_type", "construction"),
    [
        ("wordmark", "lettering-only wordmark"),
        ("lettermark", "distinct readable letters"),
        ("monogram", "deliberate shared stroke"),
        ("combination", "distinct symbol and the supplied exact text"),
        ("symbol", "recognizable pictorial symbol"),
        ("abstract", "nonliteral abstract mark"),
        ("emblem", "lettering enclosed"),
        ("mascot", "character mascot"),
    ],
)
def test_existing_logo_types_reach_their_construction_branch(
    harness: Harness, logo_type: LogoType, construction: str
) -> None:
    state = session().model_copy(update={"brief": lettering_brief(logo_type)})
    result = build_prompt(
        Store.at(harness.workspace),
        state,
        concept="A supplied identity",
        parent_id=None,
        changes="",
    )
    # Type-aware routing must alter the construction, without creating a new intent/schema.
    assert construction in result.prompt
    assert result.lockup is None
    assert result.app_icon is None
    assert "Effective symbol-plus-text lockup" not in result.prompt
    assert repr(state.brief.exact_text) in result.prompt
    assert result.revision == 0


@pytest.mark.parametrize("logo_type", ["wordmark", "lettermark", "monogram"])
def test_exact_unicode_text_survives_cli_prompt_and_import(
    harness: Harness, logo_type: LogoType
) -> None:
    exact = '  너울  Lab "온" & A\u0301!\n한  '
    slogan = "오늘도,  따뜻하게! Keep Case."
    brief = lettering_brief(logo_type, exact).model_copy(update={"slogan": slogan})
    _ = harness.brief.write_text(brief.model_dump_json(), encoding="utf-8")
    harness.init()
    before = harness.state_path.read_bytes()
    result = PromptResult.model_validate_json(
        harness.ok("prompt", "--session", "demo", "--concept", "Preserve the supplied script")
    )
    assert harness.state_path.read_bytes() == before
    assert repr(exact) in result.prompt
    assert repr(slogan) in result.prompt
    assert "romanize" in result.prompt
    assert "Hangul syllable blocks" in result.prompt
    _ = harness.prompt.write_text(result.prompt, encoding="utf-8")
    imported = Session.model_validate_json(harness.import_image(result.revision))
    assert imported.brief.exact_text == exact
    assert imported.brief.slogan == slogan
    assert imported.artifacts[0].prompt == result.prompt
    assert imported.artifacts[0].lockup is None
    assert imported.artifacts[0].review is None


@pytest.mark.parametrize(
    ("text", "styles", "concept"),
    [
        (
            "momi",
            ("playful", "multicolor", "sculpted"),
            "Broad rounded strokes, circular counters and a gently bouncing baseline",
        ),
        (
            "RIVET",
            ("athletic", "forward-slanted"),
            "Compact spacing, strong diagonal stems and one open terminal cut",
        ),
    ],
)
def test_wordmark_concept_and_user_styles_remain_data_without_a_new_preset(
    harness: Harness, text: str, styles: tuple[str, ...], concept: str
) -> None:
    brief = lettering_brief(text=text).model_copy(update={"styles": styles})
    state = session().model_copy(update={"brief": brief})
    result = build_prompt(
        Store.at(harness.workspace), state, concept=concept, parent_id=None, changes=""
    )
    assert concept in result.prompt
    assert all(style in result.prompt for style in styles)
    assert repr(text) in result.prompt
    assert "Do not add a separate icon" in result.prompt
    assert "one-color silhouette" in result.prompt
    assert "does not replace the requested palette" in result.prompt
    assert result.palette_id is None
    assert result.app_icon is None


def test_stacked_lettermark_does_not_resolve_a_symbol_lockup(harness: Harness) -> None:
    state = session().model_copy(update={"brief": lettering_brief("lettermark", "NR")})
    concept = "N above R, same geometric module, open square counters and a clear inter-row gap"
    result = build_prompt(
        Store.at(harness.workspace), state, concept=concept, parent_id=None, changes=""
    )
    assert concept in result.prompt
    assert result.lockup is None
    assert "distinct readable letters" in result.prompt
    assert "Make a combination mark" not in result.prompt
    assert "Make a lettering-only monogram" not in result.prompt


def test_strict_palette_overrides_sculpted_multicolor_style(harness: Harness) -> None:
    base = palette()
    content = PaletteContent(
        swatches=base.swatches,
        constraints=ColorConstraints(
            allowed_hex=(base.swatches[0].hex,), max_colors=1, allow_gradients=False
        ),
        source="assistant",
        selected_by="user",
        rationale="User requested one color, including sculpted letter faces",
    )
    strict = PaletteVersion.model_validate(
        content.model_dump() | {"id": PaletteId("one-color"), "digest": palette_digest(content)}
    )
    state = session(strict).model_copy(
        update={"brief": lettering_brief(), "active_palette_id": strict.id}
    )
    result = build_prompt(
        Store.at(harness.workspace),
        state,
        concept="Sculpted multicolor lettering, subject to the selected palette",
        parent_id=None,
        changes="",
    )
    assert result.palette_id == strict.id
    assert result.palette_digest == strict.digest
    assert palette_instruction(result.prompt) == strict.model_dump(
        mode="json", include={"swatches", "constraints"}
    )
    assert "depth and extra tones must obey the palette and gradient policy" in result.prompt
    assert "No gradients unless allowed" in result.prompt
    assert state.palette(strict.id) == strict


@pytest.mark.parametrize("with_parent", [False, True])
def test_resolved_combination_lockup_wins_over_original_wordmark_type(
    harness: Harness, with_parent: bool
) -> None:
    brief = lettering_brief()
    lockup = LockupIntent(layout="stacked", typography_style="Open angular lettering")
    _ = harness.brief.write_text(brief.model_dump_json(), encoding="utf-8")
    path = harness.workspace / "lockup.json"
    _ = path.write_text(lockup.model_dump_json(), encoding="utf-8")
    harness.init()
    extra: tuple[str, ...] = ("--lockup-file", str(path))
    if with_parent:
        _ = harness.import_image(0, "v1", *extra)
        extra = ("--parent", "v1", "--changes", "Widen only the counters")
    before = harness.state_path.read_bytes()
    result = PromptResult.model_validate_json(harness.ok("prompt", "--session", "demo", *extra))
    assert result.lockup == lockup
    assert lockup.model_dump_json() in result.prompt
    assert "Make a lettering-only wordmark" not in result.prompt
    assert "Do not add a separate icon" not in result.prompt
    assert "Create one wordmark" not in result.prompt
    assert harness.state_path.read_bytes() == before
    imported = Session.model_validate_json(
        harness.import_image(
            result.revision,
            "v2",
            *("--parent", "v1") if with_parent else ("--lockup-file", str(path)),
        )
    )
    assert imported.artifacts[-1].lockup == result.lockup


def test_edit_preserves_revised_parent_text_and_omits_fresh_construction(harness: Harness) -> None:
    _ = harness.brief.write_text(
        lettering_brief(text="OLD NAME").model_dump_json(), encoding="utf-8"
    )
    harness.init()
    _ = harness.prompt.write_text("Change OLD NAME to exact 너울  Lab; keep the joined strokes.")
    _ = harness.import_image()
    original = harness.state_path.read_bytes()
    store = Store.at(harness.workspace)
    state = store.load(SessionId("demo"))
    changes = 'Keep exact 너울  Lab and joined strokes; change only spacing. Quote: "KEEP".'
    result = build_prompt(store, state, concept="", parent_id=ArtifactId("v1"), changes=changes)
    assert result.parent_image_path == str(harness.state_path.parent / "artifacts/v1.png")
    assert changes in result.prompt
    assert "Initial brief exact text (historical intent): 'OLD NAME'" in result.prompt
    assert "preserve the parent's visible text" in result.prompt
    assert "Create one" not in result.prompt
    assert "Logo construction:" not in result.prompt
    assert "Make a lettering-only wordmark" not in result.prompt
    assert harness.state_path.read_bytes() == original


@pytest.mark.parametrize("preset", ["monogram", "abstract"])
def test_icon_override_bypasses_brand_lettering_guidance(harness: Harness, preset: str) -> None:
    icon = AppIconIntent.model_validate(
        {"preset": preset, "subject": "notes", "placement": "center", "text": "메모"}
        if preset == "monogram"
        else {"preset": preset, "subject": "notes", "placement": "center"}
    )
    state = session().model_copy(update={"brief": lettering_brief()})
    result = build_prompt(
        Store.at(harness.workspace), state, concept="", parent_id=None, changes="", app_icon=icon
    )
    assert result.prompt == build_app_icon_prompt(icon, state.brief, None, "", "", has_parent=False)
    assert "Logo construction:" not in result.prompt
    assert "Lettering fidelity:" not in result.prompt
    assert "너울" not in result.prompt
    assert result.app_icon == icon
    assert result.requested_background == "opaque"
