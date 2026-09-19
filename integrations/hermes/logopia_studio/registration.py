"""Native tool registration and strict request routing, with no import-time settings I/O."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Literal, assert_never
from uuid import uuid4

from pydantic import TypeAdapter

from .engine import Studio
from .gallery import publish_gallery
from .host import HermesHost
from .host_api import JsonObject, schema_for
from .host_requests import (
    Action,
    ActionRequest,
    ContinueRequest,
    DeliverRequest,
    ReconcileRequest,
    StartRequest,
    StatusRequest,
    parse_action,
    parse_start,
)
from .host_settings import load_settings
from .models import FeedbackEnvelope, StudioError

if TYPE_CHECKING:
    from pydantic import JsonValue

    from .host_api import RegistrationContext
    from .models import Workflow


def tool_schema(name: Literal["logopia_start", "logopia_action"]) -> JsonObject:
    match name:
        case "logopia_start":
            parameters = schema_for(StartRequest)
            description = (
                "Create and produce logo candidates from a concise brief, with native planning, "
                "image generation, two independent pixel critiques and a comparison gallery."
            )
        case "logopia_action":
            parameters = schema_for(ActionRequest)
            parameters["type"] = "object"
            description = (
                "Read status, continue, revise, choose, deliver or reconcile an existing workflow. "
                "Mutations require its exact expected_revision; choose/revise also require the "
                "candidate_id and candidate_sha256. Status is read-only. Never retry an unknown "
                "image outcome; reconcile inspects only saved evidence."
            )
        case _:
            assert_never(name)
    return {"name": name, "description": description, "parameters": parameters}


def checked_feedback(studio: Studio, request: FeedbackEnvelope) -> None:
    state = studio.status(request.workflow_id)
    if state.revision != request.expected_revision:
        raise StudioError("stale_revision", "Feedback revision differs from the saved workflow")
    candidate = next((item for item in state.candidates if item.id == request.candidate_id), None)
    if candidate is None or candidate.sha256 != request.candidate_sha256:
        raise StudioError(
            "stale_candidate", "Feedback candidate/hash differs from the saved original"
        )


def perform_action(studio: Studio, request: Action) -> Workflow:
    match request:
        case StatusRequest():
            return studio.status(request.workflow_id)
        case ContinueRequest():
            return studio.produce(request.workflow_id, request.expected_revision)
        case DeliverRequest():
            return studio.deliver(request.workflow_id, request.expected_revision)
        case ReconcileRequest():
            return studio.reconcile(request.workflow_id, request.expected_revision, request.job_id)
        case FeedbackEnvelope():
            checked_feedback(studio, request)
            match request.action:
                case "choose":
                    return studio.choose(
                        request.workflow_id,
                        request.expected_revision,
                        request.candidate_id,
                    )
                case "revise":
                    return studio.revise(
                        request.workflow_id,
                        request.expected_revision,
                        request.candidate_id,
                        request.keep,
                        request.change,
                    )
                case _:
                    assert_never(request.action)
        case _:
            assert_never(request)


def summary(workspace: Path, state: Workflow, gallery: Path | None) -> str:
    originals: list[JsonValue] = [
        {
            "candidate_id": item.id,
            "sha256": item.sha256,
            "path": str(workspace / item.image_path),
            "parent_id": item.parent_id,
            "direction_id": item.direction_id,
            "candidate_slot": item.candidate_slot,
            "changed_variables": list(item.changed_variables),
            "reference_conditioning": item.reference_conditioning,
            "critique_roles": [report.role for report in item.critiques],
        }
        for item in state.candidates
    ]
    return json.dumps(
        {
            "success": state.phase not in {"failed", "outcome_unknown", "cancelled"},
            "workflow_id": state.id,
            "revision": state.revision,
            "phase": state.phase,
            "selected_id": state.selected_id,
            "call_budget": TypeAdapter(JsonObject).validate_json(
                state.call_budget.model_dump_json()
            ),
            "gallery": str(gallery) if gallery else None,
            "originals": originals,
            "last_error": state.last_error[:2000] if state.last_error else None,
            "delivery": {"path": state.delivery.path, "zip_path": state.delivery.zip_path}
            if state.delivery
            else None,
        },
        ensure_ascii=False,
    )


def register(ctx: RegistrationContext, plugin_root: Path | None = None) -> None:
    root = plugin_root if plugin_root is not None else Path(__file__).resolve().parents[1]

    def invoke(args: JsonObject, *, start: bool) -> str:
        try:
            request = parse_start(args) if start else parse_action(args)
            settings = load_settings(root)
            studio = Studio(settings.workspace, settings.helper_repo, HermesHost(ctx))
            match request:
                case StartRequest():
                    created = studio.create(request.workflow_id, request.brief)
                    state = (
                        created
                        if created.phase in {"failed", "outcome_unknown", "cancelled"}
                        else studio.produce(created.id, created.revision)
                    )
                case StatusRequest():
                    return summary(settings.workspace, studio.status(request.workflow_id), None)
                case ContinueRequest() | DeliverRequest() | ReconcileRequest() | FeedbackEnvelope():
                    state = perform_action(studio, request)
                case _:
                    assert_never(request)
            output = (
                settings.workspace
                / "output"
                / "logopia-studio"
                / state.id
                / f"revision-{state.revision}-{uuid4().hex}"
            )
            gallery = publish_gallery(settings.workspace, state, output)
            return summary(settings.workspace, state, gallery)
        except StudioError as exc:
            return json.dumps(
                {"success": False, "error": exc.code, "detail": exc.detail[:2000]},
                ensure_ascii=False,
            )

    def start_tool(args: JsonObject, **kwargs: JsonValue) -> str:
        del kwargs
        return invoke(args, start=True)

    def action_tool(args: JsonObject, **kwargs: JsonValue) -> str:
        del kwargs
        return invoke(args, start=False)

    ctx.register_tool(
        name="logopia_start",
        toolset="logopia-studio",
        schema=tool_schema("logopia_start"),
        handler=start_tool,
    )
    ctx.register_tool(
        name="logopia_action",
        toolset="logopia-studio",
        schema=tool_schema("logopia_action"),
        handler=action_tool,
    )
    ctx.register_skill(
        "director",
        root / "skills" / "director" / "SKILL.md",
        description="Direct a native logo workflow with independent pixel critiques.",
    )
