#!/usr/bin/env node
// Backward-compatible entry point kept for SKILL.md and existing project scripts.
// Prefer `p3d validate --file manifest.json`.
import { runValidateCli } from '../src/validate.mjs';

runValidateCli(process.argv.slice(2));
