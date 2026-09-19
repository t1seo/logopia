# App icon artwork

Use this branch when the user asks for mobile app icon artwork. A creation or editing request authorizes that operation; no second palette approval, named-model check or API-key gate is required. If the user only asks to discuss directions, stay with the discussion. Infer the product, subject and style from the conversation, and ask only for consequential missing choices. Never infer monogram lettering from a brand name.

The shared [craft workflow](logo-craft.md) connects the product to a distinguishing
construction and concrete size checks. Keep the icon contracts below, including IP
candidate defaults. A decorative word-title emblem is a brand-logo direction, not an
extra icon preset or permission to put long title text into a non-monogram icon.

## Select a direction through conversation

| Preset ID | Direction | Example |
|---|---|---|
| `ip_mascot` | Personified character with deliberate silhouette and expression | A product-specific character with one identifying feature |
| `pictogram` | Flat, recognizable symbol with a strong silhouette | Sun and cloud for weather |
| `abstract` | Few geometric forms expressing an idea | Converging shapes for focus |
| `monogram` | Exact short Unicode lettering as the main shape | `메모` for daily notes |
| `soft_3d` | Soft dimensional subject with restrained volume | A sprout for plant care |
| `pixel_art` | Deliberate block-like pixel forms | A timer with a bold pixel silhouette |

Discover the current IDs with `icon-presets`. For an unspecified IP subject, propose three product-related directions with a short reason for each, then generate two separate candidates per direction, one lower-left and one lower-right, unless the user specifies a different scope. For a specified subject, vary three treatments of that subject. Follow [ip-mascot.md](ip-mascot.md) for the adapted character recipe and attribution. Other presets default to the requested count, or the ordinary three concepts when no count is supplied.

Placement defaults to lower corners for IP and center for other presets. Honor explicit alternatives for every preset, including centered IP or off-center monograms. Explain choices in conversation; the image prompt describes the image itself. Assign colors to the main form, identifying feature and backdrop as appropriate; a fixed palette or color count is not a universal recipe. Record free-text colors in `brief.palette` and optional structured palette roles for subject/background mapping. Only explicit locks, allowed/required colors or count restrictions enable hard constraints. Explicit user colors and strict palettes take precedence over style defaults, including soft shading.

When the user requests white, keep the brief's `background: "opaque"` and describe
the color in its palette and concept as “solid white #FFFFFF filling the entire square.”
Request that color across the full square canvas, including
unoccupied areas, with no off-white tint or exterior shadow. This does not change the
requested character colors or impose white on other projects; a white gallery
card cannot substitute for the generated icon's actual background.

## Construct a non-IP concept

Before prompting each non-IP direction, connect **product benefit → named motif → one distinguishing construction → personality and a feature to preserve when small** in one concise `concept`. Use context already supplied, preserve a specified subject and count, ask only for consequential missing input, and record reasonable assumptions for the rest. For example: “Pocket Forecast gives a calm immediate weather glance: one broad cloud partially covers a sun, leaving a substantial crescent nestled into its upper-left contour; the combined silhouette and clear crescent should remain readable small.” This makes a construction choice that “friendly weather icon” leaves open. These examples describe fictional products; adapt the reasoning to the user's product without copying a sample as a universal default.

Keep the literal motif in `app_icon.subject`; put product meaning and its construction in `--concept`, later requested refinements in `--changes`, and color descriptions in `brief.palette` or existing structured palette roles. The helper quotes product, audience, use, styles and required exclusions before authoritative constraints. Explain the specific visual relationship in the concept rather than expecting a category to select a motif automatically. Use a short design specification from [logo-craft.md](logo-craft.md) and selected [reference evidence](visual-references.md).

