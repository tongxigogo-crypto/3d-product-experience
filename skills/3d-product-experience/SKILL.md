---
name: 3d-product-experience
description: Use when building, repairing, or extending a Three.js/glTF product experience, especially an AI-generated model, a static assembly/opening state, a configurable product viewer, a Web/Mini Program shared contract, or a future panorama/room path. Protects an approved visual baseline, separates product facts from demo assumptions, evaluates GitHub/Three.js options through scoped POCs, and requires desktop/mobile visual and automated evidence before delivery.
---

# 3D Product Experience

## Outcome

Build an evolvable product-viewer experience without silently changing the approved product appearance. Treat the current model, product references, runtime behavior, and validation evidence as a contract; add capabilities through isolated assets, semantic configuration, and platform adapters.

Use the workflow for:

- Three.js + GLB/glTF product pages, H5 demos, and product detail modules.
- Cleanup or reuse of Hunyuan AI or other generated 3D candidates.
- Static opening, assembly, reveal, or disassembly states that are not yet a measured digital twin.
- Product viewers that must work on desktop and touch devices and later share content with a Mini Program.
- Evaluating a Three.js/GitHub package before it becomes a production dependency.

## Non-negotiable contract

1. **Freeze the approved baseline.** Record the path and SHA-256 of every accepted asset before editing. Never overwrite it, rescale it in place, or let a platform-compressed variant replace it. Create a versioned derivative such as `*-open-mode.glb` and keep a reversible manifest.
2. **Keep facts separate from demo assumptions.** Label guessed dimensions, cavity depth, cap placement, lighting, and static poses as `demo`. Do not present a photo-based guess as a 1:1 digital twin. Measurements, tolerances, threads, and real motion require their own evidence and phase.
3. **Preserve the silhouette and identity.** A requested detail must not change the approved bottle, cap, label proportions, color, typography, material response, or camera baseline unless the user explicitly approves a new product revision. Compare front, side, three-quarter, and macro views after every geometry/material change.
4. **Separate source, derivative, and runtime assets.** Keep editable AI/Blender sources and build artifacts outside `public/` when possible. Store provenance and hashes; make runtime GLBs reproducible or explain why they are hand-authored.
5. **Protect private references.** Original phone photos, GPS EXIF, private customer material, and unlicensed source files stay local. Strip location metadata and create a no-location derivative before any GitHub or deployment handoff. Never place raw reference paths in a public manifest.
6. **No research-only integration.** A README, benchmark, or GitHub repository is not evidence that a package works in this product. A package enters production only after a scoped POC, pinned versions, platform/license review, fallback, and visual/performance evidence.
7. **Visual acceptance is a hard gate.** Automated tests cannot approve a 3D change by themselves. Inspect screenshots or a browser session at the important states and record what was checked. If visual inspection was not possible, report “not visually accepted.”

## Workflow

### 1. Establish the baseline and evidence map

Read the project contract, product manifest, asset register, prior review notes, and current tests before touching code. Inventory:

- approved model paths and hashes;
- candidate/generated model paths and their provenance;
- reference photos/video and whether they contain sensitive metadata;
- semantic nodes, materials, camera presets, fallbacks, and existing interactions;
- current build, lint, typecheck, asset validator, E2E, and browser evidence.

Write a short change contract: desired user-visible result, preserved behavior, new assets, assumptions, risks, and rollback target.

### 2. Classify the requested capability

Use additive capability flags rather than product-specific branches:

| Level | Typical behavior | Required contract |
| --- | --- | --- |
| `static` | one model, camera presets, poster fallback | asset variant, materials, camera, fallback |
| `interactive` | orbit/zoom, hotspots, label or material cards | semantic nodes, hit target, keyboard/touch behavior, accessible fallback |
| `assembly` | static or animated open/close/reveal states | independent parts, state endpoints, camera snapshot/restore, reduced-motion path |
| `spatial` | linked panoramas or a navigable room | scene graph, node preloading, bounds, occlusion/lighting contract, device budget |

Start at the smallest level that proves the request. A static opening demo is not a license to invent a screw thread or an animation. Keep `web`, `mini`, and `fallback` asset variants explicit even when only `web` exists.

### 3. Build a renderer-independent product contract

Define `productId`, `sceneNodes`, `materials`, `hotspots`, `cameraPresets`, `assetVariants`, `fallbackContent`, `capabilities`, `platforms`, and `provenance` in a machine-readable manifest. Web and Mini Program share semantic content and asset intent, not a renderer or loader implementation. A platform adapter may choose a different Three.js version, compression, event lifecycle, and fallback.

Keep the runtime split into:

- **engine shell:** loading, quality/LOD, camera, gestures, accessibility, lifecycle, recovery;
- **product data:** model IDs, material IDs, copy, hotspots, presets, asset variants;
- **experience modules:** `open`, `reveal`, `compare`, or future product-specific actions;
- **platform adapters:** Web, Mini Program, panorama, or static poster.

