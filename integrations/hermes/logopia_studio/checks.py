"""Original and target-view evidence binding, with explicit delivery criteria."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, assert_never

from .checks_images import review_view
from .models import ReviewInput, StudioError
from .models_base import ROLE_COUNT
from .store_files import read_file, safe_path

if TYPE_CHECKING:
    from pathlib import Path

    from .models import Candidate, Critique, Workflow


__all__ = ["candidate_by_id", "review_input", "review_view", "unmet_criteria", "verify_critiques"]


def candidate_by_id(state: Workflow, candidate_id: str) -> Candidate:
    for candidate in state.candidates:
        if candidate.id == candidate_id:
            return candidate
    raise StudioError("not_found", f"Candidate {candidate_id} does not exist")


def review_input(root: Path, state: Workflow, candidate: Candidate) -> ReviewInput:
    parent = candidate_by_id(state, candidate.parent_id) if candidate.parent_id else None
    return ReviewInput(
        brief=state.brief,
        image_path=safe_path(root, candidate.image_path),
        image_sha256=candidate.sha256,
        parent_path=safe_path(root, parent.image_path) if parent else None,
        keep=candidate.keep,
        change=candidate.change,
        design_spec=candidate.design_spec,
        changed_variables=candidate.changed_variables,
    )


def verify_critiques(request: ReviewInput, reports: tuple[Critique, ...]) -> None:
    if len(reports) != ROLE_COUNT or {report.role for report in reports} != {
        "design",
        "production",
    }:
        raise StudioError("invalid_report", "Exactly two independent critique roles are required")
    if len({report.call_id for report in reports}) != ROLE_COUNT:
        raise StudioError("invalid_report", "Critique call IDs must differ")
    if hashlib.sha256(read_file(request.image_path)).hexdigest() != request.image_sha256:
        raise StudioError("hash_mismatch", "Critiqued original changed")
    parent_sha = (
        hashlib.sha256(read_file(request.parent_path)).hexdigest() if request.parent_path else None
    )
    view_sha = hashlib.sha256(
        review_view(request.image_path, request.brief.display_width)
    ).hexdigest()
    parent_view_sha = (
        hashlib.sha256(review_view(request.parent_path, request.brief.display_width)).hexdigest()
        if request.parent_path
        else None
    )
    for report in reports:
        if (
            report.image_sha256 != request.image_sha256
            or report.parent_sha256 != parent_sha
            or report.view_sha256 != view_sha
            or report.view_width != request.brief.display_width
            or report.parent_view_sha256 != parent_view_sha
        ):
            raise StudioError("invalid_report", "Report evidence differs from original/parent/view")


def unmet_criteria(state: Workflow, candidate: Candidate) -> tuple[str, ...]:
    if len(candidate.critiques) != ROLE_COUNT:
        return ("Two actual image critiques are required",)
    unmet: list[str] = []
    for report in candidate.critiques:
        for criterion in report.criteria:
            match criterion.status:
                case "pass":
                    continue
                case "not_applicable":
                    if (criterion.key == "text" and state.brief.exact_text == "") or (
                        criterion.key == "preservation" and candidate.parent_id is None
                    ):
                        continue
                case "needs_revision" | "not_observed":
                    pass
                case _:
                    assert_never(criterion.status)
            unmet.append(f"{report.role}/{criterion.key}: {criterion.status}; {criterion.fix}")
    return tuple(unmet)
