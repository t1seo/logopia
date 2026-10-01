# Changelog

Logopia's Codex plugin, Hermes plugin and local helper share one release version. Tagged releases and their notes are available on [GitHub Releases](https://github.com/t1seo/logopia/releases). See the [release guide](docs/releases.md) for versioning and publication steps.

## 0.9.0 — Unreleased

Product logo direction, color relationships and typography.

- Add an optional proposed brand strategy to Codex briefs and deliver the saved Hermes strategy to actual image requests. Exact text, effective palettes, explicit styling and parent edits retain precedence.
- Keep ordinary brand masters flat and clean, with a white canvas when compatible with the requested surface and color constraints. Remove unrequested sculpted/athletic examples from generic wordmark prompts; expressive user requests remain supported.
- Give the image model effective palette roles and constraints without internal provenance metadata. Keep the complete palette record and original hashes in the local project.
- Adapt selected Brand Building Skills and Taste brandkit principles for brand fit, color lightness/chroma/area, typography and application review, with pinned sources and bundled MIT notices. Their cinematic presentation defaults and fixed moodboard layouts are not adopted.
- Document the optional Recraft remote MCP boundary without adding credentials, paid calls or SVG export claims. Native delivery remains PNG.
- Preserve earlier samples and their findings. The [quality research](docs/research/brand-output-quality-2026-10-01.md) records the sources; the [six-image comparison](docs/qa/brand-output-quality-2026-10-01/README.md) preserves every before/after original and separates technical checks from limited visual observations.

This source version has not been tagged or published. The latest published release remains 0.8.0.

## 0.8.0 — 2026-09-15

A guided native Hermes workflow, from the brief to reviewed original delivery.

- Added a macOS/Linux Hermes native plugin for brief, direction, original generation, two separate visual critiques, explicit selection, focused revisions and checked raster delivery. The existing Codex `$logo-land` route remains available.
- Added a named-profile installer with 30-minute native tool limits and a bounded launcher that verifies canonical workflow outcomes rather than accepting a process exit or model summary as success.
- Preserve exact original PNGs, parent revisions, prompts, review findings and failed attempts. Explicit review-only recovery can use the remaining critique attempt; unknown image outcomes are never resubmitted automatically. Each workflow allows at most two requested image edits.
- Added a portable offline comparison page with original downloads, display-size previews, review status and keep/change feedback copied back to Hermes. Candidate selection does not approve delivery, and model critiques do not establish human certification or professional superiority.
- Made the Hermes workflow discoverable before the existing sixteen-logo showcase in the English and Korean READMEs, preserving its original links and the mandatory [s1dashu/ip-as-logo-skill MIT credit](THIRD_PARTY_NOTICES.md).
- Added the [actual OFFCUT example](docs/hermes-demo/README.md): three initial PNGs, two exact-parent edits and the delivered e2 package. The c1 → e1 → e2 lineage retains e1's failed preservation check; the final e2 passed both model reviews. The [native execution record](docs/qa/hermes-workflow/native-run.md) preserves the initial tool timeout and review-only recovery without new images.

See the [Hermes guide](docs/hermes.md) and [0.8.0 release notes](docs/qa/hermes-workflow/release-notes.md). Outputs remain raster PNGs; editable vectors, font files, legal clearance and platform icon packages are separate work.

## 0.7.0 — 2026-09-14

Lettering and showcase refresh.

- Added lettering-first guidance for playful multicolor wordmarks, kinetic/sporty wordmarks, geometric lettermarks and integrated monograms, using the existing logo forms and saved creative intent.
- Made exact Korean/Latin spelling, letter construction and the exclusion of unsolicited icons explicit in example requests and review guidance.
- Rebuilt both READMEs around the stacked LOGO LAND lettering master, one consolidated showcase board and three purposeful badges in the ink, mint, lilac and paper palette.
- Added the [September 2026 showcase](docs/showcase/2026-09/README.md) for ten newly generated fictional brand samples and six app icon studies, with separate PNG links and collection records.
- Reorganized bilingual documentation, sample indexes and identity guidance around the current collection while retaining earlier images, deep links and their historical findings.
- Kept raster, native-image-tool, font and platform limitations explicit; the refresh does not introduce a new lettering API, preset or session schema.

