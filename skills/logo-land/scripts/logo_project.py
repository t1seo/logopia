#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "coloraide==8.12.1", "pydantic==2.13.5", "pillow==12.3.0",
#   "typer==0.27.2", "rich==14.3.4",
# ]
# ///
# ─── How to run ───
# Install uv: https://docs.astral.sh/uv/getting-started/installation/
# uv run --project <plugin-root> <skill>/scripts/logo_project.py --help
# uv run logo_project.py --workspace <existing-workspace> list
"""Workspace-local logo sessions; actual image generation stays with the host tool."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Final, Literal

import typer
from pydantic import ValidationError

from logo_helper import delivery, workflow
from logo_helper.app_icon_cli import register_app_icon_commands
from logo_helper.asset_cli import register_asset_commands
from logo_helper.cli_options import (
    AppIconOption,
    ArtifactOption,
    LockupOption,
    PaletteOption,
    ParentOption,
    RevisionOption,
    SessionOption,
    parse_app_icon,
    parse_lockup,
    store_from,
)
from logo_helper.color_cli import register_color_commands
from logo_helper.comparison_cli import register_comparison_commands
from logo_helper.conditioning import condition_prompt
from logo_helper.conditioning_models import ReferencePlan
from logo_helper.models import ArtifactId, Brief, PaletteId, ProjectError, SessionId, VisualReview
from logo_helper.preference_cli import register_preference_commands
from logo_helper.prompts import build_prompt
from logo_helper.quality_cli import register_quality_commands
from logo_helper.storage import read_source

APP: Final = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
DEFAULT_WORKSPACE: Final = Path.cwd()
register_color_commands(APP)
register_app_icon_commands(APP)
register_comparison_commands(APP)
register_asset_commands(APP)
register_preference_commands(APP)
register_quality_commands(APP)


@APP.callback()
def options(workspace: Annotated[Path, typer.Option("--workspace")] = DEFAULT_WORKSPACE) -> None:
    """Manage local PNG files and JSON sessions; commands never invoke image APIs."""
    _ = workspace


@APP.command("init")
def init_command(
    ctx: typer.Context, session: SessionOption, brief: Annotated[Path, typer.Option("--brief")]
) -> None:
    """Create a new session from a JSON brief (revision 0)."""
    state = workflow.create(
        store_from(ctx), SessionId(session), Brief.model_validate_json(read_source(brief))
    )
    typer.echo(state.model_dump_json(indent=2))


@APP.command("list")
def list_command(ctx: typer.Context) -> None:
    """List explicit session IDs, revisions, and selections, checking saved images."""
    sessions = store_from(ctx).list_sessions()
    typer.echo(
        json.dumps(
            [
                {"id": state.id, "revision": state.revision, "selected_id": state.selected_id}
                for state in sessions
            ],
            ensure_ascii=False,
        )
    )


@APP.command("show")
def show_command(ctx: typer.Context, session: SessionOption) -> None:
    """Resume a session after verifying every image hash and decoded metadata."""
    typer.echo(store_from(ctx).load(SessionId(session)).model_dump_json(indent=2))


@APP.command("prompt")
def prompt_command(  # noqa: PLR0913 - Typer exposes one parameter per CLI option.
    ctx: typer.Context,
    *,
    session: SessionOption,
    concept: Annotated[str, typer.Option("--concept")] = "Distinct, simple brand identity",
    parent: ParentOption = None,
    changes: Annotated[str, typer.Option("--changes")] = "",
    palette: PaletteOption = None,
    lockup_file: LockupOption = None,
    app_icon_file: AppIconOption = None,
    reference_plan: Annotated[Path | None, typer.Option("--reference-plan")] = None,
) -> None:
    """Return a generation/edit prompt and exact local parent path; no image is generated."""
    store = store_from(ctx)
    result = build_prompt(
        store,
        store.load(SessionId(session)),
        concept=concept,
        parent_id=ArtifactId(parent) if parent is not None else None,
        changes=changes,
        palette_id=PaletteId(palette) if palette is not None else None,
        lockup=parse_lockup(lockup_file),
        app_icon=parse_app_icon(app_icon_file),
    )
    if reference_plan is not None:
        result = condition_prompt(
            store,
            store.load(SessionId(session)),
            result,
            ReferencePlan.model_validate_json(read_source(reference_plan)),
        )
    typer.echo(result.model_dump_json(indent=2))


@APP.command("import")
def import_command(  # noqa: PLR0913 - Typer exposes one parameter per CLI option.
    ctx: typer.Context,
    *,
    session: SessionOption,
    artifact: ArtifactOption,
    image: Annotated[Path, typer.Option("--image")],
    prompt_file: Annotated[Path, typer.Option("--prompt-file")],
    revision: RevisionOption,
    parent: ParentOption = None,
    palette: PaletteOption = None,
    lockup_file: LockupOption = None,
    app_icon_file: AppIconOption = None,
    background: Annotated[
        Literal["opaque", "transparent"] | None,
        typer.Option(
            "--background",
            help="Defaults to opaque for app icons, otherwise to the original brief.",
        ),
    ] = None,
) -> None:
    """Import a real PNG returned by the host with its actual final prompt."""
    state = workflow.import_image(
        store_from(ctx),
        SessionId(session),
        revision,
        artifact_id=ArtifactId(artifact),
        image=image,
        prompt=read_source(prompt_file).decode("utf-8"),
        parent_id=ArtifactId(parent) if parent is not None else None,
        background=background,
        palette_id=PaletteId(palette) if palette is not None else None,
        lockup=parse_lockup(lockup_file),
        app_icon=parse_app_icon(app_icon_file),
    )
    typer.echo(state.model_dump_json(indent=2))


@APP.command("select")
def select_command(
    ctx: typer.Context, session: SessionOption, artifact: ArtifactOption, revision: RevisionOption
) -> None:
    """Select an explicit stored artifact ID."""
    state = workflow.select(store_from(ctx), SessionId(session), revision, ArtifactId(artifact))
    typer.echo(state.model_dump_json(indent=2))


@APP.command("review")
def review_command(
    ctx: typer.Context,
    session: SessionOption,
    artifact: ArtifactOption,
    review_file: Annotated[Path, typer.Option("--review-file")],
    revision: RevisionOption,
) -> None:
    """Record all explicit visual checks from JSON; never infer visual quality."""
    state = workflow.review(
        store_from(ctx),
        SessionId(session),
        revision,
        ArtifactId(artifact),
        VisualReview.model_validate_json(read_source(review_file)),
    )
    typer.echo(state.model_dump_json(indent=2))


@APP.command("export")
def export_command(
    ctx: typer.Context,
    session: SessionOption,
    revision: RevisionOption,
    output: Annotated[str | None, typer.Option("--output")] = None,
) -> None:
    """Export the selected, reviewed PNG plus manifest, brand guide, and ZIP."""
    state = delivery.export(store_from(ctx), SessionId(session), revision, output)
    typer.echo(state.model_dump_json(indent=2))


@APP.command("failure")
def failure_command(
    ctx: typer.Context,
    session: SessionOption,
    revision: RevisionOption,
    prompt_file: Annotated[Path, typer.Option("--prompt-file")],
    reason: Annotated[str, typer.Option("--reason")],
    parent: ParentOption = None,
) -> None:
    """Record a failed host call without creating artifacts or retrying generation."""
    state = workflow.record_failure(
        store_from(ctx),
        SessionId(session),
        revision,
        prompt=read_source(prompt_file).decode("utf-8"),
        reason=reason,
        parent_id=ArtifactId(parent) if parent is not None else None,
    )
    typer.echo(state.model_dump_json(indent=2))


def main() -> None:
    """Translate known data and filesystem failures into machine-readable CLI errors."""
    try:
        APP()
    except (ProjectError, ValidationError, OSError, UnicodeError) as error:
        typer.echo(json.dumps({"error": str(error)}, ensure_ascii=False), err=True)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
