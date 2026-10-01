# From a brief to a recognizable mark

Use this guidance to develop or refine a logo, including expressive lettering and
app icon artwork. Quality means a design fits its purpose and its visible details
support that purpose. It is not synonymous with minimalism, a fixed color count, a
particular font or a numerical aesthetic score. The [primary-source research](../../../docs/research/logo-craft.md)
explains the observations behind this workflow; the decisions below are Logopia's
practical synthesis, not a certification of generated results.

## Make the idea specific

Use the brief already available. In `concept`, connect **what matters to the audience
→ a visual idea → a deliberate shape or lettering choice → the feature that must survive at
the intended size**. Reuse `use_cases`, `assumptions` and any saved
[brand strategy](brand-strategy.md); do not force a questionnaire. A bakery need not have wheat, a finance product need not have
an arrow, and a creation tool need not have a sparkle.

For example, a reading service whose users want an approachable place to keep personal
notes might use a quietly rounded wordmark with roomy counters and a dark, readable
text color. Describe the actual letter proportions and spacing that deliver that
intention. It does not need a book, a quotation mark fused into an initial, or a hidden
symbol. This is a proposed direction, not a tested brand claim.

When multiple concepts are requested, vary the underlying idea or construction:
letter rhythm versus a fitted joint versus an enclosing gesture, where those types
fit the brief. For lettering-only requests, vary letter skeleton, proportions or
counter treatment instead of adding symbols. Keep the requested count. A single
specified direction can go directly to one image; IP retains its dedicated direction
and candidate defaults in [ip-mascot.md](ip-mascot.md).

## Design the relationships

| Decision | Put a concrete instruction in the concept or final prompt |
|---|---|
| Recognizable construction | Name the first-read silhouette or letter rhythm. A cut, overlap or joint is useful only when it improves the idea; a coherent contour can be distinctive without an added gimmick. |
| Shape family | Choose how curves, corners, terminals, stroke weights and gaps relate. A geometric module is a starting point; optically balanced spacing can differ from equal measurements. |
| Lettering | Preserve the exact string. Identify counters, adjacent letter pairs and reading order that need room; intentional irregularity should look deliberate and remain readable. |
| Hierarchy | Decide what is read first and what supports it. Give a title, symbol and optional slogan different visual roles; do not add text to fill a gap. |
| Color roles | Assign dominant shape, lettering, accent, separator and background where needed. Judge neighboring colors together and against the actual surface, not only as isolated swatches. |
| Intended application | State a plausible display size and context. A rich title at 360px wide and an icon at 32px solve different problems; a title is not automatically its own favicon. |

Use [color-workflow.md](color-workflow.md) for real locks, restricted sets and color
evidence. Do not invent a maximum count, automatic monochrome requirement or universal
contrast ratio for logos. A multicolor title can use color as part of its identity;
still inspect whether important letter boundaries and counters remain distinguishable.
Shading, outlines and pattern should have defined roles instead of competing equally.

Review the helper's proposed prompt against this intent before the native call. Resolve
generic guidance in favor of the actual brief: a color-dependent playful title is not
silently flattened into a one-color corporate mark. Save the exact final prompt used,
including any clarification. Keep a candidate's specification compact; repeated style
adjectives, incompatible construction rules and a long list of motifs dilute it.

For an ordinary new brand logo with no supplied surface, transparency, background role
or expressive treatment that requires otherwise, choose a flat master on white when
white fits the color constraints. State
**opaque #FFFFFF across the exterior canvas**, including unoccupied corners and margins;
no cream tint, paper texture,
backdrop gradient, ambient vignette or exterior cast shadow. A colored title backplate
is foreground artwork when requested, not the canvas background. Before generation,
choose a few regions expected to remain empty based on this composition; corner IP
characters may leave the opposite upper area empty rather than all four corners.
An explicit colored/transparent surface and strict color limits always take precedence;
do not introduce white as an extra forbidden color. This master-logo default does not
change app-icon backgrounds or requested game-title/material treatments.

For ordinary IP concept artwork, keep `background: "opaque"` in structured metadata
and describe a requested white canvas as “solid white #FFFFFF filling the entire square.”
Explicit authored foreground/background requests follow [asset-intent.md](asset-intent.md)
instead; character styling must not override layer alpha requirements. See
[ip-mascot.md](ip-mascot.md) for product-specific character construction.

## Use references analytically

Use [visual-references.md](visual-references.md) to bind these observations to imported
pixels and the actual supported image-tool inputs. Reference notes alone are not conditioning.
Keep a short specification in the concept: first-read shape; construction decisions;
color/background roles; material/depth when requested; selected reference traits and exclusions;
small-size invariant; difference from other directions; concrete failure risk.
Do not combine every possible style in one direction, require meaningless cuts,
or default to stars, orbits, infinity loops or category-specific cute animals.

Inspect the actual supplied image before describing it. Separate observed features
from your interpretation of their effect: “wide counters and alternating letter
rotations” is observable; “welcoming playfulness” is a proposed reading. Identify
which broad attributes the user wants: proportions, rhythm, outline hierarchy,
material, color relationships or layout. If the reference cannot be inspected, say
so rather than inventing its details.

Create new geometry for the user's exact text and product. Do not import the source's
brand words, mascot-specific glyph substitutions or decorative assets by accident.
The reference's popularity is not evidence that every feature suits the new brief.
For outlined game titles and decorated backplates, use [game-title-logos.md](game-title-logos.md).

## Inspect and refine

Open the returned original and display it at the intended use size without rewriting
its bytes. Record the displayed size in existing review `notes`. For icons, retain the
32/48/64/128px diagnostic comparison in [app-icons.md](app-icons.md); for a wordmark, use its
actual header width rather than requiring its full name to work at icon size.

- **Meaning and distinction:** describe the feature actually visible and how it
  relates to the concept. “The fitted joint remains visible at 96px” is an observation;
  “customers will remember it” requires evidence this workflow does not provide.
  Name a mismatch such as aggressive industrial geometry for an approachable reading
  service; do not excuse it with an invented brand story after generation.
- **Optics:** inspect open counters, crowded letter pairs, joins, stroke weight,
  overshoot, visual centering and clear space. A mathematically even gap can look
  uneven between a diagonal and a round letter. Name the affected pair or region.
- **Hierarchy and color:** inspect the dominant shape before the effects. Note a
  swallowed gap, low-separation adjacent colors or a highlight hiding a stroke.
  Distinguish sampled palette evidence from visual role placement.
  Check whether one over-saturated accent or a large colored surface overwhelms the
  intended hierarchy, even when the sampled HEX values conform.
- **Use and background:** inspect reading order and recognizable shape small; check
  the requested opaque surface or actual transparency. White pixel samples from
  predeclared empty regions supplement full-image inspection; they do not prove that
  every background pixel is white or that a foreground segmentation exists.

For a required failure, request a targeted native edit of the exact parent: name the
defect, the desired change and the features to retain. “Open the first O counter and
separate the R/I pair; keep the exact name, outline hierarchy, palette and baseline”
is actionable. Save the child separately and compare the same regions at the same
size. Preserve unresolved results and report the visible limitation. Do not reroll
automatically for subjective preference; keep the existing retry limits for color
failures. Selection, creative preference and verified export remain distinct.

A one-color version or small-size alternate is a separate native-generated variant
when needed, not a claim inferred from the color master. A deliverable contains only
the variants actually generated and inspected. Follow [delivery-checks.md](delivery-checks.md)
for truthful booleans, file facts and export evidence.
