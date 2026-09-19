"""Runtime-resolved schemas for native structured responses."""

from typing import Annotated

from pydantic import Field

from .models import Criterion, Direction
from .models_base import FrozenModel
from .models_references import ReferenceAnalysis


class DirectionReport(FrozenModel):
    """The director supplies observations and intent, never provider attribution."""

    directions: Annotated[tuple[Direction, ...], Field(min_length=1, max_length=6)]
    reference_analysis: Annotated[tuple[ReferenceAnalysis, ...], Field(max_length=6)] = ()


class CriticReport(FrozenModel):
    """Host code binds model observations to independently checked input hashes."""

    summary: Annotated[str, Field(min_length=1, max_length=2000)]
    criteria: Annotated[tuple[Criterion, ...], Field(min_length=5, max_length=5)]
