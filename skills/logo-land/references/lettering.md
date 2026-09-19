# Lettering-first logos

Expressive first letters, a selective change of slant, wide counters and volumetric
lettering are optional construction choices, not mandatory 2026 effects. Preserve the
full supplied string and Hangul blocks. Never turn a name into initials to fit an app
tile; an explicitly requested small companion mark is a separate design and call.

Read this when the requested identity is made from words or letters. Use the existing
eight [logo types](logo-directions.md); no lettering preset, font installation or extra
schema is needed. The helper supplies construction guidance for the selected type;
the assistant turns the user's language and references into `styles` and a concrete
`concept`. Natural-language routing happens in conversation, not through a keyword
classifier in the Python helper.

## Route the actual request

| User language and supplied text | Route and construction |
|---|---|
| “글자 로고”, “텍스트 로고”, “레터링 로고”, “글자만”, “워드마크”, “text logo”, “custom lettering”, “name only” with a brand name | `wordmark`: the full exact name is the identity; no separate pictogram, mascot or badge. |
| “이니셜 NR을 위아래로”, “stack these letters”, “readable initials” | `lettermark`: exact supplied initials remain distinct readable letters; stacking describes their arrangement. |
| “두 이니셜의 획을 합쳐”, “interlock the initials”, “woven monogram” | `monogram`: integrate the exact characters through a shared stroke or interlock while keeping each identifiable. |
| “심볼 옆에 이름”, “symbol above the name”, “icon plus text” | `combination`: a separate symbol and exact lettering; use the existing symbol/text `lockup`. |
| “통통하고 말랑한 다색 글자”, “chunky sculpted lettering”, “앞으로 기울어진 스포츠 글자”, “athletic wordmark” | Style and construction of the requested text type, normally `wordmark`; these are not new types. |
| “게임 타이틀”, “포코피아처럼”, “outlined game title” with a shared decorative backplate | `emblem`; read [game-title-logos.md](game-title-logos.md). Without a plate, lettering stays `wordmark`; a separate motif plus lettering uses `combination`. |

Infer from the supplied string and intended structure, not a single word: “letter logo”
alone may mean a name, readable initials or integrated initials. Ask for the exact text
when absent, and clarify initials only if they cannot be determined from the request.
Do not shorten a provided name or invent an acronym. A one-letter logo can be a
lettermark; a short word is not automatically a monogram. Confirmed app-icon artwork
uses [app-icons.md](app-icons.md), including its separate Unicode monogram constraints.
Do not impose the app-icon text limit, full-bleed square or solid background on brand
lettering.

For a lettering-only brief, leave `lockup` null. A line break or stacked initials do
not create a symbol-plus-text lockup. Do not put the brand name into `font_reference`.
If a resumed artifact has a real symbol/text lockup, honor that selected parent instead
of reclassifying it from the initial brief. Missing historical metadata remains unknown.

## Make a construction decision

Use `exact_text` for the literal rendering string, `styles` for the requested appearance,
and `concept` for what will make these particular letters recognizable. Keep `slogan`
empty unless the user supplied one. A useful concept connects the brand's personality
or use to letter construction and names the feature to preserve in later edits:

- **Skeleton and silhouette:** wide or narrow proportions, stroke weight, forward
  slant, baseline and rhythm. Choose a consistent curve and terminal family.
- **Counters and spacing:** shape and size of internal openings, spacing between
  adjacent letters, word-space rhythm and the balance of filled area to negative space.
  Optical kerning changes drawn gaps, not the supplied literal spaces.
- **Signature feature:** one purposeful terminal, cut, shared stroke or legible
  ligature. It must belong to the letters and preserve their identities; do not turn a
  required glyph into an unrelated object or add ornaments to make generic type unique.

Not every logo needs a ligature or a cut. When several concepts are requested, vary
the silhouette and at least one internal construction decision, such as width plus
counter shape or slant plus spacing. Respect the requested count. Do not multiply
candidates into a matrix of colors, effects and layouts.

## Three reference-led directions

For a title with keylines, facets and a shared backplate, use the separate
[game-title recipe](game-title-logos.md). The lettering-only directions below do not
add a badge. Apply the [craft workflow](logo-craft.md) to connect the visual reference
to this brand's construction and intended use rather than copying its source words.

Extract broad visual traits from the actual supplied reference. Create new lettering
for the user's exact text; do not copy the reference's brand words, trace its letter
outlines, reproduce its distinctive symbols or invent a relationship to its brand.
The example strings below illustrate user-provided text; never substitute them into
another brief.

