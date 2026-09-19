from logo_helper.app_icon_models import AppIconIntent
from logo_helper.app_icon_prompts import build_app_icon_prompt
from logo_helper.asset_models import IconAssetIntent
from logo_helper.models import Brief


def test_product_context_and_required_conditions_reach_icon_model() -> None:
    brief = Brief(
        brand_name="SEAM",
        exact_text="",
        industry="private writing notebook",
        audience="freelance writers",
        styles=("dry cut paper",),
        forbidden=("no stars",),
        use_cases=("32px app list",),
    )
    icon = AppIconIntent(preset="abstract", subject="joined slips", placement="center")
    prompt = build_app_icon_prompt(icon, brief, None, "Open stepped seam", "", has_parent=False)
    for requirement in (
        brief.industry,
        brief.audience,
        *brief.styles,
        *brief.forbidden,
        *brief.use_cases,
    ):
        assert requirement in prompt
    assert "warm yellow and deep navy" not in prompt
    assert "muted sage" not in prompt


def test_user_colors_never_get_replaced_by_recommended_defaults() -> None:
    brief = Brief(
        brand_name="SEAM",
        exact_text="",
        industry="writing",
        audience="writers",
        palette=("violet #6542C3", "black background #000000"),
    )
    icon = AppIconIntent(preset="ip_mascot", subject="angular serious robot", placement="center")
    prompt = build_app_icon_prompt(
        icon, brief, None, "Square jaw, serious expression", "", has_parent=False
    )
    assert "#6542C3" in prompt
    assert "#000000" in prompt
    assert "cute" not in prompt


def test_foreground_prompt_does_not_request_opaque_tile() -> None:
    asset = IconAssetIntent(
        kind="apple_layered", platform="apple", role="foreground", appearance="dark"
    )
    icon = AppIconIntent(
        preset="abstract", subject="one open seam", placement="center", asset=asset
    )
    brief = Brief(
        brand_name="SEAM",
        exact_text="",
        industry="writing",
        audience="writers",
        background="transparent",
        app_icon=icon,
    )
    prompt = build_app_icon_prompt(icon, brief, None, "Open seam", "", has_parent=False)
    assert "transparent" in prompt
    assert "complete solid background covering" not in prompt
    assert "native package" in prompt


def test_store_listing_has_distinct_pixel_request() -> None:
    asset = IconAssetIntent(kind="google_play_listing", platform="android")
    icon = AppIconIntent(preset="soft_3d", subject="folded slip", placement="center", asset=asset)
    brief = Brief(
        brand_name="SEAM", exact_text="", industry="writing", audience="writers", app_icon=icon
    )
    prompt = build_app_icon_prompt(icon, brief, None, "Matte paper", "", has_parent=False)
    assert "512" in prompt
    assert "1536" not in prompt
    assert "internal" in prompt
