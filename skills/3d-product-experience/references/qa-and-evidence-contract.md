# QA and evidence contract

## Automated gates

Use project-native commands where available. The usual order is:

```text
lint
typecheck
unit and contract tests
build
asset/hash and GLB validators
browser E2E
```

Record command, commit, environment, result, and warnings. A warning is acceptable only when its scope and fallback are understood.

## Browser states to inspect

At minimum capture desktop and phone-sized evidence for:

1. initial loading and poster/failure fallback;
2. default front view;
3. representative orbit/zoom and nearest-label view;
4. each new experience state (for opening: mouth, stopper, cap interior, top artwork);
5. restore/Escape and Home;
6. reduced-motion and keyboard/screen-reader path where relevant.

Check silhouette, proportions, label legibility, material response, light/highlight obstruction, occlusion, subject hierarchy, safe-area cropping, touch-target separation, and whether a gesture conflicts with a button. Do not accept “looks right” from a single angle.

For runtime decals or transparent artwork overlays, verify their transform and
occlusion contract explicitly: parent them to the product/part coordinate
system, keep depth testing enabled, prefer the physically correct face side,
and capture both the intended front/top view and the opposite/back/bottom view.
An overlay that remains visible through the product or appears screen-fixed is
a release failure even when its default screenshot is correct.

## Color consistency hard gate

When the same approved product is rendered by different engines, revisions, devices, platform adapters, or compression paths, read and apply `color-parity-contract.md`. Measured color evidence must pass before visual review; visual review remains mandatory for geometry, highlights, metal response, transparency, and hierarchy. A visual-only comparison is not color acceptance.

## Interaction and accessibility gates

- Do not bind a tap target so broadly that it steals a touch rotation gesture.
- Preserve keyboard focus, Escape/Home semantics, visible focus, names/labels, and 2D/card fallback.
- Keep reduced-motion behavior deterministic; a static state is preferable to an invented animation.
- Test WebGL loss/retry and slow/failed asset loading without leaving the user at a blank canvas.

## Asset and privacy gates

- approved baseline hash unchanged;
- derivative GLB nodes, materials, extensions, and asset variants match the manifest;
- no raw GPS-bearing photos, private absolute paths, secrets, or unlicensed source files in shipped output;
- platform-specific limits are recorded as tested facts, not assumptions.

For supplied photos or video, run `scripts/verify-media-privacy.mjs --file ...` with `exiftool` installed. The manifest check protects declarations and paths; this read-only check inspects actual media metadata. If the tool is unavailable, stop and mark privacy verification incomplete rather than claiming the file is safe.

## Evidence record template

```markdown
# Iteration evidence

- Commit:
- Baseline asset + SHA-256:
- Derivative assets + SHA-256:
- Capability/state:
- Source/provenance and privacy handling:
- Commands and results:
- Browser viewport/device:
- Color capture contract (asset/camera/canvas/DPR/output/environment):
- Semantic region statistics and material-class thresholds:
- Screenshots/video:
- Visual findings:
- Accessibility/fallback findings:
- Performance/size findings:
- Known warnings:
- Rollback target:
- Status: accepted | provisional | deferred | rejected
```

If screenshots or a browser session were not available, mark the status `not visually accepted` regardless of automated results.
