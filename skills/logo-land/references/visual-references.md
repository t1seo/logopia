# Visual reference inputs

Use the actual image before describing it. Observations concern visible pixels; interpretations and planned construction are separate. Missing images stay unverified. A public URL or a famous app name is not image conditioning or a license.

1. `reference-add --session demo --revision 0 --reference example --image /actual/image.png` preserves PNG/JPEG bytes with SHA-256 and optional oriented ROI.
2. Record selected visual evidence in a `ReferencePlan` JSON file. Bind `image_sha256` and `roi` to the imported record. Set `inspected_by` and `inspected_on` truthfully. `observations` describes pixels; `transfer` and `avoid` specify what the direction takes or excludes. `selection_origin: "automatic"` never expresses user taste.
3. `prompt --session demo --concept 'one explicit construction' --reference-plan references.json` returns the exact final prompt plus `input_plan`. Save this response, final prompt, tool receipt and output hash per candidate. The helper itself does not generate images.
4. On Codex, call the exposed native tool with **exactly** `input_plan.arguments`, after checking its live schema. It contains `prompt` and, only when needed, `referenced_image_paths`. The exact edit parent is first, followed by positive references; negative references contribute avoidance text only. No made-up `model`, `size`, `n` or plural Hermes parameters.
5. Reopen each returned original and compare it at the same small sizes/context against the selected traits, not the creator's explanation. Preserve the original and distinguish observed success from intended design.

Example `references.json` (replace hash and date with actual evidence):

```json
{
  "mode": "text",
  "capability": "codex_native",
  "references": [{
    "reference_id": "example",
    "image_sha256": "REPLACE_WITH_IMPORTED_SHA256",
    "role": "positive",
    "observations": ["Two broad surfaces leave an open rectangular channel."],
    "transfer": ["Consistent gap width and terminal radius."],
    "avoid": ["Do not copy the original silhouette or lettering."],
    "inspected_by": "actual observer",
    "inspected_on": "2026-09-19",
    "selection_origin": "automatic",
    "rights_status": "unknown"
  }]
}
```

`mode: "text"` forwards inspected traits without attaching positive images. `mode: "image"` attaches them on `codex_native`; `text_only` rejects an image-conditioning request explicitly. ROI-only analysis also requires text mode because attaching the full source would exceed the inspected scope. Negative-only requests remain `analysis_text`. Changed, missing, invalid, duplicate or stale references fail before a request is returned.

Hermes attaches reference PNG pixels to multimodal planning and review, saves the analysis, and forwards selected traits as **text conditioning** to generation. Its current `image_generate` contract has one `image_url` reserved for the edit parent; image-conditioning requests are rejected, not silently approximated. It does not accept the helper's JPEG/ROI reference contract.

The repository's optional `docs/research/icon-craft-2026/reference-plans/` has six verified examples and runnable imports. Full source images remain in ignored `.logopia/reference-cache/`; private user references belong in `.logopia/private-references/` or ignored session storage. Missing checkout caches require reacquisition and inspection. Never include source images in a public gallery without the appropriate rights. Keep only relevant selected references in any generation prompt.
