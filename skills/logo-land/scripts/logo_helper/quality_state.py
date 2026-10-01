"""Append-only quality-loop events kept outside legacy session serialization."""

from datetime import datetime
from typing import Annotated, Literal, assert_never

from pydantic import Field

from logo_helper.model_base import Background, Digest, FrozenModel, Identifier, Text
from logo_helper.prompts import PromptResult
from logo_helper.quality_models import Critique, LoopContract


class StepRequest(FrozenModel):
    """A charged native call containing the exact prompt and verified parent input."""

    number: Annotated[int, Field(ge=1)]
    direction_id: Identifier
    created_at: datetime
    source_revision: Annotated[int, Field(ge=0)]
    source_artifact_ids: tuple[str, ...]
    input: PromptResult
    parent_sha256: Digest | None
    expected_background: Background


class StepFailure(FrozenModel):
    """Unknown outcomes remain pending until explicitly reconciled, without refunds."""

    request_number: Annotated[int, Field(ge=1)]
    outcome: Literal["failed", "unknown"]
    reason: Text
    created_at: datetime


class QualityLoop(FrozenModel):
    """Durable reservation/report ledger; ready means only ready for user review."""

    schema_version: Literal[1] = 1
    id: Identifier
    revision: Annotated[int, Field(ge=0)] = 0
    created_at: datetime
    contract: LoopContract
    brief_sha256: Digest
    requests: tuple[StepRequest, ...] = ()
    critiques: tuple[Critique, ...] = ()
    failures: tuple[StepFailure, ...] = ()

    @property
    def calls_used(self) -> int:
        return len(self.requests)

    @property
    def pending(self) -> StepRequest | None:
        if not self.requests:
            return None
        last = self.requests[-1]
        resolved = any(item.request_number == last.number for item in self.critiques) or any(
            item.request_number == last.number and item.outcome == "failed"
            for item in self.failures
        )
        return None if resolved else last

    @property
    def status(
        self,
    ) -> Literal["active", "pending", "ready_for_user_review", "exhausted", "stopped"]:
        if self.pending is not None:
            return "pending"
        if self.critiques:
            match self.critiques[-1].decision:
                case "ready":
                    return "ready_for_user_review"
                case "stop":
                    return "stopped"
                case "refine" | "reframe" | "reject":
                    pass
                case _:
                    assert_never(self.critiques[-1].decision)
        return "exhausted" if self.calls_used >= self.contract.call_budget else "active"