| Direction | Actionable construction | Palette and readability |
|---|---|---|
| Playful multicolor sculpted wordmark | Start with chunky rounded letter bodies and broad strokes; make the counters generously open, soften terminals, and establish a deliberate bouncy baseline or alternating width. Keep shallow rounded volume inside the letter bodies. A carefully fitted neighboring pair can be the signature feature. | Apply the supplied colors to purposeful letter groups or faces. Keep each letter separable without relying on color changes; highlights and shading must fit the effective palette and gradient policy. No extra character, scene, backing badge or decorative prop. |
| Strong forward-slanted athletic wordmark | Use a coherent forward axis across stems, counters and terminal cuts, a compact rhythm and strong strokes. Choose where an angular opening or one readable join adds momentum. Give slanted end letters enough optical margin so they do not look clipped. | Keep counters open and adjacent strokes distinct. Speed comes from the letters' geometry; do not add swooshes, wings, motion stripes or an underline unless requested. Do not copy a known sports wordmark. |
| Minimal geometric stacked lettermark | Keep supplied initials separately readable on a shared geometric module. Repeat stroke thickness, corner radii and counter proportions; optically balance the rows and their gap, retaining the requested reading order. | Check that the letters remain distinct in a single-color silhouette at the intended size. If the user wants fused or shared strokes instead, record `monogram` and make that integration explicit. Stacking never supplies missing initials. |

For example, a complete new brief can keep `logo_type="wordmark"`,
`exact_text="momi"`, `styles=["playful", "chunky", "sculpted"]`, and a concept such as
“A welcoming children's craft brand; broad soft strokes, open circular counters and
compact rounded joins, with a gentle baseline bounce; the lettering itself is the
whole mark, in the selected multicolor palette.” This is enough for the helper; it
does not need a new `lettering_style` or preset ID.

An athletic concept for exact `RIVET` could use “a strong forward axis, narrow open
counters, squared diagonal terminals and a close but readable IV pair for a training
brand.” A stacked `NR` lettermark could use “N above R, equal visual weight on a square
module, softly squared counters and a clear inter-row gap.” Supply the original name,
brand context and requested colors in the real brief; these examples make no claim
about generated quality or font identity.

When an effect would require forbidden extra colors or gradients, preserve its
geometric idea within the allowed palette, and explain the material limitation if it
matters. A one-color request stays one-color; a multicolor request stays multicolor.
Do not add a strict palette where the user delegated ordinary color selection.

## Exact text and revisions

Keep every source character, case, punctuation and space in `exact_text` and `slogan`.
Do not normalize, translate, romanize, capitalize or collapse repeated spaces. Preserve
Hangul syllable blocks and their vowel/consonant structure, including final consonants;
do not replace them with decorative pseudo-letters. Custom connections must leave each
required character readable. Use line breaks only when requested or clearly delegated
by the layout; keep reading order and do not silently replace word spaces with stacking.

Use the exact selected parent as the edit input. Put the requested changes and keep
notes in `changes`, for example “Keep exact `너울  상점`, the rounded terminal family,
colors and baseline; enlarge only the closed counters.” A color-only edit must not
reset a revised word, spacing, ligature, slant or arrangement to the original brief.
Explicit replacement text in the latest request wins; otherwise preserve the parent's
visible text. Save that final prompt with the actual child artifact and revision.
The initial brief does not record every later text change and is historical context,
not permission to restore the old string. Follow [typography.md](typography.md) for
symbol/text lockup inheritance and typeface-appearance edits.

## Inspect the lettering

1. Compare the actual image to the applicable exact strings character by character,
   including repeated spaces, Latin case, punctuation and Hangul components. Inspect
   each glyph, connected pair and reading order; plausible lettering is not enough.
2. At large size and the intended small display size, inspect counters, joins, kerning,
   stroke consistency, edge margins and row spacing. A wide wordmark need not work as
   a favicon unless that use was requested. Check italic overhang and 3D shadows for
   clipping; surface gloss must not conceal the letters.
3. Inspect how color, outlines and letter geometry separate adjoining forms. Record
   color dependence or merged gaps at the intended size; a deliberately multicolor
   title need not become a one-color mark unless that use is required. A silhouette
   assessment is not a verified monochrome deliverable. If a one-color proof is requested, make a separate
   native edit with its own parent and artifact ID, inspect it, and preserve the color
   master. Do not recolor the PNG with a script or claim an unmade variant passed.
4. Compare parent and child against the keep/change notes. Record actual text, spacing,
   shape and palette drift in the existing visual-review `notes`; failed required
   spelling or unreadable glyphs must not pass `text_correct` or `small_size_ok`.

Correct failed lettering with a targeted native edit, then inspect again. If it remains
wrong, preserve the unresolved result and explain the specific error. Do not silently
switch to a font-compositing workflow or promise vector paths, editable text, font-file
use, licensing or exact-font reproduction from generated raster artwork.
