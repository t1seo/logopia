"""Local blind comparisons and sidecar preferences; no model calls or approvals."""

from pathlib import Path
from typing import Annotated

import typer

from logo_helper.cli_options import store_from
from logo_helper.preference_gallery import render_preference_gallery
from logo_helper.preference_models import PreferenceSelection
from logo_helper.preference_records import record_preference
from logo_helper.preference_response import PreferenceResponse
from logo_helper.storage import read_source


def register_preference_commands(app: typer.Typer) -> None:
    _ = app.command("preference-gallery")(preference_gallery_command)
    _ = app.command("preference-record")(preference_record_command)


def preference_gallery_command(
    ctx: typer.Context,
    selection_file: Annotated[Path, typer.Option("--selection-file")],
    output: Annotated[str, typer.Option("--output")],
) -> None:
    """Render 1-12 explicit pairs, with seeded order and no creator rationale on screen."""
    selection = PreferenceSelection.model_validate_json(read_source(selection_file))
    result = render_preference_gallery(store_from(ctx), selection, output)
    typer.echo(result.model_dump_json(indent=2))


def preference_record_command(
    ctx: typer.Context,
    gallery: Annotated[str, typer.Option("--gallery")],
    response_file: Annotated[Path, typer.Option("--response-file")],
) -> None:
    """Apply downloaded observations to a new sidecar; source Session bytes stay intact."""
    response = PreferenceResponse.model_validate_json(read_source(response_file))
    result = record_preference(store_from(ctx), gallery, response)
    typer.echo(result.model_dump_json(indent=2))
