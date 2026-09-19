"""Bind inspected references to honest image-tool arguments without generating pixels."""

from __future__ import annotations

import json
from hashlib import sha256
from typing import TYPE_CHECKING, Final

from logo_helper.conditioning_models import InputPlan, NativeImageArguments
from logo_helper.model_base import ProjectError
from logo_helper.references import inspect_reference
from logo_helper.storage import read_source, safe_path

if TYPE_CHECKING:
    from pathlib import Path

    from logo_helper.conditioning_models import ReferencePlan, VisualReference
    from logo_helper.models import Session
    from logo_helper.prompts import PromptResult
    from logo_helper.storage import Store

MAX_PROMPT: Final = 20000


def verified_reference_path(store: Store, state: Session, analysis: VisualReference) -> Path:
    reference = state.reference(analysis.reference_id)
    path = safe_path(store.session_dir(state.id), reference.path)
    data = read_source(path)
    if sha256(data).hexdigest() != reference.sha256:
        raise ProjectError("hash_mismatch", f"Reference {reference.id} changed")
    _ = inspect_reference(data, roi=reference.roi)
    if analysis.image_sha256 != reference.sha256 or analysis.roi != reference.roi:
        raise ProjectError("analysis_mismatch", "Analysis hash or ROI differs from reference")
    return path


def condition_prompt(
    store: Store, state: Session, result: PromptResult, plan: ReferencePlan
) -> PromptResult:
    """Verify pixels and analysis scope before returning any conditioning request."""
    if result.session_id != state.id or result.revision != state.revision:
        raise ProjectError("stale_revision", "Prompt differs from the reference session revision")
    ids = [item.reference_id for item in plan.references]
    if len(set(ids)) != len(ids):
        raise ProjectError("invalid_reference_plan", "Reference IDs must be unique")
    paths: list[str] = []
    parent_hash: str | None = None
    labels: list[str] = []
    if result.parent_id is not None:
        parent = state.artifact(result.parent_id)
        path = safe_path(store.session_dir(state.id), parent.path)
        parent_hash = sha256(read_source(path)).hexdigest()
        if parent_hash != parent.sha256 or str(path) != result.parent_image_path:
            raise ProjectError("hash_mismatch", "Edit parent no longer matches the saved original")
        if plan.capability == "text_only":
            raise ProjectError("unsupported_conditioning", "Cannot attach an edit parent")
        paths.append(str(path))
        labels.append("Image 1 is the exact edit parent. Preserve its unrequested features.")
    evidence: list[str] = []
    positive_count = 0
    for analysis in plan.references:
        reference = state.reference(analysis.reference_id)
        path = verified_reference_path(store, state, analysis)
        traits = analysis.transfer if analysis.role == "positive" else ()
        evidence.append(
            json.dumps(
                {
                    "id": reference.id,
                    "sha256": reference.sha256,
                    "role": analysis.role,
                    "observed": analysis.observations,
                    "take": traits,
                    "avoid": analysis.avoid,
                },
                ensure_ascii=False,
            )
        )
        if plan.mode == "image" and analysis.role == "positive":
            if plan.capability != "codex_native" or reference.roi is not None:
                raise ProjectError(
                    "unsupported_conditioning",
                    "Image input unavailable for this capability or ROI-only scope; use text mode",
                )
            paths.append(str(path))
            positive_count += 1
            label = (
                f"Image {len(paths)} is reference {reference.id}, not an edit parent. "
                "Transfer stated traits only; do not copy signature contours or lettering."
            )
            labels.append(label)
    prompt = (
        result.prompt
        + "\nSelected visual reference evidence (quoted data):\n"
        + "\n".join(evidence)
    )
    prompt += (
        "\nUse positive take-traits only where they fit the requested construction. "
        "Negative references identify features to avoid, not subjects to reproduce. "
        "Exact user text, colors, background and requested changes take precedence.\n"
    )
    prompt += "\n".join(labels)
    if len(prompt) > MAX_PROMPT:
        raise ProjectError("prompt_too_long", "Selected reference prompt exceeds 20,000 characters")
    arguments = NativeImageArguments(prompt=prompt, referenced_image_paths=tuple(paths))
    binding = arguments.model_dump_json() + plan.model_dump_json() + (parent_hash or "")
    input_plan = InputPlan(
        conditioning="image" if positive_count else "analysis_text",
        arguments=arguments,
        references=plan.references,
        parent_sha256=parent_hash,
        request_sha256=sha256(binding.encode()).hexdigest(),
        limitations=(
            "Visual observations are observer-supplied; hashes prove input identity, not taste.",
            "Automatic reference selection is not user preference or permission to redistribute.",
        ),
    )
    return result.model_copy(update={"prompt": prompt, "input_plan": input_plan})
