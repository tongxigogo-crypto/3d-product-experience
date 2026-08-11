# 3D Product Experience

Reusable Codex skill for building, repairing, and extending Three.js/glTF product
experiences across Web and WeChat Mini Program adapters.

## What is included

- `skills/3d-product-experience/SKILL.md` — the main Codex skill instructions.
- `skills/3d-product-experience/references/` — product contracts, visual and
  cross-renderer QA gates, provenance, privacy, and POC guidance.
- `skills/3d-product-experience/scripts/` — dependency-light manifest and media
  privacy validators.

The package contains reusable workflow guidance only. It does not include product
GLBs, raw reference photos, customer data, private paths, credentials, or deployment
artifacts.

## Install for Codex

The repository is private. The GitHub account used for installation must have read
access first. Then run the bundled Codex skill installer:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo tong-codex/3d-product-experience-skill \
  --path skills/3d-product-experience
```

If the private-repository download fails, authenticate GitHub for Git and retry:

```bash
gh auth login
gh auth setup-git
```

Start a new Codex turn after installation so the skill discovery list refreshes.

## Use

Ask Codex to use `3d-product-experience` for a Three.js/glTF product viewer,
Web/Mini Program parity work, generated-model cleanup, or a bounded product-viewer
POC. The skill requires a frozen visual baseline, explicit product facts versus demo
assumptions, and visual plus automated evidence before delivery.

## Scope and safety

This skill is a workflow aid, not a release approval. It does not authorize changing
frozen assets, uploading code, deploying a product, or publishing a new product.
Those actions still require the project-specific confirmation and review gates.
