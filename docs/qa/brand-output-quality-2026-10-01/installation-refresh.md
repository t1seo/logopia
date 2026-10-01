# Personal installation refresh: 0.9.0

Verified on **2026-10-01 at 19:31:40 KST**. **The personal Codex plugin is installed and enabled at `0.9.0+codex.20261001103046`.** Its source and actual installed cache have identical sets of **293 files**, and all 292 non-manifest files match the installation snapshot. The 107 production files match the repository after accounting for the manifest's local cachebuster and equivalent JSON serialization. Repository manifest, Python project and locked helper remain clean development version `0.9.0`. The coordinator's final frozen-source suite passed **1,097 tests in 371.88 seconds** before installation; see [verification.md](verification.md).

Only this plugin's configuration entry was added, with `enabled = true`. The personal marketplace and all unrelated configuration remained unchanged. No commit, push, tag or public release was made during this installation check. Fresh GUI-thread skill pickup and new image generation were not performed by this installation check.

## Previous installation, checked before replacement

Before replacement, the source at `~/plugins/logo-land` and cache at `~/.codex/plugins/cache/personal/logo-land/0.6.0+codex.20260913005849` had the same 74 files and bytes, without extra files or symbolic links. Compared with historical source commit `49e9ae7`, all 73 non-manifest files matched. Parsed manifest objects matched after restoring the clean `0.6.0` version; the other serialization difference was equivalent Unicode escaping. No personal changes needed merging.

The previous installation's aggregate SHA-256 is `28a6d9bfe442fc17f5a39b421a3e2c0a349832f5ea998dee0068e0dbab6694c0`. The aggregate is calculated from sorted relative paths as `path + NUL + file_sha256_hex + LF`. The personal marketplace file SHA-256 is `422580558aa3790de35022394fc5b29eb3e15af1bea4e419bd615c95169598e6`.

The official marketplace-name helper returns `personal`; its existing `logo-land` entry uses `./plugins/logo-land`. The official plugin validator passes for the existing personal source, installed cache and current repository. The active CLI plugin directory resolves to the shared `~/.codex/plugins` directory. The shell's `~/.orca-codex` home is itself a symbolic link to this conversation's active account home, so both `config.toml` paths resolve to the same file. Neither view has an explicit `logo-land` plugin entry before refresh. This was checked by reading only matching plugin settings, without displaying unrelated configuration. These checks do not claim that a new GUI conversation has loaded the plugin.

## Durable rollback backup

On **2026-10-01 10:24:30 UTC**, the entire existing personal source was copied to **`~/plugins/logo-land.backup-20261001T102430Z`**. The source was not renamed or replaced. All 74 backed-up files match the personal source and installed cache byte-for-byte, with aggregate SHA-256 `28a6d9bfe442fc17f5a39b421a3e2c0a349832f5ea998dee0068e0dbab6694c0`. The backup contains no symbolic links. The source and marketplace hashes were unchanged after copying.

The durable backup remains separate from task-local staging and is retained for rollback. The full local receipt is `output/installation-refresh-090-032ners8/backup-receipt.json`.

## Staged payload

The task-local staging directory is `output/installation-refresh-090-032ners8/logo-land/`. Its sibling `workspace/` is the independent helper working directory; receipts remain outside the payload. Files are copied from current working-tree bytes, including new untracked production files, using the scoped `git ls-files --cached --others --exclude-standard` inventory. `git archive HEAD` is not used because this development update has not been committed.

The payload includes the existing Codex packaging roots `.codex-plugin/`, `assets/`, `skills/`, `pyproject.toml`, `uv.lock` and `THIRD_PARTY_NOTICES.md`, plus both root READMEs. The repository has no root `LICENSE` or `LICENCE` file; the three existing skill attribution licenses are included unchanged.

The following documentation preserves the direct operational skill references and this update's evidence links:

- `docs/research/brand-output-quality-2026-10-01.md` and `logo-brand-skills-plugins-2026-10-01.md`;
- `docs/research/logo-craft.md`, `font-tools.md` and `font-shortlist.json`;
- `docs/qa/brand-output-quality-2026-10-01/`, including the six related native PNGs and their existing receipts;
- the text-only `integrations/hermes/skills/director/references/THIRD_PARTY_NOTICES.md`, linked from the root attribution notice. No Hermes runtime or plugin manifest is packaged.

Tests, virtual environments, Python bytecode, runtime caches, private references and unrelated historical documentation images are excluded. All staged files are regular copies; no symbolic links are created inside the payload.

