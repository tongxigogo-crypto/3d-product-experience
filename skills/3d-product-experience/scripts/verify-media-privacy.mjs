#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import path from 'node:path';

const args = process.argv.slice(2);
const files = [];
for (let index = 0; index < args.length; index += 1) {
  if (args[index] === '--file' && args[index + 1]) {
    files.push(path.resolve(args[index + 1]));
    index += 1;
  } else if (!args[index].startsWith('--')) {
    files.push(path.resolve(args[index]));
  }
}

if (files.length === 0) {
  console.error('Usage: verify-media-privacy.mjs --file path/to/media [--file path/to/another-media]');
  process.exit(2);
}

const exiftool = spawnSync('exiftool', ['-ver'], { encoding: 'utf8' });
if (exiftool.error || exiftool.status !== 0) {
  console.error('Cannot verify media privacy: exiftool is required and was not found. Install it, then rerun this check.');
  process.exit(2);
}

const metadata = spawnSync('exiftool', [
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
  ...files,
], { encoding: 'utf8' });

if (metadata.error || metadata.status !== 0) {
  console.error('exiftool failed while reading the supplied media. No privacy decision was made.');
  console.error(metadata.stderr?.trim() ?? '');
  process.exit(1);
}

let records;
try {
  records = JSON.parse(metadata.stdout);
} catch (error) {
  console.error('Could not parse exiftool JSON output. No privacy decision was made.');
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}

const locationKeys = ['GPSLatitude', 'GPSLongitude', 'GPSPosition', 'Location', 'LocationName', 'City', 'State', 'Country'];
const failures = [];
for (const record of records) {
  const name = record.SourceFile ?? record.FileName ?? 'unknown-file';
  const rawName = String(record.FileName ?? '').match(/^IMG_\d+\.(?:jpe?g|heic|mov|mp4|png)$/i);
  if (rawName) failures.push(`${name}: raw phone filename ${record.FileName}`);
  const presentLocation = locationKeys.filter((key) => record[key] !== undefined && record[key] !== null && String(record[key]).trim() !== '' && String(record[key]).trim() !== '-');
  if (presentLocation.length > 0) failures.push(`${name}: location metadata present (${presentLocation.join(', ')})`);
}

if (failures.length > 0) {
  console.error('Media privacy check failed:');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log(JSON.stringify({ checked: files, status: 'no-location-metadata-detected' }, null, 2));
