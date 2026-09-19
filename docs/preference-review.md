# Local icon comparison and preference review

`icon-gallery` preserves the existing original-PNG and exact-prompt downloads. Its 32/48/64/128 CSS-pixel controls, light/dark surroundings, masks, candidate-peer home and list layouts are diagnostic simulations. They are not native OS rendering, required export sizes, adaptive layers, or store approval.

## Blind A/B comparison

First import real PNGs and their exact final prompts through the existing `import` command. Supply explicit session revisions and artifact IDs. The comparison never chooses the latest image implicitly. A three-pair selection for six imported originals can look like this:

```json
{
  "shared_brief": "The same product, exact text, audience, required colors and use case for all six candidates.",
  "seed": 20260919,
  "ai_review_budget": 3,
  "response_limit": 12,
  "pairs": [
    {"first": {"session": "icon-ab", "revision": 6, "artifact": "a1"}, "second": {"session": "icon-ab", "revision": 6, "artifact": "b1"}},
    {"first": {"session": "icon-ab", "revision": 6, "artifact": "a2"}, "second": {"session": "icon-ab", "revision": 6, "artifact": "b2"}},
    {"first": {"session": "icon-ab", "revision": 6, "artifact": "a3"}, "second": {"session": "icon-ab", "revision": 6, "artifact": "b3"}}
  ],
  "references": []
}
```

```sh
uv run skills/logo-land/scripts/logo_project.py --workspace "$PWD" preference-gallery \
  --selection-file comparison.json --output output/icon-ab-blind
```

Open `output/icon-ab-blind/index.html`. Candidate order is shuffled by the saved seed; left/right assignment alternates to keep the supplied first/second groups balanced across the comparison. With an odd pair count the side totals differ by one. Reusing the same seed and input recreates the order. Different reviewers should receive separately rendered seeds to reduce persistent position bias. Blinding omits method names, source IDs, prompts and creator rationale from the interface and image filenames; it is not access control. Do not give reviewers the unlinked organizer `manifest.json` until they respond.

The common brief is explicit because sessions can contain direction-specific styling. Include actual shared requirements rather than a method description. Reference summaries belong in `references` with `label`, an HTTP(S) `source_url`, positive/negative `role`, `observations`, `verification` (`image_observed` or `unverified`), and `image_sha256` for any visually observed source. An optional workspace-relative `image_path` copies a PNG/JPEG into this **local** gallery after validating its hash and decoder. Do not publish reference copies without redistribution rights. Without a local image, the summary and source link remain available; unverified sources stay labeled. Automatic references do not become user preferences.

Choose **Prefer A**, **Prefer B**, **Similar**, or **Neither suitable** and supply visible observations for brief/reference fit, shape/background, craft, effects, potential confusion, 32px details and equal-size peer context. The form downloads `preference-response.json`; no server or model call is made.

```sh
uv run skills/logo-land/scripts/logo_project.py --workspace "$PWD" preference-record \
  --gallery output/icon-ab-blind --response-file /path/to/preference-response.json
```

The command rechecks the manifest, both original hashes, exact-prompt/brief hashes, saved revisions and any local references. It creates an immutable `preference-records/<response-hash>.json` sidecar. A changed source revision requires a fresh comparison. Duplicate responses, conflicting hashes, incomplete observations, excess responses and exhausted recorded AI-call budgets are rejected. It never selects an artifact, supplies production QA, exports a file, or changes Session bytes.

Browser responses identify `reviewer_kind: "user"` and `review_calls: 0`. AI tooling must use `reviewer_kind: "ai"` and report actual positive `review_calls`; records are then marked `ai_recommendation`, not `user_preference`. The gallery caps accepted records at the configured 0–12 AI calls and 1–24 responses. It does not dispatch or reserve external calls, so callers must enforce their own pre-dispatch job budget. Identity is an explicit declaration, not authentication. User preference improvement remains unverified until a user actually responds.

This helper works with any explicitly imported static PNG, including existing brand and lettering candidates. Hermes sources must first be imported with their original prompts; no Hermes state is mutated. Ordinary non-blind galleries remain the place for original/prompt downloads and source provenance.
