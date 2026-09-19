"""Escaped candidate cards and same-width parent comparisons."""

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

from .gallery_icon import icon_diagnostics

if TYPE_CHECKING:
    from .models import Candidate, Critique, Direction, Workflow


def _critique(report: Critique) -> str:
    titles = {"design": "디자인 검토", "production": "사용 크기 검토"}
    return (
        f'<div class="review-summary"><span>{titles[report.role]}</span>'
        f"<p>{escape(report.summary)}</p></div>"
    )


def _preview(candidate: Candidate, width: int, label: str) -> str:
    height = max(1, round(width * candidate.height / candidate.width))
    return (
        f'<figure class="target"><img src="originals/{candidate.id}.png" '
        f'width="{width}" height="{height}" alt="{escape(label)}" '
        f'class="target-image"><figcaption>{escape(label)} · {width}px</figcaption></figure>'
    )


def _parent(candidate: Candidate, state: Workflow) -> str:
    if candidate.parent_id is None:
        return ""
    parent = next(item for item in state.candidates if item.id == candidate.parent_id)
    views = _preview(parent, state.brief.display_width, "이전 원본")
    views += _preview(candidate, state.brief.display_width, "수정 원본")
    return (
        f'<div class="lineage"><a href="#{parent.id}">← {parent.id}에서 수정</a>'
        f"<p>유지: {escape(' · '.join(candidate.keep) or '기록 없음')}<br>"
        f"변경: {escape(candidate.change)}</p><details><summary>이전·수정 원본 비교</summary>"
        '<div class="preview-scroll" tabindex="0" role="region" '
        'aria-label="이전과 수정 원본 비교">'
        f'<div class="parent-pair">{views}</div></div></details></div>'
    )


def _details(candidate: Candidate) -> str:
    references = "; ".join(
        f"{item.id} ({item.role}; SHA-256 {item.sha256})" for item in candidate.references
    )
    criteria = "".join(
        "".join(
            (
                f"<li><strong>{escape(item.key)} · {escape(item.status)}</strong>",
                f"<p>{escape(item.observation)}</p><p>{escape(item.fix)}</p></li>",
            )
        )
        for report in candidate.critiques
        for item in report.criteria
    )
    return (
        f'<details class="provenance"><summary>검토 조건·원본 기록</summary>'
        f"<p>출처: {escape(candidate.provider)} / {escape(candidate.model)}. "
        f"생성 출처는 검토 통과를 뜻하지 않습니다.</p>"
        f"<p>{candidate.width} &times; {candidate.height} · PNG</p>"
        f"<p>방향 {escape(candidate.direction_id)} · 후보 {candidate.candidate_slot} · "
        f"통제한 변수: {escape('; '.join(candidate.changed_variables) or '기존 단일 후보')}</p>"
        f"<p>참조 전달: {candidate.reference_conditioning} · {escape(references or '없음')}</p>"
        "<p>AI 검토와 사용자 선택은 별도 기록입니다. 플랫폼 검증은 실행되지 않았습니다.</p>"
        f"<code>SHA-256 {candidate.sha256}</code>"
        f'<a href="prompts/{candidate.id}.txt" download>정확한 생성 프롬프트 받기</a>'
        f"<ul>{criteria}</ul></details>"
    )


def candidate_card(
    candidate: Candidate,
    direction: Direction,
    state: Workflow,
    ordinal: int,
    review: str,
    download: str,
) -> str:
    selected = (
        '<span class="badge selected">현재 선택</span>' if candidate.id == state.selected_id else ""
    )
    reviews = "".join(_critique(report) for report in candidate.critiques)
    if not reviews:
        message = "두 검토가 아직 없습니다. 새 수정본은 별도 검토가 필요합니다."
        reviews = f'<p class="muted review-empty">{message}</p>'
    return "".join(
        (
            f'<article class="candidate" data-candidate="{candidate.id}" id="{candidate.id}">',
            f'<div class="card-heading"><span class="ordinal">{ordinal:02d}</span>',
            f'<div><p class="eyebrow">{candidate.id}</p>',
            f"<h3>{escape(direction.title)}</h3></div>{selected}</div>",
            f'<a class="original-stage" href="originals/{candidate.id}.png" ',
            f'aria-label="{candidate.id} 원본 열기">',
            f'<img class="original-image" src="originals/{candidate.id}.png" ',
            f'width="{candidate.width}" height="{candidate.height}" ',
            f'alt="{escape(direction.title)} 원본"></a>',
            '<div class="card-body"><span class="badge review-state">',
            f"{escape(review)}</span>",
            f'<p class="rationale">{escape(direction.rationale)}</p>',
            f'<p class="risk"><span>확인할 점</span> {escape(direction.risk)}</p>',
            '<div class="card-actions"><button type="button" ',
            f'data-feedback="{candidate.id}">이 방향으로 수정</button>',
            f'<a href="{download}" download="{candidate.id}.png" ',
            f'data-download="{candidate.id}">PNG 원본 ↓</a></div>',
            '<div class="size-preview"><p class="eyebrow">실제 표시 폭 · ',
            f"{escape(state.brief.use_case)}</p>",
            '<div class="preview-scroll" tabindex="0" role="region" ',
            f'aria-label="{candidate.id} 실제 표시 크기">',
            f"{_preview(candidate, state.brief.display_width, '흰 배경')}</div></div>",
            f'<div class="reviews">{reviews}</div>',
            icon_diagnostics(candidate, state),
            f"{_parent(candidate, state)}{_details(candidate)}</div></article>",
        )
    )
