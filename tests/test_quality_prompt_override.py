from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from logo_helper.color_models import PaletteContent, Swatch
from logo_helper.color_workflow import add_palette
from logo_helper.model_base import PaletteId, SessionId
from logo_helper.quality_cli import LoopResponse
from logo_helper.quality_loop import record_critique, record_failure, request_step, start_loop
from logo_helper.storage import Store
from tests.test_quality_loop import contract
from tests.test_quality_loop_support import assessment, imported

if TYPE_CHECKING:
    from tests.conftest import Harness


def _start(harness: Harness) -> Store:
    harness.init()
    store = Store.at(harness.workspace)
    _ = start_loop(store, "craft", contract())
    return store


def _request(harness: Harness, revision: int = 0, *, override: bool = True) -> LoopResponse:
    extra = ("--prompt-file", str(harness.prompt)) if override else ()
    return LoopResponse.model_validate_json(
        harness.ok("loop-request", "--loop", "craft", "--revision", str(revision), *extra)
    )


@pytest.mark.parametrize("prompt", ["  네뷸라 🌌\r\nKeep exact lettering.\n\n", "가" * 20000])
def test_cli_reserves_exact_utf8_prompt_and_resumes_without_source_file(
    harness: Harness, prompt: str
) -> None:
    # Given an explicit final prompt, including meaningful Unicode and whitespace.
    _ = _start(harness)
    _ = harness.prompt.write_bytes(prompt.encode("utf-8"))
    before = harness.state_path.read_bytes()
    # When the real CLI reserves the call and resumes after its source file disappears.
    reserved = _request(harness)
    harness.prompt.unlink()
    resumed = LoopResponse.model_validate_json(harness.ok("loop-show", "--loop", "craft"))
    # Then the exact native input, source intent and single charge remain persisted.
    assert reserved.state.requests[-1].input.prompt == prompt
    assert reserved.state.requests[-1].input.mode == "generation"
    assert resumed == reserved
    assert resumed.calls_used == 1
    assert harness.state_path.read_bytes() == before


@pytest.mark.parametrize("raw", [b"", b" \r\n\t", b"x" * 20001, b"\xff"])
def test_invalid_prompt_file_does_not_charge_or_mutate_loop(harness: Harness, raw: bytes) -> None:
    # Given invalid final prompt content at the CLI boundary.
    _ = _start(harness)
    _ = harness.prompt.write_bytes(raw)
    path = harness.workspace / ".logo-generator/quality-loops/craft/loop.json"
    before = path.read_bytes()
    # When a reservation is attempted.
    result = harness.run(
        "loop-request", "--loop", "craft", "--revision", "0", "--prompt-file", str(harness.prompt)
    )
    # Then no invalid request or budget charge is saved.
    assert result.returncode != 0
    assert path.read_bytes() == before


def test_cli_edit_override_keeps_real_parent_palette_and_background(harness: Harness) -> None:
    # Given a critiqued parent with a structured palette.
    store = _start(harness)
    _ = add_palette(
        store,
        SessionId("demo"),
        0,
        palette_id=PaletteId("green"),
        content=PaletteContent(
            swatches=(Swatch(hex="#007832", role="symbol"),),
            source="assistant",
            selected_by="assistant",
            rationale="Synthetic test palette",
        ),
    )
    first = request_step(store, "craft", 0)
    imported(harness, store, first)
    reviewed = record_critique(store, "craft", first.revision, assessment(store, first))
    exact = "Widen only the lower gap. Keep the supplied parent and green palette.\n"
    _ = harness.prompt.write_text(exact, encoding="utf-8")
    # When a host-authored edit is reserved through the CLI.
    result = _request(harness, reviewed.revision)
    # Then only the prompt changes; the real edit inputs stay bound to the parent.
    request = result.state.requests[-1]
    parent = store.load(SessionId("demo")).artifacts[-1]
    assert request.input.prompt == exact
    assert request.input.mode == "edit"
    assert request.input.parent_id == parent.id
    assert request.parent_sha256 == parent.sha256
    assert request.input.parent_image_path == str(
        store.session_dir(SessionId("demo")) / parent.path
    )
    assert request.input.palette_id == parent.palette_id == PaletteId("green")
    assert request.input.palette_digest == first.requests[-1].input.palette_digest
    assert request.expected_background == request.input.requested_background == "transparent"
    assert result.state.contract == reviewed.contract