The two root READMEs retain repository-navigation links to older galleries, releases, Hermes and other documentation that are not part of this Codex bundle. The old implementation-plan link in `font-tools.md` and explicitly optional repository reference-plan examples are also outside the payload. This differs from operational skill links and the new research/QA evidence links, which are checked inside staging.

## Executed checks

The official installed `plugin-creator/scripts/validate_plugin.py` was run against staging with `PYTHONDONTWRITEBYTECODE=1` and returned exit 0. From the independent sibling workspace, the staged PEP 723 entry point was executed with:

```sh
PYTHONDONTWRITEBYTECODE=1 uv run --offline --no-project --script \
  <staged-plugin>/skills/logo-land/scripts/logo_project.py --help
```

It returned exit 0 and listed the expected helper commands. UV used already available package artifacts and reported installing 14 packages into its script environment. This verifies the staged standalone entry point with an available dependency cache; it is not a cold-cache offline installation. No project environment or Python bytecode was created inside the staged payload.

The first link audit checked 247 relative links across the operational skill, new research, attribution notice and related QA pages, with zero missing targets. A subsequent audit checked 258 links after additional QA records were included, also with zero missing targets. Staging contained no forbidden cache, bytecode, virtual-environment or symbolic-link entries. The simultaneous QA run updated three receipt files; source-drift detection identified those exact files and they were resynchronized.

Raw local receipts are in the task-local staging parent: `staging-checks.json`, `staging-link-check.json`, `staging-inventory.json` and `staging-final.json`. They retain command arguments, actual outputs, file hashes and scope checks without adding private account paths to this public report.

## Final installation and independent cache checks

The final installation snapshot was taken at **2026-10-01 10:30:27 UTC / 19:30:27 KST**, after the final source tests passed. It contained **293 files, 20,732,054 bytes**, including the final `pytest-final.txt`, `pytest-intermediate.txt` and `verification.md` then present. The official staging validator passed again. The old source, old cache and durable backup were rechecked byte-for-byte, and the active home symlink still resolved to this conversation's account. `CODEX_HOME` was not reassigned.

After the final installation go-ahead, a complete regular-file copy of staging replaced the personal source. The old source was retained separately as well as in the durable backup. These official commands all returned exit 0:

```sh
python3 <plugin-creator>/scripts/read_marketplace_name.py
python3 <plugin-creator>/scripts/update_plugin_cachebuster.py ~/plugins/logo-land
python3 <plugin-creator>/scripts/validate_plugin.py ~/plugins/logo-land
codex plugin add logo-land@personal --json
```

The actual add response reported `pluginId=logo-land@personal`, `marketplaceName=personal`, `version=0.9.0+codex.20261001103046` and `authPolicy=ON_INSTALL`. Its returned `installedPath` is under this conversation's active account home and resolves to **`~/.codex/plugins/cache/personal/logo-land/0.9.0+codex.20261001103046`**. That returned directory, rather than a guessed path, was used for subsequent checks.

All 293 personal and installed-cache files match byte-for-byte. All 292 non-manifest files match the final staging snapshot. After restoring only the clean version, the personal manifest's JSON object equals the repository manifest. Every one of the 107 scoped production files remains at its frozen source hash; the repository manifest, project and locked helper are still `0.9.0`. The installed payload aggregate SHA-256 is **`e076ad86516d361baeb34f9136e697c51bd3544e9787a5e53f6f1fe7e8027182`**.

The official validator passed against the returned cache. The actual cache's standalone PEP 723 helper also passed `uv run --offline --no-project --script <installed-helper> --help` from the separate workspace, with exit 0 and the expected prompt/export commands. This again uses available UV package artifacts and does not claim a cold-cache installation. No bytecode, virtual environment or symbolic link was introduced inside the payload.

The current account now contains only the intended new setting `[plugins."logo-land@personal"]` with `enabled = true`. A normalized hash of all other configuration content remained identical before and after installation. The personal marketplace retained its recorded SHA-256. The official installation removed the previous `0.6.0` cache; this task did not delete it directly. The 74-file durable rollback backup is still present and unchanged.

The installed QA folder is the **19:30:27 KST installation snapshot**. This final installation report and any subsequent repository verification-summary edits occur after that snapshot and are intentionally not recopied into the installed payload. This avoids a self-referential documentation/hash update loop; production-byte equality and actual cache integrity were checked independently.

Final local receipts are `installation-snapshot.json`, `installation-commands.json` and `installed-verification.json` in `output/installation-refresh-090-032ners8/`. The last receipt was recorded at **19:31:40 KST** and includes the actual add response, full installed file hashes, scoped configuration checks, validator output and installed-helper output. The durable backup remains available for rollback. Open a **new Codex conversation** and invoke **`$logo-land`** to load the refreshed skill.
