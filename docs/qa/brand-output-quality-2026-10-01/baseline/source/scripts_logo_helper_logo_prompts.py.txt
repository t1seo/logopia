"""Construction guidance for existing brand-logo types, separate from app icons."""

from __future__ import annotations

from typing import TYPE_CHECKING, assert_never

if TYPE_CHECKING:
    from logo_helper.model_base import LogoType


def logo_construction(logo_type: LogoType) -> str:  # noqa: PLR0911 - One branch per existing type.
    """Describe a new logo's construction without adding a preset or changing intent."""
    match logo_type:
        case "wordmark":
            return (
                "Make a lettering-only wordmark: the supplied exact text itself is the identity. "
                "Do not add a separate icon, mascot, badge or decorative symbol. Build original "
                "letterforms from the requested styles and concept: choose a coherent width, "
                "weight, slant, curve and terminal family, then make the identifying counter "
                "shape, spacing rhythm or readable ligature deliberate. Do not merely place "
                "ordinary typeset text beside a motif. Keep every letter recognizable; a "
                "ligature must not hide, replace or invent characters. Optical kerning may "
                "balance gaps but must preserve the supplied word spaces and reading order. "
                "For requested sculpted lettering, keep volume within the letter bodies and "
                "counters open; depth and extra tones must obey the palette and gradient policy. "
                "For requested athletic lettering, use a coherent forward slant, strong strokes "
                "and purposeful cuts without adding speed symbols. Apply these treatments only "
                "when requested by the styles or concept, not as mandatory embellishments."
            )
        case "lettermark":
            return (
                "Make a lettering-only lettermark from the supplied exact text: keep the "
                "characters distinct readable letters, not an interwoven monogram. Do not "
                "derive new initials from the brand name or expand them into a wordmark. Use "
                "a shared geometric module, stroke weight and corner family; balance counters "
                "and optical gaps. Stack letters only when requested by the concept, retaining "
                "their order and script structure; stacking letters does not add a symbol or "
                "create a symbol-plus-text lockup. Do not add an unsolicited pictogram."
            )
        case "monogram":
            return (
                "Make a lettering-only monogram by integrating the supplied exact characters "
                "with a deliberate shared stroke, interlock or readable ligature. Keep each "
                "character identifiable and its script structure intact; do not invent initials, "
                "substitute glyphs or add a separate symbol. Balance shared stroke weight and "
                "negative space so the joined silhouette survives small display sizes."
            )
        case "combination":
            return (
                "Make a combination mark with a distinct symbol and the supplied exact text. "
                "Use the concept for the symbol subject and the effective lockup, when supplied, "
                "for arrangement and typeface appearance. Balance the symbol's visual weight "
                "with the lettering, keep a clear symbol-to-text gap and open letter counters, "
                "and include a slogan only when supplied. An icon alone is not this lockup."
            )
        case "symbol":
            return (
                "Build a recognizable pictorial symbol around the supplied subject, with one "
                "identifying contour and useful negative space. Avoid unrelated stock motifs."
            )
        case "abstract":
            return (
                "Build a nonliteral abstract mark around the concept's geometric or organic "
                "gesture, with coherent weight, deliberate openings and a memorable silhouette."
            )
        case "emblem":
            return (
                "Build an emblem with the supplied lettering enclosed in a coherent badge or "
                "seal. Keep the border separate from glyphs and preserve readable interior gaps."
            )
        case "mascot":
            return (
                "Build a character mascot around the supplied subject and personality, with a "
                "compact identifiable silhouette and an intentional expression."
            )
        case _:
            assert_never(logo_type)
