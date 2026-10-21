#!/usr/bin/env node
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { runValidateCli } from './validate.mjs';
import { runPrivacyCli } from './privacy.mjs';

const readVersion = () => {
  try {
    const packagePath = fileURLToPath(new URL('../package.json', import.meta.url));
    return JSON.parse(fs.readFileSync(packagePath, 'utf8')).version ?? '0.0.0';
  } catch {
    return '0.0.0';
  }
};

const USAGE = `p3d — contract checks for Three.js/glTF product viewers

Usage:
  p3d validate [--file manifest.json] [options]
  p3d privacy  [--file media] [--file media...]
  p3d --version
  p3d --help

validate options:
  --strict                    Require the full capability contract.
  --strict-privacy            Reject absolute paths, URLs, traversal, and unlabelled media.
  --require-capabilities a,b  Fail when the manifest omits a declared capability.

Exit codes:
  0  passed
  1  failed validation or privacy check
  2  usage error or missing dependency
`;

const [command, ...rest] = process.argv.slice(2);

switch (command) {
  case 'validate':
    runValidateCli(rest);
    break;
  case 'privacy':
    runPrivacyCli(rest);
    break;
  case '--version':
  case '-v':
    console.log(readVersion());
    break;
  case 'help':
  case '--help':
  case '-h':
  case undefined:
    console.log(USAGE);
    break;
  default:
    console.error(`Unknown command: ${command}\n`);
    console.error(USAGE);
    process.exit(2);
}
