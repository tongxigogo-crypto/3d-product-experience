# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
