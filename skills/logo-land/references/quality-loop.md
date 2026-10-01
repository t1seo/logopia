# Bounded logo development

Use this branch for a brand-logo task with delegated design judgment or requested
quality improvement. Keep quick exploration in the fast path when no quality
objective is active or the user explicitly switches to quick/single-pass work. The
helper coordinates real native-host requests and evidence; it never calls an image
model itself, judges beauty automatically or grants brand adoption.

For a collection, retain quality development for each brief and declare one
collection-wide call budget; do not silently multiply the budget by the number of
examples. Different brands need separate records. Asset types unsupported by this
harness use a manual ledger with the same critique and next-action discipline.
A request for multiple examples does not itself authorize single-pass treatment
of an ongoing quality-improvement task.

This version starts with a new direction and can refine the children it creates.
It cannot seed the first request from an already selected artifact. For an edit of
an existing chosen logo, use the skill's exact-parent Refine workflow, retain the
same observation/keep/change discipline and manually record the finite call budget.
Do not generate a replacement merely to make it fit this harness, or claim the
existing artifact was a verified loop parent.

## Working persona and handoffs

Use a composite senior identity designer's working habits, grounded in
[logo-foundations.md](logo-foundations.md), rather than a famous designer's name or
style. Figma's [critique practice](https://www.figma.com/blog/design-critiques-at-figma/)
distinguishes early exploration from focused problem solving; Adobe's
[logo process](https://www.adobe.com/creativecloud/design/discover/modern-logo-design.html)
moves from research and sketches to selected artwork and revision. The following
roles and state contract are Logopia's implementation of those principles.

| Role | Input and work | Handoff |
|---|---|---|
| Brand researcher | Read the real brand, products, existing assets and use conditions. Separate facts from assumptions. | A short sourced brief; fixed decisions, variable decisions and success criteria. |
| Identity designer | Explore different organizing ideas. Specify contour, proportions or solid/empty relationships and the risk to inspect. Do not combine all meanings into one symbol. | Direction hypotheses, native requests and unchanged returned originals. |
| Independent critic | See neutral IDs, fixed brief and actual images before the generator's rationale. Record first-read form, specific weak regions and unknowns; then compare intent. | Evidence-bound critique and a next action, including no suitable candidate. |
| Craft refinement | Work on the exact viable parent. Change one or two relationships while retaining its identifying feature. Compare the same views afterward. | Actual child, requested-change outcome, preserved features and regressions. |

These are responsibilities, not a requirement to spawn four agents. Delegate the
critic when available. A new role label in the same context does not make review
independent. Disclose self-review when separation is unavailable. Judge the mark
before polishing its presentation; never repair a weak first-read shape with a
longer brand story.

## Freeze the contract and budget

Create or resume a normal session first. Its brief, source artifacts and effective
palette/lockup remain the source of truth. A loop lives separately at
`.logo-generator/quality-loops/<loop-id>/loop.json`; it does not migrate or approve
the session.

Record the source evidence, requested uses, exact scope and settled decisions. For
example, Hail Mary's existing typography stays fixed and a symbol-only task has
empty `exact_text`, empty slogan and no lockup. Existing letter assets may appear
in a separate context preview; the generated symbol must not reinvent them.
`symbol_only` accepts text-free `symbol` or `abstract` source briefs; keep the
distinction described in [logo-directions.md](logo-directions.md). It does not accept
an app-icon intent, generated initials or a text lockup.

Choose two to six genuinely different direction hypotheses, not six names for the
same structure. A default budget is six native calls; the contract accepts one to
twelve. A user's smaller budget wins. State the chosen bound and proceed; delegated
work does not need another permission gate. Each `loop-request` reserves and charges
one call before dispatch, including edits and corrective background/color attempts.
Failed and unknown outcomes are not refunded. Stop earlier when there is no useful
next action. This version advances one pending request at a time: the critique
chooses whether to develop that line or move to another planned direction. It does
not generate a batch and automatically rank a winner.

This shell setup uses a fictional symbol brief and creates no image. Run from the
repository root after `uv sync --locked`, using a fresh example workspace. For an
installed copy, resolve the helper as described in [project-files.md](project-files.md).

```sh
LOGO_REPO="$PWD"
LOGO_WORKSPACE="$LOGO_REPO/output/quality-loop-example"
mkdir -p "$LOGO_WORKSPACE"
ll() {
  uv run --locked --project "$LOGO_REPO" python \
    "$LOGO_REPO/skills/logo-land/scripts/logo_project.py" \
    --workspace "$LOGO_WORKSPACE" "$@"
}
cat > "$LOGO_WORKSPACE/brief.json" <<'JSON'
{
  "brand_name": "Morrow",
  "exact_text": "",
  "industry": "A fictional personal reading-note service",
  "audience": "Casual readers keeping their own notes",
  "logo_type": "symbol",
  "background": "opaque",
  "palette": ["Dark ink symbol on solid white"],
  "forbidden": ["Lettering", "A stock book pictogram"],
  "use_cases": ["A 32px symbol next to existing header typography"]
}
JSON
cat > "$LOGO_WORKSPACE/contract.json" <<'JSON'
{
  "session_id": "morrow-symbol",
  "scope": "symbol_only",
  "fixed_typography": true,
  "fixed_decisions": ["Symbol only; existing typography is outside this task"],
  "source_evidence": ["Fictional demonstration brief; no external brand claims"],
  "success_criteria": [
    "An identifiable contour without lettering or a stock book pictogram",
    "The identifying relationship remains visible in the 32px header context"
  ],
  "use_contexts": ["32px symbol on white beside the existing text asset"],
  "directions": [
    {
      "id": "continuous",
      "idea": "A quiet continuous shape with a distinctive internal rhythm",
      "structure": "One connected contour with a broad asymmetric opening",
      "distinction": "Identity is carried by the silhouette and opening"
    },
    {
      "id": "paired",
      "idea": "A compact relationship between two deliberately unequal parts",
      "structure": "Two masses whose spacing creates one recognizable interval",
      "distinction": "Identity is carried by proportion and the shared interval"
    }
  ],
  "call_budget": 6
}
JSON
ll init --session morrow-symbol --brief "$LOGO_WORKSPACE/brief.json"
ll loop-start --loop morrow-study \
  --contract-file "$LOGO_WORKSPACE/contract.json"
ll loop-request --loop morrow-study --revision 0 --direction continuous \
  > "$LOGO_WORKSPACE/request-1.json"
```

The example directions illustrate the contract, not a recommended universal style.
Design actual hypotheses from the user's brand. Surface constraints also follow the
brief; white and flat geometry do not override requested expressive treatments.

## Execute the reserved request exactly

For an authored art direction, add `--prompt-file PATH` to `loop-request` before
reserving the call. The file supplies the exact UTF-8 native prompt, including its
line endings; it must be nonempty and at most 20,000 characters. This replaces the
compiled wording and appends no scope, palette or refinement instructions. Include
the applicable exact lettering, fixed decisions, intended color/background roles
and, for an edit, the parent features to preserve and specific changes. Read the
saved request before dispatch. Short wording is a creative option, not evidence
that output quality will improve.

The override changes only the prompt. Source revision, effective intent, parent,
contract, budget and import checks remain bound. Pending or unknown requests
cannot be rewritten. After an established failed call, retry at the same source
revision with the original exact prompt; omitting `--prompt-file` reuses it.
Changing the direction, palette or prompt is not a retry. An exceptionally large
app-icon brief can still fail the legacy icon builder's length check before an
override is applied; the failure does not reserve or charge a call.

Every command returns a wrapper with `state`, `status`, `calls_used`,
`remaining_calls` and `pending_request`. Use `state.requests[-1].input` from the
successful request result; its `prompt` is the exact native request and its
`revision` is the **source session** revision. The loop's `state.revision` is a
different counter. Do not derive either counter by guessing the number of images.

Save the prompt string without rewriting it:

```sh
uv run --locked --project "$LOGO_REPO" python - \
  "$LOGO_WORKSPACE/request-1.json" "$LOGO_WORKSPACE/request-1.txt" <<'PY'
import json
import sys
from pathlib import Path

result = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
request = result["state"]["requests"][-1]["input"]
Path(sys.argv[2]).write_text(request["prompt"], encoding="utf-8")
print(json.dumps(request, ensure_ascii=False, indent=2))
PY
```

Read [native-image.md](native-image.md) and dispatch through the real host tool:

- For `mode: "generation"`, send the exact `prompt`. This loop currently has no
  image-reference-plan option; source evidence is context, not image conditioning.
- For `mode: "edit"`, inspect and attach exactly `parent_image_path` using the live
  tool's supported local-image parameter. The observed native tool uses
  `referenced_image_paths: [parent_image_path]`. Keep `parent_id` for import.
- Do not condense the saved prompt, substitute another parent, add a mockup request
  or invent tool parameters. If the request is unsuitable, stop and record the
  reason; do not silently change the reserved operation.
- Preserve the actual call receipt, provider/tool identity, returned original path
  and hash. Model identity stays unknown if the tool does not report it.

Import the PNG identified by that call with the existing `import` command. Use the
saved prompt file, `input.revision`, the same `parent_id`, effective `palette_id`,
lockup and expected background. Omit absent options. Save the resulting artifact ID
and SHA. For this first example only, the source revision is zero, the parent and
palette are absent and the background is opaque:

```sh
# Set this to the exact PNG path returned by this native call.
LOGO_RETURNED_PNG="/absolute/path/from/the/native-call.png"
ll import --session morrow-symbol --artifact continuous-v1 \
  --image "$LOGO_RETURNED_PNG" --prompt-file "$LOGO_WORKSPACE/request-1.txt" \
  --revision 0 --background opaque
```

This command imports a real result; it does not create one. Never substitute a
fixture, an unrelated latest file or a manually drawn shape and label it native
output. Import may update the source session; it does not consume another call or
change the loop revision.

## Critique the actual result

When improvement is requested, retain the relevant earlier result as a baseline.
Compare actual images at matching intended sizes under neutral IDs and record
whether identity, form, spacing and use-size behavior improved. Background repair,
correct spelling, file integrity or agreement with the proposed direction alone
does not establish better design. If meaningful improvement is not observed,
report that outcome and keep the results experimental. A user's rejection remains
the acceptance state even when technical checks pass; do not promote those images
as successful representative work in a README or gallery.

User acceptance is separate from the harness's critique actions. A user rejection
does not require `decision: "reject"` (which schedules an unused direction); use
`stop` when no useful direction remains. Keep feedback beside the run record. A
terminal loop stays historical; further authorized development starts a linked
new loop with an explicit remaining or renewed budget, not a silently reset one.

Open the original and required use-size/context views. Give the critic neutral IDs
and the fixed brief before direction names, intended metaphors or a suggested
winner. Capture actual rendered evidence when the available tools permit it. A
gallery definition alone is not evidence that someone inspected its small view.
Use `not_observed` when rendering or inspection is unavailable.

Write a `Critique` JSON file using these fields:

| Field | Required content |
|---|---|
| `request_number`, `artifact_id`, `artifact_sha256` | The pending request and actual newly imported original, not an earlier image |
| `reviewer` | Who performed the inspection and whether it was independent or self-review |
| `evidence` | One or more objects with unique `id`, workspace-relative PNG `path`, file `sha256`, `source_artifact_sha256`, `kind` and an honest `description`; `target_width` when relevant |
| `assessments` | Exactly one entry for each criterion below, with `criterion`, `status`, concrete `observation` and `evidence_ids`; a `revise` entry also requires a stable `issue_id` such as `lower-gap-width` |
| `decision`, `reason` | The next action and why it follows from the visible result |
| `preserve`, `changes` | Features to keep and one or two actionable changes for `refine` |
| `change_result` | `initial` for fresh generation; `improved`, `unchanged`, `regressed` or `not_observed` for an edit, based on the requested change |
| `preservation_result` | `pass`, `revise` or `not_observed` for whether an edit retained its required identifying features |
| `next_direction_id` | A different unused contract direction for `reframe` or `reject` |
| `unresolved` | Remaining defects, unavailable checks and material uncertainty |

Evidence kinds are `original`, `target_size`, `one_color`, `inverse` and `context`.
File hashes bind the supplied evidence, but cannot prove the reviewer saw it or
that a context image was faithfully made. Preserve that provenance separately.
Do not relabel the large original as a target-size screenshot to satisfy a gate.

The seven criteria are `appropriateness`, `distinctiveness`, `form`, `optics`,
`use_size`, `versatility` and `scope`. Each status is `pass`, `revise` or
`not_observed`. Observed statuses cite real evidence IDs. These are reasoned
judgments with separate unknowns, not scores to average. `versatility` refers to
the required use contexts, not every possible medium or a compulsory monochrome
variant. A color-dependent title must retain its intended expression.

For a child, explicitly compare the requested change, preserved identifying
features and any regressions against its real parent at matching sizes. A smoother
curve does not compensate for loss of identity. Never claim user recall, legal
uniqueness or market preference from these observations.

An edit can advance with `refine` or `ready` only when its requested change is
`improved` and preservation is `pass`. Keep the same `issue_id` when the same
visible defect persists. If a parent and child both require revision for that
criterion and issue, the harness blocks another local refinement; reframe or stop
and record the limitation. A genuinely different new defect gets its own ID;
`not_observed` remains uncertainty rather than proof of stagnation. Do not rename
a persistent failure merely to obtain another call.

```sh
ll loop-record --loop morrow-study --revision 1 \
  --critique-file "$LOGO_WORKSPACE/critique-1.json"
ll loop-show --loop morrow-study
```

Here `1` is the loop revision after the example's first reservation. In resumed
work, use the current revision from `loop-show`.

## Let the critique choose the next action

| Decision | Use when | Next request |
|---|---|---|
| `refine` | A worthwhile identifying idea has one or two concrete defects | `loop-request` compiles keep/change notes and attaches the reviewed original as parent |
| `reframe` | The organizing idea is weak or unsuitable | Select a different unused contract direction; no edit parent |
| `reject` | This line should not advance, including a child with damaging drift | Preserve all originals and move to a different unused direction |
| `ready` | Every criterion is observed as passing for the contracted uses and no unresolved issue remains | Terminal `ready_for_user_review`; no selection or export approval |
| `stop` | Further work in this contract cannot be justified or verified | Terminal `stopped`, with the unresolved reasons preserved |

After a nonterminal critique, call `loop-request --loop ID --revision N` using the
new loop revision. It carries the decision forward; do not independently reroll
the same prompt. Read the exact new request and repeat the native/import/critique
sequence. A rejected child's parent remains unchanged, but this version does not
automatically rewind the loop to refine that parent again.

If the call failed, record it with `loop-failure --loop ID --revision N --request K
--outcome failed --reason 'Observed failure'`. If the host was interrupted or the
outcome is uncertain, use `--outcome unknown`. Unknown remains pending and charged:
reconcile the actual result or explicitly establish failure before another call.
Do not reset the ledger, retry secretly or grant a fresh budget by changing loop IDs.

When the budget is exhausted, the loop ends unresolved unless a real critique
already established readiness. Preserve the strongest supported parent or state
that none qualified. Report what was inspected, what improved, what did not and
the useful next method. If raster edits repeatedly cannot control a necessary
curve or gap, a verified vector construction handoff may be the next step; do not
claim that conversion has already occurred.

The harness validates sequence, scope, provenance, evidence links and budgets. It
cannot guarantee taste, distinctiveness or better model output. The Hermes adapter
has its own exploration flow and does not automatically execute this native-host
loop. Creative preference, user approval and the existing export checks stay
separate in both paths.
