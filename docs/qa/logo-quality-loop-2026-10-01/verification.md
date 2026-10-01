# Verification: bounded logo design loop

Execution date: 2026-10-01. Source: 0.10.0 working tree, based on main `1d620642ca55c83e3cd129ee287160f842960d34`. New production modules and tests are included even before git staging. Published release remains 0.8.0.

## Runtime and independent review

The final focused suite passed **41 tests**: 38 quality-loop tests and three real CLI scenarios. It covers prompt/parent/intent binding, fixed scope, hash/evidence drift, legacy v1/v2 byte preservation, stale revisions, unknown outcomes, failed-call budgets, repeated defects, edit improvement/preservation and no implicit selection or export.

Independent review and the fresh skill test found issues that were fixed and retested:

1. A valid text-free `abstract` brief was rejected by symbol-only scope. The unchanged forward-test input now succeeds.
2. A failed refinement/reframe could lose its controlling critique on the next request. Failed retries now retain exact prompt, parent, direction and charges, including repeated failures.
3. An already imported result could be labeled a failed call to bypass criticism. Known returned artifacts now require critique.
4. Legacy timestamps without a timezone could raise an unhandled comparison error. The boundary now reports a typed error without rewriting legacy bytes.
5. Reframing to a new subject carried old shape-specific criticism into its prompt. The ledger retains the criticism while the new native request does not import the rejected subject's geometry.

The independent re-audit reported no remaining must-fix findings and reran all 41 focused tests. Hashes verify file identity and bindings; host-supplied observation and view descriptions still require honest visual inspection.

## Checks

| Check | Result |
| --- | --- |
| Initial full pytest run | 1,129 passed in 405.71 seconds; preceded final review fixes |
| Final full pytest run | **1,138 passed in 366.14 seconds** on the final production source |
| Ruff check | Passed |
| Ruff format check | Passed; 582 Python files |
| basedpyright | 0 errors, 0 warnings, 0 notes |
| uv lock --check | Passed; no dependency updates |
| Official skill/plugin validators | Passed in skill and staging checks |
| Independent skill forward test | Passed after the preserved scope failure was corrected |
| Native production | Five real calls, three generations, two exact-parent edits; original bytes and exact prompts verified |
| HTML | Final five-candidate data, both parent comparisons, five size controls and all 15 local assets passed Node/byte checks; local HTTP returned 200. No GUI claim. |

[Initial full log](pytest-initial.txt) · [Final full log](pytest.txt) · [Actual production](native/index.html).

The earlier untracked Hail Mary research and plan were preserved. No public tag or release is created by this update. Local installation is recorded separately in [installation.md](installation.md).

The subsequent [sample rejection and instruction correction](showcase-followup.md)
and [two-document plugin refresh](installation-followup.md) are separate from the
runtime verification above. None of these technical checks establishes improved
design quality.
