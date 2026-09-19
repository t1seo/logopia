# Hermes icon craft verification · 2026-09-19

The implemented API and a validated launcher JSON example are in [CONTRACT.md](CONTRACT.md).
No paid provider was connected and no image-generation service was called by this verification.

- `uv run ruff check integrations/hermes tests/hermes`: passed.
- `uv run ruff format --check integrations/hermes tests/hermes`: 117 files formatted.
- `uv run basedpyright --pythonversion 3.11 integrations/hermes tests/hermes`: 0 errors/warnings.
- Focused host/reference/exploration/icon tests: 69 passed; the additional interrupted-fifth-slot
  reconciliation scenario passed separately.
- Full Hermes suite: **338 passed, 1 failed** in 262.58s. The failure was
  `test_unmodified_draft_is_not_reported_as_produced`: unchanged process-settlement code
  returned `process_inspection_failed: pid_listing` before the expected postcondition check.
  Its isolated rerun passed (0.78s). The underlying transient cause is not established;
  the failure is retained rather than reported as a green full run.

The new tests cover actual local PNG bytes entering both structured planning calls,
hash-bound observations reaching generated prompts, unsupported conditioning, corrupt/missing/
changed references, exact edit-parent separation, helper import/provenance, old no-reference
models, requested Hangul text, 3×3 slots, 11-image total including two edits, explicit review
budgets, unknown-call preservation and recovery from a recorded fifth-slot return.
Model transport uses explicit deterministic fakes; these tests prove wiring, not design quality.

Actual installed Chrome 153.0.8010.52 opened the native offline Gallery. Both surroundings
rendered 32/48/64/128 CSS pixels exactly; context icons were all 48px. The 390px viewport had
no horizontal overflow. Feedback retained candidate identity and did not change canonical
selection or original hashes. There were no page errors or external requests. Owned browser
contexts and temporary profiles were closed and removed. A first harness run compared an
array of two widths against a scalar; the corrected assertion and successful rerun are retained.

- [Gallery fixture](../../output/icon-craft-2026/hermes-ui-qa/gallery/index.html)
- [Browser receipt](../../output/icon-craft-2026/hermes-ui-qa/browser-receipt.json)
- [Desktop](../../output/icon-craft-2026/hermes-ui-qa/desktop-diagnostics.png),
  [mobile](../../output/icon-craft-2026/hermes-ui-qa/mobile-diagnostics.png)

These ignored local artifacts use synthetic artwork solely for functional QA. Human preference,
real-provider reference-conditioned quality, OS rendering and native platform acceptance remain
unverified here. Hermes generation is explicitly text-conditioned from multimodal reference
analysis; its single image input remains the exact edit parent. Native layers/adaptive packages
and store listing dimensions are handled by the helper's separate validation and handoff.