## 0.6.0 — Unreleased

Prepared on 2026-09-13 as the comparison and focused revision development update. At that checkpoint source metadata was 0.6.0 and the published release was v0.3.1; this draft was not published separately. Earlier unreleased drafts and their historical color-gate failures remain unchanged.

- Added `compare-gallery` to compare explicit candidates across saved projects, retaining exact original PNGs, prompts, source identities and parent lineage in a portable gallery.
- Carry selection reasons, features to preserve, requested changes and observations into comparison notes and focused revisions. App and web-header contexts are illustrative previews, not platform packages.
- Fixed legacy parent revisions with an unknown lockup so they retain that unknown intent instead of inheriting a later session default.
- Made real samples visible inline in both READMEs, with a one-click visual gallery and original-image links.
- Added [eight native samples](docs/gallery-workflow/comparison/index.html): six initial candidates and two child edits. [Observed results](docs/qa/gallery-workflow/native-samples.md) include wider Relay spacing with geometric drift, an unachieved Sprig stem bend and extra Leaflet colors; no benchmark improvement, exact font composition or export approval is claimed.

## 0.5.0 — Unreleased

Prepared on 2026-09-13 as the app icon artwork development update. At that checkpoint source metadata was 0.5.0; the published release remained 0.3.1, and the prior 0.4.0 draft and its failed color release gates remained unchanged. Sixteen independent native samples are preserved across the original and revised galleries. Samples are artwork, without platform approval claims.

### Added

- Six app icon presets: `ip_mascot`, `pictogram`, `abstract`, `monogram`, `soft_3d` and `pixel_art`, with explicit subject/placement and exact Unicode monogram intent.
- Dedicated native prompts and original-preserving icon comparison galleries with exact prompts, intent, actual dimensions, CSS masks, display sizes and original downloads.
- Conversational IP guidance adapted from s1dashu's pinned `acb834c` skill, including three directions, six independent one-pass candidates and the complete MIT notice.
- English/Korean usage instructions, a runnable Korean monogram brief, native receipt guidance and raster/platform limitations.
- [Eleven native originals](docs/app-icons/index.html) across six presets, including six IP candidates and the Korean `모` monogram, with exact prompts and [source/session/catalog/download lineage](docs/qa/app-icons/native-samples.md). Every returned 1254 × 1254 PNG is unchanged; catalog imports add no native calls or approval claims.
- Five fresh same-subject examples in a [sixteen-original comparison gallery](docs/app-icons-quality-v1/index.html), pairing each non-IP style with its earlier result and retaining all six IP originals.

### Changed

- Replaced the parody branding with an original open-frame Logo Land symbol and wordmark, applied to both READMEs and the plugin interface.
- Refined pictogram, abstract, monogram, soft 3D and pixel-art instructions around recognizable silhouettes, readable gaps, deliberate lettering and consistent materials or grid structure. Existing IP prompts and historical originals remain unchanged.
- Added product-specific construction guidance before generation, while preserving explicit user colors, lettering and placement.
- Simplified the English and Korean READMEs into installation, example requests, capabilities and sample links. Individual bilingual sample pages now provide original images and available downloads, with explicit upstream credit on IP character pages.

### Compatibility

