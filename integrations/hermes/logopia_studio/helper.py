"""Existing-helper subprocess bridge and exact import-commit reconciliation."""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .helper_models import HelperBrief, HelperSession, parse_session
from .helper_process import run_cli
from .models import Candidate, StudioError
from .store_files import immutable_file, read_file, safe_path

if TYPE_CHECKING:
    from pathlib import Path

    from .helper_models import HelperArtifact
    from .models import Job, Workflow


@dataclass(frozen=True, slots=True)
class HelperBridge:
    """Configured CLI transport, exact helper intent and canonical artifact verification."""

    root: Path
    repo: Path
    timeout: float = 60

    def invoke(self, *args: str) -> HelperSession:
        executable = shutil.which("uv")
        if executable is None:
            raise StudioError("helper_unavailable", "uv executable is required")
        script = self.repo / "skills/logo-land/scripts/logo_project.py"
        argv = (
            executable,
            "run",
            "--locked",
            "--project",
            str(self.repo),
            "python",
            str(script),
            "--workspace",
            str(self.root),
            *args,
        )
        return parse_session(run_cli(argv, self.timeout))

    def session_path(self, workflow_id: str) -> Path:
        return safe_path(self.root, f".logo-generator/sessions/{workflow_id}/session.json")

    def request_file(self, workflow_id: str, name: str, data: str) -> Path:
        path = safe_path(self.root, f".logo-generator/workflows/{workflow_id}/requests/{name}")
        immutable_file(path, data.encode("utf-8"))
        return path

    def ensure(self, state: Workflow) -> HelperSession:
        intended = HelperBrief.from_brief(state.brief)
        if self.session_path(state.id).exists():
            session = self.show(state)
        else:
            path = self.request_file(
                state.id, "brief.json", intended.model_dump_json(exclude_none=True)
            )
            session = self.invoke("init", "--session", state.id, "--brief", str(path))
        if session.id != state.id or session.brief != intended:
            raise StudioError(
                "helper_conflict", "Existing helper session differs from saved intent"
            )
        return session

    def show(self, state: Workflow) -> HelperSession:
        session = self.invoke("show", "--session", state.id)
        if session.id != state.id or session.brief != HelperBrief.from_brief(state.brief):
            raise StudioError("helper_conflict", "Session identity or saved intent differs")
        for candidate in state.candidates:
            artifact = self.artifact(session, candidate.id)
            if (
                artifact.sha256 != candidate.sha256
                or artifact.parent_id != candidate.parent_id
                or artifact.prompt != candidate.prompt
                or artifact.image.width != candidate.width
                or artifact.image.height != candidate.height
                or artifact.requested_background != state.brief.background
                or artifact.app_icon != state.brief.app_icon
                or artifact.path != f"artifacts/{candidate.id}.png"
            ):
                raise StudioError(
                    "helper_conflict", "Canonical original differs from workflow provenance"
                )
            data = read_file(safe_path(self.root, candidate.image_path))
            if hashlib.sha256(data).hexdigest() != candidate.sha256:
                raise StudioError("hash_mismatch", "Canonical original changed")
        return session

    @staticmethod
    def artifact(session: HelperSession, candidate_id: str) -> HelperArtifact:
        for artifact in session.artifacts:
            if artifact.id == candidate_id:
                return artifact
        raise StudioError("not_found", f"Helper artifact {candidate_id} does not exist")

    def import_job(self, state: Workflow, job: Job) -> Candidate:
        session = self.ensure(state)
        if job.candidate_id is None or job.direction_id is None or job.prompt is None:
            raise StudioError("invalid_job", "Image job lacks deterministic import identity")
        if job.generated is None or job.image_sha256 is None:
            raise StudioError("outcome_unknown", "No exact native return and hash were recorded")
        if not any(artifact.id == job.candidate_id for artifact in session.artifacts):
            if hashlib.sha256(read_file(job.generated.path)).hexdigest() != job.image_sha256:
                raise StudioError("hash_mismatch", "Recorded native return changed before import")
            prompt = self.request_file(state.id, f"{job.id}.txt", job.prompt)
            args = (
                "import",
                "--session",
                state.id,
                "--revision",
                str(session.revision),
                "--artifact",
                job.candidate_id,
                "--image",
                str(job.generated.path),
                "--prompt-file",
                str(prompt),
                "--background",
                state.brief.background,
            )
            if job.parent_id is not None:
                args = (*args, "--parent", job.parent_id)
            session = self.invoke(*args)
        artifact = self.artifact(session, job.candidate_id)
        if (
            artifact.sha256 != job.image_sha256
            or artifact.parent_id != job.parent_id
            or artifact.prompt != job.prompt
            or artifact.requested_background != state.brief.background
            or artifact.app_icon != state.brief.app_icon
            or artifact.path != f"artifacts/{job.candidate_id}.png"
        ):
            raise StudioError(
                "helper_conflict", "Committed import differs from exact recorded request"
            )
        path = f".logo-generator/sessions/{state.id}/artifacts/{artifact.id}.png"
        if hashlib.sha256(read_file(safe_path(self.root, path))).hexdigest() != artifact.sha256:
            raise StudioError("hash_mismatch", "Helper success has no matching original")
        return Candidate(
            id=artifact.id,
            direction_id=job.direction_id,
            candidate_slot=job.candidate_slot,
            changed_variables=job.changed_variables,
            references=job.references,
            reference_conditioning=job.reference_conditioning,
            design_spec=job.design_spec,
            reference_analysis=job.reference_analysis,
            parent_id=job.parent_id,
            image_path=path,
            sha256=artifact.sha256,
            width=artifact.image.width,
            height=artifact.image.height,
            prompt=job.prompt,
            provider=job.generated.provider,
            model=job.generated.model,
            keep=job.keep,
            change=job.change,
        )