| Preset | Make this craft decision | Compare the result concretely |
|---|---|---|
| `pictogram` | Build one compact flat emblem with a dominant filled form and a restrained supporting form, consistent curves/corners, deliberate overlap and open identifying gaps. Give the outer contour a distinguishing feature; use broad supplied color regions. | For the sun/cloud example, try one substantial sun crescent nestled into an asymmetric cloud shoulder without detached rays. Compare whether weather still reads and the silhouette is more distinctive without extra fragments. |
| `abstract` | Express the concept as one coherent nonliteral gesture with shared curvature and weight. Decide where ends meet or separate; preserve intentional openings and negative space rather than almost-touching tips. | For focus through two broad arcs, keep the strong overall presence and an open quiet center with two deliberate openings. Compare whether both arcs and openings stay distinct and suggest gathering attention; do not add a target dot, arrows or face to force the meaning. |
| `monogram` | Make the exact lettering the motif. Preserve normal script structure while balancing stroke weight, counters, joins and internal spaces, with consistent terminals and confident scale plus breathing room. Balance spacing between glyphs when multiple visible glyphs exist. | For the earlier `모` example, compare greater optical presence, an open upper counter and a balanced broad base without cramping or changing Hangul structure. For `메모`, also inspect the visible spacing. Preserve every requested code point and its order, including combining marks; code-point count does not determine visible glyph count. |
| `soft_3d` | Let one simple object's silhouette lead. Honor a specified material; otherwise choose smooth matte/satin surfaces, a near-frontal view and one broad soft light with controlled highlights. Keep the background uniform; omit extra tones or external shadows that conflict with the palette. | For the jade leaf, use softly asymmetric lobes and one shallow fold, with no botanical pores/veins, wet gloss, extra stem or external cast/contact shadow. Compare whether the shape and fold communicate gentle care before the lighting draws attention, including at small size. |
| `pixel_art` | Choose one consistent coarse square module, matching structural thickness, repeated steps and broad connected color clusters. Keep essential gaps visible; avoid mixed block scales, smoothing, gradients, dithering and stray blocks by default. | For the hourglass, use matching caps/frame and one connected upper sand mass with an empty lower chamber. Compare silhouette, staircase rhythm and sand placement; record remaining blur or grid inconsistency rather than claiming an integer-perfect grid or repairing the original. |

Style defaults yield to explicit subject, concept and changes, and to authoritative lettering, placement and palette constraints. Preserve exact supplied Unicode without normalization, initials inference or script conversion; never install fonts or claim an exact font from generated lettering. Honor explicit corner placement even for a monogram. User colors and strict palette/gradient rules override material and shading defaults; do not infer HEX locks, color counts or a universal canvas-fill percentage from these recipes.

Inspect each requested original at native size and at 32/48/64/128px using identical masks and surrounding surfaces when comparing. Describe the actual shape, gaps, letter structure, material or clusters that improved or remain weak; a result may be improved, mixed, unchanged or worse. Keep saved images paired with their actual old prompts when guidance changes. This is a creative comparison, not an aesthetic guarantee, exact-color approval, platform package or store-readiness claim; preserve every returned original without automatic artistic retries.

## JSON contract

The [complete brief example](../assets/app-icon.example.json) uses exact Korean lettering. Its `app_icon` field, or a standalone `--app-icon-file`, has this shape:

```json
{
  "preset": "monogram",
  "subject": "Rounded Korean lettering for a daily notes companion",
  "placement": "center",
  "text": "메모"
}
```

`AppIconIntent` is frozen and rejects extra fields and type coercion. `preset`, `subject` and `placement` are required and cannot be null. `subject` is 1–500 characters and cannot be whitespace-only. `placement` is exactly `center`, `lower_left` or `lower_right`. `text` defaults to null: monograms require 1–8 Unicode code points without whitespace or control characters; all other presets require null. Preserve Unicode without normalization. Code points are not the same as displayed glyphs; a combining sequence can consume more than one position.

Use `preset`, not an invented `style` key. Describe icon styling through its preset, subject and concept. Product styles and required exclusions reach the image prompt as quoted context. An ordinary concept-artwork brief requires `background: "opaque"`, `slogan: ""` and `lockup: null`; explicit [asset intent](asset-intent.md) provides role-specific alpha and size policies. Its `exact_text` is empty except for a monogram, where it equals `app_icon.text` exactly. No exact-font, editable-text or font-file usage is established by generated lettering.

## Runnable prompt example

Run from the repository root after `uv sync --locked`. This creates a fresh temporary example workspace and prints the actual helper response. Keep its path if continuing with native generation; remove only this example workspace when finished. These commands do not generate an image.

