# Hermes integration contract (v1)

This is the public implementation contract for the parallel workers. Changes require a coordinator message to all consumers. Names below are new Logopia APIs, not Hermes built-ins.

## Layout and ownership

`integrations/hermes/` is the native plugin root, with `plugin.yaml`, `__init__.py`, `skills/director/SKILL.md`, and a `logopia_studio/` Python package. It can be copied as a unit to the isolated profile. Modules use Python **3.11-compatible syntax**, Pydantic v2, Pillow, stdlib and protocols; no Hermes imports in the core. Existing helper is invoked in its separate locked uv environment. Tests use the repository environment with `integrations/hermes` on the import path.

- Core worker: `logopia_studio/__init__.py`, `models*.py`, `store*.py`, `engine*.py`, `helper*.py`, `checks*.py`, `prompts.py`, `protocols.py`; `tests/hermes/test_core*.py`, `test_helper*.py`, core fixtures owned within those modules.
- Host worker: plugin `__init__.py`, `plugin.yaml`, `logopia_studio/host*.py`, `registration.py`, `skills/director/`; `tests/hermes/test_host*.py`.
- Gallery worker: `logopia_studio/gallery*.py`, `assets/`; `tests/hermes/test_gallery*.py`, `tests/hermes/gallery*.mjs`.
- Launcher worker: `studio.py`, `logopia_studio/launcher*.py` except `launcher_process.py`; `test_launcher_cli*.py` and `test_launcher_request*.py`.
- Coordinator: `CONTRACT.md`, `logopia_studio/launcher_process.py`, `installer*.py`, associated process/installer/PIN tests, project metadata, docs, samples and integration corrections.

No direct imports from the Python 3.12 `logo_helper` package in this plugin. No vendored Hermes private implementation. No raw provider HTTP/auth code. Do not edit another worker's files. The coordinator adds the shared test/typecheck paths.

## Core public models (`logopia_studio.models`)

All external models are frozen/strict/extra-forbid and parsed from JSON. Bounded strings, strict integer versions/counts and portable IDs; no arbitrary JSON bags in persisted state. Internal records may use nominal IDs; the signatures below use the validated identifier strings at their public boundary.

`StudioBrief` fields:

- `name: str`, `exact_text: str` (preserve verbatim, empty allowed)
- `product: str`, `audience: str`, `personality: str`, `use_case: str`
- `display_width: int = 192` (16–1024 CSS pixels)
- `logo_type: Literal[wordmark,lettermark,monogram,symbol,abstract,combination,emblem,mascot] = combination`
- `mode: Literal[brand,app_icon,ip] = brand`
- `background: Literal[opaque,transparent] = opaque`
- `count: int | None = None` (explicit 1–6; effective default 3 brand/app, 6 IP; do not silently clamp)
- `colors: tuple[str,...] = ()`, `notes: str = ""`

App icons preserve supplied exact lettering and require opaque concept artwork. IP retains empty exact text and its character composition. App composition is product-specific rather than a forced centered pictogram. Optional `app_icon` metadata matches the helper preset/subject/placement/text/asset wire shape; non-concept native assets fail clearly before inference. Absent intent remains absent in legacy sessions. `effective_count` is the total initial image count.

`Strategy`: `positioning`, `audience_need`, `brand_promise`, `distinctive_principle`, `typography`, `color_roles`, `assumptions` (tuple of text). These are design proposals/inferences, not researched market facts. Source URLs may appear only when supplied/actually consulted, never invented by the planning call.

`Direction`: `id`, `title`, `motif`, `construction`, `rationale`, `risk`, `preserve` (tuple of text), `prompt` (the proposed generation prompt), optional `design_spec` and `variations`. Direction count equals `effective_direction_count`. Existing counts retain one candidate per direction. Explicit `direction_count` plus `candidates_per_direction` permits up to nine initial images, including 3×3 exploration. Variations name their slot, controlled variables and instruction; a recolor is not a new direction. Every image call returns one candidate.

