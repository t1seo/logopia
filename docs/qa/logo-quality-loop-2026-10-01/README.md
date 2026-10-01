# Logo design loop: research, implementation and actual production

2026-10-01 · Source 0.10.0, unreleased. This record separates design research, runtime correctness and the actual images. It does not claim that passing software tests produces a good logo.

## Diagnosis

The strongest observed failure was a broken connection between criticism and action. Earlier Hail Mary reviews already identified generic folder, swoosh and pebble-like forms, yet those candidates were delivered without the criticism determining a new design action. Settled typography also drifted into a new type exploration. Some native prompts were rewritten after the helper prepared them, so there is no controlled evidence that the 0.9.0 prompt update itself caused an aesthetic regression.

The image model did miss some requested details. That supports a control limitation, not a conclusion that all logo AI is incapable or that a particular model regressed. The director's weak choices and the workflow's acceptance behavior were separate problems under our control.

- [Foundations: what a logo does and what makes it work](../../research/logo-design-foundations-2026-10-01.md)
- [Designer habits, critique and iteration practice](../../research/logo-iteration-practice-2026-10-01.md)
- [Audit of actual earlier outputs, prompts and decisions](../../research/logo-quality-failure-audit-2026-10-01.md)

The research uses Figma's public official guidance and practicing identity designers' first-party cases. It does not claim hands-on Figma editor or Community-file inspection. The persona is a synthesis of documented working habits, not impersonation of a named designer or a claim of human credentials.

## What changed

The [skill](../../../skills/logo-land/SKILL.md) now separates explicit quick exploration from delegated quality development. The latter uses a [persisted loop](../../../skills/logo-land/references/quality-loop.md): fixed brief and decisions, structurally different directions, exact reserved native prompt, actual original inspection, and an explicit refine/reframe/reject/stop decision. Independent critics first describe the visible form before seeing its author's story.

The helper reserves a finite call budget before host dispatch. It verifies imported original bytes, exact prompt, parent and effective intent, retains failed and unknown reservations, and compiles concrete criticism into the next prompt. A child must show improvement and preservation before further refinement or readiness. Repeated identified defects force redirection or stopping. Missing use evidence cannot be recorded as a pass. Legacy session schemas and selection/export gates remain separate.

This first harness starts new directions and their descendants. It does not seed an existing chosen artifact, invoke an image API, produce editable vectors or certify aesthetic quality. Hermes received coordination guidance within its existing tools and two-edit budget; its internal engine has not acquired the new automatic sidecar loop.

## Actual Hail Mary production

[Open the complete five-image process](native/index.html). Every displayed PNG is the actual native output. Both refinements supplied the exact inspected parent image. Existing Inter typography was outside image generation throughout.

| Step | Actual result | Observed decision |
| --- | --- | --- |
| 1 | Crossed-fingers hand | Readable human gesture; pointed joins, a palm crease and generic illustration character required work. |
| 2 | Exact-parent hand edit | Palm crease removed and some ends softened. Genericness remained; reframe instead of recommending it. |
| 3 | Asymmetric-ear rabbit | Clear animal, but pointed features evoked a sports/game emblem; rejected direction. |
| 4 | Asymmetric arch | A coherent outer/inner relationship worth refining; excessive top weight and abrupt inner corner. |
| 5 | Exact-parent arch edit | Counter raised and inner corner softened; original character largely preserved. Stop generating and retain a promising, unverified candidate. |

Three generations and two edits used **5 of 6 reserved calls**. The final loop status is **`stopped`**, with one call unused, no selected artifact, no production visual approval and no export. A reserved call is not automatically proof of native execution; this run has five separate native receipts and five matching originals.

[Byte/prompt/lineage verification](native/verification.json) records all five hashes and dimensions. All originals are 1254 × 1254 PNGs. The [gallery](native/index.html) links each exact prompt and artifact-specific critique. The complete resumable sidecar, source paths and native receipts are retained in the local `output/hail-mary-designer-loop-2026-10-01/` workspace; the portable evidence copy here intentionally omits private native source paths.

The two independent critics used separate conversation contexts and original image inspection. They are AI assessments, not consumer research or human brand approval. The final arch's visible optical improvement is a limited result, not a general proof that 0.10.0 produces superior logos.

Official Codex Computer Use was not available in this session. No other GUI provider was substituted. Original pixels were inspected through the image viewer, but 32–64px rendering, inverse artwork and the real Inter/header/credits layout were not visually verified. HTML size controls are previews of the full PNG canvas, not evidence of a minimum usable mark size. These unknowns remain explicit in the final critique.

## Verification and installation

- [Independent skill forward test](forward-skill.md): found the legitimate abstract-symbol scope mismatch and passed with unchanged inputs after correction. No image calls were made by that preparation test.
- [Verification record](verification.md): regression tests, strict checks and independent review findings.
- [Local plugin refresh](installation.md): backup, source/cache comparison and actual installed version; published release status remains separate.