```sh
LOGO_REPO="$PWD"
LOGO_ICON_WORKSPACE="$(mktemp -d "${TMPDIR:-/tmp}/logo-land-icon-example.XXXXXX")"
ll_icon() {
  uv run --locked --project "$LOGO_REPO" python \
    "$LOGO_REPO/skills/logo-land/scripts/logo_project.py" \
    --workspace "$LOGO_ICON_WORKSPACE" "$@"
}
ll_icon icon-presets
ll_icon init --session icon-demo \
  --brief "$LOGO_REPO/skills/logo-land/assets/app-icon.example.json"
uv run --locked --project "$LOGO_REPO" python -c \
  'from pathlib import Path; import json,sys; print(json.dumps(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["app_icon"], ensure_ascii=False, indent=2))' \
  "$LOGO_REPO/skills/logo-land/assets/app-icon.example.json" \
  > "$LOGO_ICON_WORKSPACE/icon.json"
ll_icon prompt --session icon-demo --concept 'Memo Garden makes daily notes feel approachable: use only the exact 메모 lettering as the motif, with one rounded corner family, open counters and balanced visible glyph spacing; keep the welcoming letter structure clear at small size.' \
  --app-icon-file "$LOGO_ICON_WORKSPACE/icon.json" \
  > "$LOGO_ICON_WORKSPACE/prompt.json"
cat "$LOGO_ICON_WORKSPACE/prompt.json"
uv run --locked --project "$LOGO_REPO" python -c \
  'from pathlib import Path; import json,sys; print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["prompt"], end="")' \
  "$LOGO_ICON_WORKSPACE/prompt.json" > "$LOGO_ICON_WORKSPACE/icon-demo.txt"
```

Check that the response resolves `app_icon` to the Korean monogram above, `requested_background` to `opaque`, and `revision` to 0 in this untouched example. Use its exact final prompt for the native call and preserve that revision/intent for import. Put arbitrary quotes, shell metacharacters and Unicode in UTF-8 JSON/text files; use quoted heredocs such as `<<'JSON'` or an argv-based tool to create them. Do not splice user text into shell commands. JSON strings must escape literal newlines and double quotes correctly.

The next commands require an actual returned PNG, not a bundled output. Replace the placeholder with the path identified by that exact native call. If another mutation occurred, reconcile the saved generation revision before import; do not silently relabel the result with a newer revision.

```sh
LOGO_ICON_PNG='/replace/with/actual/native-tool-output.png'
ll_icon import --session icon-demo --artifact monogram --image "$LOGO_ICON_PNG" \
  --prompt-file "$LOGO_ICON_WORKSPACE/icon-demo.txt" \
  --app-icon-file "$LOGO_ICON_WORKSPACE/icon.json" --revision 0
ll_icon icon-gallery --session icon-demo --artifacts monogram \
  --output output/icon-gallery-demo
```

## Effective intent and edits

For a chosen candidate, retain its source session/artifact and the identifying feature
that made it suitable. Use the [comparison workflow](comparison-workflow.md) to save
reason, preserve/change notes and observations without adding icon fields. Reopen the
original, carry those notes into quoted `changes`, and compare the resulting child
against the same feature at the intended size.

Apply the existing construction guidance with specific observations. For an abstract
icon, name the intended opening or connection: does the gap remain visibly open at
32px, do near-touching tips make an accidental spike, and does the gesture still relate
to the product? For soft 3D, identify which contour makes the subject recognizable:
does a leaf still read as a leaf rather than a heart, and does a fold or highlight obscure
that clue when small? If recognition is ambiguous, say what you saw and suggest one
targeted requested change while keeping the successful silhouette, palette or material.
These are practical review questions, not a new score, a guaranteed style improvement
or permission for automatic artistic retries. IP keeps its default six independent calls;
geometry, expression and color defaults now follow the product and explicit user intent.

Both `prompt` and `import` accept a complete `--app-icon-file`; they use the same parse boundary. Intent precedence is the explicit file, then the parent's `app_icon` (including null), then the brief when there is no parent. A legacy parent with null intent does not become an icon merely because the brief has icon intent. Top-level null is not a complete override file, and existing artifact intent cannot be rebound.

An explicit icon file on a legacy brand session declares an icon transformation: suppress historical brand lettering, slogan and lockup in the rendered result while preserving history. Supplying an icon together with an explicit `--lockup-file` fails `intent_conflict` before mutation. Legacy concept artwork and authored backgrounds require opaque intent; foreground/monochrome and Play listing follow [asset-specific policy](asset-intent.md). Alpha-capable child imports inherit the parent background unless explicitly overridden. `PromptResult.requested_background` reflects the effective role and parent; `parent_requested_background` describes the historical parent.

Save the effective palette, icon intent, parent and revision with the final prompt. If a palette or intent was overridden for generation, pass that same override on import. Prompt construction checks the complete 20,000-character limit before any native call. Descriptive inputs are quoted and trusted constraints follow them; this is prompt hygiene, not proof of model-level injection immunity.

## Native candidates and comparison