2026-09-19 additions: `references` supplies at most six `StudioReference` records with
absolute PNG path/hash, positive/negative role, observed/transfer/avoid traits and
source/rights metadata. Real pixels go to both structured planning calls and critiques.
The art director returns `reference_analysis`, whose observed features and interpretation
are separate; the host verifies every source ID and binds its image hash. Only selected
traits are passed as text to generation. `reference_conditioning: image` is rejected:
the installed native tool has one `image_url`, retained for the actual edit parent.
No unsupported plural-image argument exists. Reference snapshots and analysis accompany
saved jobs/candidates; automatically chosen references never imply user preference.

The fast path remains three initial image calls (six IP). Exploration is opt-in and
does not replace legacy `count`; supplying both count forms is rejected. At most two
edits follow, so this implementation can issue at most eleven image calls per workflow.
`review_call_budget` may bound LLM reviews explicitly; its minimum covers two critics
per initial candidate and its maximum is 44. The default covers two attempts per
possible original/edited candidate. Every critique job reserves two LLM calls, and
the one plan job reserves two more. CLI/tool `call_budget` reports reservation bounds,
including unknown/failed attempts, rather than asserting exact provider billing.
No automatic image retry or extra material/layer pass is introduced.

Native Gallery app mode adds immutable-source 32/48/64/128px light/dark surroundings,
equal 48px candidate context, and explicitly labeled CSS-mask simulations. These are
diagnostics, not OS rendering or platform acceptance. Candidate details retain slot,
controlled variables and conditioning provenance; blind preference records are supplied
by the existing helper's separate preference workflow. QA does not become user choice.

Example native tool input (the same JSON is a launcher request file):

```json
{
  "workflow_id": "reading-exploration",
  "brief": {
    "name": "틈",
    "exact_text": "틈",
    "product": "짧은 독서 시간을 기록하는 앱",
    "audience": "출퇴근 중 읽는 독자",
    "personality": "조용하고 또렷함",
    "use_case": "앱 아이콘",
    "mode": "app_icon",
    "logo_type": "lettermark",
    "display_width": 48,
    "direction_count": 3,
    "candidates_per_direction": 3
  }
}
```

With an already configured explicit Hermes profile, submit using
`uv run --locked python integrations/hermes/studio.py run --profile logopia --request request.json --json`.
For the fast path omit both exploration fields. For references, add local `references`
records with a real digest from `shasum -a 256 /absolute/reference.png`; keep source
images in an ignored private cache. Native Apple layers, Android adaptive packages and
dimension-verified store assets use the helper handoff, not this square-only image tool.

`PlanResult`: `strategy: Strategy`, `directions: tuple[Direction,...]`, `provider`, `model`. `GeneratedImage`: `path: Path` (in-process returned path), `provider`, `model`, `receipt: str` (bounded exact native tool result, never auth).

`Criterion`: `key: Literal[text,composition,small_size,preservation,background]`, `status: Literal[pass,needs_revision,not_observed,not_applicable]`, `observation: str`, `fix: str = ""`.

`Critique`: `role: Literal[design,production]`, `provider`, `model`, `summary`, `criteria: tuple[Criterion,...]`. Both roles return all five unique criteria. No numeric quality score. N/A is permitted only for text when exact_text is empty, preservation for a new image; all other N/A fails delivery. Preserve all raw report histories; a malformed report is failure, not an approved result.

`ReviewInput`: `brief: StudioBrief`, `image_path: Path`, `image_sha256: str`, `parent_path: Path | None`, `keep: tuple[str,...]`, `change: str`. The host creates/attaches a target-width raster view in memory and passes the actual original plus that view (and parent original/view for edits) to both calls. Exact image hash and dimensions are persisted by the core. Raster views are review aids, never replacements for original artwork.

`Candidate`: `id`, `direction_id`, `parent_id: str | None`, `image_path` (workspace-relative canonical session original), `sha256`, `width`, `height`, `prompt`, `provider`, `model`, `critiques: tuple[Critique,...]`, `keep: tuple[str,...]`, `change: str`. Fields needed by gallery are stable. Additional internal validated bookkeeping fields may be added by the core worker after messaging consumers.

