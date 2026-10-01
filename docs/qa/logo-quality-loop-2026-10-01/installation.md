# Personal plugin refresh: 0.10.0

Verified on **2026-10-01 at 20:37:51 KST**. The personal Codex plugin is installed
and enabled at **`0.10.0+codex.20261001113713`**. All 329 personal-source and
installed-cache files match byte-for-byte. The 118 scoped production files and
root READMEs match the validated repository snapshot, accounting only for the
manifest's local cachebuster and equivalent JSON serialization. Repository
manifest, project and locked helper remain clean development version `0.10.0`.

The coordinator's final source validation passed **1,138 tests in 366.14 seconds**
before installation; see [verification.md](verification.md). This installation
check does not claim new GUI-thread pickup or new image generation.

## Preflight and rollback

On 2026-10-01 at 11:26:43 UTC, the personal source and actual installed cache had
identical sets of 293 regular files and identical bytes. They also matched the
previous installation's saved file hashes. Production files and root READMEs
matched repository commit `1d620642ca55c83e3cd129ee287160f842960d34`, allowing
only the manifest's recorded local cachebuster and equivalent JSON serialization.
No personal edits require merging.

The official `codex plugin list --marketplace personal --json` response identifies
the existing `logo-land@personal` installation as enabled, with local source
`~/plugins/logo-land`. The official marketplace-name helper returns `personal`.
The marketplace file is unchanged; its SHA-256 is
`422580558aa3790de35022394fc5b29eb3e15af1bea4e419bd615c95169598e6`.

A durable regular-file backup was made at
`~/plugins/logo-land.backup-20261001T112643Z`. Its 293 files match the existing
personal source and cache. The aggregate SHA-256 of sorted
`path + NUL + file_sha256_hex + LF` records is
`e076ad86516d361baeb34f9136e697c51bd3544e9787a5e53f6f1fe7e8027182`.
The source was not renamed or replaced when creating this backup.

## Packaging and completed refresh

The reversible staging directory and local receipts are under
`output/installation-refresh-0100-km9r_b5x/`. Its inventory uses
`git ls-files --cached --others --exclude-standard` so new untracked production
files are included. The payload retains the existing Codex packaging roots,
relevant operational research, attribution and QA evidence. Tests, runtime
caches, virtual environments and unrelated output are excluded.

The final installation snapshot was taken at **11:36:57 UTC / 20:36:57 KST**
after the coordinator's validation gate. It contains **329 files, 24,965,470
bytes**, including all new quality-loop modules, references, research, final test
logs and the five-image native-production evidence. The official staging validator
passed. Existing source, old cache and durable backup were rechecked unchanged
before replacement.

A verified regular-file copy of staging replaced the personal source. The old
source is retained at `~/plugins/logo-land.replaced-20261001T113713Z` in addition
to the durable backup. These official commands all returned exit 0:

```sh
python3 <plugin-creator>/scripts/read_marketplace_name.py
python3 <plugin-creator>/scripts/update_plugin_cachebuster.py ~/plugins/logo-land
python3 <plugin-creator>/scripts/validate_plugin.py ~/plugins/logo-land
codex plugin add logo-land@personal --json
```

The add response reported `pluginId=logo-land@personal`, `marketplaceName=personal`,
`version=0.10.0+codex.20261001113713` and `authPolicy=ON_INSTALL`. Its actual
`installedPath` resolves to
`~/.codex/plugins/cache/personal/logo-land/0.10.0+codex.20261001113713`.
That returned directory was used for subsequent verification.

All 329 personal and cache files match; the 328 non-manifest files match the final
staging snapshot. The installed payload aggregate SHA-256 is
`ecd8c222c886423b657b4597ad1587bb88ecb9704a1487f35ba00c5df4a5bea9`.
The marketplace file and normalized unrelated configuration are unchanged. The
existing `logo-land@personal` configuration remains `enabled = true`. The backup
is unchanged, and no symlink, bytecode or runtime cache was introduced inside the
payload. No tag or public release was created and `CODEX_HOME` was not reassigned.

## Installed helper smoke test

The official plugin validator passed against the actual installed cache. Its
standalone PEP 723 helper was executed from a separate sibling workspace with
`PYTHONDONTWRITEBYTECODE=1 uv run --offline --no-project --script ...`.
The root help and a fictional `init → loop-start → loop-request → loop-show`
sequence all passed. This used available UV package artifacts and does not claim
a cold-cache offline installation.

The smoke contract preserved `symbol_only` scope and fixed typography. It reserved
one request from a one-call budget, then resumed the same pending state without
changing the source session bytes. **No host image call was dispatched and no
image artifact was created.** The reservation is installation evidence, not a
production logo or aesthetic-quality result.

The installed QA folder is the **20:36:57 KST snapshot**. This final installation
report is intentionally not recopied into the installed payload, avoiding a
self-referential report/hash update loop. All production bytes were independently
compared with the frozen source.

Raw local receipts are `preflight.json`, `installation-snapshot.json`,
`source-replacement.json`, `installation-commands.json`, `install-response.json`
and `installed-verification.json` under
`output/installation-refresh-0100-km9r_b5x/`. Start a **new Codex conversation**
and invoke **`$logo-land`** to load the refreshed skill.
