# Eight brand studies

[Open the gallery](index.html) · [한국어 README](../../../README.ko.md) · [English README](../../../README.md)

Eight fictional briefs explore different kinds of identity: expressive Latin lettering, Hangul, editorial capitals, an abstract symbol, a lettermark, a pictorial mark, a character and a dimensional app icon. Each has its own audience, color relationship and intended application. The gallery shows the original artwork beside a small illustrative use context, with PNG and exact-prompt links.

| Study | Design focus | Intended use | Original |
|---|---|---|---|
| rillo | Vermilion brush lettering on pink; a large dot and low letter rhythm | Fruit soda packaging and a product header | [PNG](images/01-rillo-v2.png) |
| 사이 | Cobalt Hangul on yellow; flared terminals and an open oval counter | Bookshop programs and a header | [PNG](images/02-sai-v2.png) |
| ALINE | Wine-colored Roman capitals on mist; controlled stroke contrast | Architecture and craft editorial identity | [PNG](images/03-aline-v1.png) |
| TANDEM | Two apricot comma-like masses with a shared curved interval | A private conversation product | [PNG](images/04-tandem-v1.png) |
| AL | Pine-colored serif capitals on pink; balanced weight and a separated lower gap | Architecture project covers and a studio profile | [PNG](images/05-al-v2.png) |
| RED HEN | A red bird silhouette with dark details on sky blue | Bakery bags, labels and stickers | [PNG](images/06-red-hen-v1.png) |
| Pip | An orange bird with a large curved beak and half-lidded eye | A voice-note companion's app icon | [PNG](images/07-pip-v1.png) |
| Spool | An orange spool with a visible thread end on blue | A craft organizer's app icon | [PNG](images/08-spool-v1.png) |

## What was made and reviewed

The collection used **11 native image calls: eight originals and three exact-parent edits**, within a shared ceiling of twelve. The first rillo and 사이 results returned unwanted transparency and edge debris. Their second versions restore opaque backgrounds while retaining the identifying lettering. AL's second version opens the lower gap between its two letters. All eleven returned originals remain available; no scripted recoloring or contour repair was applied.

An independent model critic inspected the actual images before reading the generation prompts, then compared the three edits with their parents. The observed strengths and limits are recorded in [the review](reviews/selection.md). These selections are a director's proposed showcase, not user adoption. The briefs differ from the earlier rejected collection, so this is not a controlled before/after benchmark.

Six brand studies used the persisted quality loop. The two app-icon studies used their existing icon-intent sessions with the same collection budget and independent review. Concise authored prompts are now reserved through `loop-request --prompt-file`; exact source revisions, parent images, import matching and budgets still apply. A shorter prompt is not proof of better output.

## Research behind the directions

The research examined working identities in use, rather than treating a list of attractive adjectives as a design specification:

- [COLLINS — Sweetgreen](https://wearecollins.com/case-studies/sweetgreen/) and [Ogilvy](https://wearecollins.com/case-studies/ogilvy/): expressive lettering, rhythm and an identity's application across surfaces.
- [Studio fnt — Wisdom House](https://studiofnt.com/WISDOM-HOUSE): Hangul construction and the relationship between lettering and a publishing identity.
- [Otherway — BaseHall](https://www.otherway.com/work/basehall): how a compact identity is carried by color and everyday packaging.
- [COLLINS — Mailchimp](https://wearecollins.com/case-studies/mailchimp/): the relationship between character, lettering and a broader identity system.

These are analytical references, not image attachments to the native calls, copied brand assets or endorsements. The study names and forms are new proposals.

## Files and scope

- [Manifest](manifest.json): selected versions, all returned artifacts, hashes, parent lineage and call count.
- `briefs/`, `prompts/`, `receipts/`: fictional briefs, exact native input text and portable tool receipts. The native tool did not report a model identity.
- `images/`: unchanged native PNGs; three lettering originals are 1774 × 887 and the other five masters are 1254 × 1254. Every selected version is fully opaque.
- `data.js` and `index.html`: offline gallery. CSS hides exterior margins or scales the source for display; each original remains downloadable. Palette swatches express design intent, not exact raster HEX certification.

These are raster identity studies. They do not include editable fonts, vector masters, transparent variants, platform icon packages, print proofs or trademark clearance. Application panels are illustrative HTML, not client deployments. [QA evidence and limits](../../qa/brand-studies-2026-10-01.md) distinguish diagnostic image inspection from browser verification. Public receipts summarize the run; they are not a resumable copy of the private helper workspace.

Earlier experiments remain in the [six-use-case archive](../2026-10-01-use-cases/README.md) and [Pebble comparison](../2026-10-01-pebble-study/README.md), with their rejection history intact.
