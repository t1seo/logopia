"""Bounded creative review coordination; image calls stay with the native host."""

from pathlib import Path
from typing import Annotated, Literal

import typer

from logo_helper.cli_options import RevisionOption, store_from
from logo_helper.model_base import FrozenModel
from logo_helper.quality_loop import (
    load_loop,
    record_critique,
    record_failure,
    request_step,
    start_loop,
)
from logo_helper.quality_models import Critique, LoopContract
from logo_helper.quality_state import QualityLoop
from logo_helper.storage import read_source

LoopOption = Annotated[str, typer.Option("--loop")]


class LoopResponse(FrozenModel):
    """CLI response combining persisted state with derived budget and next-action status."""

    state: QualityLoop
    status: str
    calls_used: int
    remaining_calls: int
    pending_request: int | None


def _echo_loop(state: QualityLoop) -> None:
    response = LoopResponse(
        state=state,
        status=state.status,
        calls_used=state.calls_used,
        remaining_calls=state.contract.call_budget - state.calls_used,
        pending_request=state.pending.number if state.pending is not None else None,
    )
    typer.echo(response.model_dump_json(indent=2))


def register_quality_commands(app: typer.Typer) -> None:
    """Expose the sidecar workflow without changing legacy session commands."""
    _ = app.command("loop-start")(loop_start_command)
    _ = app.command("loop-show")(loop_show_command)
    _ = app.command("loop-request")(loop_request_command)
    _ = app.command("loop-record")(loop_record_command)
    _ = app.command("loop-failure")(loop_failure_command)


def loop_start_command(
    ctx: typer.Context,
    loop: LoopOption,
    contract_file: Annotated[Path, typer.Option("--contract-file")],
) -> None:
    """Freeze source context, scope, directions and native-call budget."""
    contract = LoopContract.model_validate_json(read_source(contract_file))
    result = start_loop(store_from(ctx), loop, contract)
    _echo_loop(result)


def loop_show_command(ctx: typer.Context, loop: LoopOption) -> None:
    """Verify and resume a loop; unknown calls and unresolved criteria stay visible."""
    result = load_loop(store_from(ctx), loop)
    _echo_loop(result)


def loop_request_command(
    ctx: typer.Context,
    loop: LoopOption,
    revision: RevisionOption,
    direction: Annotated[str | None, typer.Option("--direction")] = None,
) -> None:
    """Reserve one call and save its exact prompt and parent before host dispatch."""
    result = request_step(store_from(ctx), loop, revision, direction_id=direction)
    _echo_loop(result)


def loop_record_command(
    ctx: typer.Context,
    loop: LoopOption,
    revision: RevisionOption,
    critique_file: Annotated[Path, typer.Option("--critique-file")],
) -> None:
    """Bind observed criticism to an imported original and choose a concrete next action."""
    critique = Critique.model_validate_json(read_source(critique_file))
    result = record_critique(store_from(ctx), loop, revision, critique)
    _echo_loop(result)


def loop_failure_command(
    ctx: typer.Context,
    loop: LoopOption,
    revision: RevisionOption,
    request: Annotated[int, typer.Option("--request", min=1)],
    outcome: Annotated[Literal["failed", "unknown"], typer.Option("--outcome")],
    reason: Annotated[str, typer.Option("--reason")],
) -> None:
    """Record a failed or unknown call without refunding or silently repeating it."""
    result = record_failure(
        store_from(ctx), loop, revision, request_number=request, outcome=outcome, reason=reason
    )
    _echo_loop(result)
