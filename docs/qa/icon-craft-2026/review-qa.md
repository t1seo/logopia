# Independent hands-on QA — 2026-09-19

Review scope: the current working tree against `d7d3cd4`, using the public helper CLI in a separate temporary workspace. No image/provider calls, no changes to the six-image experiment session, and no source-code edits. Synthetic assets, where used, test file and state behavior only; they do not demonstrate design quality or human preference.

## Scenario plan, written before execution

Each row is a task: execute the listed action, compare with the expected behavior, and record its outcome below.

| ID | Priority | Action and expected behavior |
|---|---|---|
| 01 | P0 | Initialize an old-style brief without references or asset intent; produce the legacy prompt contract. |
| 02 | P0 | Import a real PNG with the saved final prompt; retain exact source bytes and prompt. |
| 03 | P0 | Import a positive reference; return exact local reference path in native image arguments. |
| 04 | P0 | Use text conditioning; retain inspected traits but omit positive image attachments. |
| 05 | P0 | Use a negative reference; forward avoidance text without image attachment or positive transfer. |
| 06 | P0 | Edit with a parent and positive reference; return the parent first and reference second. |
| 07 | P0 | Request image conditioning from text-only capability; reject explicitly before dispatch. |
| 08 | P0 | Submit stale analysis image hash; reject before returning a model request. |
| 09 | P0 | Remove an imported reference; reject with a controlled file error and unchanged session. |
| 10 | P0 | Corrupt imported reference bytes; reject with a controlled integrity error. |
| 11 | P0 | Import transparent Apple foreground; allow alpha and report no native-package validation. |
| 12 | P0 | Apply identical transparent PNG as Apple background; report failed opacity validation. |
| 13 | P0 | Check valid 512px RGBA Play listing image; enforce distinct listing requirements. |
| 14 | P0 | Render a blind gallery from two explicit saved candidates; preserve source hashes and state. |
| 15 | P0 | Record an AI response; store AI recommendation separately from QA and user selection. |
| 16 | P0 | Exceed the review-call budget; reject additional AI response without state mutation. |
| 17 | P0 | Record a human-format synthetic response; use separate user-preference sidecar, no QA/selection changes. |
| 18 | P1 | Record a duplicate response; reject duplicate rather than consume budget twice. |
| 19 | P1 | Test all four preference outcomes; accept A, B, tie and neither. |
| 20 | P1 | Omit required visible observation; reject incomplete preference review. |
| 21 | P1 | Supply invalid asset/platform/role combinations; reject at typed input boundary. |
| 22 | P1 | Supply explicit user text, color and background; keep requirements in actual prompt. |
| 23 | P1 | Generate diagnostic previews; source PNG bytes and original prompt stay unchanged. |
| 24 | P1 | Run 3×3 exploration with fake provider; count nine slots, preserve direction identity and bounded calls. |
| 25 | P1 | Interrupt/reconcile/resume exploration; preserve completed candidates and avoid duplicate generation. |

Augmentation after reviewing environment and state risks:

| ID | Priority | Action and expected behavior |
|---|---|---|
| 26 | P1 | Use workspace paths containing Korean text and spaces; public CLI succeeds. |
| 27 | P1 | Request ROI image conditioning; explicitly reject unsupported whole-source attachment. |
| 28 | P1 | Change source revision after creating a gallery; reject stale response. |
| 29 | P1 | Give AI zero reported calls or a human positive reported calls; reject inconsistent attribution. |
| 30 | P2 | Inspect existing browser QA for equal diagnostic sizes, responsive layout and simulation labeling. |

## Results

**Verdict: PASS. Confidence: high for the tested local CLI/state contracts; no claim about human preference or native-platform rendering. No blocking issues found.**

Coverage: 17/17 P0 scenarios passed, 12/12 P1 scenarios passed, and 1/1 P2 evidence-inspection scenario passed. Of these, 27 were exercised through real public CLI subprocesses, two were executed through the actual Hermes engine with a fixture provider, and one independently inspected the existing browser evidence. The fixture provider does not establish image quality or paid-provider behavior.

