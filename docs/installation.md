# Installation

[English](installation.md) · [한국어](installation.ko.md) · [Docs](README.md) · [Logopia](../README.md)

Use the checkout directly, or register it in a local marketplace to enable `$logo-land` in other projects.

## Requirements

Use a Codex environment with native image generation and editing, Python 3.12+ and `uv`. Installing the plugin does not enable a missing image tool. The plugin does not require a separate OpenAI API key or accounts with competing logo services.

## Use the repository directly

```sh
git clone https://github.com/t1seo/logopia.git
cd logopia
uv sync --locked
codex
```

In a Codex conversation opened in this folder, ask it to read the skill:

> Read skills/logo-land/SKILL.md and follow it to create a logo. The brand is Goyo, a meditation studio. Show me two calm concepts combining a symbol and the exact Korean text 고요.

This route uses the checkout's instructions. Plugin installation below makes `$logo-land` available in other project conversations.

## Install as a Codex plugin

This repository contains plugin source; it does not provide a public marketplace or a release ZIP installation route. Register your checkout in your own local marketplace:

1. Clone the repository above and note its **absolute path**.
2. Choose a separate marketplace folder, for example `/absolute/path/to/local-marketplace`. Inside it, create `.agents/plugins/marketplace.json`. Replace the JSON `path` below with the checkout's absolute path; on Windows, use `/` in the JSON path. If a marketplace already exists, add the plugin entry while preserving its name and other entries, then use that name in step 3.

```json
{
  "name": "logo-land-local",
  "plugins": [
    {
      "name": "logo-land",
      "source": {
        "source": "local",
        "path": "/absolute/path/to/logopia"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

3. Register the **marketplace root**, the folder containing `.agents`, then install the plugin. Replace the placeholder with your actual marketplace location.

```sh
codex plugin marketplace add /absolute/path/to/local-marketplace
codex plugin add logo-land@logo-land-local
```

4. Open a **new Codex conversation** and start with `$logo-land`. Enable the plugin if your environment requires it.

> $logo-land Help me create a logo that fits my brand.

The syntax above was checked against Codex CLI **0.154.0** on 2026-09-13 KST using the read-only commands below. Check your own CLI help if your version differs. The [installation records](qa/installation.md) describe earlier actual installs and their verification limits.

```sh
codex --version
codex plugin marketplace add --help
codex plugin add --help
```

## Source, release and installed versions

This checkout's Codex and Hermes manifests, Python project and locked helper package are **0.9.0, unreleased**. The latest published snapshot remains [v0.8.0](https://github.com/t1seo/logopia/releases/tag/v0.8.0); use `git checkout v0.8.0` after cloning if you want that release. The plugin name and invocation remain `logo-land` and `$logo-land`; the repository is named `logopia`.

An existing installed cache may contain an older version until refreshed. A local version such as `0.9.0+codex.<timestamp>` identifies a cache refresh and does not establish a published release. After an update and reinstall, start a new conversation to load the changed skill. GitHub source archives are repository snapshots, not one-click plugin installers. See [release guidance](releases.md) and the [changelog](../CHANGELOG.md).

## Project files

Saved projects use `.logo-generator/sessions/<id>/`; default deliveries use `output/logo-generator/<id>/`. These compatibility names remain unchanged from the earlier `logo-generator` name. New conversations use `$logo-land`; existing project folders do not need to be renamed.

For helper commands from another workspace, set `uv run --locked --project /absolute/path/to/logopia` to the plugin root and the helper's `--workspace` to your project folder. The [project-file guide](../skills/logo-land/references/project-files.md) contains full commands and schema-1 migration/recovery limits. Preserve backups and original PNGs; older v0.3.1 installations are not guaranteed to read schema-2 projects.

[Try the example requests](../README.md#try-it) · [Browse samples](samples/README.md)
