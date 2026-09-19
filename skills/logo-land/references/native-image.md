# Native image tool contract

Use the image tool actually exposed by the host. In the development host the callable tool is `image_gen__imagegen`; tool naming and availability can differ. Read its live schema before invocation. Do not install a fake MCP server for this built-in capability.

The observed schema accepts `prompt`, `referenced_image_paths`, and `num_last_images_to_include` only. Desired size, background, and visual style belong in the prompt when no corresponding tool parameter exists. `model`, `quality`, `size`, `n`, `negative_prompt`, `background`, `out`, and Responses API IDs are not parameters of this observed built-in tool. Record the actual tool/provider; model identity is unreported when the runtime does not expose it. Never infer a model from a product name or an upstream preference.

| Intent | Reference handling |
|---|---|
| New image without references | Omit both reference parameters. |
| All references or edit targets have local paths | Inspect unseen images, then pass the exact `referenced_image_paths`. Label each image's role in the prompt. |
| At least one required image only exists in the conversation | Use the smallest recent-image count containing all targets, within the current tool limit (5 in the development host). |
| Required images cannot all be included | Ask for missing images to be attached again. |

Never send both reference mechanisms together. A new design inspired by a reference remains a new design; an edit must identify the existing artifact whose identity is preserved.

## App icon branch

Follow [app-icons.md](app-icons.md), including the attributed [IP character direction](ip-mascot.md) when relevant. Use the dedicated helper prompt and preserve its final complete text before calling the tool. The helper checks the 20,000-character import limit in advance. Product and use context inform the selected construction; fixed cuteness, animal mappings and stock palettes are not defaults. Other presets have their own rendering directions; only monogram renders exact supplied lettering.

Ordinary concept artwork requests one full-bleed square raster with square outer corners, a complete solid background and approximately 1536 × 1536 in prompt text. Explicit [asset intent](asset-intent.md) selects separate layer or store-listing requirements. Record actual returned dimensions. Keep original bytes and dimensions; do not resize, replace backgrounds or manufacture platform layers. CSS rounded/circle previews illustrate possible masks and do not produce OS-native or store-ready assets.

Generate each initial candidate once. Independent draws do not inherit another candidate; an explicitly chosen visual reference is recorded through [the reference input plan](visual-references.md), with its role distinguished from an edit parent. Execute the plan's real arguments when supported; do not silently drop image inputs or invent tool parameters. For the usual IP set, use three directions with two separate left/right candidates each. Preserve all results regardless of artistic variance or color/export status. Use a durable receipt per call recording planned/running/returned/failed/unknown state, exact prompt/hash, session/artifact IDs, tool/model provenance and returned paths/hashes/dimensions. Resume that receipt after interruptions. Do not reset an unknown attempt, retry automatically, or scan for the newest file. Catalog copies preserve source receipts and do not count as additional native generation.

The user's creation request authorizes the native operation without an extra palette/model/API-key gate. If the tool is missing or fails, preserve the actual failure and existing work; no external API fallback or fake image result is allowed. Approved export remains a separate later operation with all existing strict gates.

## Artifact handling

Use the returned file path or actual returned image bytes. In hosts that save under `CODEX_HOME/generated_images`, identify the exact file from that call's result, then copy/import it into the workspace. Do not scan for “latest” files because concurrent sessions can generate unrelated images.

If only a displayed preview is returned and there is no readable image artifact, explain the file-delivery limitation. Do not invent an absolute path. Copying image bytes does not require another generation request.

For example, a concept prompt may be:

```text
Use case: logo-brand
Asset: master brand logo, standalone image
Brand: Morrow Studio, a sustainable design studio
Type: combination mark
Concept: an open geometric M with generous negative space
Text (verbatim): "Morrow Studio"
Style: flat, restrained, contemporary; clear at small sizes
Palette: forest green #174C3C
Composition: mark above a carefully spaced wordmark, wide clear margins
Background: solid white
Avoid: gradients, shadows, mockups, extra lettering, existing brand symbols
```

An edit prompt should say what changes and what stays:

```text
The supplied image is the edit target.
Change only the green logo and lettering to deep navy #183A56.
Keep the exact words, mark silhouette, composition, margins and white background.
Return one standalone master logo image, not a comparison sheet or mockup.
```

The helper can propose a prompt; the assistant must execute the image call and save the actual prompt. It has no network image endpoint and requires no OpenAI API key. An API workflow is a separate user-selected integration, outside this plugin's built-in route.

## Transparent PNG requests

For a new logo, put `"background": "transparent"` in the brief and include this requirement in the final prompt:

```text
Return one genuine RGBA PNG logo on a fully transparent background.
Empty exterior space must have alpha 0; keep the foreground visible and edges clean.
Do not draw a checkerboard, a white backing panel, a background color, or a drop shadow.
```

For an existing logo, supply its exact image as the edit target and add:

```text
Remove only the background. Preserve exact lettering, colors, shapes and layout.
Keep intentional white foreground details; make empty space and letter counters transparent.
```

Inspect the returned alpha and the actual cutout. Register a transparent edit with `import --parent <id> --background transparent`; later edits must retain that override. An alpha channel or transparent-looking preview alone does not prove a transparent background.
