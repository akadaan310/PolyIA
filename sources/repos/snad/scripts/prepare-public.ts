/** Materialize the frozen mission snapshot from Git, verify it, and package it for the lab. */
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { lstat, mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { verifyPackage, type MissionManifest } from './mission.js';

const root = process.cwd();
const manifestPath = join(root, 'mission', 'manifest.json');
let manifestBytes: Buffer;
try { manifestBytes = await readFile(manifestPath); }
catch (error) {
  if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
    console.log('No frozen mission manifest in this source snapshot; building the standalone lab.');
    process.exit(0);
  }
  throw error;
}
const manifest = JSON.parse(manifestBytes.toString()) as MissionManifest;
if (!/^[a-f0-9]{40}$/.test(manifest.sourceCommit)) throw new Error('Invalid frozen source commit');
const temporary = await mkdtemp(join(tmpdir(), 'snad-public-'));
try {
  for (const artifact of manifest.artifacts) {
    if (!artifact.path || artifact.path.startsWith('/') || artifact.path.includes('\\') || artifact.path.split('/').some(part => !part || part === '..' || part === '.')) throw new Error('Unsafe frozen artifact path');
    const bytes = execFileSync('git', ['show', `${manifest.sourceCommit}:${artifact.path}`], { cwd: root, maxBuffer: 90 * 1024 * 1024 });
    if (bytes.byteLength !== artifact.bytes || createHash('sha256').update(bytes).digest('hex') !== artifact.sha256) throw new Error(`Frozen artifact mismatch: ${artifact.path}`);
    const target = join(temporary, 'files', artifact.path);
    await mkdir(dirname(target), { recursive: true });
    await writeFile(target, bytes);
  }
  await writeFile(join(temporary, 'manifest.json'), manifestBytes);
  const verified = await verifyPackage(temporary);
  if (!verified.valid) throw new Error(verified.errors.join('\n'));
  const publicDirectory = join(root, 'web', 'public');
  // Refuse redirection through previously planted output links.
  for (const path of [publicDirectory, join(publicDirectory, 'mission'), join(publicDirectory, 'mission', 'manifest.json'), join(publicDirectory, 'snad-mission.tar.gz')]) {
    try { if ((await lstat(path)).isSymbolicLink()) throw new Error(`Symbolic publication output: ${path}`); }
    catch (error) { if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error; }
  }
  await mkdir(join(publicDirectory, 'mission'), { recursive: true });
  await writeFile(join(publicDirectory, 'mission', 'manifest.json'), manifestBytes);
  execFileSync('tar', ['-czf', join(publicDirectory, 'snad-mission.tar.gz'), '-C', temporary, 'manifest.json', 'files']);
  console.log(JSON.stringify({ frozenSourceCommit: manifest.sourceCommit, artifacts: verified.checked, contentHash: manifest.contentHash, download: 'snad-mission.tar.gz' }));
} finally { await rm(temporary, { recursive: true, force: true }); }