| ID | Result | Actual result / evidence |
|---|---|---|
| 01 | PASS | Legacy `init` and `prompt` succeeded; JSON omitted `input_plan`, preserving the previous response shape. |
| 02 | PASS | Imported original SHA-256 and saved prompt matched exact input bytes/text; later gallery/record checks retained both. |
| 03 | PASS | `mode:image` returned one verified `references/r.png` path; native argument prompt equaled the final saved prompt. |
| 04 | PASS | `analysis_text` retained the selected highlight trait and omitted `referenced_image_paths`. |
| 05 | PASS | Negative input retained avoidance text, omitted image attachments and omitted the positive transfer sentence. |
| 06 | PASS | Native argument array had exactly two paths: the selected original parent first, reference second; `parent_sha256` was present. |
| 07 | PASS | Exit 1, `unsupported_conditioning: Image input unavailable for this capability or ROI-only scope; use text mode`. |
| 08 | PASS | Exit 1, `analysis_mismatch: Analysis hash or ROI differs from reference`. |
| 09 | PASS | Exit 1, controlled `invalid_file` for missing reference; repeated test verified Session SHA-256 unchanged. |
| 10 | PASS | Exit 1, `hash_mismatch: Reference r changed`; restoring the exact temporary reference allowed `show` again. |
| 11 | PASS | A 1024px RGBA foreground with actual transparent pixels imported and passed applicable local checks, with `native_package:false`, `platform_validation:not_run`. |
| 12 | PASS | Identical alpha PNG declared as background yielded `background_opacity:fail`; transparency was not treated uniformly across roles. |
| 13 | PASS | A 512px RGBA listing passed dimension, 32-bit PNG and byte-limit checks. sRGB and appearance identity remained explicitly `not_checked`. |
| 14 | PASS | The explicit revision-4 pair produced a standalone gallery and neutral filenames. Source PNG and Session hashes were unchanged. |
| 15 | PASS | Synthetic AI response produced `ai_recommendation`, one recorded review call, `source_sessions_changed:false`; source state stayed identical. |
| 16 | PASS | Second AI response exceeded the budget of one and failed with `review_budget`; no automatic provider dispatch exists here. |
| 17 | PASS | Synthetic human-format response produced `user_preference` sidecar with zero added AI calls, without source-state mutation. This is not actual user preference evidence. |
| 18 | PASS | Exact repeated response failed with `conflict: This exact response is already recorded`. |
| 19 | PASS | Separate synthetic user-format records accepted `a`, `b`, `tie`, and `neither`. |
| 20 | PASS | Removing `small_size_32` failed typed validation; incomplete evidence could not be recorded. |
| 21 | PASS | Play-listing intent paired with Apple platform failed `init` with `invalid_asset`. |
| 22 | PASS | Actual legacy prompt retained exact Korean `기억`, explicit `#173E48`, and transparent-background request. |
| 23 | PASS | `icon-gallery` generated a local preview; foreground source PNG and Session SHA checks both returned `OK`. |
| 24 | PASS | Actual Hermes engine test produced nine unique direction/slot pairs, reserved nine initial images, two planning LLM calls and 18 review LLM calls; repeated produce emitted no duplicate; two explicit edits preserved lineage and a third was blocked. |
| 25 | PASS | Unknown outcome was not resent. A fifth-slot interruption reconciled the exact returned image, retained the first four hashes, then finished nine slots with exactly nine generation calls. |
| 26 | PASS | All local CLI paths used `/tmp/logopia-review-qa.zd0iaP/작업 공간`; Korean text and spaces worked throughout. |
| 27 | PASS | Imported 100×100 ROI was bound to analysis; requesting whole-image conditioning failed explicitly with `unsupported_conditioning`. |
| 28 | PASS | After all immutability checks, an intentional selection in the disposable session advanced its revision; old-gallery response failed `stale_revision: Expected revision 4; current revision is 5`. |
| 29 | PASS | AI with zero calls and human with positive calls both failed `invalid_review`, with distinct attribution messages. |
| 30 | PASS | Opened `browser/blind-mobile-sizes.png` and `browser/normal-desktop-64.png`; visible equal-size comparisons and stacked mobile layout agreed with recorded DOM evidence. This reviewer did not rerun browser automation. |

## Reproduction and receipts

Every manual action ran the actual entry point:

```sh
uv run --script skills/logo-land/scripts/logo_project.py \
  --workspace '/tmp/logopia-review-qa.zd0iaP/작업 공간' COMMAND ...
```

Temporary complete inputs, stdout/stderr receipts and SHA checks are under `/tmp/logopia-review-qa.zd0iaP/`. The executed shell scripts are `/tmp/logopia-review-qa-{cli,assets,preference,preservation}.sh`; they contain no provider calls. Synthetic alpha/listing fixture creation used Pillow only to exercise encoding/role checks. The actual PNGs used for import/reference routing remained unchanged; they were not regenerated or judged by fixture responses.

Executed engine tests:

```sh
uv run pytest -q tests/hermes/test_exploration_pipeline.py tests/hermes/test_craft_budget.py
# 5 passed in 13.45s
```

The command includes the two additional review-budget checks: a budget too small for both review roles is rejected, and a later edit that cannot be reviewed is blocked before a generation call. Transcript: `/tmp/logopia-review-qa-hermes.txt`.

Browser evidence independently read: [functional browser report](../preference-review-2026-09-19.md), [normal controls](browser/normal-controls.json), [mobile controls](browser/blind-mobile-controls-final.json), [mobile screenshot](browser/blind-mobile-sizes.png), [normal screenshot](browser/normal-desktop-64.png). DOM receipts report 32/48/64/128 CSSpx consistently across all six cards and peer contexts, equal light/dark surfaces, identical diagnostic masks, and no 390px mobile overflow.

## Limits

No paid/native image call or extra review-model call was made by this QA. The six-image experiment, its revision-8 session and its actual user preference records were untouched. Functional response fixtures were explicitly labeled synthetic and written only inside the temporary workspace. There is no claim of native Icon Composer/Xcode/Android package validity, verified sRGB conversion, OS appearance rendering, trademark uniqueness, or improved user preference. The targeted tests used a fixture provider; the root task's full-suite run and actual generation experiment are separate evidence.
