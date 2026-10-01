# 0.9.0 source verification — 2026-10-01

The update is unreleased. These checks cover implementation and provenance; they do not certify professional logo quality or user preference.

## Production changes checked

- Optional strict, absent-omitted brand strategy in helper briefs; fresh brand generation only.
- Explicit text, user styles, effective palette/lockup and parent edits retain priority.
- Conditional white/flat defaults preserve explicit surfaces, transparent canvases and strict color limits.
- Effective palette roles/constraints reach the image while stored provenance remains intact.
- Hermes saved strategy reaches native requests within the existing 20,000-character contract. Generation-only advice is excluded from parent edit context without trimming user direction or feedback.
- App icon/IP paths, state compatibility, original bytes and delivery gates remain covered.

## Command evidence

The final frozen-source suite passed: **1,097 tests in 371.88 seconds**, exit 0. The first broad implementation run overlapped the final Hermes compatibility correction; its stale parent-advice assertion is preserved in [the intermediate log](pytest-intermediate.txt) (1 failed, 1,092 passed). After correcting the contract and adding exact-boundary regression cases, the entire suite was rerun against the final source. Production SHA-256 values remained unchanged during that final run.

| Check | Observed result |
| --- | --- |
| Full pytest suite | [1,097 passed](pytest-final.txt), exit 0 |
| Ruff | [All checks passed](ruff-check.txt) |
| Ruff formatting | [238 files already formatted](ruff-format.txt) |
| Basedpyright, project | [0 errors, warnings or notes](basedpyright.txt) |
| Basedpyright, Hermes Python 3.11 | [0 errors, warnings or notes](basedpyright-hermes.txt) |
| `uv lock --check` | Passed; 23 packages, only project version changed |
| Official plugin validator | Passed against this checkout |
| Official skill quick validator | Skill is valid |
| LSP error diagnostics | No diagnostics for the 12 changed/new Python files |
| Node comparison/gallery logic | [13 passed, 3 browser tests skipped](node-checks.txt) |
| Independent code audit | P2 length regression fixed and rechecked; no remaining actionable finding |
| Independent goal/source audit | Approved; all 74 recorded generation-source hashes and six original PNG hashes match |

Official validators were read from the installed `.system/plugin-creator` and `.system/skill-creator` script directories. The skill validator used a temporary `uv --with pyyaml` environment; no dependency was added to the project.

The Node browser tests need separate browser tooling and were not run. They are distinct from the 13 logic checks and are not evidence of rendered UI behavior.

## Scenario evidence

- [Helper contracts and actual CLI receipts](helper-contracts.txt): prior focused regression checks, Unicode/parent preservation and legacy behavior. Synthetic PNG checks establish plumbing only.
- [Hermes contracts](hermes-contracts.txt): public workflow through the real engine/store/helper, with external inference supplied by a fixture. This is not a native model quality trial.
- [Independent skill forward evaluation](skill-forward-evaluation.md): explicit beige dimensional title, exact Hangul spacing and strict two-color transparent logo requests.
- [Native comparison](README.md): all six actual native tool calls and untouched originals, exact prompts and source/copy/import SHA equality.
- [Blind visual observations](blind-observations.md): reviewer saw neutral A/B originals and fixed briefs only; [mapping](blind-mapping.json) was disclosed afterward.

## Limits

Official Codex Computer Use was not available in the exposed tools or installed runtime. No fallback GUI provider was used. HTML structure and local links were checked, and all original PNGs were directly viewed; actual CSS display-size rendering and 32/96/180px visual approval remain unverified. Nothing was exported or marked approved to bypass that gap.

The revised samples were preferred by one AI reviewer, only slightly for the Korean wordmark. Heavy lettering, possible wave associations and symbol proportions remain concerns. Six samples with unreported model/seed parameters are a limited workflow check, not evidence of universal improvement. Recraft was researched and documented as optional; no OAuth connection, paid Recraft call, SVG exporter or actual font typesetting was added.

At the time of this verification, no git commit, tag, push or public release had been performed. The subsequent user-authorized commit, push and merge are publication steps; they do not change the recorded test or image evidence. Version 0.9.0 remains untagged and unreleased.

## Personal installation

[Installation preparation and refresh record](installation-refresh.md) tracks the previous 0.6.0 cache and its retained backup. The official CLI installed and enabled `logo-land@personal` as **0.9.0+codex.20261001103046**. All 293 personal/cache files match; the 107 production files match the source snapshot except for the intended manifest cache version. Installed validation and standalone helper execution passed. Unrelated configuration and the marketplace remain unchanged.

Repository metadata stays clean `0.9.0`. The installed QA documents are the installation-time snapshot; this final installation summary was written afterward. A new conversation is required to load changed skills; the running session's skill catalog is not refreshed in place.
