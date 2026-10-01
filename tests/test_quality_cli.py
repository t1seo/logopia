from __future__ import annotations

from typing import TYPE_CHECKING

from logo_helper.model_base import SessionId
from logo_helper.quality_cli import LoopResponse
from logo_helper.quality_models import Direction, LoopContract

if TYPE_CHECKING:
    from pathlib import Path

    from tests.conftest import Harness


def _contract_file(harness: Harness) -> Path:
    contract = LoopContract(
        session_id=SessionId("demo"),
        scope="full_logo",
        fixed_decisions=("Keep the supplied brand spelling and green palette.",),
        source_evidence=("User's existing brief.",),
        success_criteria=("A recognizable silhouette without reliance on its story.",),
        use_contexts=("Product header at 32 pixels.",),
        directions=(
            Direction(
                id="ribbon",
                idea="A folded ribbon sign",
                structure="One continuous folded silhouette",
                distinction="A wide fold with a deliberately asymmetric opening",
            ),
            Direction(
                id="imprint",
                idea="A carved seal",
                structure="Square outer mass and offset circular void",
                distinction="Compression around an off-centre opening",
            ),
        ),
        call_budget=1,
    )
    path = harness.workspace / "loop-contract.json"
    _ = path.write_text(contract.model_dump_json(), encoding="utf-8")
    return path


def test_cli_unknown_call_survives_resume_and_keeps_budget(harness: Harness) -> None:
    harness.init()
    before = harness.state_path.read_bytes()
    contract = _contract_file(harness)
    initial = LoopResponse.model_validate_json(
        harness.ok("loop-start", "--loop", "quality", "--contract-file", str(contract))
    )
    assert initial.calls_used == 0
    request = LoopResponse.model_validate_json(
        harness.ok("loop-request", "--loop", "quality", "--revision", "0")
    )
    assert request.status == "pending"
    assert request.pending_request == 1
    assert request.remaining_calls == 0
    assert "Morrow Studio" in request.state.requests[-1].input.prompt
    unknown = LoopResponse.model_validate_json(
        harness.ok(
            "loop-failure",
            "--loop",
            "quality",
            "--revision",
            "1",
            "--request",
            "1",
            "--outcome",
            "unknown",
            "--reason",
            "Host timed out; result may still arrive.",
        )
    )
    resumed = LoopResponse.model_validate_json(harness.ok("loop-show", "--loop", "quality"))
    assert resumed == unknown
    assert resumed.status == "pending"
    duplicate = harness.run("loop-request", "--loop", "quality", "--revision", "2")
    assert duplicate.returncode != 0
    failed = LoopResponse.model_validate_json(
        harness.ok(
            "loop-failure",
            "--loop",
            "quality",
            "--revision",
            "2",
            "--request",
            "1",
            "--outcome",
            "failed",
            "--reason",
            "Host confirmed no image was produced.",
        )
    )
    assert failed.status == "exhausted"
    assert failed.calls_used == 1
    assert failed.pending_request is None
    assert harness.state_path.read_bytes() == before


def test_cli_stale_request_cannot_reserve_another_call(harness: Harness) -> None:
    harness.init()
    path = _contract_file(harness)
    _ = harness.ok("loop-start", "--loop", "quality", "--contract-file", str(path))
    _ = harness.ok("loop-request", "--loop", "quality", "--revision", "0")
    stale = harness.run("loop-request", "--loop", "quality", "--revision", "0")
    assert stale.returncode != 0
    state = LoopResponse.model_validate_json(harness.ok("loop-show", "--loop", "quality"))
    assert state.calls_used == 1
    assert state.state.revision == 1


def test_cli_fixed_type_rejects_lettering_in_source(harness: Harness) -> None:
    harness.init()
    path = _contract_file(harness)
    contract = LoopContract.model_validate_json(path.read_bytes())
    symbol = contract.model_copy(update={"scope": "symbol_only", "fixed_typography": True})
    _ = path.write_text(symbol.model_dump_json(), encoding="utf-8")
    result = harness.run("loop-start", "--loop", "quality", "--contract-file", str(path))
    assert result.returncode != 0
    assert not (harness.workspace / ".logo-generator/quality-loops/quality/loop.json").exists()
    _ = path.write_text(contract.model_dump_json(), encoding="utf-8")
    recovered = LoopResponse.model_validate_json(
        harness.ok("loop-start", "--loop", "quality", "--contract-file", str(path))
    )
    assert recovered.calls_used == 0
