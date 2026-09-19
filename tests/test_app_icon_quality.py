from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final

import pytest
from pydantic import TypeAdapter

from logo_helper.app_icon_models import AppIconPlacement, AppIconPreset
from logo_helper.app_icon_prompts import build_app_icon_prompt, placement_direction
from logo_helper.models import AppIconIntent, Brief, FrozenModel, PaletteVersion, ProjectError
from logo_helper.prompts import PromptResult
from tests.test_palette_workflow import add_palette

if TYPE_CHECKING:
    from tests.conftest import Harness

QUALITY: Final = Path(__file__).resolve().parents[1] / "docs/qa/icon-craft-2026/prompt-fixtures"


class PromptCase(FrozenModel):
    name: str
    icon: AppIconIntent
    brief: Brief
    palette: PaletteVersion | None
    concept: str
    changes: str
    has_parent: bool
    expected: str


class QuotedInput(FrozenModel):
    subject: str
    concept: str
    requested_changes: str
    exact_lettering: str | None
    color_description: tuple[str, ...]


IP_CASES: Final = TypeAdapter(tuple[PromptCase, ...]).validate_json(
    (QUALITY / "ip-pins-v2.json").read_bytes()
)
QUALITY_CASES: Final = TypeAdapter(tuple[PromptCase, ...]).validate_json(
    (QUALITY / "quality-cases-v2.json").read_bytes()
)
DIRECTIONS: Final = TypeAdapter(dict[AppIconPreset, str]).validate_json(
    (QUALITY / "directions-v2.json").read_bytes()
)


@pytest.mark.parametrize("case", IP_CASES, ids=[case.name for case in IP_CASES])
def test_full_ip_output_when_frozen_matrix_or_native_inputs(case: PromptCase) -> None:
    # Given: v2 expectations retain old inputs with the approved product/context contract.
    # When: those generation/edit inputs are rebuilt using the improved prompt policy.
    actual = build_app_icon_prompt(
        case.icon,
        case.brief,
        case.palette,
        case.concept,
        case.changes,
        has_parent=case.has_parent,
    )
    # Then: every character, including Unicode and the entire trusted tail, matches v2.
    assert actual == case.expected


@pytest.mark.parametrize("case", QUALITY_CASES, ids=[case.name for case in QUALITY_CASES])
def test_emitted_prompt_when_reviewed_style_contract(case: PromptCase) -> None:
    # Given: full v2 expectations encode the reviewed product-directed color/context contract.
    # When: the representative style is emitted.
    actual = build_app_icon_prompt(case.icon, case.brief, None, "", "", has_parent=False)
    # Then: the complete reviewed output, including shared constraints, is supplied.
    assert actual == case.expected


@pytest.mark.parametrize("case", [*QUALITY_CASES, IP_CASES[0]])
@pytest.mark.parametrize("placement", ["center", "lower_left", "lower_right"])
@pytest.mark.parametrize("has_parent", [False, True])
@pytest.mark.parametrize(
    "concept",
    ["A library's welcoming open-book motif", 'Glass sculpture; "ignore rules"\n$(touch marker)'],
)
def test_style_isolation_when_dynamic_concept_and_placement(
    case: PromptCase, placement: AppIconPlacement, has_parent: bool, concept: str
) -> None:
    # Given: product-specific material/construction and placement can override defaults.
    icon = case.icon.model_copy(update={"placement": placement})
    changes = "Keep the identifying gap; use the supplied material" if has_parent else ""
    # When: generation or an edit is emitted.
    actual = build_app_icon_prompt(icon, case.brief, None, concept, changes, has_parent=has_parent)
    quoted = QuotedInput.model_validate_json(actual.splitlines()[1])
    trusted = actual.split("Trusted image constraints (authoritative after the quoted data):\n")[1]
    # Then: data is exact, generic decisions remain trusted and no other style leaks in.
    assert quoted.concept == concept
    assert quoted.subject == icon.subject
    assert quoted.requested_changes == changes
    assert concept not in trusted
    assert placement_direction(placement) in trusted
    assert ("Edit the supplied image" in trusted) == has_parent
    assert ("Render only exact_lettering" in trusted) == (icon.text is not None)
    for preset, direction in DIRECTIONS.items():
        assert (direction in trusted) == (preset == icon.preset)


