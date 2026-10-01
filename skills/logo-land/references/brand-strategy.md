# Brand context that reaches the image

Use the smallest useful brand profile when starting or substantially redirecting a
brand logo. Read existing brief/context first. Reuse what the user already supplied;
infer nonessential details explicitly as assumptions. A single logo request does not
require market research, naming, a competitor audit or a full brand questionnaire.

## Choose visible decisions

Connect the product's value and audience need to a visual choice that can be observed.
“Friendly” might mean open letter counters and soft terminals; it need not mean a cute
character. “Precise” might mean disciplined spacing and restrained color roles; it
need not mean an angular industrial emblem. Ordinary lettering, pictorial, abstract
and expressive directions are all valid when the actual brief supports them.

For a new session, the optional `brief.brand_strategy` stores six nonempty descriptions
and a list of assumptions. Its exact schema and example are in
[project-files.md](project-files.md#brand-strategy). Keep each description short:

| Field | Decision it preserves |
|---|---|
| `positioning` | Who this product is for and what makes its offer relevant. |
| `audience_need` | The user need this visual identity should support. |
| `brand_promise` | The intended character or benefit, without invented market claims. |
| `distinctive_principle` | A usable shape/lettering principle and unwanted genre cues. |
| `typography` | Letter shape, weight, rhythm and required scripts; font references are appearance only. |
| `color_roles` | Which surfaces/shapes carry the main, text and optional accent colors. |
| `assumptions` | What was inferred rather than supplied or verified. |

This is proposal data, not a marketing claim, tool instruction or new approval gate.
Existing exact text, user styles, palette constraints, lockup and the selected concept
take precedence. The helper includes it in fresh brand-logo prompts. Edits preserve
the chosen parent's identity and latest requested change; historical strategy is not
automatically re-injected to reset a revised logo. App icons use their dedicated
product/concept path and do not inherit this brand-logo default.

## Compile each concept before generation

Use a few connected sentences in `concept` and the actual final prompt:

1. State the brand reason and one visible first-read choice.
2. Specify the useful shape or letter proportions, spacing and symbol/text balance.
3. Assign color placement and visual emphasis, including the actual exterior surface.
4. State the intended small use and the feature that must remain clear.

For example, a fictional personal reading app might use this **direction**, with its
exact requested name supplied separately:

> An approachable place for personal reading notes. Make the supplied name the
> identity, with modestly rounded terminals, medium strokes and roomy counters;
> keep its syllables distinct at a 160px header width. Use deep ink for the lettering
> on white; reserve a brighter accent for a separately requested application, not
> an extra logo motif. Avoid athletic cuts and heavy badge framing.

Choose different visible decisions for different brands. This example is not a
template to repeat, a mandatory monochrome scheme or proof of a usable generated
wordmark. For symbol-plus-text work, add a concrete symbol direction and optical size
relationship; for text-free work, do not invent a wordmark.

Do not rely on a strategy document that never reaches the image tool, or submit the
entire research report as a prompt. Preserve the selected exact palette and lettering.
After generation, compare those decisions to the image using
[logo-craft.md](logo-craft.md#inspect-and-refine). Revise a visible failure instead of
retroactively inventing meaning for an accidental shape.

## Applications after the master

Only create a brand board, packaging or stationery when requested. Begin with the
selected source logo and its palette/type roles. Reuse the real original in a board;
render names, HEX values and explanatory text as actual text wherever the delivery
format permits. Mark generated mockups as application previews and inspect any
rendered logo/text for drift. Keep each actual asset separate from its presentation.

Choose applications relevant to this product. Do not impose a dark premium board,
beige stationery, cinematic lighting, metallic materials or a fixed grid. Do not draw
fake golden-ratio circles or construction grids over a raster and call them the
logo's actual geometry. A board is not editable vector artwork or a set of delivered
logo variants merely because those things appear inside its image.

The context/identity approach is adapted from Brand Building Skills; application
consistency is adapted from Taste `brandkit`. Pinned sources, scope of adaptation and
MIT notices are in [THIRD_PARTY_NOTICES.md](../../../THIRD_PARTY_NOTICES.md). The
[quality research](../../../docs/research/brand-output-quality-2026-10-01.md) separates
source observations from Logopia's design judgments.
