---
name: 3d-product-experience
description: Use when building or repairing a Three.js/glTF product viewer or its Web/Mini semantic contract.
---

# 3D Product Experience

## Outcome

Build an evolvable product-viewer experience without silently changing the approved product appearance. Treat the current model, product references, runtime behavior, and validation evidence as a contract; add capabilities through isolated assets, semantic configuration, and platform adapters.

Use the workflow for:

- Three.js + GLB/glTF product pages, H5 demos, and product detail modules.
- Soft goods, garments, and apparel viewer experiences (`apparel-garment`).
- Cleanup, decimation, and recovery of Hunyuan 3D, Tripo, or other AI-generated candidates.
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

### 0. Respect the Product 3D production boundary

This Skill governs product-viewer contracts and evidence; it is not a Blender
runtime or a claim that this repository contains a Blender/GLB/Three.js/Mini
implementation. For modeling routes, Blender state, checkpoints, and Current →
V1 → Future boundaries, read `references/product3d-production-boundary.md` and
the project-local `docs/product3d/` audit only when the task concerns modeling
architecture or production boundaries. Engineering diagnostics never
replace user visual acceptance. External research remains **待核验** until a
scoped POC or official source confirms it.

For a new 3D task, before the baseline pass, check your local 3D Research /
Capability Registry (or workspace knowledge base) and choose the route that
matches the request once for that task. It is a retrieval order, not an
automatic package choice; project code, lockfiles, and acceptance evidence
remain authoritative. If there is no documented gap, default to `reuse`. Only
after recording a gap, version/license, scoped POC, fallback, and rollback may
you search GitHub, install a package, or change renderer.

### 1. Establish the baseline and evidence map

Before touching code, read the portions of the project contract, product
manifest, asset register, prior review notes, and current tests that apply to
the requested change. Do not read unrelated test suites merely for
completeness. Inventory:

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
| `spatial` | linked panoramas or a navigable room | `SceneManifest`, light proxy/product anchors, `SceneSnapshot`, host Overlay/session, node preloading, bounds, occlusion/lighting contract, device budget; free walk is not implied |

Start at the smallest level that proves the request. A static opening demo is not a license to invent a screw thread or an animation. Keep `web`, `mini`, and `fallback` asset variants explicit even when only `web` exists.

### 3. Build a renderer-independent product contract

Define `productId`, `sceneNodes`, `materials`, `hotspots`, `cameraPresets`, `assetVariants`, `fallbackContent`, `capabilities`, `platforms`, and `provenance` in the existing machine-readable product manifest, extending it only with fields required by this task. Do not create a parallel manifest or a second system. For spatial work, keep a separate `SceneManifest`, `SceneProductAnchor`, `SceneSnapshot`, and `ViewerSession` contract; a Scene Viewer owns scene coordinates and return state, while a Product Viewer owns product GLB loading, materials, product camera, and interaction. Web and Mini Program share semantic content and asset intent, not a renderer or loader implementation. A platform adapter may choose a different Three.js version, compression, event lifecycle, and fallback.

Keep the runtime split into:

- **engine shell:** loading, quality/LOD, camera, gestures, accessibility, lifecycle, recovery;
- **product data:** model IDs, material IDs, copy, hotspots, presets, asset variants;
- **experience modules:** `open`, `reveal`, `compare`, or future product-specific actions;
- **platform adapters:** Web, Mini Program, panorama, or static poster.

Do not extract a large SDK after one product. Add a second product contract test first; extract only the seams both products actually use.

### 4. Handle candidates and product-specific states

For AI/generated candidates (Hunyuan3D, Tripo, etc.), read `references/ai-model-provenance-and-recovery.md`
for provenance, privacy, quarantine, UV, decimation, and material rules. Run the 4-step recovery pipeline
(headless decimation via `scripts/decimate_ai_glb.py`, metric transform normalization, separated orthographic
dual-sided UV re-projection, and PBR Sheen material injection). For soft goods (`apparel-garment`) and Blender
production boundaries, use `references/product3d-production-boundary.md`, `references/product-capability-contract.md`,
and `references/fabric-apparel-recipe.md`: **prioritize the AI Image-to-3D + 4-step recovery pipeline as the primary commercial route** (superior organic 3D silhouette and fabric drape), and use pure procedural quad-cage lofting (`scripts/blender_headless_garment.py`, user visual acceptance baseline 60/100) only when external 3D base meshes are prohibited. Subagent/Adversarial Critic scores are engineering diagnostics only and never replace user visual acceptance.
For an opening/reveal state, keep parts, pivots, camera snapshots, restore behavior, and reduced-motion checks in
the product manifest and evidence record. A candidate never replaces the approved runtime asset before visual acceptance.

