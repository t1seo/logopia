"""Verified local PNGs enter multimodal planning, never the parent image slot."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

from .host_images import read_png
from .models_base import StudioError

if TYPE_CHECKING:
    from .host_api import LlmInput
    from .models_references import ReferenceAnalysis, StudioReference


def reference_inputs(references: tuple[StudioReference, ...]) -> tuple[LlmInput, ...]:
    inputs: list[LlmInput] = []
    for reference in references:
        data = read_png(reference.path)
        if hashlib.sha256(data).hexdigest() != reference.sha256:
            raise StudioError(
                "reference_changed", f"Reference {reference.id} differs from its hash"
            )
        inputs.extend(
            (
                {
                    "type": "text",
                    "text": (
                        f"Reference {reference.id}; role={reference.role}. "
                        "Observe these pixels. Negative means avoid its stated traits, never copy. "
                        "Reference image pixels condition planning only; generation receives "
                        "explicitly extracted text traits. A reference is not the edit parent."
                    ),
                },
                {
                    "type": "image",
                    "data": data,
                    "mime_type": "image/png",
                    "file_name": f"reference-{reference.id}.png",
                },
            )
        )
    return tuple(inputs)


def bind_reference_analysis(
    references: tuple[StudioReference, ...],
    analysis: tuple[ReferenceAnalysis, ...],
    history: tuple[str, ...],
) -> tuple[ReferenceAnalysis, ...]:
    indexed = {item.id: item for item in references}
    if len(analysis) != len(references) or {item.reference_id for item in analysis} != set(indexed):
        raise StudioError(
            "invalid_report", "Inspect and report each supplied reference exactly once", history
        )
    bound: list[ReferenceAnalysis] = []
    for item in analysis:
        reference = indexed[item.reference_id]
        if reference.role == "negative" and item.transfer_traits:
            raise StudioError(
                "invalid_report", "Negative references cannot supply positive traits", history
            )
        bound.append(item.model_copy(update={"reference_sha256": reference.sha256}))
    _ = reference_inputs(references)
    return tuple(bound)
