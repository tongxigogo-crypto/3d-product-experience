# Product 3D Production Boundary

This reference is a planning boundary, not an implementation. A contract or
documentation repository does not contain a product runtime; real viewers
usually live in separate Web and Mini Program workspaces. Treat implementation,
static checks, device acceptance, and release status as separate evidence.

## Proposed flow

`ProductSpec` (images, dimensions, CAD, requirements) → modeling strategy
router → Blender parametric/Geometry Nodes, CAD backend, or AI reference/base
mesh → Blender assembly/material authoring → canonical glTF/GLB → glTF
Transform post-processing → glTF Validator → Web/Mini adapters. Keep product
facts, demo assumptions, source assets, derivatives, and runtime assets distinct.

## Blender state boundary

- Prefer deterministic `bpy.data` datablock edits and BMesh for mesh topology.
- Treat `bpy.ops` as context-sensitive operators. Use them only behind an
  explicit context/mode/selection precondition or a controlled override.
- A checkpoint records scene, view layer, active camera, mode/selection,
  transforms, modifiers, materials, dependency-graph update status, and hashes.
  Restore must be possible before an incremental operation.
- Source geometry and evaluated geometry are different inspection targets;
  diagnostics must say which one was measured.

## Tool maturity boundary

- **Current:** existing Web/Mini display runtimes plus project-specific asset,
  manifest, loader, render-profile, and validation code; Blender state remains
  script-driven and is not yet exposed through the proposed read/checkpoint API.
- **V1 proposal:** read-only scene/topology summaries plus checkpoint create,
  list, inspect, and restore contracts. No arbitrary code execution, exporter,
  or platform integration is implied.
- **Future:** bounded write tools, templates, transactional execution,
  canonical export and adapter integrations, each after a scoped POC and
  review. Names in research are proposals, not installed dependencies.

Engineering diagnostics can report state and deterministic failures. They cannot
approve silhouette, material, hierarchy, composition, or brand fidelity; those
remain visual inspection and explicit user acceptance gates.
