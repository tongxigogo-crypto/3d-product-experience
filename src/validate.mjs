import fs from 'node:fs';
import path from 'node:path';

/**
 * Capability ladder. Additive: a product only declares what it actually ships.
 */
export const CAPABILITIES = ['static', 'interactive', 'assembly', 'spatial'];

const isObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
const isNonEmptyString = (value) => typeof value === 'string' && value.trim().length > 0;
const isSha256 = (value) => typeof value === 'string' && /^[a-f0-9]{64}$/i.test(value);

const MEDIA_EXTENSIONS = /\.(?:jpe?g|heic|mov|mp4|png)$/i;
const ALLOWED_PRIVACY_STATUS = ['sanitized', 'stripped', 'derived'];

/**
 * Validate a renderer-neutral product manifest.
 *
 * @param {object} manifest Parsed manifest JSON.
 * @param {object} [options]
 * @param {boolean} [options.strict] Require the full capability contract.
 * @param {boolean} [options.strictPrivacy] Reject absolute paths, URLs, traversal, and unlabelled media.
 * @param {string[]} [options.requiredCapabilities] Capabilities the manifest must declare.
 * @returns {{ valid: boolean, errors: string[], summary: object }}
 */
export function validateManifest(manifest, options = {}) {
  const strict = options.strict === true;
  const strictPrivacy = strict || options.strictPrivacy === true;
  const requiredCapabilities = Array.isArray(options.requiredCapabilities)
    ? options.requiredCapabilities
    : [];

  const errors = [];

  if (!isObject(manifest)) {
    return {
      valid: false,
      errors: ['manifest root must be an object'],
      summary: { validationMode: 'basic' },
    };
  }

  const requireObject = (value, label) => {
    if (!isObject(value)) errors.push(`${label} must be an object`);
  };
  const requireArray = (value, label) => {
    if (!Array.isArray(value)) errors.push(`${label} must be an array`);
  };
  const requireString = (value, label) => {
    if (!isNonEmptyString(value)) errors.push(`${label} must be a non-empty string`);
  };
  const requireUniqueIds = (items, label) => {
    if (!Array.isArray(items)) return;
    const ids = new Set();
    for (const [index, item] of items.entries()) {
      if (!isObject(item) || !isNonEmptyString(item.id)) continue;
      if (ids.has(item.id)) errors.push(`${label}[${index}].id duplicates ${item.id}`);
      ids.add(item.id);
    }
  };

  requireString(manifest.schemaVersion, 'schemaVersion');
  requireString(manifest.productId ?? manifest.content?.productId, 'productId');
  requireObject(manifest.sourcePolicy ?? manifest.provenance, 'sourcePolicy/provenance');
  requireArray(manifest.sceneNodes, 'sceneNodes');
  requireArray(manifest.assets, 'assets');
  requireObject(manifest.fallbackContent, 'fallbackContent');

  const source = manifest.sourcePolicy ?? manifest.provenance ?? {};
  const baselineSha = source.approvedWebBaselineSha256 ?? source.baselineSha256;
  requireString(source.approvedWebBaseline ?? source.baselineAsset, 'approved baseline path');
  if (!isSha256(baselineSha)) {
    errors.push('approved baseline SHA-256 must be 64 hexadecimal characters');
  }

  const capabilities = manifest.capabilities;
  const allowedCapabilities = new Set(CAPABILITIES);
  if (strict || requiredCapabilities.length > 0) {
    requireArray(capabilities, 'capabilities');
    if (Array.isArray(capabilities)) {
      for (const capability of capabilities) {
        if (!allowedCapabilities.has(capability)) {
          errors.push(`capabilities contains unsupported value ${capability}`);
        }
      }
      if (strict && !capabilities.includes('static')) errors.push('capabilities must include static');
      for (const requiredCapability of requiredCapabilities) {
        if (!allowedCapabilities.has(requiredCapability)) {
          errors.push(`required capability is unsupported: ${requiredCapability}`);
        }
        if (!capabilities.includes(requiredCapability)) {
          errors.push(`capabilities must include ${requiredCapability}`);
        }
      }
    }
  }

  const platformContract = manifest.platforms ?? manifest.runtimes;
  const materials = manifest.materials ?? manifest.content?.materials;
  const hotspots = manifest.hotspots ?? manifest.content?.hotspots;
  const cameraPresets = manifest.cameraPresets;
  const nodes = Array.isArray(manifest.sceneNodes) ? manifest.sceneNodes : [];

  if (strict) {
    requireObject(platformContract, 'platforms/runtimes');
    if (isObject(platformContract)) {
      requireObject(platformContract.web, 'platforms/runtimes.web');
      if (isObject(platformContract.web)) {
        requireString(platformContract.web.renderer, 'platforms/runtimes.web.renderer');
        requireString(platformContract.web.status, 'platforms/runtimes.web.status');
      }
      if (platformContract.mini !== undefined) {
        requireObject(platformContract.mini, 'platforms/runtimes.mini');
      }
    }
    requireArray(materials, 'materials');
    requireArray(hotspots, 'hotspots');
    requireArray(cameraPresets, 'cameraPresets');
    requireUniqueIds(materials, 'materials');
    requireUniqueIds(hotspots, 'hotspots');
    requireUniqueIds(cameraPresets, 'cameraPresets');
    if (Array.isArray(capabilities) && capabilities.includes('interactive')) {
      if (!hotspots || hotspots.length === 0) {
        errors.push('interactive capability requires at least one hotspot');
      }
      for (const [index, hotspot] of (hotspots ?? []).entries()) {
        const label = `hotspots[${index}]`;
        if (!isObject(hotspot)) continue;
        requireString(hotspot.id, `${label}.id`);
        requireString(hotspot.node ?? hotspot.targetNode ?? hotspot.sceneNode, `${label}.target node`);
        requireString(hotspot.fallbackContent ?? hotspot.fallback, `${label}.accessible fallback`);
      }
    }
  }

  const assets = Array.isArray(manifest.assets) ? manifest.assets : [];
  const assetIds = new Set();
  for (const [index, asset] of assets.entries()) {
    const label = `assets[${index}]`;
    requireObject(asset, label);
    if (!isObject(asset)) continue;
    requireString(asset.id, `${label}.id`);
    if (
      !isNonEmptyString(asset.role) &&
      !isNonEmptyString(asset.status) &&
      !isNonEmptyString(asset.source)
    ) {
      errors.push(`${label} must declare role, status, or source`);
    }
    if (asset.id) {
      if (assetIds.has(asset.id)) errors.push(`${label}.id duplicates ${asset.id}`);
      assetIds.add(asset.id);
    }
    if (asset.sha256 !== undefined && !isSha256(asset.sha256)) {
      errors.push(`${label}.sha256 must be 64 hexadecimal characters when present`);
    }
    if (asset.path !== undefined) requireString(asset.path, `${label}.path`);
    if (strictPrivacy && isNonEmptyString(asset.path)) {
      const assetPath = asset.path;
      if (path.isAbsolute(assetPath) || /^(?:file:|https?:)/i.test(assetPath)) {
        errors.push(`${label}.path must be a repository-relative path under strict privacy`);
      }
      if (assetPath.split(/[\\/]+/).includes('..')) {
        errors.push(`${label}.path must not traverse outside the manifest repository`);
      }
      if (
        MEDIA_EXTENSIONS.test(path.extname(assetPath).toLowerCase()) &&
        !ALLOWED_PRIVACY_STATUS.includes(asset.privacyStatus)
      ) {
        errors.push(
          `${label} image/video asset must declare privacyStatus sanitized, stripped, or derived`,
        );
      }
      if (asset.metadata?.gps === true || asset.metadata?.exif === 'raw') {
        errors.push(`${label} declares raw GPS/EXIF metadata`);
      }
    }
  }

  const cameraIds = new Set(
    Array.isArray(cameraPresets)
      ? cameraPresets.map((preset) => preset?.id).filter(isNonEmptyString)
      : [],
  );
  if (strict && Array.isArray(cameraPresets)) {
    for (const [index, node] of nodes.entries()) {
      if (isObject(node) && isNonEmptyString(node.cameraPreset) && !cameraIds.has(node.cameraPreset)) {
        errors.push(`sceneNodes[${index}].cameraPreset references unknown preset ${node.cameraPreset}`);
      }
    }
  }

  const assembly = manifest.assembly ?? manifest.experiences?.assembly;
  if (strict && Array.isArray(capabilities) && capabilities.includes('assembly')) {
    requireObject(assembly, 'assembly');
    if (isObject(assembly)) {
      requireArray(assembly.parts, 'assembly.parts');
      requireArray(assembly.states, 'assembly.states');
      if (Array.isArray(assembly.parts) && assembly.parts.length === 0) {
        errors.push('assembly.parts must not be empty');
      }
      if (Array.isArray(assembly.states) && assembly.states.length < 2) {
        errors.push('assembly.states must contain at least two states');
      }
      const restore = assembly.restore ?? assembly.restoreState;
      requireObject(restore, 'assembly.restore/restoreState');
      if (isObject(restore)) {
        requireString(restore.state ?? restore.stateId ?? restore.targetState, 'assembly.restore target state');
      }
      requireObject(assembly.cameraSnapshot ?? assembly.cameraRestore, 'assembly.cameraSnapshot/cameraRestore');
      requireString(assembly.reducedMotion ?? assembly.reducedMotionPolicy, 'assembly.reducedMotion policy');
      requireUniqueIds(assembly.parts, 'assembly.parts');
      requireUniqueIds(assembly.states, 'assembly.states');
      if (Array.isArray(assembly.states)) {
        const stateIds = new Set(assembly.states.map((state) => state?.id).filter(isNonEmptyString));
        const restoreState = isObject(restore)
          ? restore.state ?? restore.stateId ?? restore.targetState
          : undefined;
        if (isNonEmptyString(restoreState) && !stateIds.has(restoreState)) {
          errors.push(`assembly.restore target state ${restoreState} is not declared in assembly.states`);
        }
      }
    }
  }

  const nodeIds = new Set();
  for (const [index, node] of nodes.entries()) {
    const label = `sceneNodes[${index}]`;
    requireObject(node, label);
    if (!isObject(node)) continue;
    requireString(node.id, `${label}.id`);
    requireString(node.semantic, `${label}.semantic`);
    requireString(node.cameraPreset, `${label}.cameraPreset`);
    requireObject(node.assetVariants, `${label}.assetVariants`);
    if (node.id) {
      if (nodeIds.has(node.id)) errors.push(`${label}.id duplicates ${node.id}`);
      nodeIds.add(node.id);
    }
    if (isObject(node.assetVariants)) {
      if (strict && !Object.hasOwn(node.assetVariants, 'fallback')) {
        errors.push(`${label}.assetVariants must declare fallback (asset ID or null)`);
      }
      for (const [variant, assetId] of Object.entries(node.assetVariants)) {
        if (assetId === null || assetId === undefined) continue;
        if (!isNonEmptyString(assetId)) {
          errors.push(`${label}.assetVariants.${variant} must be a string or null`);
        } else if (!assetIds.has(assetId)) {
          errors.push(`${label}.assetVariants.${variant} references unknown asset ${assetId}`);
        }
      }
    }
  }

  const rawPolicy = String(source.rawSupplementPolicy ?? source.privacyPolicy ?? '').toLowerCase();
  if (rawPolicy && !/(gps|metadata|local-only|never|private)/.test(rawPolicy)) {
    errors.push('source policy should explicitly describe GPS/private raw-reference handling');
  }

  const serialized = JSON.stringify(manifest);
  if (/(?:^|["'\\/])IMG_\d+\.(jpe?g|heic|mov)(?=["'\s]|$)/i.test(serialized)) {
    errors.push('manifest appears to contain a raw phone photo/video filename; use a sanitized derivative');
  }
  if (strictPrivacy && /(?:["'])(?:\/Users\/|\/private\/|\/var\/folders\/|file:)/i.test(serialized)) {
    errors.push('manifest appears to contain an absolute/private file path');
  }

  const validationMode = strictPrivacy
    ? 'strict-privacy'
    : strict
      ? 'strict'
      : requiredCapabilities.length > 0
        ? 'required-capabilities'
        : 'basic';

  return {
    valid: errors.length === 0,
    errors,
    summary: {
      productId: manifest.productId ?? manifest.content?.productId,
      sceneNodes: nodes.length,
      assets: assets.length,
      capabilities: Array.isArray(capabilities) ? capabilities : 'not-declared',
      validationMode,
      baselineSha256: baselineSha,
    },
  };
}

/**
 * Read and validate a manifest file. Throws only on unreadable or non-JSON input.
 */
export function validateManifestFile(file, options = {}) {
  const absoluteFile = path.resolve(file);
  let manifest;
  try {
    manifest = JSON.parse(fs.readFileSync(absoluteFile, 'utf8'));
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    const parseError = new Error(`Cannot read JSON manifest: ${absoluteFile}\n${reason}`);
    parseError.code = 'MANIFEST_UNREADABLE';
    throw parseError;
  }
  return { file: absoluteFile, ...validateManifest(manifest, options) };
}

const USAGE =
  'Usage: p3d validate --file path/to/manifest.json [--strict] [--strict-privacy] [--require-capabilities static,interactive]';

/**
 * CLI entry point for `p3d validate` and the legacy script path.
 * Exits with 0 on success, 1 on validation errors, 2 on usage or IO errors.
 */
export function runValidateCli(args) {
  const rest = args[0] === 'validate' ? args.slice(1) : args;
  const fileIndex = rest.indexOf('--file');
  const file = fileIndex >= 0 ? rest[fileIndex + 1] : rest[0];
  const strict = rest.includes('--strict');
  const strictPrivacy = strict || rest.includes('--strict-privacy');
  const requiredCapabilitiesIndex = rest.indexOf('--require-capabilities');
  const requiredCapabilities =
    requiredCapabilitiesIndex >= 0
      ? String(rest[requiredCapabilitiesIndex + 1] ?? '')
          .split(',')
          .map((value) => value.trim())
          .filter(Boolean)
      : [];

  if (!file || file.startsWith('--')) {
    console.error(USAGE);
    process.exit(2);
  }

  let result;
  try {
    result = validateManifestFile(file, { strict, strictPrivacy, requiredCapabilities });
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }

  if (!result.valid) {
    console.error(`Invalid product manifest: ${result.file}`);
    for (const error of result.errors) console.error(`- ${error}`);
    process.exit(1);
  }

  console.log(JSON.stringify({ file: result.file, ...result.summary }, null, 2));
}
