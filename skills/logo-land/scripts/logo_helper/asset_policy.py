"""Apply asset role policies without changing legacy flattened-artwork imports."""

from __future__ import annotations

from typing import TYPE_CHECKING

from logo_helper.asset_checks import check_icon_asset
from logo_helper.asset_models import AssetReport, IconAssetIntent
from logo_helper.model_base import Background, ProjectError

if TYPE_CHECKING:
    from logo_helper.app_icon_models import AppIconIntent
    from logo_helper.artifact_models import Artifact
    from logo_helper.brief_models import Brief


def icon_import_background(
    icon: AppIconIntent,
    explicit: Background | None,
    fallback: Background,
) -> Background:
    intent = icon.asset or IconAssetIntent()
    if not intent.allows_alpha:
        if explicit == "transparent":
            raise ProjectError(
                "intent_conflict", "This app-icon asset role requires an opaque background request"
            )
        return "opaque"
    return explicit if explicit is not None else fallback


def require_export_background(artifact: Artifact, brief: Brief) -> None:
    icon = artifact.app_icon
    if (
        icon is not None
        and icon.asset is not None
        and icon.asset.role in {"foreground", "monochrome"}
    ):
        return
    requested = artifact.effective_background(brief)
    if (requested == "transparent") != artifact.image.has_transparency:
        raise ProjectError(
            "background_mismatch",
            (
                f"Requested {requested} background differs from decoded transparency "
                f"({artifact.image.has_transparency})"
            ),
        )


def export_asset_report(artifact: Artifact, data: bytes) -> AssetReport | None:
    if artifact.app_icon is None:
        return None
    report = check_icon_asset(data, artifact.app_icon.asset or IconAssetIntent())
    if not report.passed:
        failed = ", ".join(check.code for check in report.checks if check.status == "fail")
        raise ProjectError("asset_requirements", f"Local PNG asset requirements failed: {failed}")
    return report
