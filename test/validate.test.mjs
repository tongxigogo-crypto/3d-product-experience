import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { validateManifest, validateManifestFile } from '../src/validate.mjs';

const repoRoot = fileURLToPath(new URL('..', import.meta.url));
const minimalPath = path.join(repoRoot, 'examples/minimal/manifest.json');
const spatialPath = path.join(repoRoot, 'examples/spatial/manifest.json');

const baseManifest = () => JSON.parse(fs.readFileSync(minimalPath, 'utf8'));

const messages = (result) => result.errors.join('\n');

test('the minimal example passes strict and strict-privacy', () => {
  const result = validateManifestFile(minimalPath, { strict: true, strictPrivacy: true });
  assert.equal(result.valid, true, messages(result));
  assert.equal(result.summary.validationMode, 'strict-privacy');
  assert.equal(result.summary.productId, 'demo-vessel');
});

test('the spatial example passes strict and strict-privacy', () => {
  const result = validateManifestFile(spatialPath, { strict: true, strictPrivacy: true });
  assert.equal(result.valid, true, messages(result));
  assert.deepEqual(result.summary.capabilities, ['static', 'spatial']);
});

test('a non-hex baseline hash is rejected', () => {
  const manifest = baseManifest();
  manifest.provenance.baselineSha256 = 'not-a-hash';
  const result = validateManifest(manifest, { strict: true });
  assert.equal(result.valid, false);
  assert.match(messages(result), /SHA-256 must be 64 hexadecimal/);
});

test('an absolute asset path is rejected under strict privacy', () => {
  const manifest = baseManifest();
  manifest.assets[0].path = '/Users/someone/product.glb';
  const result = validateManifest(manifest, { strict: true, strictPrivacy: true });
  assert.equal(result.valid, false);
  assert.match(messages(result), /repository-relative path under strict privacy/);
  assert.match(messages(result), /absolute\/private file path/);
});

test('path traversal is rejected', () => {
  const manifest = baseManifest();
  manifest.assets[0].path = '../outside/product.glb';
  const result = validateManifest(manifest, { strict: true, strictPrivacy: true });
  assert.equal(result.valid, false);
  assert.match(messages(result), /must not traverse outside/);
});

test('unlabelled media is rejected under strict privacy', () => {
  const manifest = baseManifest();
  delete manifest.assets[1].privacyStatus;
  const result = validateManifest(manifest, { strict: true, strictPrivacy: true });
  assert.equal(result.valid, false);
  assert.match(messages(result), /must declare privacyStatus/);
});

test('raw phone filenames are rejected', () => {
  const manifest = baseManifest();
  manifest.assets[1].path = 'assets/IMG_4821.jpg';
  manifest.assets[1].privacyStatus = 'derived';
  const result = validateManifest(manifest, { strict: true, strictPrivacy: true });
  assert.equal(result.valid, false);
  assert.match(messages(result), /raw phone photo\/video filename/);
});

test('a scene node referencing an undeclared asset is rejected', () => {
  const manifest = baseManifest();
  manifest.sceneNodes[0].assetVariants.web = 'missing-asset';
  const result = validateManifest(manifest, { strict: true });
  assert.equal(result.valid, false);
  assert.match(messages(result), /references unknown asset missing-asset/);
});

test('a scene node without a fallback variant is rejected under strict', () => {
  const manifest = baseManifest();
  delete manifest.sceneNodes[0].assetVariants.fallback;
  const result = validateManifest(manifest, { strict: true });
  assert.equal(result.valid, false);
  assert.match(messages(result), /must declare fallback/);
});

test('an unknown camera preset is rejected', () => {
  const manifest = baseManifest();
  manifest.sceneNodes[0].cameraPreset = 'not-a-preset';
  const result = validateManifest(manifest, { strict: true });
  assert.equal(result.valid, false);
  assert.match(messages(result), /references unknown preset not-a-preset/);
});

test('interactive without a hotspot is rejected', () => {
  const manifest = baseManifest();
  manifest.hotspots = [];
  const result = validateManifest(manifest, { strict: true });
  assert.equal(result.valid, false);
  assert.match(messages(result), /interactive capability requires at least one hotspot/);
});

test('capabilities must include static under strict', () => {
  const manifest = baseManifest();
  manifest.capabilities = ['interactive'];
  const result = validateManifest(manifest, { strict: true });
  assert.equal(result.valid, false);
  assert.match(messages(result), /must include static/);
});

test('assembly needs at least two states and one part', () => {
  const manifest = baseManifest();
  manifest.capabilities = ['static', 'assembly'];
  manifest.assembly = {
    parts: [],
    states: [{ id: 'closed' }],
    restore: { state: 'open' },
    cameraSnapshot: { restore: true },
    reducedMotion: 'jump-to-end-state',
  };
  const result = validateManifest(manifest, { strict: true });
  assert.equal(result.valid, false);
  assert.match(messages(result), /assembly\.parts must not be empty/);
  assert.match(messages(result), /assembly\.states must contain at least two states/);
  assert.match(messages(result), /restore target state open is not declared/);
});

test('required capabilities are enforced', () => {
  const manifest = baseManifest();
  const result = validateManifest(manifest, { requiredCapabilities: ['assembly'] });
  assert.equal(result.valid, false);
  assert.match(messages(result), /capabilities must include assembly/);
});

test('a privacy policy without GPS or local-only language is rejected', () => {
  const manifest = baseManifest();
  manifest.provenance.privacyPolicy = 'We handle media responsibly.';
  const result = validateManifest(manifest, { strict: true });
  assert.equal(result.valid, false);
  assert.match(messages(result), /should explicitly describe GPS\/private raw-reference handling/);
});

test('the CLI exits 0 for a valid manifest', () => {
  const run = spawnSync(process.execPath, ['src/cli.mjs', 'validate', '--file', minimalPath, '--strict'], {
    cwd: repoRoot,
    encoding: 'utf8',
  });
  assert.equal(run.status, 0, run.stderr);
  // --strict implies the privacy gate, matching the documented pre-0.1 behaviour.
  assert.match(run.stdout, /"validationMode": "strict-privacy"/);
});

test('the CLI exits 1 for an invalid manifest', () => {
  const run = spawnSync(
    process.execPath,
    ['scripts/validate-product-manifest.mjs', '--file', path.join(repoRoot, 'package.json')],
    { cwd: repoRoot, encoding: 'utf8' },
  );
  assert.equal(run.status, 1, run.stderr);
  assert.match(run.stderr, /Invalid product manifest/);
});

test('the CLI exits 2 without a file argument', () => {
  const run = spawnSync(process.execPath, ['src/cli.mjs', 'validate'], {
    cwd: repoRoot,
    encoding: 'utf8',
  });
  assert.equal(run.status, 2);
  assert.match(run.stderr, /Usage: p3d validate/);
});
