# Plugin POC decision record

Use this record whenever a Three.js/GitHub package might become a runtime dependency. Set the product-specific target before measuring; the defaults below make decisions comparable, not universal.

## POC setup

```text
Need:
Product/capability:
Scope: web | mini | panorama
Baseline commit and asset hash:
Package + version + Three.js version:
License/source:
Test scene and command:
Target devices/browsers:
Fallback and rollback:
```

## Default starting thresholds

Override a threshold only with a written reason and evidence:

- no new uncaught console errors or WebGL context failures;
- no regression in the approved baseline screenshot/state contract;
- sustained realtime rendering target: at least 30 FPS on the supported mobile floor and 50 FPS on the supported desktop floor;
- median cold-load time regression no more than 10% against the same scene, or a documented user-visible benefit that justifies it;
- compressed JavaScript increase no more than 150 KB gzip for a small product slice, or a recorded budget exception;
- peak memory and asset buffers remain within the target device budget; for the current Mini preparation contract, treat 2048 px textures and 10 MiB ArrayBuffers as starting checks, not release guarantees;
- touch, keyboard, reduced-motion, accessible fallback, and slow/failure loading remain usable.

## Evidence table

| Measure | Baseline | POC | Target/exception | Evidence |
| --- | ---: | ---: | --- | --- |
| JS gzip |  |  |  |  |
| Cold load |  |  |  |  |
| Mobile FPS |  |  |  |  |
| Desktop FPS |  |  |  |  |
| Peak memory |  |  |  |  |
| Asset bytes/textures |  |  |  |  |
| Console/WebGL errors |  |  |  |  |
| Visual state parity |  |  | pass/fail | screenshots |
| Interaction/accessibility |  |  | pass/fail | E2E/device |

## Reproducible measurement protocol

- Use the same commit, browser version, viewport, device, network profile, and quality setting for baseline and POC.
- Record three cold loads (cache disabled or a clean context) and three warm loads; report the median and the slowest run.
- Sample FPS for at least 30 seconds after the scene settles; report the median and lowest sustained value, not a single counter reading.
- Record peak JS/GPU memory using the same available browser/device tooling. If a platform cannot expose one measure, mark it unavailable rather than inventing it.
- Save the exact command, raw output path, screenshot/video path, and device/browser metadata in the decision record.
- A measurement without a reproducible command or evidence file is a note, not a release gate.

## Decision

```text
Status: accept | defer | reject
Reason:
Production files changed:
Fallback verified:
Removal/rollback command:
Follow-up device or material evidence:
Owner/date:
```

An option with good benchmark numbers but no visual or fallback evidence remains `defer`.