For ordinary concept artwork, request one full-bleed square raster with square outer corners and a complete solid background, approximately 1536 × 1536 in prompt text. Explicit layer and store-listing requests use [asset intent](asset-intent.md). Preserve actual returned dimensions and original PNG bytes, even when dimensions, placement or style differ. Never resize, replace the background, build a contact sheet as the generation output, silently reuse another candidate as a reference in a fresh independent draw, or repeat a call automatically to improve its appearance.

Each candidate needs its own helper session when generated in parallel. Record a durable per-call receipt with planned/running/returned/failed/unknown state, exact prompt/hash, session/artifact IDs, actual tool/provider, returned paths/hashes and dimensions. If the runtime does not expose the model, record it as unreported. Resume the same receipt after an interruption; never reset an unknown attempt or scan for the newest file. A failed native call is a failure record, not a generated image. Read [native-image.md](native-image.md) before calling the real tool.

`icon-gallery --session ID --artifacts comma-separated-IDs --output relative-directory` publishes explicitly selected icon originals, their exact prompt text, intent, actual dimensions and a machine-readable manifest. Every chosen original is included regardless of selection, visual review, color conformance or export status. It verifies original hashes without mutating session state. Empty/duplicate/non-icon selections, existing destinations, reserved paths, escaping paths and symlink paths are rejected; owned staging is rolled back on failure.

Open the gallery locally, including from a file URL. Square/rounded/circle CSS previews, 32/48/64/128px display sizes, light/dark surfaces and preset filtering/reset do not alter image bytes. Masks are illustrative, images use contain behavior, and original downloads retain their pixels. The page works without network requests and does not rank candidates or show default alpha/color PASS badges.

For a method-blind, counterbalanced A/B decision, use [preference-gallery](preference-review.md). It supports A/B/tie/neither and evidence-bound AI or user responses without approving QA, selecting an artifact or exporting.

For parallel source sessions, use `compare-gallery --selection-file ... --output ...`
with explicit session/artifact pairs and current revisions. It also accepts brand-logo
originals. The [selection file example](comparison-workflow.md#comparison-input)
records each candidate's reason, keep/change notes and observation. Its illustrative
home-screen/header/favicon contexts and 16/32/64/128px views help inspect intended
uses; a square preview is not a newly produced platform icon. Copying a card preserves
its source identity as text and does not select, approve or trigger an edit.

Optional approved export still requires selection, actual visual review, background and integrity checks, and fresh strict-color evidence. No style relaxes those gates. Its three ZIP files remain `logo.png`, `manifest.json` and `brand-guide.md`, with selected `app_icon` metadata and artwork limitations. The raster does not establish an Icon Composer document, Android adaptive foreground/background layers, OS-native assets, an app build or store acceptance. Platform packaging requires separate work.

The session and export manifest remain schema 2 with optional icon snapshots. The v1 parser and byte-exact backup behavior remain unchanged. Older readers are not promised to read icon-bearing v2 files; keep originals and backups rather than editing schema numbers to downgrade.

## Repository demonstration status

The repository includes `docs/app-icons/index.html`, titled “Small canvas, big character.”, with eleven independently generated native originals: `ip-a1`, `ip-a2`, `ip-b1`, `ip-b2`, `ip-c1`, `ip-c2`, `pictogram`, `abstract`, `monogram`, `soft-3d`, `pixel-art`. Open the page locally after cloning the repository; these demonstration assets are separate from the installed skill.

The six IP candidates pair owl, capybara and puppy reading companions with requested left/right placements. The other fictional products demonstrate weather, focus, Korean notes with the exact requested syllable `모`, plant care and a timer. Every returned image is 1254 × 1254, preserving the actual output despite the approximately 1536-square prompt request. Extra details, shading and other artistic variation remain unchanged.

Each original has one native call receipt under `docs/qa/app-icons/native/`. The aggregate `docs/qa/app-icons/native-samples.json` and `.md` record original hashes, exact prompts, intent and receipt lineage. The separate `icon-collection` catalog uses normal imports of those same bytes with explicit matching icon intent and opaque background. Its import revisions 0–10 are catalog operations; all native generation revisions remain 0 in their source sessions. Catalog copies do not represent additional native generations.

The gallery contains all eleven original PNGs and prompt downloads across all six presets. Comparison is independent of selection, visual approval, strict-color conformance or approved export. Earlier logo/color galleries and failed color release gates retain their own history; the 0.5.0 source update remains unreleased, the older 0.4.0 draft remains unpublished and the published release remains 0.3.1.
