# 3D Product Experience

[![ci](https://github.com/tongxigogo-crypto/3d-product-experience/actions/workflows/ci.yml/badge.svg)](https://github.com/tongxigogo-crypto/3d-product-experience/actions/workflows/ci.yml)

> **License: [CC BY-NC 4.0](LICENSE) — non-commercial only.**
> Reposting, translating, summarizing or rewriting this content requires **credit + a link back + a note of what you changed**. Commercial use, paid repackaging and platform resale are **not permitted** without written authorization.
> Full terms and the attribution checklist: **[NOTICE.md](NOTICE.md)**
>
> 中文：本项目**禁止商用**，转载/翻译/改写**必须署名并回链**。细则见 [NOTICE.md](NOTICE.md)。

A contract toolkit for Three.js / glTF product viewers.

It does not render anything. It stops a product viewer from silently changing an
approved product, and it turns "looks fine to me" into a checkable record.

```
p3d validate --file manifest.json --strict --strict-privacy
```

## The three failures this exists to prevent

| Failure | What it looks like | What this repo gives you |
| --- | --- | --- |
| The asset drifted | Someone re-exported the GLB, the silhouette moved 4%, the build stayed green | A frozen baseline SHA-256 that the manifest must carry and that CI can diff |
| The demo impersonated the product | An AI-generated mesh is shown as a 1:1 digital twin, with invented threads and a guessed opening | Explicit `demo` labelling, a provenance record, and a `capabilities` ladder that forbids shipping assets a product does not have |
| Green tests, broken picture | lint + unit + build all pass; nobody opened the page on a phone | Visual acceptance is a separate, mandatory gate that no automated check can satisfy |

## What is in the box

Three layers, usable independently.

**1. A machine-readable contract** — `references/product-capability-contract.md`
defines a renderer-neutral product manifest: semantic node IDs, material IDs,
hotspots, camera presets, per-platform asset variants, fallbacks, provenance and
capability flags. Web and Mini Program share the intent, not the loader.

**2. A validator** — `p3d` (zero dependencies, Node >= 20) enforces the contract:

```sh
npx 3d-product-experience validate --file product.manifest.json --strict --strict-privacy
```

- basic mode accepts legacy manifests;
- `--strict` requires the capability ladder, platform contract, hotspot fallbacks,
  camera presets, assembly state endpoints, and a declared fallback variant per node;
- `--strict-privacy` additionally rejects absolute paths, URLs, `..` traversal,
  unlabelled images/video, and raw GPS/EXIF declarations.

Library use:

```js
import { validateManifest } from '3d-product-experience';

const { valid, errors, summary } = validateManifest(manifest, {
  strict: true,
  strictPrivacy: true,
  requiredCapabilities: ['static', 'interactive'],
});
```

**3. An agent skill and physical recipes** — `SKILL.md` is the operating procedure for an AI coding
agent: establish the baseline, classify the capability, build the contract,
record provenance, validate in layers, close the iteration. `references/` holds
the deeper contracts and physical recipes (QA and evidence, colour parity, POC decisions,
apparel fabric sheen & J-curve armscye recipes, AI image-to-3D 4-step reconstruction, and 1-base-GLB multi-SKU batch texture swapping). `scripts/` provides headless Blender and Python automation (`decimate_ai_glb.py`, `blender_headless_garment.py`, `blender_headless_lathe.py`). Load it with any agent that reads `SKILL.md`.

## Quick start

```sh
git clone https://github.com/tongxigogo-crypto/3d-product-experience.git
cd 3d-product-experience
npm test                 # 18 contract tests, no install step
npm run validate:examples
```

Point the validator at your own manifest:

```sh
node src/cli.mjs validate --file path/to/your/manifest.json --strict --strict-privacy
```

Copy `examples/minimal/manifest.json` as the starting shape. The example assets
are not distributed with this repository — the manifest declares what your build
must produce, it is not a sample project.

## Capability ladder

Additive. A product declares what it actually ships, and nothing more.

| Level | Behaviour | Contract required before it ships |
| --- | --- | --- |
| `static` | one model, camera presets, poster fallback | asset variant, materials, camera, fallback |
| `interactive` | orbit/zoom, hotspots, material or ingredient cards | semantic nodes, hit target, keyboard/touch behaviour, accessible fallback |
| `assembly` | static or animated open/close/reveal states | independent parts, state endpoints, camera snapshot/restore, reduced-motion path |
| `spatial` | linked panoramas or a navigable room | `SceneManifest`, product anchors, `SceneSnapshot`, host overlay, node preloading, device budget |

A static opening demo is not a licence to invent a screw thread. Free walk is not
implied by `spatial`.

## Live demo

**https://tongxigogo-crypto.github.io/3d-product-experience/**

`docs/` is a static page that reads the same manifest shape and drives a Three.js
viewer with semantic camera presets and hotspots. The model is Khronos'
[Damaged Helmet](https://github.com/KhronosGroup/glTF-Sample-Assets) (CC BY 4.0),
loaded from a CDN — no private asset is redistributed here.

```sh
npm run demo    # http://localhost:4173
```

The demo is a reference adapter. It is deliberately small: it shows where the
contract plugs in, not how to build a product site.

## Repository layout

```
SKILL.md                    agent procedure
references/                 contracts: capability, QA evidence, colour parity,
                            POC decisions, research matrix, provenance, boundary
src/                        validator + privacy checker (no dependencies)
scripts/                    backward-compatible CLI entry points
examples/                   manifest shapes for static/interactive and spatial
test/                       contract tests
docs/                       static demo (GitHub Pages)
```

## Status

Honest scope, at `0.2.0`:

- The validator and its test suite are implemented; 18 contract tests pass on
  Node 20 and 22 (the CI matrix).
- The manifest contract has been used on one commercial product viewer (Web) and
  one Mini Program build. Those projects are private; no numbers are claimed here
  that a reader cannot verify.
- The colour-parity pipeline is documented as a contract, not shipped as code.
- The privacy checker shells out to `exiftool`; if it is missing the check exits
  `2` and reports "not verified" rather than "clean".

## Design rules

1. Freeze before editing: record path and SHA-256 of every accepted asset.
2. Facts and demo assumptions never share a field.
3. A requested detail must not move the approved silhouette.
4. Source, derivative and runtime assets stay separate.
5. Private references stay local; ship only no-location derivatives.
6. A GitHub README is not evidence that a package works in your product.
7. Visual acceptance is a hard gate. A passing build is not acceptance.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Manifests from real products (with the
brand details removed) are the most useful contribution.

## License & Commercial Restrictions

This project is licensed under the **[Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](LICENSE)**. The `references/` documents are original prose; third-party libraries named in the research matrix are referenced, not vendored.

### ⚠️ Non-Commercial & Platform Redistribution Restrictions

- **Personal & Research Use**: Free for personal learning, testing, and academic research.
- **No Commercial Use**: You may not use this material (prompts, skill manifests, contracts, schemas, or source code) for commercial purposes without explicit prior written authorization.
- **No Paid Marketplace / Platform Resale**: Explicitly prohibited from packaging, repackaging, or listing this project as a paid skill, tool, or MCP on any third-party agent marketplace or platform (including but not limited to Tencent WorkBuddy, Dify, Coze, GPT Store, etc.).

### Attribution is mandatory

CC BY-NC 4.0 requires **three things at once** when you share or adapt this work:

1. **Credit** — name `tongxigogo-crypto` and link back to this repository;
2. **License notice** — link to <https://creativecommons.org/licenses/by-nc/4.0/>;
3. **Indicate changes** — say what you translated, cut, reordered or rewrote.

Translation, summarization and rewriting are legally **adaptations**, not exemptions. Stripping the license block, or naming the author only in SEO metadata while the body carries no credit and no link, does not satisfy any of the three.

The full checklist, the list of recorded non-compliant uses, and how to request commercial permission live in **[NOTICE.md](NOTICE.md)**.
