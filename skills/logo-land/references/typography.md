# Typography and symbol-plus-text layouts

Read this for combination marks, wordmarks, exact lettering or changes to typeface appearance. These are native raster-generation instructions; a saved font name is only a requested visual reference. A generated image does not prove that the named font file was used, licensed, embedded or made editable.

For lettering-first construction, natural request routing and the distinction between
readable lettermarks and integrated monograms, read [lettering.md](lettering.md).
Store letter shape and spacing decisions in `styles` and `concept`, not a new preset
or a fabricated symbol/text lockup. The layouts below arrange a separate symbol with
text; stacked letters alone remain a lettering-only arrangement.

## Choose the actual logo type

The existing `logo_type=combination` means a symbol plus the requested text in one logo. Make its arrangement explicit. A `wordmark` contains the lettering itself without an unsolicited icon. An icon-only variant omits text deliberately; it is not a complete combination mark, and cannot satisfy a request that requires a name or slogan. Record a deliberately text-free brief with empty `exact_text`, or record a variant's actual omission in its final prompt and provenance; do not imply the missing words passed exact-text review.

| Request | Intent |
|---|---|
| Symbol left of the name | `layout=horizontal`, `symbol_position=start`. |
| Symbol right of the name | `layout=horizontal`, `symbol_position=end`. |
| Symbol above the name | `layout=stacked`, `symbol_position=start`. |
| Symbol below the name | `layout=stacked`, `symbol_position=end`. |

`text_alignment` is `start`, `center` or `end` within the text block. For horizontal English/Korean lockups, start/end symbol placement means left/right; for stacked lockups it means above/below. Do not silently introduce vertical writing. Align visually by perceived symbol weight and lettering, keeping a readable gap and clear margins. A horizontal mark often suits a wide header; a stacked mark can suit a square area. Treat these as use-based choices, not extra mandatory variants.

Store `typography_style` as useful plain language, for example “rounded sans-serif appearance, medium weight, open counters, comfortable Hangul spacing.” Optional `font_reference` records a requested look, not a verified font identity. Omit it when no named font was requested or selected. The structured lockup is intent; inspect the actual image before declaring the requested layout successful.

An illustrative lockup object is:

```json
{
  "layout": "horizontal",
  "symbol_position": "start",
  "text_alignment": "start",
  "typography_style": "Rounded sans-serif appearance; medium weight; open Hangul counters",
  "font_reference": null
}
```

Keep `exact_text` and `slogan` as separate source strings, preserving every character, space, capitalization and punctuation. Do not translate, romanize, abbreviate, add a tagline or break a Hangul syllable into decorative pseudo-letters. When the user already specified arrangement and feel, generate without a second questionnaire. If layout is delegated, choose for the stated use and record the assumption.

## Give typography a brand role

Translate the intended character into visible letter choices: width, stroke weight,
terminal shape, counters and spacing rhythm. “High quality”, “premium” or a famous
font name alone leaves those choices unresolved. A calm wordmark may be distinguished
by proportion and spacing without custom cuts or a forced ligature. Keep supplied
athletic, playful, retro or sculpted treatments when they serve the actual request.

Balance a combination mark by visual mass, not identical bounding-box height. Keep
the name readable at its real header width rather than shrinking it to accommodate
an oversized emblem. For mixed Hangul/Latin, inspect the actual strings together:
syllable density, perceived stroke weight, baseline, counters, punctuation and gaps.
Matching nominal font sizes does not guarantee optical balance; do not apply a fixed
Latin/Hangul scale factor to every brand. Character-by-character correctness and
visual balance are separate checks.

If the user also requests product typography, distinguish three possible roles:

| Role | What can be delivered here |
|---|---|
| Logo lettering | Generated visual letterforms, with exact-text and appearance review. |
| Supporting display/UI/body family | A recommendation with purpose, source, available weights and script coverage checked against current official metadata. |
| Actual typesetting | Only claim a font was used when a separate workflow really loaded that font, composed the text and inspected its output. |

One family may serve multiple supporting roles; a second font is not mandatory.
Verify the license and required characters before recommending a real family for
use or redistribution. Distinguish that verified recommendation from custom logo
lettering; a raster cannot identify its generator's font, provide editable text or
prove Hangul coverage. This skill does not install/download fonts or silently switch
to a typesetting engine. Keep those limits explicit when discussing a brand guide.

## Build and revise the prompt

Include symbol subject, layout/position, relative symbol-to-text size, text alignment, exact brand string, exact slogan when supplied, typeface appearance, palette roles and background. Use quotation-delimited verbatim text, such as brand `"달빛 빵집"` and slogan `"오늘도, 따뜻하게!"`. Never turn an example into the user's brand.

For an edit, inspect and supply the exact selected image. Omitted lockup intent inherits the parent's saved intent; an explicit override replaces it for the new child. New generations may use the brief's lockup. A legacy parent's unknown intent stays unknown unless supplied; do not invent structured historical typography from appearance alone. Save the effective lockup returned by the helper and use it consistently at prompt/import.

