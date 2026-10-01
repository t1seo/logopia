# Conversational color workflow

Use this reference when choosing or changing a logo's colors. The helper records intent and measures images; the host's native image tool creates or edits the logo. Command and file schemas live in [project-files.md](project-files.md).

## Translate the request once

| Entry point | Capture | Next decision |
|---|---|---|
| Automatic: “Choose warm colors for my bakery.” | Brief, tone, use and any existing constraints | Offer up to three candidates; select with a reason if choice was delegated. |
| Anchor: “Keep #247A52; make its companions warmer.” | Exact locked sRGB and colors allowed to change | Retain the anchor verbatim; revise unlocked companions. |
| Restricted: “Only black and ivory, at most two colors.” | Concrete allowed HEX values and maximum count | Explain proposed HEX for named colors; do not invent measured historical values. |
| Reference: “Use this photo's colors.” | Actual local PNG/JPEG, reference role and extraction scope | Extract colors, distinguish background dominance, then select a usable subset. |

These are composable inputs, not exclusive modes. Keep proposal source (`assistant`, `local_harmony`, `reference`, `leonardo`) separate from constraints. A photo can suggest the companion while a locked color and a count limit govern the entire candidate.

Do not repeat a complete brief or require palette approval when the user already authorized generation. When they say “choose for me,” record assistant selection and the reason, state the chosen direction briefly, and continue. When they ask “show colors first,” present candidates and wait before generation. Preserve the requested concept count: three palette options are not nine logo calls. Assign one chosen palette to each requested concept, or share a selected palette when comparing shapes.

Use roles to explain placement: primary symbol, lettering, accent, or opaque background. A role is intent to inspect, not proof of where a measured color occurred. Transparency is not a color swatch. A CSS preview surface is not part of the PNG.

## Compose and validate constraints

Public color values accept `#RGB` or `#RRGGBB`, normalize to uppercase six-digit sRGB and deduplicate. Names, CSS expressions and alpha HEX are not structured color input. Translate conversational “black” into an explicit proposal such as `#000000`, with that assumption visible.

| Field | Meaning |
|---|---|
| `locked_hex` | Preserve exact intent; each locked color needs sampled presence evidence. |
| `allowed_hex` | Optional permitted set; every member need not appear. |
| `max_colors` | Optional integer 1–8; null imposes no explicit count limit. |
| `required_hex` | Colors the user explicitly requires to appear, beyond permission alone. |
| `allow_gradients` | False by default; reject a gradient request combined with an allowed-set/count restriction. |

Each locked, allowed and required list supports at most eight normalized unique colors. Locked and required colors must belong to any allowed set. Their distinct union must fit the maximum. Reject a conflict before native calls and explain the exact competing requirements; do not choose which explicit constraint to discard. Ask only for the unresolved choice.

For “Use this photo, keep #247A52, at most two colors, choose for me,” compose:

```json
{
  "locked_hex": ["#247A52"],
  "allowed_hex": null,
  "max_colors": 2,
  "required_hex": [],
  "allow_gradients": false
}
```

Extract from the supplied reference, retain the exact anchor, and choose one compatible extracted companion. Record the actual reference ID/hash/scope, `source=reference`, assistant selection and rationale. Do not fabricate an extracted HEX when no image was read. A reference is not automatically an edit parent or permission to reproduce its design.

Count visible design colors in the declared full image or ROI, including opaque backgrounds and intentional white/black artwork. An opaque ivory surface consumes a slot in a two-color logo; do not quietly add white as a third color. Transparent exterior and CSS backgrounds are excluded. Do not count every antialiased RGB value as an additional design color, or claim automatic foreground segmentation.

## Suggest a coherent direction

Ordinary proposals prefer about three colors without imposing a strict three-color rule. Reduce that suggestion to fit the user's limits. Assign a role and short rationale to each retained swatch; omit decorative colors with no purpose. Local monochromatic, analogous and complementary proposals use OKLCH calculations, preserve locked sRGB values, and gamut-map generated companions only. An achromatic anchor uses documented companion hues 45°, 145° and 250°. Determinism applies to the same structured local inputs and calculation version, not to conversation or native image pixels.

The following are original, ordinary sRGB starting suggestions. Their names describe a possible brief, not universal industry rules, measured reference colors, Pantone equivalents, or guaranteed contrast results.

| Direction | Primary | Lettering | Accent or requested opaque surface | Why try it |
|---|---|---|---|---|
| Warm bakery | `#A84432` | `#3A2620` | `#F4E3C1` | Terracotta, dark brown and cream can support a handmade brief. |
| Quiet technology | `#2357A5` | `#142238` | `#C1DCE3` | Blue, dark ink and pale cyan can separate a precise symbol from its name. |
| Botanical | `#247A52` | `#193B2B` | `#EADFC5` | Green, deep green and sand can keep an organic mark restrained. |
| Playful studio | `#6B3FA0` | `#28213D` | `#FFC857` | Violet, ink and yellow can emphasize one expressive detail. |
| Editorial craft | `#9B473C` | `#2C2927` | `#EDE4D5` | Muted red, charcoal and paper can support a typographic treatment. |
| Black and ivory | `#000000` | `#000000` | `#F4EBDD` | Two distinct colors can support either a badge or a reversed treatment. |

The shared black roles in the last row are one color, not duplicate swatches. For transparent work, use a listed pale tone only when it belongs to visible artwork; otherwise omit it. For a locked green request, never substitute one of these palettes wholesale.

## Bind each generation and edit

Save the selected palette as an immutable version with constraints, source evidence, selection authority and rationale. Build a prompt using its effective ID/digest and save the returned session revision. Include exact HEX, role placement, forbidden extra colors/gradients where constrained, exact text and requested background. After the native call, import the exact returned PNG using the same revision and intent. If the session changed, resolve `stale_revision` and rebuild the binding; do not attach the result to a different palette silently.