Do not extract a large SDK after one product. Add a second product contract test first; extract only the seams both products actually use.

### 4. Handle AI-generated model candidates safely

Treat Hunyuan AI (or another generator) as a geometry/material starting point, not as brand truth. Record tool/model version, prompt or input references, seed if available, source hash, units, transforms, and derivative steps. Then:

1. preserve the generated source unchanged;
2. audit the silhouette against approved V1/reference photos;
3. remove hallucinated text, logos, embossing, white rectangles, side labels, and residual colored glyphs;
4. rebuild brand typography from an approved source as a decal/geometry/material layer;
5. separate ceramic, metal/gilt, transparent stopper, liner, and liquid materials where the experience needs them;
6. validate UVs and atlas sampling so a cap never samples bottle text or develops a texture spike;
7. compare macro cap/mouth views and full-bottle views before considering the derivative.

If the candidate cannot meet the visual contract, keep it as a quarantined preview and do not substitute it for the approved runtime model.

For an opening/reveal demo, make the parts independently addressable. Put the cap, liner, stopper, and emblem in a stable node contract; use one coordinate system for bounds, pivot, and overlays. Save camera target, distance, azimuth, elevation, and rotation before entering the state. Escape or “restore” must return that snapshot; Home must return the documented default. Assert these transitions in tests and inspect them in a browser. A missing top emblem or a cap that becomes a disk is a release failure, not a polish item.

### 5. Integrate Three.js research incrementally

Keep the existing Three.js/GLTFLoader/KTX2/Meshopt/LOD path unless a measured requirement proves it insufficient. Use the decision matrix in `references/research-integration-matrix.md`. Every candidate follows this order:

1. state the user behavior or asset problem;
2. pin Three.js/package versions and license;
3. create an isolated branch/POC with the smallest scene;
4. measure bundle/asset size, load time, frame rate, memory, and platform limits;
5. preserve the current fallback and visual baseline;
6. record accept, defer, or reject with deletion/rollback steps.

Do not install indoor-360 packages for a bottle task. Do not replace a realtime viewer with a scroll/pre-rendered system without an explicit product decision.

### 6. Validate in layers

When an approved product crosses renderer versions, devices, Web/Mini adapters, or compression paths, apply `references/color-parity-contract.md` before visual sign-off. Eyeballing, a single RGB pixel, fixed page coordinates without a framing contract, or a global average Delta E are not release evidence.

Run the repository’s applicable commands, normally:

```text
lint → typecheck → unit/contract tests → build
asset/hash/GLB validators → browser E2E → desktop/mobile visual review
```

The exact command names are project-owned. At minimum verify:

- approved baseline hash is unchanged;
- new GLB nodes/materials/variants satisfy the manifest;
- no raw GPS/private path is shipped;
- loading failure, WebGL recovery, poster/2D fallback, reduced motion, keyboard, screen reader, and touch behavior remain usable;
- opening/restore/Home state transitions preserve the camera and do not conflict with mobile rotation gestures;
- full-bottle silhouette, cap side/interior, mouth/stopper, top artwork, label typography, material response, subject hierarchy, and safe areas are correct at desktop and phone sizes;
- warnings are classified and recorded rather than silently ignored.

Capture command output, hashes, browser screenshots or video, viewport/device, and known limitations in an evidence record. Never call a change final when only a build passed.

### 7. Close the iteration for the next product

For every accepted or deferred change, update a small decision log containing:

- baseline and derivative hashes;
- source/provenance and sensitive-file handling;
- capability level and platform variants;
- files and contracts changed;
- verification evidence and remaining warnings;
- rollback target and follow-up material needed for a true digital twin.

Keep the engine extensible through data and adapters, not speculative abstractions. A future product may have no opening state, many hotspots, a room panorama, or a different complexity budget; its manifest should enable or omit capabilities without weakening baseline or fallback guarantees.

## Included references and script

- `references/ai-model-provenance-and-recovery.md` — generated-model failure modes, provenance, and privacy rules.
- `references/product-capability-contract.md` — renderer-neutral manifest shape and complexity ladder.
- `references/research-integration-matrix.md` — researched Three.js/GitHub options and the POC gates for each.
- `references/poc-decision-record.md` — comparable plugin POC measurements, thresholds, and accept/defer/reject record.
- `references/qa-and-evidence-contract.md` — visual, automated, accessibility, performance, and evidence gates.
- `references/color-parity-contract.md` — repeatable cross-renderer capture conditions, semantic region sampling, material-specific CIEDE2000 gates, and invalid-evidence rules.
- `scripts/validate-product-manifest.mjs` — dependency-free structural validator for a product manifest; run basic mode for legacy manifests and `--strict --strict-privacy` for new product contracts.
- `scripts/verify-media-privacy.mjs` — read-only `exiftool` check for GPS/location metadata before a media derivative enters GitHub or deployment.

Use the references only when the corresponding decision is in scope. Do not copy this Skill’s example values, private paths, raw photos, or proprietary GLBs into another product.