`Workflow`: `schema_version=1`, `id`, `revision`, `brief`, `phase`, `strategy: Strategy | None`, `directions`, `candidates`, `selected_id: str | None`, `jobs`, `feedback`, `delivery` (optional), `last_error: str | None`. Phase literals: `draft`, `planning`, `generating`, `reviewing`, `awaiting_choice`, `revising`, `ready`, `delivered`, `failed`, `outcome_unknown`, `cancelled`. `jobs`/`feedback`/`delivery` internal models are core-owned; gallery shows candidates even during failure/unknown outcomes.

`StudioError(code: str, detail: str)` is the typed boundary exception.

## Host protocol (`logopia_studio.protocols`)

Synchronous, finite methods; host owns model and image transport. No filesystem lock held across these calls.

```text
class DesignHost(Protocol):
    plan(brief: StudioBrief) -> PlanResult
    generate(prompt: str, parent: Path | None, background: str) -> GeneratedImage
    critique(request: ReviewInput) -> tuple[Critique, ...]
```

The core verifies exactly two critique roles. `HermesHost(ctx)` implements the protocol in `host.py`. It calls separate strategist and art-director structured completions, then two independent image-based critics when asked. Leave provider/model/profile overrides unset. Record actual result attribution. It uses `ctx.dispatch_tool("image_generate", args)` exactly once per generate; for an edit pass the exact parent as `image_url`, square aspect and no upscaling. Parse the native JSON `success`/`image`/attribution response; only an actual local regular PNG is an accepted result. Do not treat a JSON success flag or provider requested resolution as image validation.

## Engine (`logopia_studio.engine`)

```text
Studio(workspace: Path, helper_repo: Path, host: DesignHost)
    create(workflow_id: str, brief: StudioBrief) -> Workflow
    status(workflow_id: str) -> Workflow
    produce(workflow_id: str, expected_revision: int) -> Workflow
    revise(workflow_id: str, expected_revision: int, candidate_id: str,
           keep: tuple[str, ...], change: str) -> Workflow
    choose(workflow_id: str, expected_revision: int, candidate_id: str) -> Workflow
    deliver(workflow_id: str, expected_revision: int) -> Workflow
```

`create` is local only, idempotent only when the entire brief is equal; conflicting reuse fails. `produce` plans once, generates the agreed count (one request per candidate), imports and critiques actual originals, then stops at awaiting_choice. Resume reuses completed planning/images; an unknown in-flight image prevents an automatic new request. A critique failure preserves the original and permits a critique-only resume. Completed production never regenerates on a repeated produce request.

`revise` requires an exact existing candidate and nonblank change; keeps the chosen parent, records keep/change, creates one child native call, imports and reviews the child. At most two dispatched edit calls per workflow, including unknown/failed calls. Never overwrite the parent, reset counters on restart, or copy the parent's review to a child.

`choose` records an explicit decision; it does not approve visual quality. A fully reviewed candidate can become ready, otherwise remains awaiting_choice with its unmet criteria. `deliver` requires selection, the two valid actual image critiques and all required checks; invokes the existing helper review/select/export and records its actual verified output. Repeating delivery returns the existing verified receipt, no duplicate package. Existing PNG decode/hash/background/color gates stay authoritative.

Store/load verifies candidate originals via the existing helper (the exact session). Source/helper files are not copied wholesale into the native plugin. Short workflow locks and optimistic revisions reject overlap; active/unknown jobs and cancellation need explicit observable states. Helper operations are subprocess argv with timeout and JSON boundary validation, not shell commands. A committed import followed by interrupted bookkeeping must reconcile the exact deterministic artifact/hash/parent/prompt rather than re-generate or overwrite.

The core worker may add explicit `interrupt`/`reconcile` helpers needed by the launcher, but must message their public signatures. Never resume an unresolved native call by guessing newest cache files or resetting revision numbers.

## Gallery (`logopia_studio.gallery`)

`publish_gallery(workspace: Path, state: Workflow, output: Path) -> Path` publishes a fresh self-contained folder and returns its `index.html` path. Copy actual original bytes/prompts with digest verification, immutable output and rollback of only owned files. No live server needed. Extra coordinator sample packaging is separate.

