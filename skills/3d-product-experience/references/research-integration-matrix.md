# Three.js and GitHub research integration matrix

Research status is not production status. These entries describe useful directions from the Three.js/Web/Mini/indoor-scene survey; each remains deferred until the stated proof exists.

| Option | Useful when | Safe boundary | Proof required before production |
| --- | --- | --- | --- |
| Existing Three.js + GLTFLoader + KTX2 + Meshopt + hand-authored LOD | Current product shell and known GLB pipeline | Preserve as baseline; do not migrate for novelty | Existing regression, GLB contract, browser visual and device evidence |
| `three-mesh-bvh` | True mesh picking, material-region hit tests, occlusion, or ray queries exceed screen-space fallback | Isolated POC; keep current hotspot/card fallback | POC accuracy, build size, Three compatibility, desktop/touch E2E, visual occlusion evidence |
| `camera-controls` | Room bounds, first-person/orthographic zoom, camera paths, or robust presets are needed | Do not replace simple bottle orbit/zoom by default | POC with camera contract, gesture/accessibility regression, bundle/performance evidence |
| Photo Sphere Viewer | Future linked indoor panoramas with markers and async node loading | Separate panorama adapter, not a bottle renderer | Two-node panorama POC, mobile memory/load evidence, navigation fallback |
| Pannellum | Lightweight panorama fallback or constrained deployment | Use only when its feature set and licensing fit the project | Same panorama contract and device checks |
| `gltf-progressive` | Standalone room prototype where progressive glTF delivery is the actual bottleneck | Never replace the production bottle’s hand-authored LOD without proof | Network/quality benchmark, cache behavior, memory and fallback evidence |
| `threejs-miniprogram` | Reference for a first WeChat Mini Program slice | Pin its older Three.js compatibility; do not copy Web lifecycle code | DevTools build plus iPhone/Android real-device test with one low-spec GLB |
| `three-platformize` | Platform abstraction experiments for Mini/alternate runtimes | Treat documented texture/ArrayBuffer/dynamic JS/WASM limits as hypotheses until device-tested | Real-device POC, compression choice, memory/load/error evidence |
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
