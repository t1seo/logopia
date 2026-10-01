# Releases and versioning

Logopia uses `MAJOR.MINOR.PATCH` versions and Git tags named `vMAJOR.MINOR.PATCH`. The Codex plugin, Hermes plugin and local helper are released together from [t1seo/logopia](https://github.com/t1seo/logopia). The first tagged release is [v0.3.1](https://github.com/t1seo/logopia/releases/tag/v0.3.1), continuing the earlier internal 0.3.0 plugin builds.

The latest release is **[0.8.0](https://github.com/t1seo/logopia/releases/tag/v0.8.0)**. It adds a guided [native Hermes workflow](hermes.md), with distinct directions, actual image critiques, preserved revisions and checked PNG delivery. See the [release notes](qa/hermes-workflow/release-notes.md) and [real OFFCUT example](hermes-demo/README.md).

The current source version is **0.10.0, unreleased**. It adds a bounded native-host [logo development loop](../skills/logo-land/references/quality-loop.md), informed by primary-source identity-design research and an audit of earlier output failures. The 0.9.0 brand-strategy changes are retained as an earlier unpublished draft. Neither source version changes the latest published release or relabels historical samples as new results. See the [changelog](../CHANGELOG.md).

The existing Codex workflow and sixteen white-background showcase originals remain available. The earlier [0.7.0 lettering refresh](qa/lettering-refresh/release-notes.md) retains its [verification record](qa/lettering-refresh/verification.md).

The earlier 0.4.0 native color experiments remain [historical failed validation](qa/color-workflow/README.md); their draft and evidence are not republished or reclassified as passing. Strict palette exports still require measured conformance, and generated spelling, alpha and colors need inspection. This release does not guarantee exact raster colors, editable fonts, vectors or platform-ready icon layers.

For v0.3.1, the helper's earlier 0.1.0 metadata was aligned with the plugin version. Those initial release notes summarize existing capabilities and release preparation changes; there is no earlier v0.3.0 tag to compare against.

## Choosing a version

| Change | Version increment |
|---|---|
| Fixes, documentation, presentation, or metadata without an incompatible behavior change | Patch, such as 0.3.1 → 0.3.2 |
| New functionality during the 0.x development series | Minor, such as 0.3.1 → 0.4.0 |
| Incompatible changes during the 0.x series | Minor, with migration instructions in the release notes |
| A stable public compatibility contract | 1.0.0; later incompatible changes increment the major version |

After 1.0.0, compatible new functionality increments the minor version and compatible fixes increment the patch version. Do not move or replace a published tag; publish another version for corrections.

## Preparing a release

1. Set the same clean version in `.codex-plugin/plugin.json`, `integrations/hermes/plugin.yaml` and `pyproject.toml`, then run `uv lock` to update the helper entry in `uv.lock`. Do not upgrade dependencies as part of a version-only change.
2. Update both root README badges and links, add an entry to [CHANGELOG.md](../CHANGELOG.md), and prepare English release notes. Keep the Release badge tied to the actual published release and describe any unreleased source version separately. Keep the default README and GitHub About description in English. Link generated samples only after their native receipts and actual files exist.
3. Run `uv lock --check`, `uv run --locked pytest`, `uv run --locked ruff check .`, and `uv run --locked basedpyright`. Validate the plugin manifest using the installed `plugin-creator` skill's `scripts/validate_plugin.py`. Check the README badge links and sample images.
4. When validating a personal installation, sync the existing personal plugin source, apply its local cachebuster, reinstall, and update the [installation record](qa/installation.md) with the returned version. Recheck that the repository version remains clean. Record release checks with their execution source, as in the [v0.3.1 validation record](qa/release-031.md).
5. Review and commit the release files on `main`, then push the commit. Create an annotated tag at the exact validated commit and push that tag. Publish with `gh release create`, `--verify-tag`, an English `--title`, and `--notes-file` pointing to the prepared notes.
6. Verify that the remote `main` and peeled tag refer to the validated commit, that GitHub reports the release as published and latest, and that the worktree is clean. Record the checks without claiming an image was generated during a documentation-only release. Keep repository visibility unchanged.

Before creating a tag or release, check whether the intended version already exists. If it does, inspect it and select a new version for new changes. Do not overwrite it.

## Local plugin installations

Personal development installations may use a version such as `0.10.0+codex.<timestamp>` to refresh the Codex cache. Apply the official cachebuster helper to the personal plugin source and reinstall it from its existing marketplace. Keep the repository manifest, `pyproject.toml` and `uv.lock` at the clean source version `0.10.0`; create a release tag only through an authorized publication workflow. The cachebuster is not a separate public release. Existing installations can retain an older payload until refreshed, so record source and installed-cache versions/hashes separately rather than inferring one from the other.

Open a new Codex conversation after reinstalling so the updated plugin is discovered. The [installation record](qa/installation.md) distinguishes release versions from local cache versions.

## Using a release

Check out a tag in the cloned repository, then follow the [English installation instructions](../README.md#install-as-a-codex-plugin) or [Korean instructions](../README.ko.md#codex-플러그인으로-설치). GitHub's automatic ZIP and tar.gz downloads contain source snapshots. They do not replace the documented local marketplace installation process.