Use an ivory/ink surrounding UI and white original-image cards. Page hierarchy: brand/phase + one next action; short strategy; candidate grid; inline target-size preview/review/parent relation; optional details; feedback panel. State is a snapshot with workflow ID/revision and selected ID. Candidate preview/favorite does not change canonical selection. Feedback copy includes exact workflow/revision/candidate and keep/change text, labelled to send to Hermes. Include direct PNG links regardless of review; final ZIP link only if it truly exists. User strings escaped; no unsafe HTML/JS interpolation or remote calls. Keyboard, narrow viewport, reload, selection, clipboard fallback and no-result states are part of QA.

## Native registration and launcher

Plugin name/toolset: `logopia-studio`. Skill namespace: `logopia-studio:director`.

- `logopia_start` tool fields: `workflow_id`, `brief` (StudioBrief schema). It creates then produces and publishes a fresh gallery.
- `logopia_action` fields: `workflow_id`, `action` (`status`,`continue`,`revise`,`choose`,`deliver`), `expected_revision` (required for mutation), `candidate_id`, `keep`, `change` as appropriate. Status is read-only; continue calls produce. Strictly reject inappropriate/missing fields. Return a small JSON summary plus gallery/original paths, not full PNG/base64 or verbose reports.
- Tool callbacks resolve workspace/helper location from validated local `settings.json` installed by the coordinator. Model arguments never select arbitrary directories or command strings. Registration doctor must work without this file; invocations fail clearly until configured.
- Installer: copy plugin to `<explicit-profile-home>/plugins/logopia-studio`, write local settings with exact helper repo/workspace, enable only in that named profile. Default Hermes home/model unchanged. No repository-stored absolute developer paths or credentials.
- `studio.py` provides `install`, `run --request FILE`, `show --workflow ID`, `gallery --workflow ID`. `run` uses Hermes chat with exact query file/toolsets/skill and a hard owned-process deadline. Canonical state, not Hermes prose/exit code, determines completion. No hidden inference on show/gallery/install.

## Quality prompt requirements

Follow the existing craft, color, typography, app icon and IP guidance, with concise resources carried into the native plugin by the host worker. Meaning/construction differs across directions, exact lettering is explicit, colors have roles, no stock logo collage or staged mockup is substituted for an original. App/IP prompts follow their native corner/scale rules; do not put the internal word `opaque` into an IP prompt. Brand PNGs request pure white presentation unless transparent explicitly requested. Critique calls see the actual pixels and target size, concrete required fixes and regression checks; inference cannot promise legal uniqueness or expert certification.

## Gap review resolutions (binding; supersede shorthand above)

G1. Declare/check Pydantic >=2.12,<3 and Pillow >=11.2,<13. Test native code with `basedpyright --pythonversion 3.11`, real Hermes interpreter import and doctor, separately from repository Python3.12 tests. The installer reports missing dependencies; it does not install into or upgrade Hermes implicitly. Helper argv is exactly `uv run --locked --project <repo> python <repo>/skills/logo-land/scripts/logo_project.py --workspace <workspace> <command>`. Python3.11 protocol/type alias syntax takes precedence over recommendations for PEP695 syntax.

G2. Add engine `interrupt(workflow_id, expected_revision, reason)` and `reconcile(workflow_id, expected_revision, job_id)` with no inference. Interrupt is called after the owned runner settles; it marks a dispatched native call unknown, preserves results and never asserts provider cancellation. Reconcile considers only a recorded exact return/receipt/helper commit; absent evidence remains unknown, no cache guessing or new call. A status read does not interrupt active work. Native tool action may expose reconcile with job_id. Before each invocation reserve its operation/attempt/request digest: plan pair at most once (two roles, no automatic planning retry); initial image calls exactly the agreed count; edits at most two total; critique pair at most twice per candidate (second only on explicit continue after failure). Timeouts are 120 seconds per role, planning max_tokens 6000 and critique 2400, image concurrency one, launcher default hard deadline 1800 seconds and ten-second owned-process grace. Provider-internal retries are not claimed to be controlled by these logical-call budgets. Late returns may be retained but never change a cancelled choice or silently resume the sequence.

