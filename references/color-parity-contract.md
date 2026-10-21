# Cross-renderer color-parity contract

Use this gate whenever the same approved product is rendered by different engines, Three.js revisions, devices, Web/Mini adapters, or compression paths. Visual review is required after measurement, but eyesight alone must never approve color parity.

## 0. Automated pipeline (reference layout)

A repeatable, dependency-free capture-and-compare pipeline is described here as
a layout to copy into your own project. It is a contract, not a shipped tool:
this repository does not contain these files. Structure:

```text
color-parity/
  probes.json            # semantic probe definitions (relative coords + masks + tolerances)
  web-capture.js         # paste into DevTools console; captures web-probes.json
  color-metrics.mjs      # sRGB -> CIE Lab (D65), CIEDE2000, CIE76; no dependencies
  color-metrics.test.mjs # unit tests for the math
  compare.mjs            # web-probes.json vs mini-probes.json -> diff-report.json
  capture-screenshot-probes.mjs  # optional screenshot-based sampler
  README.md
```

Command chain:

```sh
# 1. Web: open the viewer, expose window.__three = { renderer, scene, camera },
#    paste web-capture.js, save output as web-probes.json.
# 2. Mini: run the automator capture (capture-mini-simulator.mjs) or the
#    viewer's captureColorProbes() export -> mini-probes.json.
node scripts/color-parity/compare.mjs web-probes.json mini-probes.json
```

The pipeline is the acceptance metric, not a diagnostic. If probes are missing or
the report is not generated, the color gate is not passed — do not substitute an
eyeball comparison.

### Evidence freshness and iteration rule

- Every renderer, material-profile, light, camera, asset, or compression change
  invalidates earlier captures and `diff-report.json` files. Recapture both sides
  or explicitly mark the old report stale; never combine current code with an
  older candidate's screenshots or metrics.
- Diagnose by semantic material family before changing numeric color: diffuse
  body, metal, print/decal, transparent, seal, and part edge. Confirm that
  glTF defaults did not accidentally make a nonmetal material metallic and that
  required tangents/environment processing are available in both renderers.
- Correct renderer-version capability gaps in a named platform adapter. Do not
  use trial-and-error RGB multipliers to make one screenshot look close, and do
  not overwrite the accepted GLB to compensate for a runtime difference.
- Do not apply screen-space or world-height RGB bands to a product to imitate
  environment lighting. Such compensation can appear acceptable in one front
  capture but becomes a false color band during orbit or top/bottom inspection.
  If a spatial correction is unavoidable, require product-space masks plus
  front, side, top, and bottom measurements before accepting it.
- A visual review follows a passing metric report and checks material response,
  highlight motion, transparency, seams, and identity artwork. It never replaces
  the report.

### Probe file contract

`probes.json` defines semantic regions in normalized coordinates (rx, ry in 0..1
of the canvas), each with an alpha-masked median sampler:

```json
{
  "metric": "CIEDE2000",
  "tolerance": { "deltaE_pass": 2, "deltaE_warning": 3, "deltaE_fail": 5 },
  "sampling": { "method": "median", "shape": "square", "radius": 2, "minSamples": 5 },
  "probes": [
    {
      "name": "body-main",
      "rx": 0.38, "ry": 0.5,
      "sampling": { "method": "median", "shape": "square", "radius": 3, "minSamples": 15,
                    "mask": { "alphaMin": 200 } },
      "description": "opaque material interior"
    }
  ]
}
```

Rules:

- opaque materials use `mask.alphaMin` (keep alpha >= ~200); transparent
  background probes use `mask.alphaMax` (keep alpha <= ~8);
- place probes inside stable material interiors, away from seams, labels,
  highlights, UI, and antialiasing edges;
- sampling reports `fallbackUsed` / `rejectedCount` so an under-sampled region
  is flagged instead of being silently trusted;
- a probe entry in a capture file may be a single `{r,g,b,a}` pixel, a
  `{rgb:{r,g,b}}` value, or a region capture containing `samples` and sampling
  metadata; compare.mjs normalizes all three;
- every product writes its own probe coordinates and material-class tolerances;
  never reuse another product's constants as-is.

### Capture condition fields