- Session and manifest schema 2 gain optional icon snapshots. Existing state reads, frozen v1 parsing and first-mutation byte-exact v1 backups remain; older readers are not promised to read icon-bearing v2 files.
- Explicit icon transforms preserve legacy history while suppressing old brand lettering/lockups in rendering. Icon background is opaque; conflicting explicit lockup or transparent import is rejected before mutation.
- Creative galleries preserve all selected icon originals independently of review/color/export status. Optional approved export retains existing gates, fresh strict-color checks, the three ZIP payload filenames and original PNG bytes.
- Semantic style colors do not create hard constraints or relax explicit palettes. Approximate requested dimensions, font appearance and illustrative masks do not establish exact output size, font-file usage, platform layers or store acceptance.

See the [app icon contract](plans/logo-land-app-icons.md) and [documentation verification](docs/qa/app-icons/docs.md). Existing logo/color sample descriptions and historical validation snapshots remain intact.

## 0.4.0 — Unreleased

Prepared on 2026-09-13. Publication is withheld because the required restricted-color and white-transparent native samples did not pass after the bounded repair attempts. At that checkpoint source and personal development versions were 0.4.0; the published release was 0.3.1. This historical draft remained unpublished as subsequent development continued at 0.6.0.

### Added

- Automatic, anchor, restricted and reference-derived palettes with composable constraints and immutable version history.
- Local ColorAide calculations, bounded PNG/JPEG reference extraction, sampled color reports and strict export checks.
- Structured horizontal/stacked symbol-plus-text layouts, exact lettering and inherited typography appearance references.
- Font/typography research covering official services, community skills/MCPs and Korean/Latin family references.
- Portable color comparison pages with light/dark and small-size previews.

### Changed

- Session schema 2 reads schema 1 without rewriting it; the first successful mutation preserves an exact v1 backup. Earlier releases cannot read v2 sessions.
- Manifest schema 2 separates intended palettes and requested font appearance from measured raster evidence. Export recomputes color checks while preserving original PNG bytes and the three ZIP payload files.
- English and Korean instructions cover the new color, lockup and migration workflows.

### Compatibility

- Otherwise valid legacy and advisory PNGs remain exportable when optional EXIF color analysis is unavailable. The report records unavailable evidence; strict exports still require determinate conformance, and original-byte integrity checks remain enforced.
- Palette-less reports retain unsupported ICC profile reasons. Newly generated Dark previews use the same `#171717` surface as the default contrast measurements.

Color checks use sampled raster heuristics; they do not certify exact pixels, Pantone/CMYK matching, fonts or accessibility. A font reference describes requested appearance, and no font files or additional MCP server are installed. Native image generation remains the only creation/editing path.

See the [live samples](docs/colors/index.html) and [validation record](docs/qa/color-workflow/README.md) for observed outcomes, limitations and repair attempts.

## 0.3.1 — 2026-09-12

This is the first tagged GitHub release, continuing the internal 0.3.0 plugin builds. Earlier work was distributed through local development installations without release tags. This entry covers the capabilities accumulated before the first tag as well as the release preparation changes; there is no earlier tagged release to compare against.

### Included

- Conversational logo creation with native Codex image generation, eight logo types, concept comparison, and reference-based revisions.
- Transparent PNG generation and background removal, with pixel checks and visual review before export.
- Saved sessions, original image history, and verified PNG, ZIP, and brand guide delivery.
- Ten real logo samples, the Logo Land brand logo, and a transparent logo preview.
- Separate English and Korean READMEs with centered release, feature, and language badges.

### Changed

- English is the default README and plugin presentation language; the Korean README remains available separately.
- The plugin manifest, helper metadata, and lockfile now use the same release version: 0.3.1. The helper previously used 0.1.0; its version now follows the plugin, with no dependency upgrades or runtime changes in the alignment.
- Added a documented versioning and release process.

### Fixed

- Replaced empty sample table headers with explicit brand, logo type, and generated logo columns.
- Made English and Korean documentation badges link to their respective READMEs.

The helper manages files and provenance; image generation requires the native Codex image tool. GitHub source archives are repository snapshots, not plugin installation packages.

See the [release validation record](docs/qa/release-031.md) for checks and their scope. No new image-generation run was performed for this release preparation.
