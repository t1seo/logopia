"""Session mutations run under one cooperative lock and optimistic revision check."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from pydantic import ValidationError

from logo_helper.asset_policy import icon_import_background
from logo_helper.images import inspect_png
from logo_helper.import_reports import initial_report
from logo_helper.intent import resolve_intent
from logo_helper.models import (
    AppIconIntent,
    Artifact,
    ArtifactId,
    Background,
    Brief,
    FailedAttempt,
    LockupIntent,
    PaletteId,
    ProjectError,
    Session,
    SessionId,
    VisualReview,
)
from logo_helper.storage import Store, read_source, safe_path, validate_id, write_new

if TYPE_CHECKING:
    from pathlib import Path


def advance(state: Session) -> Session:
    return state.model_copy(
        update={"revision": state.revision + 1, "updated_at": datetime.now(UTC)}
    )


def create(store: Store, identifier: SessionId, brief: Brief) -> Session:
    """Create a new session exclusively, leaving any existing data untouched."""
    now = datetime.now(UTC)
    state = Session(id=identifier, brief=brief, created_at=now, updated_at=now)
    with store.locked(identifier):
        directory = store.session_dir(identifier)
        directory.mkdir(parents=True)
        try:
            store.save(state)
        except OSError:
            directory.rmdir()
            raise
    return state


def import_image(
    store: Store,
    identifier: SessionId,
    revision: int,
    *,
    artifact_id: ArtifactId,
    image: Path,
    prompt: str,
    parent_id: ArtifactId | None,
    background: Background | None = None,
    palette_id: PaletteId | None = None,
    lockup: LockupIntent | None = None,
    app_icon: AppIconIntent | None = None,
) -> Session:
    """Decode first, copy original bytes exclusively, then commit success metadata."""
    _ = validate_id(artifact_id)
    data = read_source(image)
    facts = inspect_png(data)
    with store.locked(identifier):
        state = store.expect(identifier, revision)
        if any(item.id == artifact_id for item in state.artifacts):
            raise ProjectError("conflict", f"Artifact {artifact_id} already exists")
        intent = resolve_intent(state, parent_id, palette_id, lockup, app_icon)
        requested_background = background if background is not None else state.brief.background
        if intent.app_icon is not None:
            inherited_background = (
                state.artifact(parent_id).effective_background(state.brief)
                if parent_id is not None
                else state.brief.background
            )
            requested_background = icon_import_background(
                intent.app_icon, background, inherited_background
            )
        artifact = Artifact(
            id=artifact_id,
            path=f"artifacts/{artifact_id}.png",
            image=facts,
            sha256=hashlib.sha256(data).hexdigest(),
            prompt=prompt,
            parent_id=parent_id,
            created_at=datetime.now(UTC),
            requested_background=requested_background,
            palette_id=intent.palette.id if intent.palette is not None else None,
            lockup=intent.lockup,
            app_icon=intent.app_icon,
        )
        reports = state.color_reports
        if intent.palette is not None:
            reports = (*reports, initial_report(data, artifact, intent.palette))
        updated = advance(
            state.model_copy(
                update={
                    "artifacts": (*state.artifacts, artifact),
                    "color_reports": reports,
                }
            )
        )
        updated = Session.model_validate_json(updated.model_dump_json())
        directory = store.session_dir(identifier)
        safe_path(directory, "artifacts").mkdir(exist_ok=True)
        destination = safe_path(directory, artifact.path)
        write_new(destination, data)
        try:
            store.save(updated)
        except (OSError, ProjectError, ValidationError):
            destination.unlink()
            raise
    return updated


def select(store: Store, identifier: SessionId, revision: int, artifact_id: ArtifactId) -> Session:
    with store.locked(identifier):
        state = store.expect(identifier, revision)
        _ = state.artifact(artifact_id)
        updated = advance(state.model_copy(update={"selected_id": artifact_id}))
        store.save(updated)
    return updated


def review(
    store: Store,
    identifier: SessionId,
    revision: int,
    artifact_id: ArtifactId,
    assessment: VisualReview,
) -> Session:
    """Record the host assessment explicitly; failed checks remain visible on resume."""
    with store.locked(identifier):
        state = store.expect(identifier, revision)
        chosen = state.artifact(artifact_id).model_copy(
            update={"review": assessment, "reviewed_at": datetime.now(UTC)},
        )
        artifacts = tuple(chosen if item.id == artifact_id else item for item in state.artifacts)
        updated = advance(state.model_copy(update={"artifacts": artifacts}))
        store.save(updated)
    return updated


def record_failure(
    store: Store,
    identifier: SessionId,
    revision: int,
    *,
    prompt: str,
    reason: str,
    parent_id: ArtifactId | None,
) -> Session:
    with store.locked(identifier):
        state = store.expect(identifier, revision)
        if parent_id is not None:
            _ = state.artifact(parent_id)
        failure = FailedAttempt(
            prompt=prompt,
            reason=reason,
            parent_id=parent_id,
            created_at=datetime.now(UTC),
        )
        updated = advance(state.model_copy(update={"failures": (*state.failures, failure)}))
        store.save(updated)
    return updated