For an edit, precedence is explicit palette → selected parent's palette → unknown structured intent for a legacy parent. New generations use the explicit or active palette. The original brief and the current active palette cannot reset a revised parent's colors. Geometry-only changes inherit; changing colors creates a new palette version with its real parent. Keep all old versions and artifacts.

For example, `a-v1` uses green, `a-v2` changes it to navy, and `a-v3` changes spacing only. `a-v3` retains navy even if green is active for new concepts. Selecting `a-v1` later resolves its green palette and report. Preserve parent lockup and exact lettering with the same care; see [typography.md](typography.md). Background omission is a separate legacy contract: explicitly retain a transparent variant on import rather than assuming palette/lockup inheritance also changes background behavior.

### Combined request through the helper

Use the helper invocation prefix and workspace rules in [project-files.md](project-files.md); these are its subcommands, not standalone shell programs. For an initialized revision-0 session, save a request file with `seed_hex="#247A52"` and the composed object above under `constraints`. With `--reference`, the helper binds the real extraction/source evidence; do not invent or prefill extracted colors. Existing inputs should use their current revision instead of the illustrative numbers below.

```text
reference-add --session moon-bakery --reference photo-1 --image /workspace/photo.png --revision 0
palette-propose --session moon-bakery --request-file /workspace/request.json --reference photo-1
palette-add --session moon-bakery --palette green-sand-v1 --palette-file /workspace/chosen-palette.json --revision 1
prompt --session moon-bakery --concept "Moon symbol with the exact brand name" --palette green-sand-v1 --lockup-file /workspace/lockup.json
```

The proposal returns candidates and extraction evidence without changing state. Save the selected candidate object, including truthful source/selection/rationale fields, as `chosen-palette.json`; do not pass the entire proposal envelope as a palette. `palette-add` creates the version and makes it active. The lockup file contains the object described in [typography.md](typography.md). Omit it when no structured lockup is intended.

Save the final prompt, execute the native image call, and inspect its actual output before continuing. If the returned prompt revision is 2 and no intervening mutation occurred:

```text
import --session moon-bakery --artifact a-v1 --image /actual/returned/logo.png --prompt-file /workspace/a-v1.txt --palette green-sand-v1 --lockup-file /workspace/lockup.json --background transparent --revision 2
color-gallery --session moon-bakery --artifacts a-v1 --output output/color-galleries/moon-bakery-v1
```

Import keeps the PNG even if its initial color report is mismatch/indeterminate; inspect the report separately from generation success. The gallery is read-only and uses a fresh destination. To change companions, add a new palette with `--parent-palette green-sand-v1` and use it explicitly with the actual image's `--parent` on prompt/import. For a geometry-only edit, omit the palette/lockup overrides so the chosen parent's intent resolves. `color-analyze` appends a new report using the current revision when another analysis is needed; never submit a claimed pass as evidence.

## Explain measurement and repair honestly

Intended HEX is exact palette data; a native raster is assessed with a sampled tolerance. Present intended and measured swatches separately, naming report status, source image/hash, palette, scope and limitations. Never label a palette card or a visual impression as a measured pass.

The local `logo-color-v1` report samples at most 16,384 positions. Fully transparent pixels are excluded, alpha ≥250 supplies core samples, and partial alpha is reported separately. Original PNG bytes remain unchanged; supported profile conversion happens only in analysis memory. Untagged input is explicitly assumed sRGB; unsupported profile evidence is indeterminate. A full-image histogram does not prove color roles or inspect every tiny accent.

The policy compares sampled colors in Lab D50 using ΔE00, initially ≤5. Restricted checks require ≥99% matching core coverage. A locked/required color needs ≥32 matching samples and ≥0.5% share; too little core evidence or excessive partial alpha can make a strict result indeterminate. These are product heuristics, not exact-pixel, print-proof or accessibility guarantees. Use the report's actual measurements and reasons instead of calculating a pass in conversation.

Explicit locks, allowed sets, required colors or count limits trigger strict checks. A strict mismatch blocks export with `color_mismatch`; missing/indeterminate evidence requires `color_review_required`. Visual approval cannot override these results. Auto/reference suggestions without explicit restrictions are advisory and may export with truthful limitations. Legacy palette-less artifacts remain color-unverified; do not infer old HEX values from free-text briefs. Export recomputes evidence from the verified selected PNG.

For a mismatch, use the exact previous image in at most two additional native edits for the same user request. Preserve lettering, shape, layout and background unless the user changed them. Save each attempt and inspect/report it. If both repairs fail, retain the candidates and explain the unresolved constraint; do not promise a compliant final package, silently relax thresholds, or recolor through Python. A later user decision to change intent creates a new version.

Contrast ratios apply to explicit foreground/surface pairs. Inspect on light/dark surfaces and at useful small sizes, but do not treat a blanket AA threshold as a logo certification. Logo and brand-name text is excluded from WCAG's minimum text-contrast requirement; other usage may have its own requirements. See [W3C's explanation](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).

## Guidance provenance

Brief-led color proposals and perceptual-space guidance are selectively adapted from [meodai's Color Expert](https://github.com/meodai/skill.color-expert/blob/6514810aaab15cdd0e4202af52a6afed27ed314d/SKILL.md), CC BY 4.0. The constraints, palette examples, raster policy and version workflow here are Logo Land-specific. See [THIRD_PARTY_NOTICES.md](../../../THIRD_PARTY_NOTICES.md) for credits, pinned licenses and modification scope; no upstream reference collection is bundled.
