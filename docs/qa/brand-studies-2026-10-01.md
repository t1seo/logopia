# Brand studies: technical verification

Verified on 2026-10-01 against the 0.10.0 working tree based on
`81b0268f07e01c9ec8ad5ae2c6636713824f374f`. This record covers the exact-prompt
reservation change and repository checks. It does not establish aesthetic quality,
user acceptance or production readiness of the generated artwork.

## Repository checks

| Check | Result |
| --- | --- |
| `uv run --locked pytest` | **1,151 passed in 433.62 seconds** |
| `uv run --locked ruff check .` | Passed |
| `uv run --locked ruff format --check .` | Passed; 592 files already formatted |
| `uv run --locked basedpyright` | 0 errors, 0 warnings, 0 notes |
| `uv lock --check` | Passed; no dependency changes |
| Official skill `quick_validate.py` | Passed |
| Official plugin `validate_plugin.py` | Passed |
| Four changed Python files: no-excuse audit | No violations |
| `git diff --check` | Passed |
| Changed source/test hashes after the full run | Unchanged from the run's initial snapshot |

Raw logs, the source hash snapshot and independent review notes are retained locally
under `output/brand-studies-20261001/qa/code/`. That ignored runtime directory is
not part of the public evidence bundle.

## Exact-prompt reservation

`loop-request --prompt-file` saves the supplied UTF-8 string without rewriting it.
The normal source revision, direction, parent, palette, background, budget and
critique bindings remain in force. The saved request remains the input to the
native call; this option does not perform image generation.

Thirteen new regression cases cover exact Unicode/newline preservation, the
20,000-character boundary, malformed inputs without mutation, edit-parent and
palette retention, immutable pending/unknown calls, failed-call retries, rejected
prompt-mismatched imports and a successful evidence-bound review without selection
or approval. These use explicitly synthetic images; they are protocol tests.

An independent read-only reviewer found no must-fix regression in the four-file
change and its existing storage/verification paths. Failed retries reuse the
complete saved input and reject changed prompt/direction or source revision before
another reservation. The combined overridden-edit → unknown → failed → retry path
and mutation after a failed call were additionally traced statically; no separate
runtime coverage is claimed for those combinations.

## Limits

An authored prompt replaces the compiled text; contractual instructions are not
automatically appended. Preserved metadata does not prove semantic compliance of
that text or the returned image. The director must include applicable scope,
lettering, color and edit-preservation instructions and inspect the actual result.

The `full_logo` loop can carry app-icon intent, while `symbol_only` rejects it.
An unusually large app-icon brief can still exceed the legacy icon builder's own
20,000-character limit before a shorter override is substituted. This fails before
reservation or charging. The present change does not claim to replace that builder
for every valid icon brief; broader support requires separate work and testing.

## Native artwork and review

The [collection manifest](../showcase/2026-10-01-brand-studies/manifest.json)
accounts for eight initial generations and three exact-parent edits: eleven native
calls within a shared budget of twelve. Every public original and exact prompt
matches its receipt SHA256; all three parent hashes match their preserved originals.
Selected rillo and 사이 v2 masters repair unwanted transparency and edge debris.
AL v2 widens the lower letter gap. All eight selected PNGs are fully opaque. The
tool reported no model identity, so none is inferred.

An independent model critic inspected the eight initial images, three edits and ten
final small-size diagnostics. A second diagnostic reviewer also compared AL v1 at
the same height. The [selection review](../showcase/2026-10-01-brand-studies/reviews/selection.md)
records concrete form strengths and small-detail limitations. These are model
judgments, not user adoption, a blind recognition study or a quality benchmark
against the earlier collection's different briefs.

Eleven separately labeled diagnostic PNGs were made with macOS `sips`: exterior
margin crop and proportional downsample for brand marks; full-canvas 56px and 32px
views for icons. They were directly opened at actual pixel sizes. All eleven native
source PNG hashes were unchanged before and after diagnostics. The public
[diagnostic manifest](../showcase/2026-10-01-brand-studies/reviews/size-previews.json)
binds source hashes, crop bounds, output hashes and dimensions. These previews are
not modified logo masters, background fixes or browser screenshots.

The six brand loops recorded their final evidence-bound critiques and ended
`stopped` with application inspection unresolved. All six passed the observed
original/form/small-size checks; none was promoted to `ready_for_user_review`
without context evidence. Director selection for this study remains a separate
decision. The two icon studies retained their existing icon-intent sessions and
manual collection ledger. [Portable outcomes](../showcase/2026-10-01-brand-studies/reviews/loop-outcomes.json)
preserve this distinction without claiming to be resumable private loop state.

## Gallery verification

The actual HTML script and final data executed in a minimal Node DOM mock: eight
cards, sixteen master/application images, filters with counts 8/3/3/2, and original,
download and prompt destinations were checked. The final pass checked 64 local
paths, including the README, manifest and reviews, over HTTP. All passed; the 22
original/prompt hashes also matched the manifest. This is static/script and link
verification, not browser visual QA.

Official Codex Computer Use encountered active user interaction in Chrome. The
agent preserved user tabs and stopped navigation attempts. The final eight-card
layout, responsive viewport, browser filters and download interactions were not
visually verified. An early two-item file-URL attempt showed a blank body; its cause
was not established, and no offline browser pass is claimed. The local HTTP preview
remains available. Raw GUI limitations and static/link evidence are retained in
`output/brand-studies-20261001/qa/`.

## Personal installation

The six changed production/skill files were applied to the existing personal
plugin after the full checks passed, with a complete backup and the official
cachebuster/install flow. The enabled installation reports
`0.10.0+codex.20261001132615`. All six files match the repository and actual returned
cache; the other 322 payload files remain unchanged, with only the manifest's
cachebuster additionally updated. Marketplace and configuration files were unchanged.

Official validators and a smoke run through the installed CLI passed. The smoke
run exercised `init`, `loop-start`, `loop-request --prompt-file` and `loop-show`,
checking exact Unicode/newline preservation without an image call. Loading the
updated skill in a new GUI conversation was not verified. This is a local install,
not a tagged release; the latest published release remains 0.8.0.
