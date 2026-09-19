from collections.abc import Callable
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Literal

from logopia_studio.checks import review_view
from logopia_studio.models import (
    Criterion,
    Critique,
    Direction,
    GeneratedImage,
    PlanResult,
    ReviewInput,
    Strategy,
    StudioBrief,
    StudioError,
)
from logopia_studio.models_references import CandidateVariation
from PIL import Image

REPO = Path(__file__).resolve().parents[2]


def brief(count: int = 1) -> StudioBrief:
    return StudioBrief(
        name="Fixture Core",
        exact_text="",
        product="Ring tool",
        audience="Makers",
        personality="Clear",
        use_case="App",
        count=count,
    )


@dataclass(frozen=True, slots=True)
class FixtureHost:
    """Labelled deterministic transport fixture; lists accumulate observed calls."""

    root: Path
    mode: Literal["pass", "unknown", "bad_report", "revise", "missing"] = "pass"
    on_generate: Callable[[], None] | None = None
    calls: list[Path | None] = field(default_factory=list)
    plans: list[StudioBrief] = field(default_factory=list)
    reviews: list[ReviewInput] = field(default_factory=list)

    def plan(self, brief: StudioBrief) -> PlanResult:
        self.plans.append(brief)
        strategy = Strategy(
            positioning="Fixture proposal",
            audience_need="Clarity",
            brand_promise="Useful",
            distinctive_principle="Open ring",
            typography="No lettering",
            color_roles="Teal on white",
            assumptions=(),
        )
        directions = tuple(
            Direction(
                id=f"d{i}",
                title=f"Ring {i}",
                motif="Ring",
                construction="Open circle",
                rationale="Continuity",
                risk="Generic",
                preserve=("White background",),
                prompt="Fixture only teal ring.",
                variations=tuple(
                    CandidateVariation(
                        slot=slot,
                        changed_variables=(f"Gap {slot}px",),
                        instruction=f"Use gap {slot}px",
                    )
                    for slot in range(1, brief.candidates_per_direction + 1)
                ),
            )
            for i in range(1, brief.effective_direction_count + 1)
        )
        return PlanResult(
            strategy=strategy, directions=directions, provider="fixture", model="stub"
        )

    def generate(self, prompt: str, parent: Path | None, background: str) -> GeneratedImage:
        assert prompt
        assert background in {"opaque", "transparent"}
        self.calls.append(parent)
        if self.on_generate is not None:
            self.on_generate()
        if self.mode == "unknown":
            raise StudioError("outcome_unknown", "Fixture unknown native result")
        path = self.root / f"native-{len(self.calls)}.png"
        if self.mode != "missing":
            with Image.new("RGB", (64, 64), "white") as image:
                image.putpixel((32, 32), (0, 128, 100))
                image.save(path)
        return GeneratedImage(
            path=path, provider="fixture", model="stub", receipt='{"label":"deterministic fixture"}'
        )

    def critique(self, request: ReviewInput) -> tuple[Critique, ...]:
        self.reviews.append(request)
        if self.mode == "bad_report" and len(self.reviews) == 1:
            raise StudioError(
                "invalid_report", "Fixture malformed report", raw_reports=('{"oops":1}',)
            )
        criteria = (
            Criterion(key="text", status="not_applicable", observation="No requested text"),
            Criterion(
                key="composition",
                status="needs_revision" if self.mode == "revise" else "pass",
                observation="Fixture ring",
                fix="Spacing" if self.mode == "revise" else "",
            ),
            Criterion(key="small_size", status="pass", observation="Fixture target view"),
            Criterion(
                key="preservation",
                status="pass" if request.parent_path else "not_applicable",
                observation="Fixture parent compared" if request.parent_path else "New image",
            ),
            Criterion(key="background", status="pass", observation="White fixture"),
        )
        parent_hash = (
            sha256(request.parent_path.read_bytes()).hexdigest() if request.parent_path else None
        )
        parent_view = (
            sha256(review_view(request.parent_path, request.brief.display_width)).hexdigest()
            if request.parent_path
            else None
        )
        return tuple(
            Critique(
                role=role,
                provider="fixture",
                model="stub",
                summary="Fixture visual pass",
                criteria=criteria,
                call_id=f"{role}-{len(self.reviews)}",
                image_sha256=request.image_sha256,
                parent_sha256=parent_hash,
                view_sha256=sha256(
                    review_view(request.image_path, request.brief.display_width)
                ).hexdigest(),
                view_width=request.brief.display_width,
                parent_view_sha256=parent_view,
            )
            for role in ("design", "production")
        )
