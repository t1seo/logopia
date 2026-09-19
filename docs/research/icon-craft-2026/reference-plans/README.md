# Runnable reference plans

These six files use `logo_helper.conditioning_models.ReferencePlan` directly. They bind short visual observations to the first inspected image of each case in [references.json](../references.json). Select a relevant case for the brief; do not inject the whole library into every prompt.

Every plan defaults to `mode: "text"`, `capability: "codex_native"`, `selection_origin: "automatic"` and `rights_status: "unknown"`. The helper copies and verifies real image bytes, then adds the recorded observations and transfer/avoid traits to the prompt. It does not attach the reference pixels in text mode, generate an image, or save an automatic selection as user taste. This distinction also applies when the host has image-conditioning capability.

| Plan / reference ID | Local input image |
| --- | --- |
| `things-os26` | `.logopia/reference-cache/things-os26-new.jpg` |
| `craft-current-store` | `.logopia/reference-cache/craft-appstore.jpg` |
| `gentler-streak-current-store` | `.logopia/reference-cache/gentler-streak-appstore.jpg` |
| `notboring-timer-current-store` | `.logopia/reference-cache/notboring-timer-appstore.jpg` |
| `linear-brand-system` | `.logopia/reference-cache/linear/logo-dark.png` |
| `friends-of-figma-2026` | `.logopia/reference-cache/friends-figma-badges.png` |

The ignored cache is local to this research session and is absent from a fresh clone. Do not fabricate missing files or observations. Reacquired images must match the recorded hash; changed source artwork needs a new inspection and plan. Original sources and rights notes are in [the evidence document](../sources.md). Attribution does not grant redistribution or image-conditioning permission. Linear additionally publishes explicit restrictions on altering or combining its brand assets. Keep these third-party plans in text mode unless the intended image use is separately authorized.

All plans have `roi: null`: import the entire original image without `--roi-file`. Things observations distinguish its two icons from the surrounding dock/device screenshot; Friends of Figma observations cover the whole badge grid. The Linear plan binds only `logo-dark.png`, so it does not claim to observe a wordmark or tile in that input. For a cropped or ROI-scoped reference, create a new plan whose hash and ROI match its imported evidence.

From the repository root, this example creates a disposable local session and prints the exact text-conditioning input plan. The commands make no image or paid Provider calls.

```sh
REFERENCE_WORKSPACE=$(mktemp -d)
cat > "$REFERENCE_WORKSPACE/brief.json" <<'JSON'
{
  "brand_name": "Quiet Shelf",
  "exact_text": "",
  "industry": "Personal reading notes",
  "audience": "Readers collecting short passages",
  "logo_type": "abstract",
  "background": "opaque",
  "app_icon": {
    "preset": "abstract",
    "subject": "A single folded ribbon with one open counter",
    "placement": "center"
  }
}
JSON

uv run --locked python skills/logo-land/scripts/logo_project.py \
  --workspace "$REFERENCE_WORKSPACE" init \
  --session reference-demo --brief "$REFERENCE_WORKSPACE/brief.json"

uv run --locked python skills/logo-land/scripts/logo_project.py \
  --workspace "$REFERENCE_WORKSPACE" reference-add \
  --session reference-demo --reference craft-current-store \
  --image .logopia/reference-cache/craft-appstore.jpg --revision 0

uv run --locked python skills/logo-land/scripts/logo_project.py \
  --workspace "$REFERENCE_WORKSPACE" prompt \
  --session reference-demo \
  --concept 'One folded ribbon; share one curve radius and retain an open counter at 32px.' \
  --reference-plan docs/research/icon-craft-2026/reference-plans/craft-current-store.json \
  > "$REFERENCE_WORKSPACE/prompt.json"
```

The result has `input_plan.conditioning: "analysis_text"`, the reference ID/hash and observer metadata. For this generation request, `input_plan.arguments` has no `referenced_image_paths`. Reference import advances revision to 1; when using an existing session, use its actual revision instead of the example's `0`. A parent image remains separate and is supplied only by an explicit edit request.

Validate every plan against the actual Pydantic model without importing images or invoking a Provider:

```sh
PYTHONPATH=skills/logo-land/scripts uv run --locked python -c '
from pathlib import Path
from logo_helper.conditioning_models import ReferencePlan
for path in sorted(Path("docs/research/icon-craft-2026/reference-plans").glob("*.json")):
    plan = ReferencePlan.model_validate_json(path.read_bytes())
    print(path.name, plan.mode, plan.references[0].reference_id)
'
```

Validated on 2026-09-19: all six plans parsed with the repository model. Each was also exercised through the real CLI's `init`, `reference-add`, and `prompt --reference-plan` commands in temporary workspaces. The output preserved the matching image hash, automatic origin and text-only conditioning, with no reference image paths in generation arguments. This verifies data connectivity, not aesthetic improvement or user preference.
