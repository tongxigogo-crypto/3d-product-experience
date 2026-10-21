# docs — reference adapter

A single static page that proves the contract is implementable.

- reads `manifest.json` (same shape as `examples/minimal`),
- builds the preset buttons and hotspots from the manifest,
- owns the numbers: the manifest declares `front` / `three-quarter` / `macro`
  as intent, this file maps them to camera positions,
- falls back to a poster panel when the model fails to load,
- respects `prefers-reduced-motion` (no camera tween) and keyboard access
  (`1`–`3` for presets, `Esc` to restore).

## Run locally

```sh
npm run demo    # http://localhost:4173
```

## Publish

GitHub Pages can serve this directory directly:
**Settings → Pages → Source: Deploy from a branch → `main` / `/docs`**.

## What it deliberately does not do

- It does not validate the manifest at runtime. Build-time validation is the
  gate; a viewer that silently accepts a broken manifest hides the failure.
- It does not ship a product asset. The model is Khronos' *Damaged Helmet*
  (CC BY 4.0) loaded from a CDN.
- It is not an SDK. There is no engine shell, no LOD policy, no platform adapter
  beyond a single `if` on `capabilities`. Those belong to a real product.
