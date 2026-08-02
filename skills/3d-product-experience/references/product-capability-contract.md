# Product capability contract

The contract is semantic and renderer-neutral. Web, Mini Program, and future panorama adapters consume the same intent while keeping their loaders, event lifecycles, compression, and fallback behavior separate.

## Minimal shape

```json
{
  "schemaVersion": "0.1",
  "productId": "product-id",
  "provenance": { "baselineAsset": "path", "baselineSha256": "64-hex" },
  "capabilities": ["static", "interactive"],
  "platforms": {
    "web": { "renderer": "three.js", "status": "current" },
    "mini": { "renderer": "platform-adapter", "status": "planned" }
  },
  "sceneNodes": [
    {
      "id": "shell",
      "semantic": "approved-product-shell",
      "assetVariants": { "web": "shell-web", "mini": "shell-mini", "fallback": "poster" },
      "materialIds": ["ceramic", "gilt"],
      "cameraPreset": "front"
    }
  ],
  "materials": [],
  "hotspots": [],
  "cameraPresets": [],
  "fallbackContent": { "poster": "poster-id", "failure": "2d-card" },
  "assets": []
}
```

## Contract rules

- `id` values are stable semantic IDs; renderers must not be required to know mesh indices.
- Every runtime scene node declares an asset variant or an explicit `null`/deferred policy per platform.
- Every interactive hotspot declares a semantic target and an accessible 2D/card fallback.
- Camera presets describe intent (`front`, `macro-label`, `open-mouth`, `panorama-node`); numeric values remain adapter-specific unless a shared calibration is proven.
- `capabilities` is additive. A product without `assembly` must not load opening-only assets; a product with `spatial` must also declare device budgets and fallback nodes.
- `provenance` and asset hashes make a promotion/reversal auditable.

## Complexity ladder

### `static`

One model, controlled camera presets, poster fallback, and an accessible text/product card. The first slice for a new product.

### `interactive`

Orbit/zoom, touch gestures, keyboard controls, semantic hotspots, material/ingredient cards, reduced-motion behavior, and hit-test fallback.

### `assembly`

Independent parts, state endpoints, optional animation, camera snapshot/restore, per-state lighting, and a no-animation path. A static opening demo belongs here with only a terminal state.

### `spatial`

Linked panoramas or a navigable room with node preloading, bounds, occlusion, lighting, camera paths, memory budgets, and device-specific fallback. Keep this separate from the bottle viewer until a real requirement exists.

## Extending safely

Add a new capability by adding a contract field, an isolated experience module, and tests for the old capabilities. Do not create an all-purpose viewer API until a second product proves the seam. If Web and Mini diverge, preserve shared semantic IDs and content while allowing platform-specific asset variants and renderers.

## Validation modes

Run `scripts/validate-product-manifest.mjs --file manifest.json` for a compatibility check on an existing project. For a new product, run `--strict --strict-privacy`: it requires the capability ladder, platform/material/hotspot/camera collections, interactive fallbacks and targets, assembly parts/states/camera-restore/reduced-motion fields, repository-relative media paths, and sanitized media declarations. If a slice must include a known capability set, add `--require-capabilities static,interactive`. Project-specific GLB, EXIF, device, and visual validators remain necessary.
