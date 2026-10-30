# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **`NOTICE.md`** — a plain-language companion to `LICENSE`: what is allowed, the
  three simultaneous attribution obligations under CC BY-NC 4.0, what counts as
  prohibited, how to request commercial permission, and how to report a
  non-compliant repost. It also records the verified non-compliant uses of this
  repository (first entry: 2026-10-25, `alixixi.com`), with the reproduction
  method so anyone can check the finding.
- **Attribution requirement** — README (EN + zh-CN) now states explicitly that
  translation, summarization and rewriting are adaptations and therefore require
  credit, a license link and a change note. Leaving the author only in SEO
  metadata, or deleting the license block, does not satisfy the license.
- **License block at the end of `SKILL.md`** — the Skill file is the artifact most
  likely to be copied out on its own, away from `LICENSE` and `NOTICE.md`. It now
  carries its own source, license and attribution terms.
- **License banner at the top of `README.md` / `README.zh-CN.md`** — the
  restriction is visible before the reader scrolls to the bottom.

### Changed

- `README.md` / `README.zh-CN.md` — the license sections link to `NOTICE.md`
  instead of restating the terms in two places.

## [0.3.0] - 2026-10-25

### Added

- **Apparel and Soft Goods Pipeline (`apparel-garment`)**:
  - `references/fabric-apparel-recipe.md`: 260gsm combed-cotton PBR Sheen recipes, J-curve tailored armscyes (`W_SHOULDER > W_PIT`), local-centroid inner cuff contraction (preventing underarm lining penetration), and post-smoothing (`Subsurf + CorrectiveSmooth`) hairline (`1.1 mm`) stitch groove etching.
  - `references/image-to-3d-pipeline.md`: step-by-step SOP for 4-step AI GLB reconstruction (`--mode rebuild`) and 1-base-GLB multi-SKU batch texture swapping (`--mode swap` / `--mode batch`).
  - `references/glass-liquid-optics-recipe.md`: optical PBR recipes for transmissive glass, liquids, IOR, chromatic dispersion, and caustic approximations.
  - `references/single-file-bundle-guide.md`: esbuild IIFE bundling guidelines for standalone offline HTML viewers, inlining Base64 GLB assets, and avoiding browser sandbox CORS issues.
  - `references/state-engine-architecture.md`: decoupling interactive state machines and scientific/physical laws from Three.js rendering loops.
- **Headless Pipeline Scripts**:
  - `scripts/decimate_ai_glb.py`: dual-mode utility supporting 4-step headless Blender reconstruction (`--mode rebuild`) and instant 1-base-GLB texture swapping & standalone HTML bundling (`--mode swap` / `--mode batch`, ~1s/SKU without Blender).
  - `scripts/blender_headless_garment.py`: parametric quad-cage lofting script for zero-external-model apparel baselines with J-curve armscye and hairline seam grooves.
  - `scripts/blender_headless_lathe.py`: parametric rotational lathe generator for double-walled bottles, jars, and cylindrical glassware.

### Changed

- Updated `SKILL.md` to classify soft goods (`apparel-garment`) and set route priority: AI Image-to-3D + 4-step recovery as the primary commercial production route, and procedural quad-cage lofting as the zero-external-model fallback baseline.

## [0.2.0] - 2026-10-22

The skill becomes a toolkit: the contract is now enforced by code, not only
described in prose.

### Added

- `p3d validate` CLI with `--strict`, `--strict-privacy`, and
  `--require-capabilities`, plus a programmatic `validateManifest` API.
- `p3d privacy` CLI wrapping a read-only `exiftool` location-metadata check.
- Product manifest contract: semantic scene nodes, material IDs, hotspots,
  camera presets, per-platform asset variants, fallback declarations, provenance
  and baseline SHA-256.
- Capability ladder (`static` → `interactive` → `assembly` → `spatial`) with
  additive validation, including assembly state endpoints and spatial scene seams.
- `examples/minimal` and `examples/spatial`, both validated in CI.
- 18 contract tests covering the privacy gate, traversal, unknown asset
  references, camera preset resolution, capability requirements and assembly
  state endpoints.
- Static demo adapter under `docs/`, publishing a manifest-driven Three.js
  viewer through GitHub Pages.
- GitHub Actions workflow running the tests on Node 20 and 22.

### Changed

- **Repository layout flattened.** The skill now lives at the repository root
  instead of `skills/3d-product-experience/`. Git history and the `v0.1.0` tag
  are preserved; nothing was rewritten.
- `scripts/validate-product-manifest.mjs` and `scripts/verify-media-privacy.mjs`
  became thin wrappers over `src/`, so existing `SKILL.md` commands keep working.
- `engines` now requires Node >= 20. Node 18 is past end of life and the CI
  matrix no longer covers it.
- References renamed their example vocabulary from one product family
  (`bottle` / `cap` / `label`) to neutral terms (`product` / `part` / `surface`),
  so the contract does not read as tied to a single client project.

### Notes

- `--strict` implies the privacy gate. This matches the pre-release behaviour and
  is pinned by a test.
- The colour-parity pipeline is documented as a contract; its capture and compare
  scripts are not shipped in this release.

## [0.1.0] - 2026-08-02

First private version of the skill.

### Added

- `SKILL.md`: agent procedure for establishing a baseline, classifying a
  capability, building the contract, recording provenance, validating in layers
  and closing an iteration.
- Seven reference contracts: capability, QA and evidence, colour parity, POC
  decisions, research integration matrix, AI provenance and recovery, production
  boundary.
- `scripts/validate-product-manifest.mjs` and `scripts/verify-media-privacy.mjs`.
