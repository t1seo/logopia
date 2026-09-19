# App-icon artwork and platform handoff

`app_icon.asset` is optional. Existing sessions without it retain the existing opaque flattened
concept-artwork intent, prompt snapshots, and original PNGs. New metadata keeps asset purpose,
platform, layer role, home appearance, and Icon Composer editing mode separate from visual style.

| `kind` | `platform` / `role` | Local checks | Remaining work |
| --- | --- | --- | --- |
| `concept_artwork` | unspecified/apple/android / composite | PNG integrity and existing opaque-background request | Choose a platform deliverable |
| `apple_layered` | apple / foreground or background | Foreground alpha allowed; background opaque | Real separate layers, Icon Composer, Xcode, appearances |
| `android_adaptive` | android / foreground, background, monochrome | Square raster; opaque background; normalized 66/108-circle diagnostic for foreground/monochrome | Map to 108 dp, adaptive resources, launcher/OEM rendering |
| `google_play_listing` | android / composite | 512×512 px, source 8-bit RGBA PNG, ≤1,048,576 bytes | Confirm sRGB, full-square outer edge, Play Console |

Google Play allows transparency; the check warns that the store's UI background shows through.
An explicit opaque/transparent request still applies to the listing. Foreground-layer alpha is
independent of the flattened brief's background default. Imports preserve valid original PNGs
even when a local platform check fails, so they can be inspected and revised; export repeats
checks and blocks failed hard requirements. QA, user selection, and platform validation remain
separate. No command extracts fictitious editable layers or generates extra images.

Add this to an existing `app_icon` object when importing an **actually authored** Apple foreground:

```json
{
  "preset": "abstract",
  "subject": "a folded ribbon with a continuous inner counter",
  "placement": "center",
  "asset": {
    "kind": "apple_layered",
    "platform": "apple",
    "role": "foreground",
    "appearance": "clear_dark",
    "composer_mode": "mono"
  }
}
```

Use the existing brief/init, import, review, select, and export commands. `asset-check` is a
read-only report for an imported artifact and needs neither selection nor a passing visual review:

```sh
uv run skills/logo-land/scripts/logo_project.py --workspace . import \
  --session icon-demo --revision 0 --artifact foreground-v1 \
  --image authored-foreground.png --prompt-file actual-prompt.txt \
  --app-icon-file foreground-intent.json

uv run skills/logo-land/scripts/logo_project.py --workspace . asset-check \
  --session icon-demo --artifact foreground-v1
```

The output binds its diagnostics to `source_sha256`, lists measured checks and unperformed visual
checks, and gives platform-specific handoff steps. `platform_validation` stays `not_run` and
`native_package` stays `false`. Export includes the same report in `manifest.json`. Failed checks
are reported as data by `asset-check`; export enforces hard failures. Originals are never resized,
flattened, recolored, or overwritten by these checks.

Android's circle is a conservative diagnostic guide: a 66 dp diameter relative to a 108 dp layer,
not 66 source pixels or a 66-square whose corners are guaranteed safe. It counts all nonzero-alpha
pixels outside that circle. Decorative overflow produces a warning; the software cannot infer
which pixels constitute the essential logo. Mask and home-screen previews remain simulations.

Apple home appearance values are `default`, `dark`, `clear_light`, `clear_dark`, `tinted_light`,
and `tinted_dark` (or `unspecified`). Composer modes are independently `default`, `dark`, and `mono`.
Android launcher intent also accepts `themed`; Play listing intent is `default` or `unspecified`.
This PNG helper does not prepare legacy Xcode asset catalogs, whose
dark-icon transparency rules differ from a layered icon's opaque background layer.

Checked 2026-09-19 against [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/app-icons),
[Icon Composer](https://developer.apple.com/icon-composer/),
[Android adaptive icons](https://developer.android.com/develop/ui/compose/system/icon_design_adaptive),
the [official Android icon codelab](https://developer.android.com/codelabs/basic-android-kotlin-compose-training-change-app-icon),
and [Play listing specifications](https://developer.android.com/distribute/google-play/resources/icon-design-specifications).