### 5. Integrate Three.js research incrementally

Keep the existing Three.js/GLTFLoader/KTX2/Meshopt/LOD path unless a measured requirement proves it insufficient. Use the decision matrix in `references/research-integration-matrix.md`. Every candidate follows this order:

1. state the user behavior or asset problem;
2. pin Three.js/package versions and license;
3. create an isolated branch/POC with the smallest scene;
4. measure bundle/asset size, load time, frame rate, memory, and platform limits;
5. preserve the current fallback and visual baseline;
6. record accept, defer, or reject with deletion/rollback steps.

Do not install indoor-360 packages for a bottle task. Do not replace a realtime viewer with a scroll/pre-rendered system without an explicit product decision.

### 5.1 Spatial scene POC

Use this only when the user asks to enter or navigate a 3D space. Follow the
`SceneManifest` / `SceneProductAnchor` / `SceneSnapshot` / host Overlay boundary
in `references/product-capability-contract.md`; the first slice uses lightweight
anchors and an existing Product Viewer. Defer free walk, collision, navmesh,
multi-room portals, large assets, and Mini spatial parity until browser and
mobile evidence satisfies the explicit acceptance contract.

### 6. Validate in layers

For B2B page order, responsive 3D interaction, accessibility, privacy, and
visual evidence, read `references/qa-and-evidence-contract.md`. Apply
`references/color-parity-contract.md` when an approved product crosses renderer,
device, adapter, or compression boundaries. Asset acceptance and page readiness
remain separate gates.

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
- if `spatial` is enabled, `SceneManifest` anchors resolve to the correct Product Viewer, the host restores a versioned `SceneSnapshot`, an unavailable Viewer leaves the scene usable, and the desktop/mobile return path has browser evidence;
- when opening/reveal is in scope, opening/restore/Home state transitions preserve the camera and do not conflict with mobile rotation gestures;
- when a bottle product is in scope, full-bottle silhouette, cap side/interior, mouth/stopper, top artwork, label typography, material response, subject hierarchy, and safe areas are correct at desktop and phone sizes;
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

- `references/product3d-production-boundary.md` — modeling/runtime boundary, Blender state rules, and the Current → V1 → Future maturity contract.
- `references/ai-model-provenance-and-recovery.md` — generated-model failure modes, provenance, and privacy rules.
- `references/image-to-3d-pipeline.md` — step-by-step SOP for 4-step AI GLB reconstruction (`--mode rebuild`) and 1-base-GLB instant batch SKU generation (`--mode swap` / `--mode batch`).
- `references/product-capability-contract.md` — renderer-neutral manifest shape and complexity ladder.
- `references/research-integration-matrix.md` — researched Three.js/GitHub options and the POC gates for each.
- `references/poc-decision-record.md` — comparable plugin POC measurements, thresholds, and accept/defer/reject record.
- `references/qa-and-evidence-contract.md` — visual, automated, accessibility, performance, and evidence gates.
- `references/color-parity-contract.md` — repeatable cross-renderer capture conditions, semantic region sampling, material-specific CIEDE2000 gates, and invalid-evidence rules.
- `references/fabric-apparel-recipe.md` — physical simulation recipe for garments, PBR Sheen parameters, quad cage topology, drop shoulders, and dual-sided zero-bleed UV projection.
- `references/glass-liquid-optics-recipe.md` — optical PBR recipes for transmissive glass, liquids, IOR, chromatic dispersion, and caustic approximations.
- `references/single-file-bundle-guide.md` — esbuild IIFE bundling guidelines for standalone offline HTML viewers, inlining Base64 GLB assets, and avoiding browser sandbox CORS issues.
- `references/state-engine-architecture.md` — decoupling interactive state machines and scientific/physical laws from Three.js rendering loops.
- `scripts/validate-product-manifest.mjs` — dependency-free structural validator for a product manifest; run basic mode for legacy manifests and `--strict --strict-privacy` for new product contracts.
- `scripts/verify-media-privacy.mjs` — read-only `exiftool` check for GPS/location metadata before a media derivative enters GitHub or deployment.
- `scripts/decimate_ai_glb.py` — AI-generated GLB 4-step reconstruction tool (`--mode rebuild`) AND 1-base-GLB instant multi-SKU texture-swap/batch bundler (`--mode swap` / `--mode batch`, ~1s/SKU without launching Blender).
- `scripts/blender_headless_lathe.py` — Blender headless parametric rotational lathe script for bottles, jars, and cylindrical containers.
- `scripts/blender_headless_garment.py` — Blender headless parametric quad cage lofting script for T-shirts and garments without external GLBs.

Use the references only when the corresponding decision is in scope. Do not copy this Skill’s example values, private paths, raw photos, or proprietary GLBs into another product.
