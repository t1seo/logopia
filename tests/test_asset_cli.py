from __future__ import annotations

from hashlib import sha256
from typing import TYPE_CHECKING, Literal

import pytest
from PIL import Image

from logo_helper.app_icon_models import AppIconIntent
from logo_helper.asset_models import AssetReport, IconAssetIntent
from logo_helper.brief_models import Brief
from logo_helper.models import Session
from logo_helper.prompts import PromptResult

if TYPE_CHECKING:
    from tests.conftest import Harness


def prepare_asset(
    harness: Harness,
    asset: IconAssetIntent,
    *,
    background: Literal["opaque", "transparent"] = "opaque",
) -> None:
    brief = Brief(
        brand_name="Fold",
        exact_text="",
        industry="notes",
        audience="writers",
        background=background,
        app_icon=AppIconIntent(
            preset="abstract", subject="folded ribbon", placement="center", asset=asset
        ),
    )
    _ = harness.brief.write_text(brief.model_dump_json())


def test_foreground_alpha_can_import_check_and_export_without_mutating_original(
    harness: Harness,
) -> None:
    # Given: a real transparent foreground PNG, not a fabricated layer decomposition.
    prepare_asset(
        harness,
        IconAssetIntent(
            kind="apple_layered",
            platform="apple",
            role="foreground",
            appearance="clear_light",
            composer_mode="mono",
        ),
    )
    original = harness.png.read_bytes()
    harness.prepare_export()
    before = harness.state_path.read_bytes()
    # When: the actual CLI checks the selected single layer and delivers its original bytes.
    report = AssetReport.model_validate_json(
        harness.ok("asset-check", "--session", "demo", "--artifact", "v1")
    )
    assert harness.state_path.read_bytes() == before
    _ = harness.ok("export", "--session", "demo", "--revision", "3")
    # Then: alpha is allowed and both report and export deny native-platform validation.
    assert report.passed
    assert report.native_package is False
    assert report.platform_validation == "not_run"
    assert report.source_sha256 == sha256(original).hexdigest()
    assert harness.png.read_bytes() == original
    folder = harness.workspace / "output/logo-generator/demo"
    assert (folder / "logo.png").read_bytes() == original
    assert '"platform_validation": "not_run"' in (folder / "manifest.json").read_text()


def test_apple_background_alpha_is_failed_diagnostic_and_export_is_blocked(
    harness: Harness,
) -> None:
    # Given: the same alpha-bearing PNG is declared as a full-bleed background.
    prepare_asset(
        harness, IconAssetIntent(kind="apple_layered", platform="apple", role="background")
    )
    harness.prepare_export()
    # When: checks run through CLI, independently from explicit visual QA.
    report = AssetReport.model_validate_json(
        harness.ok("asset-check", "--session", "demo", "--artifact", "v1")
    )
    result = harness.run("export", "--session", "demo", "--revision", "3")
    # Then: a completed QA form cannot convert the PNG to an opaque background.
    assert not report.passed
    assert any(
        check.code == "background_opacity" and check.status == "fail" for check in report.checks
    )
    assert result.returncode != 0
    assert not (harness.workspace / "output/logo-generator/demo").exists()


