import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, symlink, rename } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { buildPackage, verifyPackage } from '../scripts/mission.js';

test('offline handoff verifies content and rejects changed source evidence', async () => {
  const root = await mkdtemp(join(tmpdir(), 'snad-mission-'));
  await mkdir(join(root, 'src'));
  await writeFile(join(root, 'src', 'example.txt'), 'Original orthography: قَالَ\n');
  const destination = join(root, 'package');
  const manifest = await buildPackage({ root, destination, paths: ['src/example.txt'], sourceCommit: 'a'.repeat(40) });
  assert.equal(manifest.artifacts.length, 1);
  assert.equal(manifest.artifacts[0].path, 'src/example.txt');
  assert.equal((await verifyPackage(destination)).valid, true);
  await writeFile(join(destination, 'files', 'src', 'example.txt'), 'Changed');
  const changed = await verifyPackage(destination);
  assert.equal(changed.valid, false);
  assert.ok(changed.errors.some(x => x.includes('src/example.txt')));
});

test('manifest integrity detects changed objectives and excludes traversal paths', async () => {
  const root = await mkdtemp(join(tmpdir(), 'snad-mission-'));
  await writeFile(join(root, 'a.txt'), 'a');
  const destination = join(root, 'package');
  await buildPackage({ root, destination, paths: ['a.txt'], sourceCommit: 'b'.repeat(40) });
  const file = join(destination, 'manifest.json');
  const manifest = JSON.parse(await readFile(file, 'utf8'));
  manifest.objectives[0].status = 'invented-success';
  await writeFile(file, JSON.stringify(manifest));
  assert.equal((await verifyPackage(destination)).valid, false);
  await assert.rejects(() => buildPackage({ root, destination, paths: ['../secret'], sourceCommit: 'b'.repeat(40) }), /path/i);
});

test('content hash is independent of input file order and does not assert authenticity', async () => {
  const root = await mkdtemp(join(tmpdir(), 'snad-mission-'));
  await writeFile(join(root, 'a'), 'a');
  await writeFile(join(root, 'b'), 'b');
  const a = await buildPackage({ root, destination: join(root, 'one'), paths: ['b', 'a'], sourceCommit: 'c'.repeat(40) });
  const b = await buildPackage({ root, destination: join(root, 'two'), paths: ['a', 'b'], sourceCommit: 'c'.repeat(40) });
  assert.equal(a.contentHash, b.contentHash);
  assert.match(a.integrityMeaning, /not.*authenticity/);
});

test('package export refuses destination links without overwriting external files', async () => {
  const root = await mkdtemp(join(tmpdir(), 'snad-mission-'));
  await writeFile(join(root, 'input'), 'replacement');
  await writeFile(join(root, 'outside'), 'original');
  const destination = join(root, 'package');
  await mkdir(join(destination, 'files'), { recursive: true });
  await symlink(join(root, 'outside'), join(destination, 'files', 'input'));
  await assert.rejects(() => buildPackage({ root, destination, paths: ['input'], sourceCommit: 'd'.repeat(40) }), /[Ss]ymbolic/);
  assert.equal(await readFile(join(root, 'outside'), 'utf8'), 'original');
});

test('package verifier rejects a linked files root and unlisted executable files', async () => {
  const root = await mkdtemp(join(tmpdir(), 'snad-mission-'));
  await writeFile(join(root, 'input'), 'source');
  const destination = join(root, 'package');
  await buildPackage({ root, destination, paths: ['input'], sourceCommit: 'e'.repeat(40) });
  await rename(join(destination, 'files'), join(root, 'external'));
  await symlink(join(root, 'external'), join(destination, 'files'));
  assert.equal((await verifyPackage(destination)).valid, false);

  const clean = join(root, 'clean');
  await buildPackage({ root, destination: clean, paths: ['input'], sourceCommit: 'e'.repeat(40) });
  await writeFile(join(clean, 'files', 'unlisted.test.ts'), 'throw new Error("unlisted");');
  const result = await verifyPackage(clean);
  assert.equal(result.valid, false);
  assert.ok(result.errors.some(error => error.includes('unlisted')));
});

test('the packaged verifier runs with Node before dependency installation', async () => {
  const root = await mkdtemp(join(tmpdir(), 'snad-mission-'));
  await mkdir(join(root, 'scripts'));
  await writeFile(join(root, 'scripts', 'mission.ts'), await readFile(new URL('../scripts/mission.ts', import.meta.url)));
  const destination = join(root, 'package');
  const manifest = await buildPackage({ root, destination, paths: ['scripts/mission.ts'], sourceCommit: 'f'.repeat(40) });
  assert.match(manifest.nextPermittedOperation.command, /^node --experimental-strip-types/);
  const output = execFileSync(process.execPath, ['--experimental-strip-types', join(destination, 'files', 'scripts', 'mission.ts'), 'verify', '--package', destination], { encoding: 'utf8', cwd: root });
  assert.equal(JSON.parse(output).valid, true);
});
