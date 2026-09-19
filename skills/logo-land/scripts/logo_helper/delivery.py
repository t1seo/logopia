"""Export a reviewed original PNG with truthful provenance and a matching ZIP."""

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from logo_helper.app_icon_guide import ARTWORK_LIMITATIONS, app_icon_guide
from logo_helper.app_icon_models import AppIconIntent
from logo_helper.asset_models import AssetReport
from logo_helper.asset_policy import export_asset_report, require_export_background
from logo_helper.color_delivery import (
    COLOR_LIMITS,
    COLOR_METHOD,
    ColorDelivery,
    ColorPolicy,
    export_colors,
)
from logo_helper.color_guide import color_guide, typography_guide
from logo_helper.color_models import PaletteVersion
from logo_helper.color_reports import ColorReport
from logo_helper.export_bundle import publish_bundle
from logo_helper.lockup_models import LockupIntent
from logo_helper.models import (
    Artifact,
    Background,
    Brief,
    ExportRecord,
    FrozenModel,
    ProjectError,
    Session,
    SessionId,
)
from logo_helper.storage import Store, read_source, safe_path
from logo_helper.workflow import advance


class Manifest(FrozenModel):
    """Describe the actual exported artifact without promising vector or legal rights."""

    schema_version: Literal[2] = 2
    session_id: SessionId
    revision: int
    exported_at: datetime
    image_file: Literal["logo.png"] = "logo.png"
    source: Artifact
    brief: Brief
    media_kind: Literal["raster"] = "raster"
    requested_background: Background
    transparency_verified: bool
    intended_palette: PaletteVersion | None
    color_report: ColorReport
    color_policy: ColorPolicy
    warnings: tuple[str, ...] = ()
    color_method: str = COLOR_METHOD
    color_limits: tuple[str, ...] = COLOR_LIMITS
    lockup_intent: LockupIntent | None = None
    font_reference_usage: Literal["appearance-reference-only"] = "appearance-reference-only"
    app_icon: AppIconIntent | None = None
    artwork_limitations: str | None = None
    asset_report: AssetReport | None = None


def guide(state: Session, artifact: Artifact, evidence: ColorDelivery | None = None) -> str:
    """Separate requested brand choices from measured PNG facts and host review."""
    brief = state.brief
    selected_request = "\n".join(f"> {line}" for line in artifact.prompt.splitlines())
    history = (
        f"# {brief.brand_name}\n\n"
        f"Selected artifact: {artifact.id}\n\n"
        f"Initial brief text: {brief.exact_text}\n\nInitial brief slogan: {brief.slogan}\n\n"
        f"Initial brief styles: {', '.join(brief.styles)}\n\n"
        "Initial brief palette (historical intent, not measured or final color specifications): "
        f"{', '.join(brief.palette)}\n\n"
        f"Initial brief background (historical intent): {brief.background}\n\n"
        f"Selected artifact requested background: {artifact.effective_background(brief)}\n\n"
        f"Intended uses: {', '.join(brief.use_cases)}\n\n"
        f"Actual deliverable: PNG raster, "
        f"{artifact.image.width} x {artifact.image.height} pixels.\n\n"
        f"Pixels below full opacity: {artifact.image.transparent_pixels}. "
        f"Visible pixels: {artifact.image.visible_pixels}.\n\n"
        "The original bytes are preserved. Do not enlarge beyond a useful raster resolution. "
        "Keep clear space around the mark and verify legibility at its final display size.\n\n"
        "This package does not include editable SVG/EPS/AI vectors, licensed font files, "
        "CMYK print proofs, or trademark/exclusivity guarantees. "
        "Initial colors and styles describe historical intent; the supplied PNG is the actual "
        "artwork. The selected version request is authoritative for changes to the initial brief. "
        "The manifest records the explicit visual review and generation/edit prompt.\n\n"
        "## Selected version request\n\n"
        f"{selected_request}\n\n"
    )
    return (
        history
        + (
            color_guide(evidence)
            if evidence
            else "Color evidence was not recomputed for this guide.\n"
        )
        + "\n"
        + typography_guide(artifact)
        + app_icon_guide(artifact.app_icon)
    )


def _export_destination(root: Path, relative: str) -> Path:
    destination = safe_path(root, relative)
    if destination.relative_to(root).parts[0].casefold() == ".logo-generator":
        raise ProjectError(
            "reserved_output",
            "Export destination cannot be inside reserved .logo-generator storage",
        )
    return destination


def export(store: Store, identifier: SessionId, revision: int, output: str | None) -> Session:
    """Stage a complete bundle before publishing it to a new workspace directory."""
    relative = output if output is not None else f"output/logo-generator/{identifier}"
    destination = _export_destination(store.root, relative)
    with store.locked(identifier):
        state = store.expect(identifier, revision)
        if state.selected_id is None:
            raise ProjectError("not_selected", "Select an artifact before export")
        artifact = state.artifact(state.selected_id)
        if artifact.review is None or not artifact.review.passed:
            raise ProjectError("review_required", "All explicit visual review checks must pass")
        requested_background = artifact.effective_background(state.brief)
        require_export_background(artifact, state.brief)
        if destination.exists():
            raise ProjectError("conflict", f"Export destination already exists: {destination}")
        data = read_source(safe_path(store.session_dir(identifier), artifact.path))
        if hashlib.sha256(data).hexdigest() != artifact.sha256:
            raise ProjectError("hash_mismatch", "Selected image changed during export")
        asset_report = export_asset_report(artifact, data)
        now = datetime.now(UTC)
        evidence = export_colors(state, artifact, data, now)
        record = ExportRecord(path=relative, artifact_id=artifact.id, created_at=now)
        updated = advance(
            state.model_copy(
                update={
                    "exports": (*state.exports, record),
                    "color_reports": (*state.color_reports, evidence.report),
                }
            )
        )
        manifest = Manifest(
            session_id=identifier,
            revision=updated.revision,
            exported_at=now,
            source=artifact,
            brief=state.brief,
            requested_background=requested_background,
            transparency_verified=artifact.image.has_transparency,
            intended_palette=evidence.palette,
            color_report=evidence.report,
            color_policy=evidence.policy,
            warnings=evidence.warnings,
            lockup_intent=artifact.lockup,
            app_icon=artifact.app_icon,
            artwork_limitations=ARTWORK_LIMITATIONS if artifact.app_icon is not None else None,
            asset_report=asset_report,
        )
        with publish_bundle(
            destination,
            data,
            manifest.model_dump_json(indent=2).encode("utf-8"),
            guide(state, artifact, evidence).encode("utf-8"),
        ):
            store.save(updated)
    return updated
