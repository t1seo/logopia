from pathlib import Path

from logopia_studio.host_prompts import plan_instructions
from logopia_studio.models import StudioBrief
from logopia_studio.prompts import image_prompt
from tests.hermes.test_core_fixtures import FixtureHost, brief


def test_brand_white_presentation_is_preserved(tmp_path: Path) -> None:
    # Given the existing brand prompt policy.
    request = brief()
    direction = FixtureHost(tmp_path).plan(request).directions[0]
    # When a brand prompt is assembled, then original art and white presentation remain explicit.
    prompt = image_prompt(request, direction)
    assert "Pure white solid background." in prompt
    assert "Original logo artwork" in prompt
    assert direction.prompt in prompt


def test_ip_preserves_character_and_chosen_single_background(tmp_path: Path) -> None:
    # Given an IP direction with its own purposeful solid background.
    request = brief().model_copy(update={"mode": "ip", "count": None})
    direction = (
        FixtureHost(tmp_path)
        .plan(request)
        .directions[0]
        .model_copy(
            update={
                "prompt": "Blue creature portrait in the lower corner on a yellow solid background."
            }
        )
    )
    # When an IP prompt is assembled, then brand presentation cannot override the character intent.
    prompt = image_prompt(request, direction)
    assert "Pure white" not in prompt
    assert "Original logo artwork" not in prompt
    assert "opaque" not in prompt
    assert "lower corner" in prompt
    assert direction.prompt in prompt


def test_ip_user_shape_and_colors_override_recipe_defaults(tmp_path: Path) -> None:
    # Given an explicitly serious angular character with three subject colors.
    request = StudioBrief(
        name="Switchyard",
        exact_text="",
        product="Industrial maintenance scheduler",
        audience="Plant engineers",
        personality="Serious and angular",
        use_case="Team character portrait",
        mode="ip",
        colors=("red shell", "ivory face", "slate joints", "solid white background"),
    )
    direction = (
        FixtureHost(tmp_path)
        .plan(request)
        .directions[0]
        .model_copy(
            update={
                "prompt": (
                    "An angular inspection robot with a long rectangular head, red shell, "
                    "ivory face and slate joints on solid white; a composed expression "
                    "and centered stance."
                )
            }
        )
    )
    # When actual planning and image inputs are assembled, then saved choices stay authoritative.
    instructions = plan_instructions("directions", request)
    prompt = image_prompt(request, direction)
    assert request.effective_count == 6
    assert "Return exactly 6 independent directions" in instructions
    assert direction.prompt in prompt
    assert request.product in prompt
    assert request.personality in prompt
    assert all(color in prompt for color in request.colors)
    for obsolete in (
        "cute simple mascot",
        "rounded heavy forms",
        "two purposeful character colors",
        "four to seven",
        "warm yellow and deep",
        "muted sage",
        "Avoid logo/app-icon/use-case",
        "By default propose three",
    ):
        assert obsolete not in instructions + prompt


def test_app_icon_preserves_chosen_filled_background(tmp_path: Path) -> None:
    # Given an app icon direction with a chosen navy filled square background.
    request = brief().model_copy(update={"mode": "app_icon"})
    direction = (
        FixtureHost(tmp_path)
        .plan(request)
        .directions[0]
        .model_copy(
            update={"prompt": "Centered cream pictogram on a navy filled square background."}
        )
    )
    # When assembled, then brand white cannot override the app icon's background intent.
    prompt = image_prompt(request, direction)
    assert "Pure white" not in prompt
    assert "Centered simple pictogram" not in prompt
    assert "no lettering" not in prompt
    assert direction.prompt in prompt
