"""Read-only local asset diagnostics through the existing helper CLI."""

from hashlib import sha256

import typer

from logo_helper.asset_checks import check_icon_asset
from logo_helper.asset_models import IconAssetIntent
from logo_helper.cli_options import ArtifactOption, SessionOption, store_from
from logo_helper.model_base import ArtifactId, ProjectError, SessionId
from logo_helper.storage import read_source, safe_path


def register_asset_commands(app: typer.Typer) -> None:
    _ = app.command("asset-check")(asset_check_command)


def asset_check_command(
    ctx: typer.Context, session: SessionOption, artifact: ArtifactOption
) -> None:
    """Check original PNG bytes and print a handoff without claiming a native platform package."""
    store = store_from(ctx)
    identifier = SessionId(session)
    state = store.load(identifier)
    source = state.artifact(ArtifactId(artifact))
    if source.app_icon is None:
        raise ProjectError("invalid_asset", "Artifact has no app-icon asset intent")
    data = read_source(safe_path(store.session_dir(identifier), source.path))
    if sha256(data).hexdigest() != source.sha256:
        raise ProjectError("hash_mismatch", "Original PNG changed before asset checks")
    report = check_icon_asset(data, source.app_icon.asset or IconAssetIntent())
    typer.echo(report.model_dump_json(indent=2))
