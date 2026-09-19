# Product-directed prompt contract v2

These fixtures test the revised prompt policy on the unchanged inputs from the
app-icon quality matrix. They are expected text, not new image-generation evidence.
The original `docs/qa/app-icons/` fixtures and saved generation prompts remain
unchanged; `baseline-sha256.json` records the five source files used here.

The new expected strings apply only three reviewed changes to the old contracts:

- Include the supplied product, audience, use, styles and required exclusions as
  quoted context. Previously the prompt omitted this information, so the old
  blanket exclusion of `Audience` contradicted the new requirement. Exact brand
  text is still not introduced as unsolicited lettering.
- Replace the unrelated yellow/navy/sage fallback with product-directed shape,
  supporting-feature and background color roles. Explicit free-text and structured
  palettes remain unchanged, and an unspecified palette stays unspecified in state.
- Replace mandatory cute, heavy, rounded character proportions and two default
  subject colors with a deliberate expression, silhouette and curve/weight family
  suited to the supplied product. The chosen subject, pose, expression, material
  and colors remain authoritative.

The expected text was derived by applying those explicit replacements and adding
the quoted context to the prior fixtures; it was not copied wholesale from the
current builder. The five non-character style directions retain their exact text.
`directions-v2.json` also pins the character direction so all six styles participate
in the existing isolation assertions.

The tests still compare complete strings, verify exact Unicode, preserve parent
and palette intent, reject content beyond 20,000 characters, and keep the original
historical-prompt import/gallery preservation test pointed at the old fixture.
The 20,000-character boundary is computed from the new full expected strings, so
the newly included context counts toward the same limit.
