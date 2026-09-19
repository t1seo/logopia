"""Bounded native strategy, generation and independent pixel-critique transport."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Final, Literal, TypeVar
from uuid import uuid4

from pydantic import BaseModel, TypeAdapter, ValidationError

from .host_api import ImageArguments, JsonObject, LlmInput, schema_for
from .host_images import image_evidence, parse_receipt, read_png, verify_unchanged
from .host_models import CriticReport, DirectionReport
from .host_prompts import critique_instructions, plan_instructions
from .host_references import bind_reference_analysis, reference_inputs
from .models import Critique, GeneratedImage, PlanResult, Strategy
from .models import StudioError as HostError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .host_api import Completion, HermesContext
    from .host_images import PngEvidence
    from .models import ReviewInput, StudioBrief

ReportT = TypeVar("ReportT", bound=BaseModel)
PROMPT_LIMIT: Final = 24000
CRITERION_COUNT: Final = 5


def parse_report(model: type[ReportT], raw: str, history: tuple[str, ...]) -> ReportT:
    if len(raw.encode("utf-8")) > 32 * 1024:
        raise HostError("invalid_report", "Structured report exceeds 32 KiB", history)
    try:
        return model.model_validate_json(raw)
    except ValidationError as exc:
        raise HostError("invalid_report", str(exc), (*history, raw)) from exc


def image_inputs(label: str, evidence: PngEvidence) -> tuple[LlmInput, ...]:
    return (
        {"type": "text", "text": f"{label}: original PNG; then target view at {evidence.width}px."},
        {
            "type": "image",
            "data": evidence.original,
            "mime_type": "image/png",
            "file_name": f"{label}-original.png",
        },
        {
            "type": "image",
            "data": evidence.view,
            "mime_type": "image/png",
            "file_name": f"{label}-target.png",
        },
    )


class HermesHost:
    """Use only ctx.llm.complete_structured and one native dispatch per image request."""

    def __init__(self, ctx: HermesContext) -> None:
        self._ctx: HermesContext = ctx

    def _complete(
        self,
        model: type[BaseModel],
        instructions: str,
        inputs: Sequence[LlmInput],
        purpose: str,
        max_tokens: int,
        history: tuple[str, ...] = (),
    ) -> Completion:
        try:
            result = self._ctx.llm.complete_structured(
                instructions=instructions,
                input=inputs,
                json_schema=schema_for(model),
                schema_name=model.__name__,
                timeout=120.0,
                max_tokens=max_tokens,
                purpose=purpose,
            )
        except TimeoutError as exc:
            if not history:
                raise
            raise HostError("host_timeout", str(exc), history) from exc
        except OSError as exc:
            raise HostError("host_transport_unknown", str(exc), history) from exc
        except HostError as exc:
            raise HostError(exc.code, exc.detail, (*history, *exc.raw_reports)) from exc
        except (RuntimeError, ValueError) as exc:
            raise HostError("host_completion_failed", str(exc), history) from exc
        if not result.provider.strip() or not result.model.strip():
            raise HostError(
                "missing_attribution",
                "Structured completion omitted attribution",
                (*history, result.text),
            )
        return result

    def plan(self, brief: StudioBrief) -> PlanResult:
        inputs: tuple[LlmInput, ...] = (
            {"type": "text", "text": brief.model_dump_json()},
            *reference_inputs(brief.references),
        )
        first = self._complete(
            Strategy,
            plan_instructions("strategy", brief),
            inputs,
            "logopia.strategy",
            6000,
        )
        strategy = parse_report(Strategy, first.text, ())
        second = self._complete(
            DirectionReport,
            plan_instructions("directions", brief),
            (*inputs, {"type": "text", "text": strategy.model_dump_json()}),
            "logopia.directions",
            6000,
            (first.text,),
        )
        report = parse_report(DirectionReport, second.text, (first.text,))
        if len(report.directions) != brief.effective_direction_count:
            raise HostError(
                "invalid_plan",
                "Direction count differs from the saved brief",
                (first.text, second.text),
            )
        if len({direction.id for direction in report.directions}) != len(report.directions):
            raise HostError(
                "invalid_plan", "Direction IDs must be unique", (first.text, second.text)
            )
        if (first.provider, first.model) != (second.provider, second.model):
            raise HostError(
                "attribution_changed",
                "Planning calls returned different attribution",
                (first.text, second.text),
            )
        return PlanResult(
            strategy=strategy,
            directions=report.directions,
            provider=second.provider,
            model=second.model,
            reference_analysis=bind_reference_analysis(
                brief.references, report.reference_analysis, (first.text, second.text)
            ),
        )

    def generate(self, prompt: str, parent: Path | None, background: str) -> GeneratedImage:
        if not prompt.strip() or len(prompt) > PROMPT_LIMIT:
            raise HostError("invalid_prompt", "Generation requires a bounded nonblank prompt")
        if background not in {"opaque", "transparent"}:
            raise HostError("invalid_background", "Unknown saved background")
        parent_bytes = read_png(parent) if parent is not None else None
        args: ImageArguments = {"prompt": prompt, "aspect_ratio": "square"}
        if parent is not None:
            args["image_url"] = str(parent)
        raw = self._ctx.dispatch_tool("image_generate", args)
        receipt = parse_receipt(raw)
        if receipt.image is None:
            raise HostError("invalid_receipt", "Missing native image", (raw,))
        output = Path(receipt.image)
        try:
            _ = read_png(output)
            current_parent = read_png(parent) if parent is not None else None
        except HostError as exc:
            raise HostError(exc.code, exc.detail, (raw,)) from exc
        if parent is not None and (output == parent or current_parent != parent_bytes):
            raise HostError(
                "parent_changed", "Native generation changed/reused the exact parent", (raw,)
            )
        return GeneratedImage(
            path=output, provider=receipt.provider, model=receipt.model, receipt=raw
        )

    def critique(self, request: ReviewInput) -> tuple[Critique, ...]:
        original = image_evidence(request.image_path, request.brief.display_width)
        if original.sha256 != request.image_sha256:
            raise HostError("image_changed", "Review original no longer matches its saved hash")
        parent = (
            image_evidence(request.parent_path, request.brief.display_width)
            if request.parent_path is not None
            else None
        )
        context = json.dumps(
            {
                "brief": TypeAdapter(JsonObject).validate_json(request.brief.model_dump_json()),
                "keep": request.keep,
                "change": request.change,
                "has_parent": parent is not None,
                "design_intent_not_observation": (
                    TypeAdapter(JsonObject).validate_json(request.design_spec.model_dump_json())
                    if request.design_spec is not None
                    else None
                ),
                "changed_variables": request.changed_variables,
            },
            ensure_ascii=False,
        )
        inputs: tuple[LlmInput, ...] = (
            {"type": "text", "text": context},
            *image_inputs("candidate", original),
            *(image_inputs("parent", parent) if parent is not None else ()),
            *reference_inputs(request.brief.references),
        )
        reports: list[Critique] = []
        raw_reports: tuple[str, ...] = ()
        roles: tuple[Literal["design", "production"], ...] = ("design", "production")
        for role in roles:
            call_id = uuid4().hex
            result = self._complete(
                CriticReport,
                critique_instructions(role),
                inputs,
                f"logopia.critique.{role}",
                2400,
                raw_reports,
            )
            parsed = parse_report(CriticReport, result.text, raw_reports)
            raw_reports = (*raw_reports, result.text)
            if len({item.key for item in parsed.criteria}) != CRITERION_COUNT:
                raise HostError(
                    "invalid_report", "Critic must return five unique keys", raw_reports
                )
            for criterion in parsed.criteria:
                allowed_na = (criterion.key == "text" and request.brief.exact_text == "") or (
                    criterion.key == "preservation" and parent is None
                )
                if criterion.status == "not_applicable" and not allowed_na:
                    raise HostError(
                        "invalid_report", "Critic used an inapplicable exemption", raw_reports
                    )
            try:
                bound = Critique(
                    role=role,
                    provider=result.provider,
                    model=result.model,
                    summary=parsed.summary,
                    criteria=parsed.criteria,
                    call_id=call_id,
                    image_sha256=original.sha256,
                    parent_sha256=parent.sha256 if parent else None,
                    view_sha256=original.view_sha256,
                    view_width=original.width,
                    parent_view_sha256=parent.view_sha256 if parent else None,
                )
            except ValidationError as exc:
                raise HostError("invalid_report", str(exc), raw_reports) from exc
            reports.append(bound)
        verify_unchanged(request.image_path, original.sha256, raw_reports)
        if parent is not None and request.parent_path is not None:
            verify_unchanged(request.parent_path, parent.sha256, raw_reports, parent=True)
        return tuple(reports)