@pytest.mark.parametrize("unknown", [False, True])
def test_pending_call_cannot_be_replaced_with_another_prompt(
    harness: Harness, unknown: bool
) -> None:
    # Given a pending call, optionally with an unknown host outcome.
    store = _start(harness)
    reserved = _request(harness).state
    state = (
        record_failure(
            store,
            "craft",
            reserved.revision,
            request_number=1,
            outcome="unknown",
            reason="Synthetic unknown host outcome",
        )
        if unknown
        else reserved
    )
    _ = harness.prompt.write_text("Different prompt", encoding="utf-8")
    # When the caller tries to overwrite the pending request.
    result = harness.run(
        "loop-request",
        "--loop",
        "craft",
        "--revision",
        str(state.revision),
        "--prompt-file",
        str(harness.prompt),
    )
    # Then the original pending request survives without an extra charge.
    resumed = LoopResponse.model_validate_json(harness.ok("loop-show", "--loop", "craft"))
    assert result.returncode != 0
    assert "pending_request" in result.stderr
    assert resumed.state == state


@pytest.mark.parametrize("replace", [False, True])
def test_confirmed_failure_retry_preserves_exact_input(harness: Harness, replace: bool) -> None:
    # Given a failed host-authored call whose original input is recorded.
    store = _start(harness)
    reserved = _request(harness).state
    failed = record_failure(
        store,
        "craft",
        reserved.revision,
        request_number=1,
        outcome="failed",
        reason="Synthetic host confirmed failure",
    )
    _ = harness.prompt.write_text("Replacement direction", encoding="utf-8")
    extra = ("--prompt-file", str(harness.prompt)) if replace else ()
    # When retrying with no override or an incompatible replacement.
    result = harness.run(
        "loop-request", "--loop", "craft", "--revision", str(failed.revision), *extra
    )
    # Then a retry reuses the recorded input; replacements fail without a charge.
    resumed = LoopResponse.model_validate_json(harness.ok("loop-show", "--loop", "craft"))
    if replace:
        assert result.returncode != 0
        assert "retry_conflict" in result.stderr
        assert resumed.state == failed
    else:
        assert result.returncode == 0
        assert resumed.state.requests[-1].input == reserved.requests[-1].input
        assert resumed.calls_used == 2


def test_different_import_prompt_cannot_resolve_reserved_override(harness: Harness) -> None:
    # Given a reservation whose real imported fixture has a different saved prompt.
    store = _start(harness)
    reserved = _request(harness).state
    _ = harness.prompt.write_text("Different submitted prompt", encoding="utf-8")
    _ = harness.import_image()
    report = assessment(store, reserved)
    path = harness.workspace / "critique.json"
    _ = path.write_text(report.model_dump_json(), encoding="utf-8")
    # When recording the critique through the CLI.
    result = harness.run(
        "loop-record",
        "--loop",
        "craft",
        "--revision",
        str(reserved.revision),
        "--critique-file",
        str(path),
    )
    # Then prompt equality still blocks the mismatched result.
    assert result.returncode != 0
    assert "reserved call" in result.stderr
    resumed = LoopResponse.model_validate_json(harness.ok("loop-show", "--loop", "craft"))
    assert resumed.state == reserved


def test_exact_override_import_completes_quality_review_without_selecting(harness: Harness) -> None:
    # Given an imported fixture with the exact reserved UTF-8 prompt.
    store = _start(harness)
    _ = harness.prompt.write_bytes("  Fixture only: 모로\r\n".encode())
    reserved = _request(harness).state
    _ = harness.import_image()
    report = assessment(store, reserved, decision="ready", unresolved=None)
    path = harness.workspace / "critique.json"
    _ = path.write_text(report.model_dump_json(), encoding="utf-8")
    # When the real CLI records the evidence-bound critique.
    result = LoopResponse.model_validate_json(
        harness.ok(
            "loop-record",
            "--loop",
            "craft",
            "--revision",
            str(reserved.revision),
            "--critique-file",
            str(path),
        )
    )
    # Then the loop reaches review readiness without selecting or approving the fixture.
    assert result.status == "ready_for_user_review"
    source = store.load(SessionId("demo"))
    assert source.selected_id is None
    assert source.artifacts[-1].review is None
