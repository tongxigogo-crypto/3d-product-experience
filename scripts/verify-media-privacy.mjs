#!/usr/bin/env node
// Backward-compatible entry point kept for SKILL.md and existing project scripts.
// Prefer `p3d privacy --file media`.
import { runPrivacyCli } from '../src/privacy.mjs';

runPrivacyCli(process.argv.slice(2));
