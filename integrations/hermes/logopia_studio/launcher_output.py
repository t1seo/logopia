"""Small command receipts retain paths and saved state without dumping model logs."""

from pathlib import Path
from typing import ClassVar
from uuid import uuid4

from pydantic import BaseModel, ConfigDict

from .gallery import publish_gallery
from .models import Workflow
from .models_budget import CallBudget
from .store_files import safe_path


class CommandResult(BaseModel):
    """Machine-readable CLI result; success is a verified action postcondition."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, strict=True, extra="forbid")
    success: bool
    message: str
    workflow_id: str | None = None
    revision: int | None = None
    phase: str | None = None
    selected_id: str | None = None
    candidate_count: int = 0
    call_budget: CallBudget | None = None
    gallery: str | None = None
    logs: str | None = None
    error: str | None = None
    installation: str | None = None


def state_result(
    state: Workflow,
    *,
    success: bool = True,
    message: str = "Saved workflow",
    gallery: Path | None = None,
    logs: Path | None = None,
    error: str | None = None,
) -> CommandResult:
    return CommandResult(
        success=success,
        message=message,
        workflow_id=state.id,
        revision=state.revision,
        phase=state.phase,
        selected_id=state.selected_id,
        candidate_count=len(state.candidates),
        call_budget=state.call_budget,
        gallery=str(gallery) if gallery is not None else None,
        logs=str(logs) if logs is not None else None,
        error=error,
    )


def fresh_gallery(workspace: Path, state: Workflow, output: Path | None = None) -> Path:
    target = (
        output
        if output is not None
        else safe_path(
            workspace,
            f"output/logopia-studio/{state.id}/revision-{state.revision}-{uuid4().hex}",
        )
    )
    return publish_gallery(workspace, state, target)


def format_result(result: CommandResult) -> str:
    lines = [result.message]
    if result.workflow_id is not None:
        identity = f"Workflow: {result.workflow_id} | revision {result.revision} | {result.phase}"
        lines.append(f"{identity} | {result.candidate_count} original(s)")
    if result.selected_id is not None:
        lines.append(f"Selected: {result.selected_id}")
    if result.gallery is not None:
        lines.append(f"Gallery: {result.gallery}")
    if result.installation is not None:
        lines.append(f"Plugin: {result.installation}")
    if result.error is not None:
        lines.append(f"Error: {result.error}")
    if result.logs is not None and not result.success:
        lines.append(f"Process logs: {result.logs}")
    return "\n".join(lines)
