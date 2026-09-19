"""Escaped blind-review markup; no prompts, methods or source IDs reach the UI."""

from html import escape
from pathlib import Path
from string import Template
from typing import Final

from logo_helper.preference_models import PreferenceCandidate, PreferenceManifest, PreferencePair

EVIDENCE_LABELS: Final = (
    ("brief_reference_fit", "Brief and references: which visible feature fits or conflicts?"),
    ("shape_background", "Shape and background: identify the focal form and separation."),
    ("craft_detail", "Craft: locate a curve, join, spacing or lettering detail."),
    ("effects_material", "Effects: where does material or decoration support or obscure form?"),
    ("distinctiveness", "Confusion: what overlaps a reference or another candidate?"),
    ("small_size_32", "32 px: name a surviving or lost feature and its location."),
    ("peer_context", "Peer context: what stays identifiable among equal-size candidates?"),
)


def _candidate(candidate: PreferenceCandidate, side: str) -> str:
    image = escape(candidate.image_file)
    sizes = "".join(
        (
            f'<figure><img src="{image}" alt="{side} at {size} px" '
            f'width="{size}" height="{size}"><figcaption>{size} px</figcaption></figure>'
        )
        for size in (32, 48, 64, 128)
    )
    return (
        f'<section class="candidate"><h3>Candidate {side}</h3>'
        f'<div class="size-strip light">{sizes}</div>'
        f'<div class="size-strip dark">{sizes}</div>'
        f'<a href="{image}" target="_blank" rel="noopener">Open original {side}</a>'
        f'<span class="dimensions">{candidate.width} &times; {candidate.height} px</span></section>'
    )


def _pair(pair: PreferencePair, peers: str) -> str:
    fields = "".join(
        (
            f'<label for="{pair.id}-{key}">{label}</label><textarea '
            f'id="{pair.id}-{key}" name="{key}" rows="2" maxlength="2000" required></textarea>'
        )
        for key, label in EVIDENCE_LABELS
    )
    choices = "".join(
        (
            f'<label><input type="radio" name="{pair.id}-outcome" '
            f'value="{value}" required>{label}</label>'
        )
        for value, label in (
            ("a", "Prefer A"),
            ("b", "Prefer B"),
            ("tie", "Similar"),
            ("neither", "Neither suitable"),
        )
    )
    return (
        f'<article class="pair" data-pair="{pair.id}" data-a-hash="{pair.a.sha256}" '
        f'data-b-hash="{pair.b.sha256}"><h2>Comparison {pair.id[-2:]}</h2>'
        f'<div class="pair-grid">{_candidate(pair.a, "A")}{_candidate(pair.b, "B")}</div>'
        '<details class="peer-context"><summary>Equal-size candidate peers · simulation</summary>'
        f'<div class="home light">{peers}</div><div class="home dark">{peers}</div>'
        f'<div class="app-list light">{peers}</div><div class="app-list dark">{peers}</div>'
        f'</details><fieldset class="outcomes"><legend>Your observation</legend>{choices}'
        f'</fieldset><div class="evidence">{fields}</div></article>'
    )


def render_preference_markup(manifest: PreferenceManifest, digest: str) -> str:
    """Render source-free HTML with response data only in escaped attributes."""
    candidates = {
        (item.source.session, item.source.artifact): item
        for pair in manifest.pairs
        for item in (pair.a, pair.b)
    }
    peers = "".join(
        (
            f'<figure><img src="{escape(item.image_file)}" alt="Peer {number}" '
            f'width="48" height="48"><figcaption>Peer {number}</figcaption></figure>'
        )
        for number, item in enumerate(candidates.values(), 1)
    )
    references = "".join(
        "<li><strong>"
        + escape(item.label)
        + f" · {item.role}</strong><p>"
        + escape(item.observations)
        + "</p><p>Evidence: "
        + item.verification
        + f' · <a href="{escape(str(item.source_url))}" target="_blank" '
        + 'rel="noopener">Source</a></p>'
        + (
            (
                f'<img class="reference-image" src="{escape(item.image_path)}" '
                f'alt="{escape(item.label)}">'
            )
            if item.image_path is not None
            else ""
        )
        + "</li>"
        for item in manifest.references
    )
    template = Path(__file__).resolve().parents[2] / "assets/preference-gallery.template.html"
    return Template(template.read_text(encoding="utf-8")).substitute(
        brief=escape(manifest.shared_brief),
        references=references or "<li>No reference was supplied for this comparison.</li>",
        cards="".join(_pair(pair, peers) for pair in manifest.pairs),
        digest=digest,
        count=len(manifest.pairs),
        budget=manifest.ai_review_budget,
    )