G2 settlement clarification from final review: after the ten-second graceful period, forced-stop verification has a separate ten-second budget, plus bounded cleanup of an active numeric-PID query. The launcher owns its newly created OS session; the helper keeps a separate process group in that session and remains in its separate locked Python environment. Numeric PID discovery must verify exact SID/PGID membership before signalling, preserve other sessions, and report inspection/budget failure rather than invent settlement. No process-name/argument/environment scan, IPC broker, Python pre-exec hook or watcher is needed. Installer recovery covers both rename operations and preserves an unresolved old backup instead of deleting it during temporary cleanup.

G3. Persist deterministic session/artifact IDs, parent/intent/prompt hash and export destination before each helper mutation. Recover import after helper commit by verifying the exact stored original/hash/parent/prompt/intent. Recover export after helper commit by verifying the helper ExportRecord, manifest, PNG and ZIP payload, then attach the missing receipt only. Never produce a duplicate package on resume or overwrite/remove foreign output. These are recoverable two-store operations, not atomic cross-file transactions.

G4. Add host-attached fields to `Critique`: `call_id: str`, `image_sha256: str`, `parent_sha256: str | None`, `view_sha256: str`, `view_width: int`. These are computed from actual inputs, not supplied by the model. The model supplies only role-specific summary/criteria; host parses strictly and binds attribution/evidence. Core accepts only matching original/parent/view conditions and unique design/production roles, each with five unique keys. A helper boolean is true only when both matching role criteria pass, except explicitly observed N/A for empty text or a new image's preservation. `needs_revision`/`not_observed`/other N/A fails. For edits, include/check parent target view as well, with additional hash field if needed and communicated. Failed reports cannot replace history or borrow parent approval.

G5. `StudioBrief.colors` is advisory. Add `color_policy: Literal[advisory] = advisory` so an explicit strict policy is rejected, not misrepresented. The director routes exact/strict palette workflows to the existing skill/helper path. This initial `revise` preserves exact text, colors and background; its scope is construction, spacing and detail changes. The director explains an incompatible text/background/palette request before calling it; a new brief is a separate workflow. Extra structured overrides fail validation. Prompt/import/review all use the same saved intent, with explicit `--background` on every import. Do not claim semantic detection of every possible conflicting natural-language request.

G6. Core exports strict `FeedbackEnvelope`: `schema_version: Literal[1]`, `workflow_id`, `expected_revision`, `candidate_id`, `candidate_sha256`, `action: Literal[choose,revise]`, `keep: tuple[str,...]`, `change: str`. Cap individual notes at 2000 characters and total accepted request file/tool payload at 32 KiB. Choose requires empty change; revise requires nonblank change. The gallery copies this exact JSON as a draft. Registration accepts those fields for choose/revise and checks candidate hash before mutation. Engine choose/revise signatures stay as above; host verifies hash against the loaded revision and the engine CAS rejects intervening state changes. Stale feedback is a no-call error; do not silently substitute the latest revision. User can explicitly reapply to current state via Hermes after seeing the change. No-JS still shows originals/identity and explains that feedback drafting needs JavaScript.

Local `settings.json` is strict schema 1: `schema_version`, absolute `workspace`, absolute `helper_repo`. It is an installed-local file, never part of public package content or a model-supplied argument. Settings are not read during module import/doctor. The main native tools are `logopia_start` and `logopia_action`; keep their names stable.

G7. Real execution exposed Hermes's separate 420-second tool-executor limit. Installation configures `timeouts.tools.sequential_call` and `timeouts.tools.concurrent_batch` to 1800 seconds through the public CLI in the explicit named profile only. The owned process deadline remains finite and independent. A settled process with an unfinished job must not be described as a launcher timeout unless that actually happened. An explicit `continue` may retire an unknown **read-only critique** and consume its one remaining review attempt, preserving the original job/error and all saved images/planning. `engine_recovery.can_resume_critique(state)` exposes that narrow eligibility to launcher preflight. Unknown plan/image/edit/delivery, active jobs, exhausted review budgets and stale requests remain blocked. A late superseded critique cannot replace a newer result. Repeating `logopia_start` in a failed, cancelled or unknown state does not retry; only explicit continuation can do so. This clarification permits review recovery, never automatic image resubmission.
