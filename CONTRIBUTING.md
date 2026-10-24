# Contributing

The most useful contribution is a **real product manifest with the brand removed**.
It teaches the contract more than another opinion about folder structure.

## Before you open a PR

```sh
npm test
npm run validate:examples
```

No install step is required; the project has no runtime dependencies.

## What a good PR looks like

| Change | Required evidence |
| --- | --- |
| New or changed manifest field | The validator rule that enforces it, plus a passing and a failing fixture |
| New capability level | A minimal example under `examples/`, and the fields it adds to the contract |
| Changed error message | Update the assertion in `test/validate.test.mjs` in the same commit |
| Docs-only | Link the section you changed; no evidence gate |
| Demo change | A screenshot at desktop and phone width, and a note on what you checked |

## What gets rejected

- A rule that only works because one specific product has that shape. The contract
  must stay renderer-neutral and product-neutral.
- Silent promotion of an unapproved asset, or a change that moves the approved
  silhouette without an explicit product revision.
- Test fixtures containing real customer names, private absolute paths, raw phone
  filenames, or GPS-bearing media.
- "Improvements" that reformat unrelated files.

## Reporting a problem

Use the issue forms. For a manifest that fails validation, include the manifest
(minus brand data) and the exact command. For a visual regression, include both
screenshots and the viewport size — "looks wrong" cannot be triaged.

## Commits

Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`) keep the
changelog generatable. One logical change per commit.

## License

By contributing you agree your contribution is licensed under CC-BY-NC-4.0.
