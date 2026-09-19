# Preference is separate from production QA

Use `preference-gallery --selection-file comparison.json --output output/blind` for 1–12 explicit candidate pairs. Each source identifies `session`, `revision`, `artifact`; include `shared_brief`, `references`, `seed`, `ai_review_budget` and `response_limit`. Same input/seed yields the same balanced order. The interface hides method names, creator self-reviews and source filenames. The unlinked manifest is the organizer's mapping, not access control.

Allow `a`, `b`, `tie`, `neither`. Require visible evidence for brief/reference fit, shape/background, curves/terminals/spacing/typography, effects, possible confusion, 32px recognition and equal-size peers. Do not invent beauty scores, global uniqueness or trademark clearance. A metaphor that needs no verbal explanation can still work; symmetry and color count are not absolute criteria.

The offline form downloads a response. `preference-record --gallery output/blind --response-file response.json` checks candidate hashes/revisions and appends a separate immutable record. It never sets the session selection, production review or export status. AI observers declare `reviewer_kind: ai` and actual `review_calls`; humans use `user` and zero model calls. Budget checks constrain accepted records; an external caller must reserve any model calls before dispatch. No additional review provider runs automatically.

32/48/64/128 CSSpx, light/dark surroundings and masks are diagnostic simulations, not official universal icon sizes or OS screenshots. Keep both candidates at the same size and use the same peer set. Do not present a tilted glossy mockup as evidence of a strong silhouette. The repository's `docs/preference-review.md` contains a complete six-original input example.
