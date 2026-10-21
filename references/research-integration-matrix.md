# Three.js and GitHub research integration matrix

Research status is not production status. These entries describe useful directions from the Three.js/Web/Mini/indoor-scene survey; each remains deferred until the stated proof exists.

After the entry skill selects a route, use this matrix to compare research
options. A matching verified baseline remains the default reuse path. Do not
install a package or restart GitHub selection until the gap, scope,
version/license, fallback, and rollback are recorded.

For the first spatial slice, keep `SceneManifest`, `SceneProductAnchor`,
`SceneSnapshot`, and `ViewerSession` in the platform host and use external
projects only to compare scene graph, room, navigation, or camera concepts.

| Option | Useful when | Safe boundary | Proof required before production |
| --- | --- | --- | --- |
| Existing Three.js + GLTFLoader + KTX2 + Meshopt + hand-authored LOD | Current product shell and known GLB pipeline | Preserve as baseline; do not migrate for novelty | Existing regression, GLB contract, browser visual and device evidence |
| `glTF-Transform` | GLB size, texture, mesh, metadata, or repeatable build-time optimization is the measured problem | Build-time derivative only; preserve semantic nodes/materials, runtime decoder path, baseline hash, and rollback | Before/after asset/hash/visual comparison, load/memory/device evidence, pinned version/license |
| `meshoptimizer` / Khronos glTF Validator | Mesh compression or structural validation is required by an existing runtime contract | Keep compression/validation in the asset pipeline; do not silently alter product geometry or viewer code | Validator report, decoder compatibility, size/load/memory and fixed-view evidence |
| `three-mesh-bvh` | True mesh picking, material-region hit tests, occlusion, or ray queries exceed screen-space fallback | Isolated POC; keep current hotspot/card fallback | POC accuracy, build size, Three compatibility, desktop/touch E2E, visual occlusion evidence |
| `camera-controls` | Room bounds, first-person/orthographic zoom, camera paths, or robust presets are needed | Do not replace simple product orbit/zoom by default | POC with camera contract, gesture/accessibility regression, bundle/performance evidence |
| SPHR | A lightweight scene graph, linked panoramas/3DGS layers, navigation nodes, tours, or camera moves are being compared | Borrow scene/route concepts only; keep the current platform and Product Viewer runtimes | Small scene/anchor POC, camera snapshot/return evidence, license and device/memory review |
| OpenVGAL | Room/door/product topology or connected-room JSON is needed for a showroom/floor-plan model | Borrow `room → door → product` data ideas; do not migrate its Babylon.js runtime | Two-room or two-anchor POC, back/restore behavior, asset and license review |
| Threepipe | Viewer/configurator/editor plugins, serialization, or resource disposal are a measured gap | Isolated comparison only; do not replace the existing Three.js baseline for architecture convenience | Same-product feature POC, bundle/load/memory evidence, pinned version/license and rollback |
| Pascal Viewer | Node registry, stacked/exploded/solo levels, cutaway, or camera modes are required | Concept reference only; no React/R3F/WebGPU migration without a separately approved route | Narrow interaction POC, platform/browser support, accessibility/performance and license evidence |
| xeokit BIM Viewer | Multi-model BIM coordination, object state, viewpoints, or sectioning is explicitly required | BIM/AGPL-specific; API shape reference only for the current product platform | Requirement proof, license decision, model-size/device evidence and isolated adapter |
| Needle Engine | XR, physics, multiplayer, or multi-scene runtime is explicitly required | Commercial/EULA and heavier runtime; defer for ordinary showroom/product entry | Explicit product decision, licensing review, smallest scene POC, device/perf and rollback evidence |
| Photo Sphere Viewer | Future linked indoor panoramas with markers and async node loading | Separate panorama adapter, not a product renderer | Two-node panorama POC, mobile memory/load evidence, navigation fallback |
| Pannellum | Lightweight panorama fallback or constrained deployment | Use only when its feature set and licensing fit the project | Same panorama contract and device checks |
| `gltf-progressive` | Standalone room prototype where progressive glTF delivery is the actual bottleneck | Never replace the production product’s hand-authored LOD without proof | Network/quality benchmark, cache behavior, memory and fallback evidence |
| `threejs-miniprogram` | Reference for a first WeChat Mini Program slice | Pin its older Three.js compatibility; do not copy Web lifecycle code | DevTools build plus iPhone/Android real-device test with one low-spec GLB |
| `three-platformize` | Platform abstraction experiments for Mini/alternate runtimes | Treat documented texture/ArrayBuffer/dynamic JS/WASM limits as hypotheses until device-tested | Real-device POC, compression choice, memory/load/error evidence |
| Product/CADQuery/Geometry Nodes pipeline | Silhouette, part interfaces, threads, or measured manufacturing geometry is explicitly required | Keep source geometry and canonical GLB separate from runtime; AI mesh is only a candidate/base | Measured dimensions, fixed-view comparison, topology/material/hash evidence and user visual acceptance |
| Flooring profile/Extrude/Geometry Nodes pipeline | A floor/profile product needs repeatable cross-section, groove, extrusion, UV, or variant generation | Generate isolated candidates; do not overwrite the frozen Web/Mini runtime asset or contract | Cross-section/length/UV checks, four-view render, GLB/runtime validation and rollback |
| `scroll-world` | Pre-rendered continuous camera/scrub stories | Separate from realtime Three.js; choose per experience | Product decision, asset budget, reduced-motion/keyboard fallback, visual comparison |
| `img2threejs` | Process reference for blockout → structure → form → material → lighting → interaction | Guidance and quality gates only; never a substitute for the approved GLB | Apply the process to a disposable candidate and keep provenance |

## Integration record

For each option create a short record:

```text
Need: the user behavior or asset problem
Scope: web / mini / panorama and affected capabilities
Versions: Three.js, package, loader, license
POC: isolated branch, smallest scene, commands
Evidence: type/build/E2E, screenshots, size, load, frame/memory, devices
Fallback: how the current baseline still works
Decision: accept / defer / reject
Rollback: dependency and file removal steps
```

Use `references/poc-decision-record.md` when numbers need to be compared across products. It supplies starting budgets for bundle, cold load, FPS, memory, visual parity, and accessibility; a product may override them only with an explicit evidence-backed exception.

Never install a package merely because a research note mentions it. Indoor 360° belongs to a later web phase unless the current product brief changes.
