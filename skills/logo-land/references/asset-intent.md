# Artwork and platform assets

An omitted `app_icon.asset` preserves the existing opaque concept-artwork contract. An optional asset separates kind, platform, authored role and Appearance from the shape preset/material:

```json
{"kind":"apple_layered","platform":"apple","role":"foreground","appearance":"dark","composer_mode":"dark"}
```

- `concept_artwork`: one flattened PNG, `role: composite`. It is not a native icon package.
- `apple_layered`: an actual authored `foreground` or `background`, platform `apple`. Imported backgrounds are opaque; foreground alpha is allowed. Home Appearance (`default`, `dark`, `clear_light`, `clear_dark`, `tinted_light`, `tinted_dark`) differs from Composer modes (`default`, `dark`, `mono`). No automatic extraction of layers from a flattened original. Legacy asset-catalog Dark PNG is a different handoff path, not this imported background contract.
- `android_adaptive`: actual `foreground`, `background` or `monochrome`, platform `android`. The 108dp canvas and central 66/108 diameter guide are normalized layout concepts, not a fixed output-pixel size. Essential shape identification requires visual inspection; an alpha footprint warning is not a pass/fail beauty rule.
- `google_play_listing`: `composite`, platform `android`, 512×512px/32-bit PNG/≤1024KB. Transparent images are not universally forbidden. Keep requested backgrounds, square source corners, and distinguish an outer tile shadow from internal object shading.

`asset-check --session demo --artifact a1` returns hash-bound local diagnostics and handoff tasks. Export applies these policies alongside existing integrity, explicit visual review and palette checks. Foreground transparency alone never fails a layered foreground. sRGB metadata, authored layer availability, original masks, dynamic effects and actual OS appearances still require the reported checks.

Only generate or edit an additional layer when requested and count it as an image call. Icon Composer/Xcode/Android builds, editable native documents, dynamic OS rendering and store approval are unsupported by this PNG helper. CSS masks and small-size views are diagnostic simulations. See the repository's `docs/icon-assets.md` for executable examples.
