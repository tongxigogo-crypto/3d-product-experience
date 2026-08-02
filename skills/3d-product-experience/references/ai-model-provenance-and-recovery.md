# AI-generated model provenance and recovery

## Why this reference exists

Generative 3D tools are useful for a first geometry pass, but they commonly invent brand text, smooth away real joins, change proportions, or bake a texture artifact into a material. The generated file is evidence of a candidate, not evidence of the product.

## Required provenance record

Store this beside the derivative, not inside a public asset URL:

```json
{
  "sourceTool": "Hunyuan 3D",
  "sourceToolVersion": "record-if-known",
  "sourceFile": "local/path/or/artifact-id",
  "sourceSha256": "64-hex-digest",
  "promptOrInputRef": "sanitized-reference-id",
  "seed": "record-if-known",
  "unitsAndTransforms": "record assumptions",
  "derivedAt": "YYYY-MM-DD",
  "derivativeSteps": ["clean text", "separate materials", "compress"],
  "reviewStatus": "candidate|provisional|approved"
}
```

Do not claim an exact dimension, thread, tolerance, liquid volume, or opening motion unless a measured source and its uncertainty are recorded.

## Recovery sequence

1. Hash and freeze the approved runtime asset before touching a candidate.
2. Keep the generated source unchanged; work in a versioned build directory.
3. Compare the candidate silhouette in front, side, three-quarter, and macro views.
4. Remove AI-generated glyphs and logos. Rebuild approved typography from a trusted label source.
5. Inspect for white/rectangular patches, residual orange or nonsense text, texture stretching, UV atlas bleed, and normals that turn a cap or mouth into a different shape.
6. Split materials and semantic parts needed by the requested capability.
7. Validate the derivative, then compare it against the baseline again.
8. If it fails, quarantine the derivative as a preview. Never silently promote it or overwrite the baseline.

## Privacy boundary

Original iPhone photos can contain GPS EXIF and other metadata. Keep them local-only. Use a reproducible, no-location derivative for a repository or deployment and record its new hash. A screenshot shown in a chat is not a license to commit the original file.

## Known failure patterns to prevent

| Failure | Prevention |
| --- | --- |
| Generated model changes the approved bottle/cap silhouette | Freeze the baseline; perform side-by-side silhouette review before runtime integration |
| A cap is cut from a single old mesh and becomes a thin disk | Rebuild independent outer/inner parts from references; do not infer hidden structure from one view |
| Cap interior or transparent stopper is too large, shallow, or opaque | Use a semantic part contract, macro reference views, and a dedicated visual gate |
| Top artwork disappears after restore | Use one coordinate system for bounds and overlays; assert visibility in both states and inspect an elevated browser view |
| Cap UV samples bottle text or creates spikes | Pin a clean ceramic atlas region and inspect top/side macro renders |
| A label number is changed from one proof to another and called real | Treat each product variant as separate evidence; do not synthesize regulated/brand facts |
