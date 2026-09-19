# Project files and helper

Resolve the plugin root from the installed skill location (two directories above `SKILL.md`). `--workspace` is the user's project directory; it is independent of the plugin location. Python 3.12+, uv, Pydantic v2, Pillow and the pinned ColorAide dependency are needed for the helper. The host's native image tool needs no separate API key from this plugin.

Invoke the helper with an argv-based shell tool or correctly quoted arguments. Put arbitrary user text in JSON/text files, not interpolated shell command strings. Commands emit JSON. Read errors and exit codes before proceeding.

The workspace must already exist. Session, artifact, palette and reference IDs match `^[a-z0-9][a-z0-9_-]{0,63}$`; brand text can contain Unicode. Successful commands emit JSON on stdout. Known file/schema/domain errors emit JSON on stderr with exit 1; invalid CLI arguments use Typer's exit 2. `--help` is human-readable text. Inputs have a 64 MiB file limit and a 40-million-pixel image limit. Logo artifacts must be static PNG; palette references may be static PNG or JPEG.

The first invocation may download dependencies. Direct execution of the `.py` script through uv uses its PEP 723 environment with pinned direct dependencies, separately from the project's lockfile. To run the full locked project environment, use `uv run --locked --project /absolute/path/to/logo-land python /absolute/path/to/logo-land/skills/logo-land/scripts/logo_project.py ...`.

After preparing the dependency cache, local palette math, reference extraction and reports need no network service. This is not a cold-cache offline-install promise. A copied skill can use `uv run /absolute/path/to/copied/skills/logo-land/scripts/logo_project.py --workspace /absolute/path/to/workspace list` without a checkout. Missing ColorAide is reported as `color_engine_unavailable`; no command installs an MCP, launches `npx`, fetches a remote reference URL or calls an image API. Optional providers are described in [color-providers.md](color-providers.md).

```sh
uv run --project /absolute/path/to/logo-land /absolute/path/to/logo-land/skills/logo-land/scripts/logo_project.py --workspace /absolute/path/to/workspace list
```

The long prefix above is omitted from the command examples below. Never run the bare subcommands as standalone shell commands.

## Brief

Required string fields: `brand_name`, `exact_text`, `industry`, `audience`. Set `exact_text` to an empty string for a deliberately text-free symbol. Preserve user text verbatim.

Optional fields:

| Field | Type / default |
|---|---|
| `slogan` | string, empty |
| `logo_type` | wordmark / lettermark / monogram / symbol / abstract / combination / emblem / mascot; combination |
| `styles`, `palette`, `forbidden`, `use_cases`, `assumptions` | arrays of strings, empty |
| `background` | opaque / transparent; opaque |
| `concept_count` | integer, 3 |
| `lockup` | `LockupIntent` object or null; null |
| `app_icon` | `AppIconIntent` object or null; null |

Use [brief.example.json](../assets/brief.example.json) as a starting shape. Do not treat its fictional brand as the user's brand. For an unknown audience or other nonessential field, record a reasonable assumption rather than claiming the user supplied it.

The brief's free-text `palette` is historical intent, not a structured restriction or a measured color report. Save enforceable intent with `palette-add`. `lockup` uses the same object accepted by `--lockup-file` below. The exact text and slogan remain verbatim strings; do not encode replacement lettering in the font reference.

## App icon intent and commands

Read [app-icons.md](app-icons.md) for the complete schema, six preset IDs, runnable `icon-presets` → `init` → `prompt` example and original comparison gallery. The [icon brief example](../assets/app-icon.example.json) renders the exact Unicode monogram `메모`. Legacy/concept icon briefs require opaque background, empty slogan and null lockup; explicit [asset intent](asset-intent.md) selects role-specific alpha policies; only monograms have nonempty exact text. A standalone `--app-icon-file` contains the complete `app_icon` object, not the whole brief or a `{ "app_icon": ... }` wrapper.

Both `prompt` and `import` accept `--app-icon-file`. Precedence is explicit file, then parent's icon intent including null, then brief intent when no parent exists. An explicit file can transform a legacy brand session, suppressing its historical lettering/slogan/lockup in rendering without changing saved history. Explicit icon plus lockup fails `intent_conflict` before mutation. Transparent input conflicts with legacy/concept and opaque background roles; authored foreground/monochrome and Play listing use their separate asset policies. Alpha-capable icon children inherit the parent background unless explicitly overridden; legacy/concept imports remain opaque; non-icon omission retains the background behavior documented below. Prompt responses expose resolved `app_icon` and `requested_background`; the historical `parent_requested_background` stays unchanged. Save the exact returned revision and all effective intent for import.

