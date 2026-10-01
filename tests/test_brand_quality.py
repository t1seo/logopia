from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pydantic import JsonValue, TypeAdapter

from logo_helper.color_models import (
    ColorConstraints,
    PaletteContent,
    PaletteVersion,
    SourceEvidence,
    Swatch,
    palette_digest,
)
from logo_helper.models import Background, Brief, LockupIntent, PaletteId
from logo_helper.prompts import PromptResult, build_prompt
from logo_helper.storage import Store
from tests.test_brand_strategy import strategy_brief
from tests.test_color_models import session

if TYPE_CHECKING:
    from tests.conftest import Harness


def generation(harness: Harness, brief: Brief, palette: PaletteVersion | None = None) -> str:
    state = session(*(() if palette is None else (palette,))).model_copy(
        update={"brief": brief, "active_palette_id": None if palette is None else palette.id}
    )
    return build_prompt(
        Store.at(harness.workspace), state, concept="One open fold", parent_id=None, changes=""
    ).prompt


def render_palette() -> PaletteVersion:
    content = PaletteContent(
        swatches=(Swatch(hex="#6542C3", role="mark"), Swatch(hex="#000000", role="canvas")),
        constraints=ColorConstraints(
            allowed_hex=("#6542C3", "#000000"), required_hex=("#6542C3",), max_colors=2
        ),
        source="assistant",
        source_evidence=SourceEvidence(response="SOURCE_ONLY /private/plan.json"),
        selected_by="user",
        rationale="PRIVATE_RATIONALE",
    )
    return PaletteVersion.model_validate(
        content.model_dump() | {"id": PaletteId("violet"), "digest": palette_digest(content)}
    )


def palette_instruction(prompt: str) -> JsonValue:
    line = next(line for line in prompt.splitlines() if line.startswith("Effective structured"))
    payload = line.split(": ", 1)[1].split(". Keep locked", 1)[0]
    adapter: TypeAdapter[JsonValue] = TypeAdapter(JsonValue)
    return adapter.validate_json(payload)


@pytest.mark.parametrize("background", ["opaque", "transparent"])
def test_canvas_default_obeys_alpha_request(harness: Harness, background: Background) -> None:
    # Given: no requested canvas color and no selected palette.
    brief = session().brief.model_copy(update={"background": background})
    # When: a fresh brand logo is requested.
    prompt = generation(harness, brief)
    # Then: white is an opaque fallback, never a fill for transparent output.
    assert ("#FFFFFF" in prompt) == (background == "opaque")
    assert "flat" in prompt.casefold()
    assert "unless explicitly requested" in prompt.casefold()


def test_wordmark_does_not_prime_unrequested_genres(harness: Harness) -> None:
    # Given: a wordmark without sculpted or sports direction.
    brief = session().brief.model_copy(update={"logo_type": "wordmark"})
    # When: its construction prompt is built.
    prompt = generation(harness, brief).casefold()
    # Then: unrequested treatments are absent while lettering construction remains.
    assert all(style not in prompt for style in ("sculpted", "athletic", "forward slant"))
    assert "lettering-only wordmark" in prompt


@pytest.mark.parametrize(
    ("allowed", "max_colors", "white_expected"),
    [
        (None, None, True),
        (None, 1, False),
        (None, 2, True),
        (("#6542C3", "#FFFFFF"), None, True),
        (("#6542C3",), None, False),
        (("#6542C3", "#FFFFFF"), 1, False),
    ],
)
def test_advisory_foreground_palette_uses_white_only_when_constraints_allow_it(
    harness: Harness, allowed: tuple[str, ...] | None, max_colors: int | None, white_expected: bool
) -> None:
    # Given: a single selected foreground color with varying explicit limits.
    content = PaletteContent(
        swatches=(Swatch(hex="#6542C3", role="primary foreground"),),
        constraints=ColorConstraints(
            locked_hex=("#6542C3",), allowed_hex=allowed, max_colors=max_colors
        ),
        source="assistant",
        selected_by="user",
        rationale="Foreground color requested",
    )
    palette = PaletteVersion.model_validate(
        content.model_dump() | {"id": PaletteId("foreground"), "digest": palette_digest(content)}
    )
    # When: a new logo needs an opaque canvas without a supplied background.
    prompt = generation(harness, session().brief, palette)
    rendering = next(line for line in prompt.splitlines() if line.startswith("Brand rendering:"))
    # Then: advisory color alone does not force a colored canvas, but real limits are respected.
    assert ("#FFFFFF" in rendering) == white_expected
    assert palette_instruction(prompt) == palette.model_dump(
        mode="json", include={"swatches", "constraints"}
    )


def test_structured_palette_excludes_provenance_but_preserves_every_render_constraint(
    harness: Harness,
) -> None:
    # Given: locked intent plus non-rendering source metadata.
    palette = render_palette()
    # When: the palette is sent to the image model.
    prompt = generation(harness, session().brief, palette)
    # Then: only rendering data is exposed and no out-of-palette white is invented.
    assert palette_instruction(prompt) == palette.model_dump(
        mode="json", include={"swatches", "constraints"}
    )
    assert palette.digest not in prompt
    assert "SOURCE_ONLY" not in prompt
    assert "PRIVATE_RATIONALE" not in prompt
    assert "#FFFFFF" not in prompt


def test_user_style_canvas_and_lockup_remain_above_advisory_strategy(harness: Harness) -> None:
    # Given: an incompatible strategy suggestion alongside explicit user appearance.
    lockup = LockupIntent(layout="horizontal", typography_style="Narrow geometric sans")
    brief = strategy_brief().model_copy(
        update={"styles": ("Sculpted chrome",), "palette": ("beige canvas",), "lockup": lockup}
    )
    # When: a generation is prepared.
    prompt = generation(harness, brief)
    # Then: the user's values remain exact and the strategy is explicitly subordinate.
    assert "Sculpted chrome" in prompt
    assert "beige canvas" in prompt
    assert lockup.model_dump_json() in prompt
    assert "those requests take precedence" in prompt
    assert "unless explicitly requested" in prompt


def test_parent_edit_has_no_new_canvas_or_flatness_default(harness: Harness) -> None:
    # Given: an existing logo that may have changed from its initial brief.
    harness.init()
    _ = harness.import_image()
    # When: only a gap is changed using the CLI.
    result = PromptResult.model_validate_json(
        harness.ok("prompt", "--session", "demo", "--parent", "v1", "--changes", "Open the gap")
    )
    # Then: the edit receives no fresh rendering or construction defaults.
    assert "#FFFFFF" not in result.prompt
    assert "Brand rendering" not in result.prompt
    assert "Logo construction:" not in result.prompt
    assert result.mode == "edit"
