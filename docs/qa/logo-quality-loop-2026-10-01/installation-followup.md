# Personal plugin follow-up: quality-mode routing

Verified on **2026-10-01 at 21:22:39 KST / 12:22:39 UTC**. The personal
`logo-land@personal` plugin is installed and enabled at
**`0.10.0+codex.20261001122135`**. This follow-up updates only two skill documents
plus the manifest's local cachebuster. It does not refresh the installed README,
research, gallery or QA snapshots, change Python source, or create a public release.
The [earlier installation record](installation.md) remains an unchanged historical
snapshot.

The updated guidance keeps an active quality-improvement objective when a later
request asks for examples, a showcase or README images. It also carries independent
critique and a declared shared budget into multi-brief collections, and requires
comparison with a relevant earlier result when improvement is requested. These
workflow instructions do not establish better visual output by themselves.

## Preflight and backup

Before editing, all **329 files** in both `~/plugins/logo-land` and the prior
`0.10.0+codex.20261001113713` cache matched the hashes saved in
`output/installation-refresh-0100-km9r_b5x/installed-verification.json`.
There were no added, missing or locally modified payload files. The official
marketplace-name helper returned `personal`; `codex plugin list` confirmed that
the existing local marketplace source was `~/plugins/logo-land` and enabled.

A complete regular-file backup was created at
`~/plugins/logo-land.backup-20261001T122116Z-quality-routing`. Every backup hash
matched the prior receipt before replacement and again after installation.
The old version's cache directory was absent after the official reinstall; the
verified full backup remains available. The first post-install verification
attempt recorded this absence, then the completed check used the returned new
cache and the backup instead of assuming old caches persist.

## Exact update and verification

Only these repository files were copied into the personal source:

| File | SHA-256 in repository, personal source and new cache |
| --- | --- |
| `skills/logo-land/SKILL.md` | `d2a21a819077accc413b53e9dd02ce335cc026d9fbd1025661c760f6ff37d179` |
| `skills/logo-land/references/quality-loop.md` | `2190ccf8a37a39a3af694f5fef1de1bc87491e47909a52501515d0c2d1ff5003` |

The official `read_marketplace_name.py`, `update_plugin_cachebuster.py`,
`validate_plugin.py` and skill `quick_validate.py` helpers passed, followed by
`codex plugin add logo-land@personal --json`. No marketplace or configuration
file was hand-edited. The add response returned the new version and installed
path, which resolves to:

`~/.codex/plugins/cache/personal/logo-land/0.10.0+codex.20261001122135`

All **329 new cache files match the personal source**. Exactly three paths differ
from the previous payload: the two documents above and
`.codex-plugin/plugin.json`, whose only semantic change is its cachebuster
version. The other **326 files remain byte-identical**, including all Python
modules and the historical installed documentation. Both official validators
also passed against the actual returned cache. Marketplace and configuration
file hashes are unchanged, and the official listing confirms the new version is
enabled. No symlink or runtime cache was introduced into the payload.

Local receipts are retained under `output/installation-quality-followup-D5nOO3/`:
`preflight.json`, `plugin-list-before.json`, `document-replacement.json`,
`commands.json`, `install-response.json`, `verification-attempt-1.json`,
`plugin-list-after.json` and `installed-verification.json`.

This document is repository evidence and is intentionally not copied back into
the installed payload. No new image was generated, and the full Python test suite
was not rerun for this two-document update. The prior source checks remain in
[verification.md](verification.md).

**New GUI-thread pickup has not been verified.** Start a new Codex conversation
and invoke **`$logo-land`** to load and try the refreshed skill.