`icon-presets` emits JSON discovery. `icon-gallery --session ID --artifacts a1,a2 --output output/icon-comparison` publishes only explicitly selected icon artifacts, including their unchanged original PNGs, exact prompts, intent and actual dimensions. It accepts unapproved or color-mismatched originals without changing state; it is independent of approved export. Use a new workspace-relative destination. See [app-icons.md](app-icons.md) for rejected paths, controls and limitations.

## Runnable color examples

For read-only comparison across sessions, use
`compare-gallery --selection-file /workspace/selection.json --output output/comparison-1`.
The [comparison workflow](comparison-workflow.md#comparison-input) defines the explicit
session/revision/artifact entries and optional decision text. Save this input in the
workspace so a later conversation can recover the source and reason. The command
does not add session fields, select an artifact or approve an export.

Run these POSIX-shell examples from the repository root after `uv sync --locked`. They create a separate demonstration workspace and use its current JSON responses for revisions. Reusing the same directory/session IDs will fail safely; choose a fresh directory for another run. No command in this section generates an image.

```sh
LOGO_REPO="$PWD"
LOGO_WORKSPACE="$LOGO_REPO/output/color-doc-example"
mkdir -p "$LOGO_WORKSPACE"
ll() {
  uv run --locked --project "$LOGO_REPO" python \
    "$LOGO_REPO/skills/logo-land/scripts/logo_project.py" \
    --workspace "$LOGO_WORKSPACE" "$@"
}
ll init --session color-demo --brief "$LOGO_REPO/skills/logo-land/assets/brief.example.json"
ll --help
```

### Four entry points and combined restrictions

The following files are `PaletteRequest` objects. The automatic example is a local-harmony proposal seeded with a deliberate warm direction; it is not a measured bakery palette. No restrictions makes the proposal advisory. `selected_by` records who chose it.

```sh
cat > "$LOGO_WORKSPACE/auto.json" <<'JSON'
{
  "seed_hex": "#A84432",
  "selected_by": "assistant",
  "rationale": "A warm terracotta starting point for this fictional bakery brief."
}
JSON
cat > "$LOGO_WORKSPACE/anchor.json" <<'JSON'
{
  "seed_hex": "#247A52",
  "constraints": {"locked_hex": ["#247A52"]},
  "selected_by": "assistant"
}
JSON
cat > "$LOGO_WORKSPACE/restricted.json" <<'JSON'
{
  "seed_hex": "#000000",
  "constraints": {
    "allowed_hex": ["#000000", "#F4EBDD"],
    "required_hex": ["#000000", "#F4EBDD"],
    "max_colors": 2,
    "allow_gradients": false
  }
}
JSON
cat > "$LOGO_WORKSPACE/reference.json" <<'JSON'
{"selected_by": "assistant"}
JSON
cat > "$LOGO_WORKSPACE/combined.json" <<'JSON'
{
  "seed_hex": "#247A52",
  "constraints": {
    "locked_hex": ["#247A52"],
    "allowed_hex": null,
    "max_colors": 2,
    "required_hex": [],
    "allow_gradients": false
  },
  "selected_by": "assistant"
}
JSON
ll palette-propose --session color-demo --request-file "$LOGO_WORKSPACE/auto.json"
ll palette-propose --session color-demo --request-file "$LOGO_WORKSPACE/anchor.json"
ll palette-propose --session color-demo --request-file "$LOGO_WORKSPACE/restricted.json"
```

All color values accept only `#RGB` or `#RRGGBB` and normalize to uppercase six-digit sRGB. Defaults are empty locks/required colors, no allowed set or count limit, and no gradients. `allowed_hex` permits colors without requiring every one to appear; `required_hex` explicitly requires presence. The union of locked and required colors must belong to any allowed set and fit `max_colors` (1–8). An allowed-set/count restriction cannot be combined with gradients. Conflicts fail before image calls.

For the runnable reference example, use the existing public Logo Land transparent PNG as a color source. It is a historical image used to exercise extraction, not a newly generated logo. Replace it with the user's real local reference in ordinary work. The command copies original bytes and records a hash; moving the external source later does not break the project. A reference is separate from an edit parent.

```sh
ll reference-add --session color-demo --reference photo-1 \
  --image "$LOGO_REPO/assets/logo-transparent.png" --revision 0
ll palette-propose --session color-demo --reference photo-1 \
  --request-file "$LOGO_WORKSPACE/reference.json"
ll palette-propose --session color-demo --reference photo-1 \
  --request-file "$LOGO_WORKSPACE/combined.json" > "$LOGO_WORKSPACE/proposals.json"
```

`--reference` binds real extraction to the request and supplies `source="reference"`, reference ID/hash and extraction evidence. Preserve that evidence when saving a candidate; fabricated or changed reference extraction evidence is rejected against the stored original. Do not invent `extracted_colors` or a provider response. Without `--reference`, a local-harmony request defaults to `source="local_harmony"`. Assistant/provider proposals instead use actual `swatches` plus their truthful source/evidence; Leonardo is optional and must not be claimed when no call occurred.

The proposal response has `session_id`, `revision`, `candidates`, `warnings` and optional `extraction`. Inspect all of them. Extraction is an estimate from the full image or declared region, includes intentional white, excludes fully transparent pixels and may be dominated by an opaque background. It does not prove conformance or color placement.

To extract only a region, pass `--roi-file` to `reference-add`. Its complete JSON shape is below; coordinates refer to the image after EXIF orientation and must fit its dimensions. Omit the option for full-image analysis.

```json
{"x": 0, "y": 0, "width": 256, "height": 256}
```

Select one candidate, respecting the user's approval preference. The following explicitly selects the first candidate after the assistant has assessed it. It writes only that `PaletteContent`, not the proposal envelope. `palette-add` calculates the immutable version digest and makes this palette active for new generations.

```sh
uv run --locked --project "$LOGO_REPO" python -c \
  'import json,sys; p=json.load(open(sys.argv[1])); print(json.dumps(p["candidates"][0], ensure_ascii=False, indent=2))' \
  "$LOGO_WORKSPACE/proposals.json" > "$LOGO_WORKSPACE/chosen-palette.json"
ll palette-add --session color-demo --palette green-reference-v1 \
  --palette-file "$LOGO_WORKSPACE/chosen-palette.json" --revision 1
```

For a hand-authored palette, `--palette-file` accepts this complete minimal `PaletteContent` example. These swatches are proposed intent, not extraction results. Use a fresh palette ID and the current revision when adding it.

```json
{
  "swatches": [
    {"hex": "#247A52", "role": "primary symbol"},
    {"hex": "#193B2B", "role": "exact brand lettering"}
  ],
  "constraints": {"locked_hex": ["#247A52"], "max_colors": 2},
  "source": "assistant",
  "source_evidence": {"notes": ["Original proposed direction; not sampled from an image."]},
  "selected_by": "assistant",
  "rationale": "Keep the required green symbol and use a darker green for the name."
}
```

### Lockup and exact lettering

This runnable horizontal lockup keeps the example brief's exact `Morrow Studio` text. A stacked alternative uses `layout="stacked"` and usually `text_alignment="center"`. `symbol_position="start"` means before/above the text; `end` means after/below. To generate the exact Hangul `밤결`, set both `brand_name` and `exact_text` in a separate brief to that string before initializing its own session.

```sh
cat > "$LOGO_WORKSPACE/lockup.json" <<'JSON'
{
  "layout": "horizontal",
  "symbol_position": "start",
  "text_alignment": "start",
  "typography_style": "Calm geometric sans-serif with open counters",
  "font_reference": "Space Grotesk, requested visual reference only"
}
JSON
ll prompt --session color-demo --concept 'A leaf symbol beside the exact text Morrow Studio' \
  --palette green-reference-v1 --lockup-file "$LOGO_WORKSPACE/lockup.json" \
  > "$LOGO_WORKSPACE/prompt.json"
uv run --locked --project "$LOGO_REPO" python -c \
  'import json,sys; print(json.load(open(sys.argv[1]))["prompt"])' \
  "$LOGO_WORKSPACE/prompt.json" > "$LOGO_WORKSPACE/a-v1.txt"
```

A complete stacked override is:

```json
{
  "layout": "stacked",
  "symbol_position": "start",
  "text_alignment": "center",
  "typography_style": "Calm Korean sans-serif with clearly separated Hangul syllables",
  "font_reference": "Noto Sans KR, requested visual reference only"
}
```

Font references describe requested appearance, never actual font-file provenance. The raster still needs exact-text and layout inspection. See [typography.md](typography.md) and the [font research](../../../docs/research/font-tools.md).

### Actual image import, report and gallery

`prompt.json` returns the effective palette ID/digest, lockup, revision and parent image path. Inspect those values and use the saved final text for the actual native image call. If you change the final prompt, save the exact text that was submitted. The commands below require the **actual returned PNG** at the assigned path; the placeholder is not a bundled generated result.

```sh
LOGO_GENERATED_PNG='/replace/with/actual/native-tool-output.png'
ll import --session color-demo --artifact a-v1 --image "$LOGO_GENERATED_PNG" \
  --prompt-file "$LOGO_WORKSPACE/a-v1.txt" --palette green-reference-v1 \
  --lockup-file "$LOGO_WORKSPACE/lockup.json" --revision 2
ll color-analyze --session color-demo --artifact a-v1 --revision 3 \
  > "$LOGO_WORKSPACE/analyzed.json"
ll color-gallery --session color-demo --artifacts a-v1 \
  --output output/color-galleries/color-demo-v1
```

These revisions assume the exact sequence above without another mutation. Use `show` to resolve a newer revision; a stale import must fail instead of silently changing its intent. The example brief requests an opaque PNG. For a transparent variant, request transparency in the actual native call and pass `--background transparent` on import.

Import retains the original even when color analysis is unavailable or returns mismatch/indeterminate. Inspect its result and the appended `color_reports`; report failure is not image-generation failure. `color-analyze` creates a report from original bytes, takes optional `--roi-file`, and never accepts a caller-supplied pass. Reports contain IDs/hashes, palette binding, policy and engine versions, profile treatment, sampling scope, status/reasons, measured swatches, target sample counts/ΔE00 and contrast guidance. Quantized display swatches are estimates; conformance uses the original sampled colors.

`color-gallery` takes a comma-separated explicit artifact list, for example `--artifacts a-v1,a-v2`. It creates `index.html` and unchanged PNG copies in a fresh workspace-relative directory. Open that local page in a browser for light/dark/checkerboard backgrounds and small/large previews. It does not change selection, state revision or image bytes. Gallery destinations are separate from exports; existing directories are not overwritten. It omits full prompts, absolute local paths and unselected private reference images.

For a color edit, add a new palette with `--parent-palette green-reference-v1`, then pass that new `--palette` alongside the real image's `--parent` to both `prompt` and `import`. For spacing-only edits, omit palette/lockup overrides: the parent wins over active new-generation intent. Legacy parents with no structured palette stay unknown. Background omission retains its independent behavior described below.

## Session lifecycle

```text
init --session morrow-demo --brief /workspace/brief.json
list
show --session morrow-demo
prompt --session morrow-demo --concept "Open geometric M with generous negative space"
```

`init` creates revision 0. `prompt` returns proposed `prompt` text and `parent_image_path` when applicable; it does not call image generation or mutate state. Save the final prompt as a UTF-8 file before the actual image call. Import only the actual returned PNG:

```text
import --session morrow-demo --artifact a-v1 --image /actual/generated/image.png --prompt-file /workspace/prompts/a-v1.txt --revision 0
```

Every mutation increments `revision`. Use the revision from the latest successful response or `show`; do not copy the illustrative numbers blindly. Stable IDs must be unique. The helper copies the source and preserves the original.

For an edit:

```text
prompt --session morrow-demo --concept "Chosen geometric direction" --parent a-v1 --changes "Change green to navy, preserving shape and exact text"
import --session morrow-demo --artifact a-v2 --image /actual/edited/image.png --prompt-file /workspace/prompts/a-v2.txt --parent a-v1 --revision 1
```

Between those commands the assistant must view the actual parent, invoke the native edit tool with it, and inspect the returned image. Saving a prompt or importing an unrelated file does not prove an edit happened.

For non-icon work, when the user changes the background requirement, pass `--background opaque` or `--background transparent` on import. This records that artifact's requested background independently of the original brief. For example, a transparent child of an opaque original uses `--parent a-v1 --background transparent`. On subsequent edits retaining that variant, pass the same override again. Omitting it defaults to the original brief, not the parent's override. Icon mode instead requires opaque and records it when the option is omitted. Never infer or weaken the request from the generated pixels. Legacy sessions without this field remain readable and use their original brief.

For a tool failure, preserve the attempt without a fake artifact:

```text
failure --session morrow-demo --prompt-file /workspace/prompts/a-v2.txt --reason "Actual tool error summary" --parent a-v1 --revision 1
```

## Select, review and export

Select the user's choice or a choice they delegated to the assistant. Write a visual review JSON with the schema in [delivery-checks.md](delivery-checks.md), based on actual inspection.

```text
select --session morrow-demo --artifact a-v2 --revision 2
review --session morrow-demo --artifact a-v2 --review-file /workspace/review.json --revision 3
export --session morrow-demo --revision 4
```

The default final output is `output/logo-generator/<session-id>/` under the workspace. `--output` can select a new workspace-relative destination. Use a fresh output directory for another delivery version; never replace an earlier package. If the requested destination is outside the workspace, first export and verify inside it, then copy the complete verified package to the explicitly requested location without overwriting existing files.

The internal `.logo-generator` directory is reserved for sessions and locks and cannot be used as an export destination. Use a normal output folder such as `deliveries/version-2`.

The helper requires all visual checks to pass and rechecks real file metadata and hashes. It also recomputes the selected artifact's color report for export. Strict mismatches fail with `color_mismatch`; missing or indeterminate strict evidence fails with `color_review_required`. Unrestricted palettes remain advisory and palette-less legacy artifacts remain color-unverified. The expanded manifest uses schema 2, while the ZIP still contains exactly `logo.png`, `manifest.json` and `brand-guide.md`. See [delivery-checks.md](delivery-checks.md) for report interpretation. It cannot independently certify a reviewer's design judgment. If it rejects a corrupt, opaque-when-transparent-required, or modified image, fix the underlying problem; do not edit state or report JSON to bypass it.

## Resume and preserve

Sessions live at `.logo-generator/sessions/<session-id>/`. Read them through `show` in a new conversation, reopen relevant PNGs, and continue using saved IDs. Missing or changed images, unsupported schema, stale revisions and duplicate IDs are errors, not reasons to reset the workspace. Do not delete a lock unless it has been independently proven stale and recovery is explicitly warranted.

Resume a comparison with its full `(session, artifact)` identity and saved notes, not
an ordinal card number or a bare `v1`. Gallery revision is historical; obtain current
revision with `show`, check the source hash and intent, and reconcile any intervening
selection/review/edit before continuing. Retain the old gallery as a snapshot and use
a fresh selection file/output directory for a new comparison. See the
[resume sequence](comparison-workflow.md#resume-a-chosen-source) for safely quoted
keep/change data and the prompt/import revision boundary.

Lockup precedence is an explicit complete `--lockup-file`, otherwise the parent's
saved lockup including null, otherwise the brief for a new generation. A null parent
does not fall back to brief typography and does not clear text visible in the original.
It remains unknown structured intent. Palette and icon intent keep their independent
parent precedence; new-generation defaults do not rewrite existing artifacts.

Keep final prompts and failed attempts for reproducibility. The prompt records the requested design; generated lettering, intended palette values and font appearance still need visual verification. Do not store account credentials or base64 images in brief/state text.

Schema 2 adds append-only palettes, references and reports, plus active new-generation intent and per-artifact palette/lockup bindings. For schema 1, `show`, `list` and `prompt` read through an in-memory adapter without rewriting bytes or incrementing the revision. The first successful explicit mutation writes a verified, byte-exact `session.v1.backup.json` in the session directory before atomically saving schema 2. A failed save may leave that verified backup available for retry, while preserving the old state bytes; a conflicting backup is never overwritten. Old artifacts keep null structured palettes and do not receive invented HEX or passing evidence.

Keep the backup together with the original files when archiving the project. Forward reading of schema 1 does not promise that v0.3.1 reads schema 2. No automatic downgrade is provided, and the v1 backup does not contain later v2 edits. Do not restore it over current work or hand-edit the schema version to downgrade. Preserve both versions and arrange an explicit recovery workflow if the older tool must be used.

The 0.5.0 development source adds optional `app_icon` snapshots to brief/artifact/effective intent/prompt results while retaining session and manifest schema 2. The frozen v1 parser is unchanged. Reads preserve old v1/v2 state bytes and existing artifact intent cannot be rebound. Older readers are not promised to read new icon-bearing v2 files, even though the schema number is unchanged. Approved icon exports include selected icon metadata and raster/platform limitations while preserving the same three ZIP payload filenames and PNG bytes.

## Compatibility after the Logo Land rename

Logo Land was previously called `logo-generator`. The skill path and invocation are now `skills/logo-land` and `$logo-land`. Existing `.logo-generator/` session storage and `output/logo-generator/` default deliveries remain unchanged; no folder migration is required for the rename. The separate schema-1-to-2 transition follows the backup rules above. Historical sample prompts retain the original invocation.
