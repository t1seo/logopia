# Preference review functional verification

The initial checks below use explicitly labeled synthetic fixtures. They verify software behavior, not icon quality or a real user's design preference. A later section records rendering checks with the six actual generated SEAM icons.

- `uv run pytest -q tests/test_app_icon_gallery.py tests/test_icon_context.py tests/test_preference_*.py`: **56 passed**.
- Ruff check/format and basedpyright on all new preference modules, the edited icon-gallery module, and their tests: **clean; 0 type errors/warnings**.
- Existing icon-gallery original PNG bytes and exact prompts remain paired; 32/48/64/128 sizes, source/revision checks, no-reference input, invalid paths, failed publication cleanup, all four preference outcomes, response hashes, AI/user distinction, independent recorded-review budget, stale/mismatched/corrupt records and unchanged Session bytes are covered.

In Orca's embedded desktop browser, the local CLI output was opened and inspected. Both candidates decoded successfully, with equal measured widths of **32, 48, 64 and 128 CSS px**. The circle control applied **50% CSS border radius** to both, and opened home peers both measured **48px**. There was no horizontal overflow at the tested **1399px** viewport.

The form produced a **1,286-byte JSON response** through its actual submit/download handler. Its reviewer explicitly says “Functional browser QA only; not a real user preference.” Applying that response with the public `preference-record` CLI succeeded, and the source Session SHA-256 remained identical. This synthetic `user_preference` fixture tests the user input route; it is not human preference evidence.

The normal icon-gallery was also opened. Selecting **48px + dark surface + rounded mask** produced `[48,48]` widths in original cards, home peers and list peers, **23% CSS border radius**, and background `rgb(32,36,32)`. Original and exact-prompt download links remained available.

Local ignored evidence:

- `output/icon-craft-2026/preference-ui-qa/browser-desktop.png`
- `output/icon-craft-2026/preference-ui-qa/browser-open-peers.json`
- `output/icon-craft-2026/preference-ui-qa/downloaded-response.json`
- `output/icon-craft-2026/preference-ui-qa/session-before.sha256`
- `output/icon-craft-2026/preference-ui-qa/normal-controls.json`
- `output/icon-craft-2026/preference-ui-qa/test_real_cli_when_gallery_and0/작업 공간/{cli-blind,normal-icons}/index.html`

No model calls were made by these commands. The per-gallery AI budget limits accepted records; an external caller must enforce its job budget before dispatching a review. Blinding is interface-level, not access control over the organizer manifest. Native OS rendering, mobile viewport behavior, authenticated reviewer identity and real-user preference remain unverified by this functional check.

## Six actual SEAM originals: browser rendering check

The normal and blind galleries in `docs/research/icon-craft-2026/experiment/` were opened with their six real generated 1254px PNGs. This pass inspected rendering only: **no preference option was selected, no observation or reviewer name was entered, and no preference record was created**.

- All six originals and their repeated preview images decoded successfully. Normal-gallery cards, home peers and list peers measured exactly **32/48/64/128 CSS px** when each size control was selected.
- Both light and dark surroundings were applied equally. The square/rounded/circle controls applied the same **0px/23%/50% CSS border radius** to every candidate and context. These are diagnostic masks, not platform shape specifications.
- The blind gallery showed **three pairs**, A/B labels only, and **48px peers** in identical home/list contexts. Source artifact IDs, method names and creator rationale were absent from the pair interface. Reference evidence was text/source links only; there were **zero reference-image copies**.
- At **1399px** desktop width there was no horizontal overflow. At **390 × 844 CSS px**, both normal and blind layouts switched to one column with no horizontal overflow; the four diagnostic sizes retained their dimensions. The narrow screenshots use an explicit browser viewport at **device scale factor 1**, not native phone rendering.
- SHA-256 verification after browsing passed for **all 18 PNG files**: six originals plus their six normal-gallery and six blind-gallery copies. See `originals-before.sha256` and `originals-after-check.txt` under the evidence directory.

Reviewed screenshot evidence in `docs/qa/icon-craft-2026/browser/`:

- `normal-desktop-64.png`: six candidates at the same 64px tile size.
- `normal-mobile-peers.png`: all six peers in a 390px-wide home/list simulation.
- `blind-desktop-sizes.png`, `blind-desktop-pair02.png`, `blind-desktop-pair03.png`: all three actual A/B pairs, 32/48/64/128px on light/dark surfaces.
- `blind-mobile-sizes.png`: a 390px-wide single-column A/B comparison.

The browser's iPhone device preset initially produced a duplicated lower region in captured screenshots while DOM measurements remained correct. Those captures were discarded from the published evidence and retaken using Orca's documented `viewport --width 390 --height 844 --scale 1 --mobile` command. The final screenshots were opened and visually checked. No Logopia code changes were required. User preference, OS icon behavior and platform acceptance remain unverified.
