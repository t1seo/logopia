"""Read-only icon diagnostics use equal CSS pixels and labeled mask simulations."""

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Candidate, Workflow


def icon_diagnostics(candidate: Candidate, state: Workflow) -> str:
    if state.brief.mode != "app_icon":
        return ""
    groups: list[str] = []
    for name, background, color in (("밝은", "#f5f5f5", "#151515"), ("어두운", "#242424", "#fff")):
        sizes = "".join(
            (
                f'<figure data-diagnostic-size="{width}" style="margin:0;flex:none">'
                f'<img src="originals/{candidate.id}.png" width="{width}" height="{width}" '
                f'alt="{escape(candidate.id)} {width}px {name} 주변" '
                f'style="display:block;width:{width}px;height:{width}px;object-fit:contain">'
                f"<figcaption>{width}px</figcaption></figure>"
            )
            for width in (32, 48, 64, 128)
        )
        group = (
            f'<div style="padding:12px;background:{background};color:{color}">'
            f'<p>{name} 주변 배경</p><div style="display:flex;align-items:end;'
            f'flex-wrap:wrap;gap:16px">{sizes}</div></div>'
        )
        groups.append(group)
    masks = "".join(
        (
            f'<figure style="margin:0"><img src="originals/{candidate.id}.png" width="64" '
            f'height="64" style="width:64px;height:64px;object-fit:contain;{mask}" '
            f'alt="{label} 시뮬레이션"><figcaption>{label}</figcaption></figure>'
        )
        for label, mask in (
            ("원형 Mask", "clip-path:circle(50%)"),
            ("둥근 사각 Mask", "border-radius:22%"),
        )
    )
    return "".join(
        (
            '<details class="icon-diagnostics"><summary>앱 아이콘 진단 비교</summary>',
            "<p>32/48/64/128px는 진단 크기입니다. 주변 배경은 원본을 변경하지 않습니다.</p>",
            "".join(groups),
            '<div data-platform-preview="simulation" style="display:flex;gap:24px;padding:12px">',
            masks,
            "</div><p>CSS Mask 시뮬레이션이며 실제 OS 렌더링이나 심사 결과가 아닙니다.</p>",
            "</details>",
        )
    )


def icon_context(state: Workflow) -> str:
    if state.brief.mode != "app_icon" or not state.candidates:
        return ""
    icons = "".join(
        (
            f'<figure style="margin:0;text-align:center"><img src="originals/{item.id}.png" '
            'width="48" height="48" style="width:48px;height:48px;'
            'object-fit:contain;display:block" '
            f'alt="{item.id}"><figcaption>{item.id}</figcaption></figure>'
        )
        for item in state.candidates
    )
    return (
        '<div data-icon-context="48"><p>동일한 48px 앱 목록 비교 · 홈 화면 시뮬레이션</p>'
        '<div style="display:flex;flex-wrap:wrap;gap:24px;padding:24px;background:#e9e9e9">'
        f"{icons}</div>"
        "</div>"
    )
