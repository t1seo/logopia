# Optional vector provider

Read this when a user requests actual SVG artwork. Native image generation and the
Logopia helper remain a PNG workflow. This reference documents an optional service
route; it does not add an SVG import/export command or install/connect a provider.

[Recraft's official remote MCP](https://www.recraft.ai/docs/mcp-reference/remote-server)
uses `https://mcp.recraft.ai/mcp`, Streamable HTTP and OAuth 2.0. It offers vector
generation and raster vectorization and shares Recraft Studio subscription credits.
Use the current connected tool schema, not a remembered tool name or API-key recipe.

If Recraft is already connected and the requested operation is authorized, use the
exact selected original as the reference/input supported by the tool. Preserve its
source artifact, final instructions and actual returned file. Service text alone is
not a local SVG artifact. If unavailable, report that limit and retain the PNG result;
do not silently connect an account, spend through another provider or claim SVG is
included in the existing package.

Inspect the returned SVG as a separate deliverable: confirm actual vector shapes or
paths rather than an embedded raster wrapper, render it, and compare spelling,
counters, silhouette, line weight, color and small-size appearance to the chosen
source. Check for clipped viewBox content and missing fonts/resources. An SVG with
live text still depends on its actual font setup; vectorization is not proof of
lettering accuracy, optical quality or editable font layers. Keep unresolved
differences visible and do not use a successful service call as design approval.

The helper currently accepts static PNG logo artifacts. Keep any separately verified
SVG beside the source project with provenance; do not rename it to PNG, add it to an
unchanged helper ZIP or advertise vector support as an installed Logopia capability.
There is no automatic vectorization fallback in the standard workflow.
