import { spawnSync } from 'node:child_process';
import path from 'node:path';

const LOCATION_KEYS = [
  'GPSLatitude',
  'GPSLongitude',
  'GPSPosition',
  'Location',
  'LocationName',
  'City',
  'State',
  'Country',
];

const RAW_PHONE_NAME = /^IMG_\d+\.(?:jpe?g|heic|mov|mp4|png)$/i;

/**
 * Read location metadata from supplied media and decide whether the files are
 * safe to ship. Read-only: the files are never modified.
 *
 * @param {string[]} files
 * @param {{ exiftoolCommand?: string }} [options]
 * @returns {{ ok: boolean, unavailable?: boolean, checked: string[], failures: string[] }}
 */
export function verifyMediaPrivacy(files, options = {}) {
  const exiftoolCommand = options.exiftoolCommand ?? 'exiftool';
  const absoluteFiles = files.map((file) => path.resolve(file));

  const version = spawnSync(exiftoolCommand, ['-ver'], { encoding: 'utf8' });
  if (version.error || version.status !== 0) {
    return {
      ok: false,
      unavailable: true,
      checked: absoluteFiles,
      failures: [
        `exiftool is required and was not found (command: ${exiftoolCommand}). Install it, then rerun this check.`,
      ],
    };
  }

  const metadata = spawnSync(
    exiftoolCommand,
    [
      '-json',
      '-GPSLatitude',
      '-GPSLongitude',
      '-GPSPosition',
      '-Location',
      '-LocationName',
      '-City',
      '-State',
      '-Country',
      '-FileName',
      ...absoluteFiles,
    ],
    { encoding: 'utf8' },
  );

  if (metadata.error || metadata.status !== 0) {
    return {
      ok: false,
      checked: absoluteFiles,
      failures: [`exiftool failed while reading the supplied media. No privacy decision was made. ${metadata.stderr?.trim() ?? ''}`.trim()],
    };
  }

  let records;
  try {
    records = JSON.parse(metadata.stdout);
  } catch (error) {
    return {
      ok: false,
      checked: absoluteFiles,
      failures: [
        `Could not parse exiftool JSON output. No privacy decision was made. ${error instanceof Error ? error.message : String(error)}`,
      ],
    };
  }

  const failures = [];
  for (const record of records) {
    const name = record.SourceFile ?? record.FileName ?? 'unknown-file';
    if (RAW_PHONE_NAME.test(String(record.FileName ?? ''))) {
      failures.push(`${name}: raw phone filename ${record.FileName}`);
    }
    const presentLocation = LOCATION_KEYS.filter(
      (key) =>
        record[key] !== undefined &&
        record[key] !== null &&
        String(record[key]).trim() !== '' &&
        String(record[key]).trim() !== '-',
    );
    if (presentLocation.length > 0) {
      failures.push(`${name}: location metadata present (${presentLocation.join(', ')})`);
    }
  }

  return { ok: failures.length === 0, checked: absoluteFiles, failures };
}

const USAGE = 'Usage: p3d privacy --file path/to/media [--file path/to/another-media]';

/**
 * CLI entry point for `p3d privacy` and the legacy script path.
 * Exits with 0 when clean, 1 when metadata is present, 2 on usage or missing exiftool.
 */
export function runPrivacyCli(args) {
  const rest = args[0] === 'privacy' ? args.slice(1) : args;
  const files = [];
  for (let index = 0; index < rest.length; index += 1) {
    if (rest[index] === '--file' && rest[index + 1]) {
      files.push(path.resolve(rest[index + 1]));
      index += 1;
    } else if (!rest[index].startsWith('--')) {
      files.push(path.resolve(rest[index]));
    }
  }

  if (files.length === 0) {
    console.error(USAGE);
    process.exit(2);
  }

  const result = verifyMediaPrivacy(files);

  if (result.unavailable) {
    console.error(`Cannot verify media privacy: ${result.failures[0]}`);
    process.exit(2);
  }

  if (!result.ok) {
    console.error('Media privacy check failed:');
    for (const failure of result.failures) console.error(`- ${failure}`);
    process.exit(1);
  }

  console.log(JSON.stringify({ checked: result.checked, status: 'no-location-metadata-detected' }, null, 2));
}
