# Intentional icon craft, 2026-09-19

Continue the existing helper/Hermes architecture at baseline `d7d3cd40e00ca602d1900a016f0db714bc961930`. No provider connection, push, deployment, release, new backend, or native-package claims. Preserve originals, existing sessions, exact strings, and default call counts.

## Work ledger

1. **Complete:** inspect representative original PNGs and actual-size views against saved prompts; preserve baseline; verify R1–R11 and ~6 diverse first-party image references in an ignored cache. Record observations, code causes, and hypotheses separately.
2. **Complete:** connect verified visual reference evidence and explicit positive/negative roles to helper prompts/native request plans; product-aware construction and removal of unrelated defaults. Test missing/corrupt references, precedence, no-reference compatibility, parent separation, and unsupported tool capabilities.
3. **Complete:** add optional platform asset intent and role-specific validation/handoff without pretending flattened PNGs have layers. Test foreground alpha, background opacity, dimensions, Appearance vocabularies, immutable preview originals.
4. **Complete:** extend existing gallery with 48px and balanced context; provide blind A/B and evidence-bound preference records separate from QA, AI recommendation, and selection. Test all four outcomes and no implicit approval.
5. **Complete:** separate Hermes directions/candidates, preserve default 3 (IP 6), support opt-in 3×3 with bounded generation/edit/review/recovery, provenance and resume invariants. Test uncertain outcomes and old state.
6. **Complete:** execute a native-tool 3 baseline / 3 improved comparison with saved exact prompts, outputs, receipts/settings and ≤12 generation/edit calls total; if unavailable record actual failure without paid fallback or ambiguous retries. User preference remains unverified.
7. **Complete:** full pytest/ruff/type checks, actual CLI/browser QA, post-implementation review, concise docs and usage examples. Final suite: 1059 passed; all five review perspectives passed after corrections.

## Interfaces and ownership

- Root: helper reference conditioning/prompt connection, focused prompt defaults, existing PNG observations, baseline experiment, integration docs/QA.
- Research: `docs/research/icon-craft-2026/{sources.md,references.json}`, ignored first-party image cache.
- Platform: helper asset models/policies/import/export checks and associated tests, isolated new CLI registration.
- Gallery/preference: helper gallery and isolated preference models/CLI/templates/tests.
- Hermes: native workflow models/host/pipeline/budgets/launcher/gallery metadata/tests/director guidance.

## Checks and constraints

- Preserve the current 3-image fast path, with no automatic extra material or layer stage.
- Job counts differ from actual calls: planning and critique currently each dispatch two LLM completions. Track budgets honestly; never automatically resend an unknown image outcome.
- Hermes has one `image_url`: parent plus reference cannot both be image-conditioned. Use reference pixels in multimodal planning and report textual transfer explicitly.
- Helper default is flattened artwork; platform-native deliverables require real user-supplied layers and external tools.
- Research images stay ignored. Citations are not redistribution permission. Automated references never become user preference.
- QA: `uv run pytest -q`, `uv run ruff check skills/logo-land/scripts integrations/hermes tests`, `uv run ruff format --check skills/logo-land/scripts integrations/hermes tests`, `uv run basedpyright`, real CLI examples and browser controls.
- Human approval, OS rendering, store approval, global uniqueness, and causal design-quality gains are never inferred from tests or AI review.

## Completion evidence

Six native originals (3 baseline + 3 improved), exact prompts and call receipts are in `docs/research/icon-craft-2026/experiment/`. No additional image calls; user preference remains unverified. Research sources and six reference plans are connected to actual CLI/model inputs. Browser QA preserved 18 PNG hashes. The first full suite passed 1043 tests; parent-background/IP-validation followups passed targeted tests and the final full run passed 1059 tests in 340.37s. Ruff, format and type checks passed. See `docs/qa/icon-craft-2026/README.md` for exact commands and review findings. No provider setup, push, release, or deployment occurred.
