# Make a logo with Hermes

[English](hermes.md) · [한국어](hermes.ko.md) · [Logopia](../README.md)

Describe the brand once. Hermes develops distinct directions, generates original artwork, checks the pixels in two separate reviews, and refines a promising candidate. You can choose the candidate yourself or delegate that judgment within the existing call limits.

**Brief → directions → original candidates → visual review → select, refine or stop → verified delivery**

## Start a conversation

Use [Hermes Agent](https://hermes-agent.nousresearch.com/) on macOS or Linux, a working Hermes image provider, Python 3.12+ and `uv`. This native plugin uses Hermes's public plugin and structured-image APIs. Its code supports the Hermes Python 3.11+ runtime; the local file helper runs separately in the repository's locked Python 3.12+ environment. The installer checks the plugin and its dependencies (Pydantic 2.12+ below 3, Pillow 11.2+ below 13); it does not install Hermes or configure an image provider.

From your Logopia checkout, create a dedicated profile once and configure its model and tools:

```sh
uv sync --locked
hermes profile create logopia --no-alias --no-skills
hermes -p logopia setup
uv run --locked python integrations/hermes/studio.py install --profile logopia
hermes -p logopia chat --toolsets logopia-studio,image_gen --skills logopia-studio:director
```

If the profile already exists, skip creation and reuse its working settings. Installation sets that named profile's native sequential and concurrent tool limits (`timeouts.tools.sequential_call` and `timeouts.tools.concurrent_batch`) to 1,800 seconds each, or 30 minutes, so the complete workflow can finish. It keeps the profile's existing provider/model selection and leaves the default profile separate. For a different project directory, add `--workspace /absolute/path/to/project` to installation.

An interrupted update restores the previous plugin when possible. If another file occupies its location or restoration fails, the old files remain under that profile's `plugins/.logopia-install-*/previous` directory. Keep that recovery copy until the installation is restored; the interrupted update is not reported as successful.

Try:

> Create three concepts for OFFCUT, a repairable furniture studio using reclaimed wood. Our customers live in small city homes. Make it warm, resourceful and precise. Combine a memorable symbol with the exact text OFFCUT on white. Compare the whole logo at 192 pixels wide.

The comparison page opens original PNGs directly. It shows each direction, its small-size view, concrete review findings and parent versions. Reviewing or drafting feedback in that page does not change your saved selection.

## Choose and refine

Select a candidate in the page, describe **what to keep** and **what to change**, then copy its request back to Hermes. For example:

> Keep the symbol, OFFCUT lettering and colors. Increase the gap between the symbol and lettering, and open the narrow internal gap in the symbol.

Every revision uses the exact parent image and receives new reviews. The parent remains available. Ask Hermes to deliver the selected candidate after its required checks pass; choosing a candidate alone does not approve its quality.

To delegate design decisions, say, for example:

> Research our existing brand, then develop a symbol. Our typography is already fixed; do not generate a wordmark. Compare the actual forms, choose only if there is a viable idea, and use up to two targeted revisions to address visible defects. If none is suitable, retain the work and explain why.

The director uses the current `logopia_action` tools for that work; it does not need another choice from you before each authorized edit. It first describes the visible form, then checks brand fit, construction and use-size evidence. A revision names what to preserve and which one or two defects to change. It compares the child against the exact parent and can retain the parent when the edit regresses. A one-pass or candidate-only request still stops after the agreed candidates.

If every idea is weak, the director reports no recommendation and leaves selection empty. An existing selection cannot currently be cleared through the Hermes API; the report must withdraw that recommendation explicitly and must not deliver it. Reaching a call limit does not make a weak candidate ready. An agent's delegated selection is reported as an agent decision, not as your approval.

This is a **conversation-directed loop over the existing engine**. The engine itself stops at `awaiting_choice` after initial reviews and after every edit. It reserves at most two edits, including failed and unknown attempts; it has no automatic re-planning, reject-all state or decision-author field. A new plan or changed brief needs a separate workflow and must not be used to silently reset a task's budget. The Codex helper's separate quality-loop state and commands are not native Hermes tools and do not transfer into a Hermes workflow.

The updated direction follows the [logo foundations research](research/logo-design-foundations-2026-10-01.md) and [iteration research](research/logo-iteration-practice-2026-10-01.md), including Figma's design and critique practices. The research informs the director's decisions; it does not establish a measured improvement in logo quality. The native engine's two structured critics and delivery checks remain separate from that additional judgment.

## Actual example: OFFCUT

The [OFFCUT example](hermes-demo/README.md) preserves three initial candidates and two native edits, with the exact chain **c1 → e1 → e2**. The first edit improved letter spacing but failed preservation because the symbol-to-word gap narrowed. The final e2 restored that gap, passed both model critiques and was delivered at workflow revision 47. Compare the [initial c1 PNG](hermes-demo/originals/c1.png) and [refined e2 PNG](hermes-demo/originals/e2.png), or download the actual [delivery ZIP](hermes-demo/delivery/logo-package.zip).

This is a curated example with the coordinator's recorded selection, not user approval or resumable private state. Download its folder and open `index.html` locally to use the offline comparison. The [execution record](qa/hermes-workflow/native-run.md) also retains the initial 420-second native timeout and the explicit critique-only continuation that added no image jobs.

## Continue saved work

Ask Hermes for the workflow's status or use the local commands below, replacing `offcut-hermes-demo` with your saved workflow ID. Reading status and rebuilding the page do not call an image model.

```sh
uv run --locked python integrations/hermes/studio.py show --workflow offcut-hermes-demo
uv run --locked python integrations/hermes/studio.py gallery --workflow offcut-hermes-demo
```

For a saved tool-request JSON file, the bounded launcher checks the exact workflow revision and, for candidate actions, the original hash before starting Hermes:

```sh
uv run --locked python integrations/hermes/studio.py run --profile logopia --request request.json
```

The launcher's own deadline defaults to 30 minutes; `--timeout` accepts 1–3,600 seconds. Shutdown allows a ten-second graceful period followed by up to ten seconds for forced-stop verification, plus bounded cleanup of an active PID query. It checks the groups in its own session, including the local helper. These bounds are separate from the named profile's native tool limits. A process exit code or Hermes's final message alone cannot establish success: the launcher checks the saved workflow result. Stopping the local process does not prove that the image provider cancelled its request.

If an old feedback request is rejected, open the latest state and explicitly reapply your change. An interrupted image request can have an unknown outcome; it is never resubmitted automatically. Completed originals stay saved under `.logo-generator/sessions/`; workflow decisions live under `.logo-generator/workflows/`.

If only a read-only image critique failed or was interrupted, Hermes can continue the saved workflow when that continuation is covered by your request, including delegated iteration. An eligible candidate may use its one remaining review attempt without generating new images, retaining the failed attempt in its history. An unresolved image request remains blocked until its exact recorded outcome can be reconciled; no retry, new cache-file guess or fresh original is automatic. Repeating the original creation request does not restart failed or interrupted work.

## Scope

- Brand logos, product-specific app icons and IP characters. App directions may use a signature mark, compact lettering, object, organic form, character or modular geometry. IP subjects, proportions, expression and colors follow the brief; cuteness and a fixed palette are not defaults.
- The fast path still creates three brand/app candidates or six IP candidates. Legacy `count` accepts one to six. Opt-in `direction_count: 3` with `candidates_per_direction: 3` creates nine candidates across three directions, varying construction within each direction. Do not combine these exploration fields with `count`. Initial generation is capped at nine images, with up to two requested edits; failed or unknown image attempts still consume their reservation.
- Exact brand or app lettering, including Hangul, without automatic initials. Inspect generated spelling. App/IP artwork uses a filled square; IP portraits contain no lettering. Optional `app_icon` metadata uses the helper's monogram contract for text: one to eight Unicode code points without whitespace or controls. Transparent brand PNGs remain supported.
- Symbol-only work uses `logo_type: symbol` and empty `exact_text`, with the brand name retained in `name`. Existing typography and other fixed assets belong in the brief's `notes`; generating similar-looking lettering does not preserve a real font asset. Any later composition must use the actual established asset.
- Up to six hash-verified local PNG references reach both planning calls and image critiques. Observations, interpretations and transferable traits are saved separately. Generation receives the selected traits as **text conditioning**. Hermes's native `image_generate` has one `image_url`, reserved for the exact edit parent; explicit `reference_conditioning: image` is rejected. Negative references supply avoid-traits, and automatic references do not become user preferences. See the [input contract](../integrations/hermes/CONTRACT.md) for reference fields.
- Advisory colors and two model critique calls per candidate, within a saved review-call budget. Requested edits preserve wording, colors and background and receive fresh design/lettering and production/use-size reviews. Use a new brief to change those requirements; strict palettes use the existing [`$logo-land` Codex skill](../skills/logo-land/SKILL.md). Reviews are AI observations, separate from your choice and from platform validation.
- The app gallery compares unchanged originals at 32/48/64/128px on light and dark surroundings, in an equal-size 48px context, and under labeled CSS-mask simulations. These diagnostic sizes and simulations are not OS rendering or platform approval. The helper provides the separate [blind preference workflow](preference-review.md).
- Native critique evidence binds each original and parent hash to an actual target-width raster view. That width describes the entire PNG, including its margins; it is not a measured ink width. A saved view or HTML size setting alone does not prove that a person or agent observed a successful small-size rendering. Missing observations remain unresolved, and model-review passes do not establish distinctiveness or market recognition.
- Original raster PNGs and checked delivery packages. The native Hermes path produces flat concept artwork; optional platform/appearance metadata does not create editable layers. Apple layered, Android adaptive and size-verified store assets require the [helper asset handoff](icon-assets.md). Editable vectors, font files and trademark clearance remain separate work.

For example, save this native `logopia_start` input as `request.json` and use the bounded `studio.py run` command above:

```json
{
  "workflow_id": "reading-exploration",
  "brief": {
    "name": "틈",
    "exact_text": "틈",
    "product": "An app that records short reading sessions",
    "audience": "Readers on their commute",
    "personality": "Quiet and distinct",
    "use_case": "App icon",
    "mode": "app_icon",
    "logo_type": "lettermark",
    "display_width": 48,
    "direction_count": 3,
    "candidates_per_direction": 3
  }
}
```

Omit both exploration fields to retain the three-image fast path. Existing saved prompts, originals and selections are preserved; new optional fields do not trigger regeneration.

The IP direction adapts [s1dashu/ip-as-logo-skill](https://github.com/s1dashu/ip-as-logo-skill), with its [MIT notice](../integrations/hermes/skills/director/references/ip-as-logo.LICENSE).