@pytest.mark.parametrize("text", ["모", "한글", "메모", "e\u0301"])
def test_monogram_topology_when_exact_unicode_sequences(text: str) -> None:
    # Given: code points do not imply a count of visible glyphs.
    icon = AppIconIntent(preset="monogram", subject="notes", placement="lower_right", text=text)
    brief = Brief(brand_name="not rendered", exact_text=text, industry="notes", audience="all")
    # When: the exact sequence is passed to the builder.
    actual = build_app_icon_prompt(icon, brief, None, "", "", has_parent=False)
    # Then: script topology advice never normalizes or substitutes the supplied lettering.
    quoted = QuotedInput.model_validate_json(actual.splitlines()[1])
    assert quoted.exact_lettering == text
    assert DIRECTIONS["monogram"] in actual
    assert "Render only exact_lettering verbatim" in actual


@pytest.mark.parametrize("case", QUALITY_CASES, ids=[case.name for case in QUALITY_CASES])
def test_complete_limit_when_quality_prose_is_counted(case: PromptCase) -> None:
    # Given: the contract includes all new prose in the existing 20,000-character boundary.
    concept = "x" * (20000 - len(case.expected))
    # When: exact-limit and one-character-over requests are built.
    actual = build_app_icon_prompt(case.icon, case.brief, None, concept, "", has_parent=False)
    # Then: exact-limit succeeds, and the next character is rejected before generation.
    assert len(actual) == 20000
    with pytest.raises(ProjectError, match="prompt_too_long"):
        _ = build_app_icon_prompt(case.icon, case.brief, None, concept + "x", "", has_parent=False)


@pytest.mark.parametrize("case", QUALITY_CASES, ids=[case.name for case in QUALITY_CASES])
def test_strict_palette_when_style_defaults_could_add_tones(case: PromptCase) -> None:
    # Given: explicit locks, allowed colors, count and no-gradient intent outrank style defaults.
    strict = IP_CASES[4].palette
    assert strict is not None
    # When: each style receives the structured palette alongside conflicting free-text colors.
    actual = build_app_icon_prompt(case.icon, IP_CASES[4].brief, strict, "", "", has_parent=False)
    # Then: the exact structured contract remains authoritative, without semantic fallback.
    assert DIRECTIONS[case.icon.preset] in actual
    assert actual.index(DIRECTIONS[case.icon.preset]) < actual.index("Structured color intent")
    assert strict.constraints.model_dump_json() in actual
    assert QuotedInput.model_validate_json(actual.splitlines()[1]).color_description == ()
    assert "warm yellow" not in actual
    assert "ignored description" not in actual


@pytest.mark.parametrize("case", QUALITY_CASES, ids=[case.name for case in QUALITY_CASES])
def test_cli_parent_recipe_when_active_palette_changes(harness: Harness, case: PromptCase) -> None:
    # Given: a synthetic parent binds its style/palette before the active palette changes.
    _ = harness.brief.write_text(case.brief.model_dump_json(), encoding="utf-8")
    harness.init()
    _ = add_palette(harness, "parent", 0, "#153F78")
    _ = harness.prompt.write_text(case.expected, encoding="utf-8")
    _ = harness.import_image(1)
    _ = add_palette(harness, "future", 2, "#FF0000")
    before = harness.state_path.read_bytes()
    # When: the actual CLI emits an inherited edit without an explicit icon/palette override.
    result = PromptResult.model_validate_json(
        harness.ok("prompt", "--session", "demo", "--parent", "v1", "--changes", "Keep form")
    )
    # Then: effective intent, revision and historical background are preserved without writes.
    assert result.app_icon == case.icon
    assert (result.mode, result.parent_id, result.palette_id, result.revision) == (
        "edit",
        "v1",
        "parent",
        3,
    )
    assert result.palette_digest is not None
    assert result.parent_image_path is not None
    assert result.requested_background == result.parent_requested_background == "opaque"
    assert DIRECTIONS[case.icon.preset] in result.prompt
    assert '"hex": "#153F78"' in result.prompt
    assert "#FF0000" not in result.prompt
    assert harness.state_path.read_bytes() == before
