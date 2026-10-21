# Examples

Two manifest shapes, both validated by CI.

| Directory | Capabilities | What it shows |
| --- | --- | --- |
| `minimal/` | `static`, `interactive` | The smallest manifest that passes `--strict --strict-privacy`: one node, one hotspot, three camera presets, a declared fallback. |
| `spatial/` | `static`, `spatial` | The same product placed in a room: `SceneManifest`, a product anchor, a device budget, and a return route back to the product viewer. |

## What these are not

- **Not a sample project.** The assets are not distributed. `assets/demo-vessel.glb`
  is a path your build is expected to produce; the repository only owns the
  contract that describes it.
- **Not real hashes.** The `baselineSha256` values are format-valid placeholders.
  Replace them with the digest of your own approved asset:

  ```sh
  shasum -a 256 path/to/approved.glb
  ```

- **Not a style guide.** Field names are the contract. Add a field only when a
  validator rule needs it.

## Checking them

```sh
npm run validate:examples
# or individually
node src/cli.mjs validate --file examples/minimal/manifest.json --strict --strict-privacy
```
