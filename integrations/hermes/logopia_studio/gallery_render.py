"""Render a self-contained, inert-data snapshot with core feedback envelopes."""

from __future__ import annotations

import json
from base64 import b64encode
from html import escape
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING, Final

from .gallery_cards import candidate_card
from .gallery_icon import icon_context
from .gallery_package import package_panel
from .gallery_strategy import strategy_panel
from .models import FeedbackEnvelope

if TYPE_CHECKING:
    from .gallery_files import GalleryFile
    from .models import Phase, Workflow

ASSETS: Final = Path(__file__).resolve().parent.parent / "assets"
PHASES: Final[dict[Phase, tuple[str, str]]] = {
    "draft": ("브리프 준비됨", "Hermes에서 첫 방향을 만들어 주세요."),
    "planning": ("방향 구상 중", "Hermes에서 진행 상태를 확인해 주세요."),
    "generating": ("원본 생성 중", "도착한 원본부터 살펴보세요."),
    "reviewing": ("원본 검토 중", "검토 기록이 있는 후보부터 살펴보세요."),
    "awaiting_choice": ("방향 비교", "원본을 비교하고 유지할 점과 바꿀 점을 남겨 주세요."),
    "revising": ("선택 방향 수정 중", "이전 원본과 도착한 수정본을 비교해 주세요."),
    "ready": ("선택 원본 준비됨", "Hermes에서 선택 원본의 전달을 요청해 주세요."),
    "delivered": ("전달 파일 준비됨", "선택 원본과 브랜드 가이드를 패키지로 받아 보세요."),
    "failed": (
        "작업 확인 필요",
        "저장된 원본은 그대로 있습니다. Hermes에서 다음 작업을 확인해 주세요.",
    ),
    "outcome_unknown": ("결과 확인 필요", "Hermes에서 진행하던 요청의 결과를 확인해 주세요."),
    "cancelled": ("작업 중단됨", "저장된 원본을 살펴보고 Hermes에서 이어갈 방향을 알려 주세요."),
}


def _metadata(state: Workflow) -> str:
    envelopes = [
        FeedbackEnvelope(
            workflow_id=state.id,
            expected_revision=state.revision,
            candidate_id=item.id,
            candidate_sha256=item.sha256,
            action="choose",
            keep=item.keep,
        ).model_dump_json()
        for item in state.candidates
    ]
    raw = (
        f'{{"workflow_id":{json.dumps(state.id)},"expected_revision":{state.revision},'
        f'"candidates":[{",".join(envelopes)}]}}'
    )
    return (
        raw.replace("<", "\\u003c")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render_gallery(
    state: Workflow, reviews: tuple[str, ...], files: tuple[GalleryFile, ...]
) -> str:
    directions = {item.id: item for item in state.directions}
    downloads = {
        item.path.stem: "data:image/png;base64," + b64encode(item.data).decode("ascii")
        for item in files
        if item.path.parent.name == "originals"
    }
    cards = "".join(
        candidate_card(
            item, directions[item.direction_id], state, index, review, downloads[item.id]
        )
        for index, (item, review) in enumerate(zip(state.candidates, reviews, strict=True), start=1)
    )
    if not cards:
        title = "아직 비교할 원본이 없습니다"
        next_step = "Hermes에서 저장된 상태를 확인해 주세요."
        cards = f'<div class="empty-state"><h3>{title}</h3><p>{next_step}</p></div>'
    phase, next_action = PHASES[state.phase]
    script = (ASSETS / "gallery-feedback.mjs").read_text(encoding="utf-8")
    script += "\n" + (ASSETS / "gallery-ui.mjs").read_text(encoding="utf-8")
    return Template((ASSETS / "gallery.html").read_text(encoding="utf-8")).substitute(
        style=(ASSETS / "gallery.css").read_text(encoding="utf-8"),
        script=script,
        brand=escape(state.brief.name),
        product=escape(state.brief.product),
        phase=phase,
        next_action=next_action,
        workflow=state.id,
        revision=state.revision,
        selected=escape(state.selected_id or "아직 선택하지 않음"),
        strategy=strategy_panel(state.strategy) + icon_context(state),
        delivery=package_panel(state, files),
        cards=cards,
        count=len(state.candidates),
        metadata=_metadata(state),
        exact_text=escape(state.brief.exact_text or "문구 없는 심볼"),
        last_error=(
            "".join(
                (
                    '<details class="error-details"><summary>저장된 작업 오류 보기</summary>',
                    f"<p>{escape(state.last_error)}</p></details>",
                )
            )
            if state.last_error
            else ""
        ),
    )