@pytest.mark.parametrize("pixels", [108, 432])
def test_android_safe_zone_uses_dp_ratio_instead_of_fixed_pixels(
    harness: Harness,
    pixels: int,
) -> None:
    # Given: equivalent centered foregrounds at two raster densities.
    prepare_asset(
        harness,
        IconAssetIntent(kind="android_adaptive", platform="android", role="foreground"),
        background="transparent",
    )
    with Image.new("RGBA", (pixels, pixels), (0, 0, 0, 0)) as image:
        image.putpixel((pixels // 2, pixels // 2), (255, 255, 255, 255))
        image.save(harness.png)
    harness.init()
    _ = harness.import_image()
    # When: the imported artifact is measured without raster editing.
    report = AssetReport.model_validate_json(
        harness.ok("asset-check", "--session", "demo", "--artifact", "v1")
    )
    # Then: source pixels are not mistaken for dp, and the central mark remains in bounds.
    assert report.safe_zone is not None
    assert report.safe_zone.layer_dp == 108
    assert report.safe_zone.normalized_diameter == pytest.approx(66 / 108)
    assert report.safe_zone.visible_pixels_outside == 0


def test_android_square_safe_zone_corners_are_not_claimed_safe(harness: Harness) -> None:
    # Given: a pixel inside the central 66-square but outside its guaranteed circular area.
    prepare_asset(
        harness,
        IconAssetIntent(kind="android_adaptive", platform="android", role="foreground"),
        background="transparent",
    )
    with Image.new("RGBA", (108, 108), (0, 0, 0, 0)) as image:
        image.putpixel((22, 22), (255, 255, 255, 255))
        image.save(harness.png)
    harness.init()
    _ = harness.import_image()
    # When: the safe-zone diagnostic evaluates normalized pixel centers.
    report = AssetReport.model_validate_json(
        harness.ok("asset-check", "--session", "demo", "--artifact", "v1")
    )
    # Then: clipping risk is evidence, not an automatic aesthetic rejection.
    assert report.safe_zone is not None
    assert report.safe_zone.visible_pixels_outside == 1
    assert report.passed
    assert any(
        check.code == "android_safe_zone" and check.status == "warning" for check in report.checks
    )


def test_play_transparency_is_warning_not_false_platform_failure(harness: Harness) -> None:
    # Given: current Play specifications allow transparency with a UI-background caveat.
    prepare_asset(
        harness,
        IconAssetIntent(kind="google_play_listing", platform="android"),
        background="transparent",
    )
    with Image.new("RGBA", (512, 512), (10, 100, 200, 128)) as image:
        image.save(harness.png)
    harness.prepare_export()
    # When: the listing artwork is checked and exported as a flat PNG.
    report = AssetReport.model_validate_json(
        harness.ok("asset-check", "--session", "demo", "--artifact", "v1")
    )
    _ = harness.ok("export", "--session", "demo", "--revision", "3")
    # Then: launcher-layer requirements are not imposed on the store listing.
    assert report.passed
    assert report.safe_zone is None
    assert any(
        check.code == "play_transparency" and check.status == "warning" for check in report.checks
    )


def test_play_wrong_size_or_rgb_encoding_prevents_delivery(harness: Harness) -> None:
    # Given: the declared listing is a valid PNG but violates real store byte requirements.
    prepare_asset(harness, IconAssetIntent(kind="google_play_listing", platform="android"))
    with Image.new("RGB", (1024, 1024), (10, 100, 200)) as image:
        image.save(harness.png)
    harness.prepare_export()
    # When: platform-specific local checks are required at the export boundary.
    result = harness.run("export", "--session", "demo", "--revision", "3")
    # Then: passing visual QA does not silently package an invalid listing.
    assert result.returncode != 0
    assert "asset_requirements" in result.stderr
    assert Session.model_validate_json(harness.state_path.read_bytes()).exports == ()


def test_asset_check_rejects_changed_source_instead_of_reporting_stale_evidence(
    harness: Harness,
) -> None:
    # Given: saved facts disagree with the bytes at the artifact's immutable path.
    prepare_asset(harness, IconAssetIntent())
    harness.init()
    _ = harness.import_image()
    _ = (harness.state_path.parent / "artifacts/v1.png").write_bytes(b"tampered")
    # When: the real diagnostic resolves the source.
    result = harness.run("asset-check", "--session", "demo", "--artifact", "v1")
    # Then: no successful check is returned for the missing original.
    assert result.returncode != 0
    assert "hash_mismatch" in result.stderr


def test_play_edit_preserves_parent_background_over_historical_brief(harness: Harness) -> None:
    prepare_asset(harness, IconAssetIntent(kind="google_play_listing", platform="android"))
    harness.init()
    _ = harness.import_image(0, "v1", "--background", "transparent")
    result = PromptResult.model_validate_json(
        harness.ok(
            "prompt", "--session", "demo", "--parent", "v1", "--changes", "Widen the opening"
        )
    )
    assert result.requested_background == "transparent"
    assert "Honor the requested transparent background" in result.prompt
    assert "Honor the requested opaque background" not in result.prompt


@pytest.mark.parametrize("explicit", [None, "opaque"])
def test_play_child_import_inherits_background_unless_overridden(
    harness: Harness, explicit: str | None
) -> None:
    prepare_asset(harness, IconAssetIntent(kind="google_play_listing", platform="android"))
    harness.init()
    _ = harness.import_image(0, "v1", "--background", "transparent")
    extra = ("--background", explicit) if explicit is not None else ()
    _ = harness.import_image(1, "v2", "--parent", "v1", *extra)
    state = Session.model_validate_json(harness.state_path.read_bytes())
    assert state.artifacts[1].requested_background == (explicit or "transparent")
    assert state.artifacts[0].requested_background == "transparent"
