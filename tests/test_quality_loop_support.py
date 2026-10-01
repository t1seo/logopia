from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Literal

from PIL import Image

from logo_helper.model_base import ArtifactId
from logo_helper.quality_models import Criterion, CriterionAssessment, Critique, ViewEvidence
from logo_helper.workflow import import_image

if TYPE_CHECKING:
    from logo_helper.quality_state import QualityLoop
    from logo_helper.storage import Store
    from tests.conftest import Harness


def imported(harness: Harness, store: Store, state: QualityLoop, identifier: str = "v1") -> None:
    request = state.requests[-1]
    _ = import_image(
        store,
        state.contract.session_id,
        request.source_revision,
        artifact_id=ArtifactId(identifier),
        image=harness.png,
        prompt=request.input.prompt,
        parent_id=request.input.parent_id,
        background=request.expected_background,
        palette_id=request.input.palette_id,
        lockup=request.input.lockup,
    )


def assessment(
    store: Store,
    state: QualityLoop,
    *,
    artifact: str = "v1",
    decision: Literal["refine", "reframe", "reject", "ready", "stop"] = "refine",
    unresolved: Criterion | None = "optics",
) -> Critique:
    source = store.load(state.contract.session_id)
    image = source.artifact(ArtifactId(artifact))
    original_path = store.session_dir(source.id) / image.path
    evidence: list[ViewEvidence] = [
        ViewEvidence(
            id="original",
            path=str(original_path.relative_to(store.root)),
            sha256=image.sha256,
            source_artifact_sha256=image.sha256,
            kind="original",
            description="Synthetic fixture: reviewer assertions only, no design-quality claim",
        )
    ]
    for identifier, size in (("small", 8), ("context", 32)):
        path = store.root / f"{artifact}-{identifier}.png"
        with Image.new("RGB", (size, size), "green") as rendered:
            rendered.save(path)
        evidence.append(
            ViewEvidence(
                id=identifier,
                path=path.name,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                source_artifact_sha256=image.sha256,
                kind="target_size" if identifier == "small" else "context",
                target_width=size if identifier == "small" else None,
                description="Synthetic test evidence, not an actual logo inspection",
            )
        )
    criteria: tuple[Criterion, ...] = (
        "appropriateness",
        "distinctiveness",
        "form",
        "optics",
        "use_size",
        "versatility",
        "scope",
    )
    return Critique(
        request_number=state.calls_used,
        artifact_id=image.id,
        artifact_sha256=image.sha256,
        reviewer="Synthetic test fixture",
        evidence=tuple(evidence),
        assessments=tuple(
            CriterionAssessment(
                criterion=criterion,
                status="revise" if criterion == unresolved else "pass",
                issue_id="lower-gap-width" if criterion == unresolved else None,
                observation="The lower gap is narrower than the upper gap in the supplied fixture",
                evidence_ids=("small",)
                if criterion == "use_size"
                else ("context",)
                if criterion == "versatility"
                else ("original",),
            )
            for criterion in criteria
        ),
        decision=decision,
        reason="Make the visible spacing consistent",
        preserve=("Keep the outer contour",) if decision == "refine" else (),
        changes=("Widen only the lower gap",) if decision == "refine" else (),
        next_direction_id="two" if decision in {"reframe", "reject"} else None,
        change_result="improved" if image.parent_id is not None else "initial",
        preservation_result="pass" if image.parent_id is not None else "not_observed",
    )
