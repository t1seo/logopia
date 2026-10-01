"""Build host image-tool prompts while keeping generation outside this helper."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from logo_helper.app_icon_models import omit_absent
from logo_helper.app_icon_prompts import build_app_icon_prompt
from logo_helper.asset_policy import icon_import_background
from logo_helper.conditioning_models import InputPlan, no_input_plan
from logo_helper.intent import resolve_intent
from logo_helper.logo_prompts import logo_construction, logo_rendering
from logo_helper.models import (
    AppIconIntent,
    ArtifactId,
    Background,
    Digest,
    FrozenModel,
    LockupIntent,
    PaletteId,
    ProjectError,
    Session,
)
from logo_helper.storage import Store, safe_path


class PromptResult(FrozenModel):
    """A host-call instruction plus the exact verified local edit target, when present."""

    mode: Literal["generation", "edit"]
    session_id: str
    revision: int
    prompt: str
    parent_id: ArtifactId | None
    parent_image_path: str | None
    parent_requested_background: Background | None = None
    palette_id: PaletteId | None = None
    palette_digest: Digest | None = None
    lockup: LockupIntent | None = None
    app_icon: AppIconIntent | None = Field(default=None, exclude_if=omit_absent)
    requested_background: Background | None = Field(default=None, exclude_if=omit_absent)
    input_plan: InputPlan | None = Field(default=None, exclude_if=no_input_plan)


def build_prompt(  # noqa: PLR0913 - Shared explicit intent options mirror the CLI boundary.
    store: Store,
    state: Session,
    *,
    concept: str,
    parent_id: ArtifactId | None,
    changes: str,
    palette_id: PaletteId | None = None,
    lockup: LockupIntent | None = None,
    app_icon: AppIconIntent | None = None,
) -> PromptResult:
    """Preserve exact text and bind edits to an existing parent without changing state."""
    if bool(changes.strip()) != (parent_id is not None):
        raise ProjectError(
            "invalid_request", "An edit requires both --parent and nonempty --changes"
        )
    brief = state.brief
    intent = resolve_intent(state, parent_id, palette_id, lockup, app_icon)
    if intent.app_icon is not None:
        parent = state.artifact(parent_id) if parent_id is not None else None
        background = icon_import_background(
            intent.app_icon,
            None,
            parent.effective_background(brief) if parent is not None else brief.background,
        )
        return PromptResult(
            mode="edit" if parent is not None else "generation",
            session_id=state.id,
            revision=state.revision,
            prompt=build_app_icon_prompt(
                intent.app_icon,
                brief,
                intent.palette,
                concept,
                changes,
                has_parent=parent is not None,
                background=background,
            ),
            parent_id=parent_id,
            parent_image_path=str(safe_path(store.session_dir(state.id), parent.path))
            if parent is not None
            else None,
            parent_requested_background=parent.effective_background(brief)
            if parent is not None
            else None,
            palette_id=intent.palette.id if intent.palette is not None else None,
            palette_digest=intent.palette.digest if intent.palette is not None else None,
            app_icon=intent.app_icon,
            requested_background=background,
        )
    background_label = (
        "Initial brief background (historical intent)" if parent_id is not None else "Background"
    )
    # A resolved symbol/text layout is stronger evidence than an original type label.
    # Parent edits never receive fresh type defaults: their visible type may have changed.
    logo_type = "combination" if intent.lockup is not None else brief.logo_type
    subject = (
        (
            f"Original brief logo type (historical intent): {brief.logo_type}. "
            f"Original brand context: {brief.brand_name}. "
        )
        if parent_id is not None
        else f"Create one {logo_type} logo for {brief.brand_name}. "
    )
    lettering = (
        (
            f"Initial brief exact text (historical intent): {brief.exact_text!r}. "
            f"Initial brief slogan (historical intent): {brief.slogan!r}.\n"
        )
        if parent_id is not None
        else (
            f"Exact text (copy verbatim, no other words): {brief.exact_text!r}. "
            f"Exact slogan: {brief.slogan!r}.\n"
            "Render only the supplied exact text and nonempty slogan; the brand context is "
            "not additional lettering. Empty strings request no corresponding text.\n"
        )
    )
    direction = (
        f"{subject}{lettering}Industry: {brief.industry}. Audience: {brief.audience}.\n"
        f"Styles: {', '.join(brief.styles)}. Original brief palette context: "
        f"{', '.join(brief.palette)}.\n"
        f"Avoid: {', '.join(brief.forbidden)}. Use cases: {', '.join(brief.use_cases)}.\n"
        f"{background_label}: {brief.background}. Produce a real PNG raster image. "
        "Use clean, readable shapes at small sizes; leave safe margins. "
        "Do not draw a transparency checkerboard, mockup, watermarks, or a concept grid.\n"
        f"Concept direction: {concept}. Assumptions: {', '.join(brief.assumptions)}."
    )
    if parent_id is None:
        direction += (
            f"\n{logo_rendering(brief.background, intent.palette)}"
            f"\nLogo construction: {logo_construction(logo_type)} "
            "Use style references for broad construction traits, not their brand words or "
            "traced signature shapes. The identity should remain recognizable in a "
            "one-color silhouette at the intended use size. This construction check does not "
            "replace the requested palette or request an extra monochrome image."
        )
        if brief.brand_strategy is not None:
            direction += (
                "\nSupporting brand strategy (proposed context, not verified market facts): "
                f"{brief.brand_strategy.prompt_context()}\n"
                "Use this context only where compatible with the supplied exact text, slogan, "
                "palette constraints, explicit lockup, styles and concept; those requests take "
                "precedence. Strategy does not authorize new lettering, colors or motifs."
            )
    parent_path: str | None = None
    parent_background: Background | None = None
    mode: Literal["generation", "edit"] = "generation"
    if parent_id is not None:
        parent = state.artifact(parent_id)
        parent_background = parent.effective_background(brief)
        parent_path = str(safe_path(store.session_dir(state.id), parent.path))
        mode = "edit"
        direction = (
            f"Edit the supplied parent logo {parent_id}; do not recreate an unrelated logo.\n"
            f"Parent requested background: {parent_background}; preserve it unless the latest "
            "requested changes specify another background.\n"
            f"Latest requested changes (authoritative): {changes}. Preserve all unrequested "
            "text, geometry, layout, silhouette, and brand identity from that parent, including "
            "its letter shapes, counters, spacing and ligatures. "
            "Requested changes override conflicting parent intent and fields in the following "
            "original brief context; its type, lettering, styles and background are historical, "
            "not new requests. Do not restore historical text or apply new logo-type defaults. "
            "Use explicitly requested replacement lettering verbatim; otherwise preserve the "
            f"parent's visible text and slogan.\n{direction}"
        )
    if intent.palette is not None:
        palette = intent.palette
        direction += (
            "\nEffective structured palette intent (authoritative over historical palette): "
            f"{palette.model_dump_json(include={'swatches', 'constraints'})}. "
            "Keep locked and required HEX values exactly in intent; "
            "use the declared roles and allowed colors/count. Opaque backgrounds count as "
            "visible design colors; transparent pixels do not. No gradients unless allowed. "
            "Raster fidelity is measured after generation, never promised as exact pixels."
        )
    if intent.lockup is not None:
        direction += (
            f"\nEffective symbol-plus-text lockup: {intent.lockup.model_dump_json()}. "
            "Horizontal start/end means symbol left/right of text; stacked start/end means "
            "symbol above/below text. For edits, latest requested changes take precedence; "
            "preserve unrequested parent lettering instead of restoring historical strings. "
            "Font reference is "
            "a requested visual direction, not proof of an installed or licensed font file."
        )
    direction += (
        "\nLettering fidelity: preserve every Unicode character, capitalization, punctuation, "
        "space and reading order in the applicable text. Keep Hangul syllable blocks intact; "
        "do not translate, romanize, abbreviate or substitute lookalike glyphs. Shape changes "
        "must keep required text readable, including counters and joins at the intended size."
    )
    return PromptResult(
        mode=mode,
        session_id=state.id,
        revision=state.revision,
        prompt=direction,
        parent_id=parent_id,
        parent_image_path=parent_path,
        parent_requested_background=parent_background,
        palette_id=intent.palette.id if intent.palette is not None else None,
        palette_digest=intent.palette.digest if intent.palette is not None else None,
        lockup=intent.lockup,
    )