Both capture files must record `platform`, `threeVersion`, `renderProfile`,
`outputColorPipeline`, `canvasSize`, and `pixelRatio`. compare.mjs warns when
these diverge (e.g. different render profile, output pipeline, or aspect ratio)
before interpreting color values.

### Metric

sRGB -> D65 CIE Lab -> CIEDE2000 (Sharma/Wu/Dalal 2005) is the primary metric;
CIE76 is reported alongside for continuity. The math in color-metrics.mjs is
dependency-free and unit-tested. Do not use a global average as the acceptance
metric — report per-probe PASS/WARN/FAIL and the average only as context.

## 1. Lock capture conditions

A comparison is invalid unless both captures record and match:

- approved asset hash, product state, transform, and animation time;
- viewport CSS size, drawing-buffer size, aspect ratio, and DPR;
- camera FOV, position, target, azimuth, polar angle, distance, and framing;
- output color space, tone mapping, exposure, clear color, and alpha mode;
- environment/HDR hash, rotation, intensity, and every direct light;
- capture after model, textures, environment, and shaders have settled.

Verify framing before sampling. If the object-mask overlap, projected center, or projected product height falls outside the product contract, stop and mark the capture invalid; do not interpret its color values.

## 2. Sample semantic regions

Define regions from material, node, UV, object-ID, or an equivalent product-space mask. For every important opaque material, keep at least three separated stable interior patches. Erode masks away from silhouettes, seams, labels, antialiasing, UI, hotspots, shadows, and clipped or saturated highlights.

Record region name, material class, mask source, eligible pixel count, excluded count, and capture coordinates. A missing required region, fallback sample, or insufficient eligible-pixel count is a failed capture. Fixed page-relative coordinates and one RGB pixel may be used only as temporary diagnostics.

## 3. Measure distributions

Convert sRGB to D65 CIE Lab and calculate CIEDE2000 per eligible pixel or stable patch. Report P50, P95, maximum, and P50 absolute lightness difference `|Delta L*|`. Do not use a global average as an acceptance metric.

Unless the product contract is stricter, use these defaults:

| Material class | P50 Delta E00 | P95 Delta E00 | Additional requirement |
| --- | ---: | ---: | --- |
| Diffuse paint, ceramic, plastic | <= 2.0 | <= 3.0 | P50 `|Delta L*| <= 2.0` |
| Print, decal, label interior | <= 2.0 | <= 3.0 | inspect edge geometry separately |
| Metal, non-specular interior | <= 3.0 | <= 5.0 | zero wrong-material leakage |
| Transparent or translucent | no base-color gate | no base-color gate | compare opacity, silhouette, thickness overlap, refraction, and edge behavior under the same environment |
| Emissive | product-specific | product-specific | record luminance and tone-mapping conditions |

Metal highlights and transparent reflections are view- and environment-dependent. Compare their placement, clipping, leakage, and behavior separately. Matching screen RGB does not prove material equivalence.

### Renderer calibration boundaries

A platform adapter may compensate for missing capabilities (e.g. an r108 Mini
runtime without `RoomEnvironment`/PMREM gets a restrained forward fill and a
patched exact-sRGB output function). Keep such compensation in a named
render-profile module; never bake it into the approved source GLB. The render
profile id must be recorded in the capture file so a divergence between Web and
Mini is detectable before comparison.

## 4. Reject invalid evidence

Block release when:

- capture conditions differ or are unrecorded;
- only an eyeball comparison is supplied;
- a sample crosses a material boundary, seam, highlight, or UI;
- a required region is absent, undersampled, or uses fallback pixels;
- one global tolerance is used for every material class;
- a GLB base color is altered merely to compensate for a platform renderer;
- any required P50/P95 gate fails, even when a global average passes.
- the report or screenshot was produced by a different code/material profile
  than the build being accepted.

## 5. Preserve evidence and calibration boundaries

Store the capture manifest, semantic region specification, raw regional distributions, summarized report (`diff-report.json`), screenshots, renderer/device versions, and accepted asset hashes. Keep renderer compensation in a named platform adapter. Never write one product's calibration constants into this general contract or silently bake them into the approved source asset.

For a new product or a new color: copy the pipeline files, redefine only the
probe coordinates and material-class tolerances, run the same command chain,
and keep the diff-report.json as the release evidence. Do not start from
eyeballing.