If the chosen parent already contains revised lettering, preserve that visible text
unless the latest request replaces it. The initial brief's strings and logo type are
historical context; do not restore them during a color or geometry edit. Quote an
explicit replacement string in `changes` and save the final submitted prompt so the
next review can identify the applicable text without rewriting the original brief.

For “make it stacked,” change layout and only the necessary arrangement while preserving symbol identity, exact lettering/slogan, palette, typeface appearance and requested background. For “rounder lettering,” change the typography appearance while keeping layout/position and other identity features. Geometry-only and color-only edits retain the parent's lockup. Neither a newly active palette nor the original brief should reset a parent's revised typography.

Keep the selection reason and invariants beside the source session/artifact, following
[comparison-workflow.md](comparison-workflow.md). For example, “keep the open symbol,
exact `틈` text and green; increase only the symbol-to-text gap.” Reopen the original and
record these as quoted `changes`; inspect each invariant again on the child. A null
legacy lockup means unknown structured intent, even if the initial brief has a lockup.
It does not request deletion of visible lettering or license a new inferred layout.

Turning an icon parent into a symbol-plus-text brand logo is not an implicit lockup
edit: icon intent is inherited and conflicts with an explicit lockup. Plan that as a
separate future conversion workflow with a suitable source and explicit intent. Actual
font-file composition, editable lettering and exact symbol preservation also remain
future capabilities; a header preview does not implement them.

Horizontal and stacked outputs are separate native edits only when requested or needed for the agreed deliverables. Do not generate all combinations of layout, color and typeface by default. Keep each actual parent, final prompt and independent artifact ID; label a comparison sheet as a presentation.

## Verify text and claims

Compare the actual output against both source strings character by character, especially Hangul syllables, spaces, punctuation and Latin case. Then inspect symbol/text balance, line breaks, slogan legibility, letter counters, kerning, color placement and small-size appearance on the intended surfaces. Color sampling cannot verify typography or role placement.

If lettering is wrong, request a targeted native edit using the exact source strings and preserve the remaining identity. Do not mark exact-text review passed because the letters look plausible. If the result remains wrong, retain it as unresolved. A separately typeset wordmark can be discussed as a separate user-selected workflow, but this release does not install fonts or use Python/another engine to repair the raster.

Deliver typography as requested appearance and observed visual review, not “uses licensed font X,” editable text, outlined vectors, embedded fonts or guaranteed glyph coverage. Exact font reproduction or editable font delivery needs a separately verified workflow. No font binaries are bundled or downloaded by this skill.

## Research-backed appearance references

The [font-tools research](https://github.com/t1seo/logo-land/blob/main/docs/research/font-tools.md) records inspected primary sources, licenses and limits. Use this small shortlist when helpful; these are appearance suggestions, not font selection controls for the image tool.

| Reference | Suggested visual direction | Verified source limit |
|---|---|---|
| Noto Sans KR / Pretendard base family | Balanced modern Korean/Latin lettering | Use the Korean-capable regional/base family; Pretendard Std is Latin-oriented. |
| Noto Serif KR | Editorial or literary Korean/Latin lettering | Fine strokes still require actual-size inspection. |
| Gowun Dodum | Gentle, warm Korean/Latin lettering | Publisher metadata declares one 400 weight; do not invent a bold font variant. |
| Montserrat / Fraunces / Space Grotesk | Geometric / soft retro / technical Latin lettering | The inspected distributions do not declare Hangul; choose a Korean appearance companion for Korean strings. |
| Black Han Sans | Conditional short, heavy Hangul display | Metadata and description conflict about Latin; the description names 2,580 Korean characters. Do not use it as the mixed-script default or promise full Hangul coverage. |

These are publisher declarations, not binary glyph tests or proof of generated spelling. The research links each selected family's OFL-1.1 file; naming a family does not establish actual font-file use. For a mixed-script brief, describe each treatment separately, for example “Space Grotesk-like Latin name with balanced Pretendard-like Korean slogan,” while preserving both exact strings.

Google Fonts' catalog/CSS and metadata API, Adobe Fonts/Typekit's service/API, community font skills/MCPs, and fontTools' library are distinct surfaces. None is required here. The inspected community font suggestions do not validate individual Hangul glyphs; the download-oriented Microck MCP is excluded. Consult the research only when that distinction matters, and do not install or connect these tools as part of creating a logo.
## Reference-informed typography

Separate a wordmark's spacing and clear space from a mark or square app tile. Preserve
requested expressive lettering, outlines and depth when they serve the title. Inspect
specific counters, joins and adjacent pairs rather than preferring a generic SaaS font.
The [visual reference route](visual-references.md) carries selected observed traits;
brand names alone and claimed font identities are insufficient evidence.
