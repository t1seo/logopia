# Follow-up: sample rejection and routing correction

Date: 2026-10-01. This supplements, rather than replaces, the earlier runtime
[verification](verification.md). No Python production source changed during this
follow-up. The full 1,138-test result verifies the helper's behavior, not logo taste.

## Observed failure

Six new use-case samples bypassed the bounded design-development workflow. Each
started with one generation; two received background cleanup. The user rejected
all six for insufficient design quality and no meaningful improvement. This
feedback supersedes any earlier assistant recommendation; PNG and browser checks
do not supersede the user's acceptance state.

Both READMEs, gallery indexes and the six-card HTML now preserve those results as
rejected experiments. The README image tables are collapsed by default. Earlier
collections remain historical, not alternative proof of current quality.

## Instruction change and forward check

A separate read-only agent evaluated the on-disk instructions against three
scenarios:

| Scenario | Observed routing |
| --- | --- |
| Quality improvement followed by six README examples | Retain quality development, separate brand records and an explicit collection-wide budget |
| New request for three quick, one-pass icon ideas | Fast exploration with the requested three, without automatic quality retries |
| All candidates rejected although PNG/link checks pass | Preserve rejection; continue only with a useful next action inside the budget, or stop |

The check exposed two instruction ambiguities, which were clarified: an explicit
user switch to quick exploration takes precedence; user acceptance is separate
from the harness action `reject`, which requires a next unused direction. Terminal
loops remain historical; a later authorized loop records its relationship and
budget explicitly. The host chooses the collection ledger location; no new
cross-session scheduler was implemented. This is a routing check, not evidence of
improved output quality.

## Verification scope

- Official skill and plugin validators passed after the final instruction edit.
- All 103 skill payload files match the actual refreshed local cache; see the
  [installation follow-up](installation-followup.md).
- The six-example documentation worker checked 756 local references, HTML
  structure, IDs/ARIA and default-collapsed details. Subsequent Pebble links were
  checked separately.
- Official Codex Computer Use inspected the six-example gallery's image loading,
  2/3/1/6 filter counts, brief details and original-image navigation. These are
  browser usability checks only. It did not test a narrow device viewport,
  cross-browser behavior, every link or disk downloads.
- The [focused Pebble comparison](../../showcase/2026-10-01-pebble-study/README.md)
  retains the old result, actual new calls and independent criticism. It does not
  constitute an approved identity or a successful production showcase.

Local browser screenshots include unrelated browser chrome, so they remain under
ignored `output/` paths. Public HTML preserves the image references and CSS display
conditions, not a claim that its source alone proves visual inspection.
