import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { copyFile, lstat, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, isAbsolute, join, parse, relative, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';

export interface Artifact { path: string; sha256: string; bytes: number }
export interface MissionManifest {
  schemaVersion: 'snad.mission/1';
  missionId: 'snad-attribution-transition-grammar-v1';
  sourceCommit: string;
  repository: { requested: string; local: string; remoteStatus: string };
  integrityMeaning: string;
  objectives: { id: string; status: string; evidence: string[] }[];
  objectiveEdges: { from: string; to: string; relation: string }[];
  events: { id: string; kind: string; evidence: string }[];
  blockers: { id: string; description: string }[];
  nextPermittedOperation: { command: string; cwd: string; effects: string; authorization: string };
  continuation: string[];
  artifacts: Artifact[];
  contentHash: string;
}
function hash(data: string | Uint8Array): string { return createHash('sha256').update(data).digest('hex'); }
function canonical(value: unknown): string {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value !== null && typeof value === 'object') {
    return '{' + Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => JSON.stringify(k) + ':' + canonical(v)).join(',') + '}';
  }
  return JSON.stringify(value);
}
function safePath(path: string): string {
  if (!path || isAbsolute(path) || path.includes('\\') || path.split('/').some(x => x === '..' || x === '.' || !x)) throw new Error(`Unsafe artifact path: ${path}`);
  if (path.split('/').some(x => x === '.git' || x.startsWith('.env'))) throw new Error(`Private artifact path: ${path}`);
  return path;
}
async function noSymlinks(path: string): Promise<void> {
  const absolute = resolve(path);
  let cursor = parse(absolute).root;
  for (const part of absolute.slice(cursor.length).split(sep).filter(Boolean)) {
    cursor = join(cursor, part);
    try {
      if ((await lstat(cursor)).isSymbolicLink()) throw new Error(`Symbolic artifact path: ${path}`);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') return;
      throw error;
    }
  }
}
async function regularFile(root: string, path: string): Promise<string> {
  safePath(path);
  await noSymlinks(root);
  const filename = resolve(root, path);
  if (!filename.startsWith(resolve(root) + sep)) throw new Error('Artifact path leaves package');
  // Reject symlinks in every component, including directories.
  let cursor = resolve(root);
  for (const part of path.split('/')) {
    cursor = join(cursor, part);
    if ((await lstat(cursor)).isSymbolicLink()) throw new Error(`Symbolic artifact path: ${path}`);
  }
  if (!(await lstat(filename)).isFile()) throw new Error(`Artifact path is not a file: ${path}`);
  return filename;
}
async function listedFiles(root: string, prefix = ''): Promise<string[]> {
  await noSymlinks(root);
  const files: string[] = [];
  for (const entry of await readdir(join(root, prefix), { withFileTypes: true })) {
    const path = prefix ? `${prefix}/${entry.name}` : entry.name;
    if (entry.isSymbolicLink()) throw new Error(`Symbolic artifact path: ${path}`);
    if (entry.isDirectory()) files.push(...await listedFiles(root, path));
    else if (entry.isFile()) files.push(path);
    else throw new Error(`Non-regular artifact path: ${path}`);
  }
  return files;
}

export async function buildPackage(options: { root: string; destination: string; paths: string[]; sourceCommit: string }): Promise<MissionManifest> {
  if (!/^[a-f0-9]{40}$/.test(options.sourceCommit)) throw new Error('sourceCommit must be an exact 40-character Git commit');
  const paths = [...new Set(options.paths)].sort();
  // Validate all paths before writing a partial package.
  const files = await Promise.all(paths.map(path => regularFile(options.root, path)));
  await noSymlinks(options.destination);
  await mkdir(join(options.destination, 'files'), { recursive: true });
  const artifacts: Artifact[] = [];
  for (let i = 0; i < paths.length; i++) {
    const data = await readFile(files[i]);
    const target = join(options.destination, 'files', paths[i]);
    await noSymlinks(target);
    await mkdir(dirname(target), { recursive: true });
    await copyFile(files[i], target);
    artifacts.push({ path: paths[i], sha256: hash(data), bytes: data.byteLength });
  }
  // Release-v1 metadata below preserves the original freeze-time publication state.
  // Later GitHub publication is recorded in evidence/publication.json; reproducing
  // the historical package must not rewrite its manifest or frozen source identity.
  const body: Omit<MissionManifest, 'contentHash'> = {
    schemaVersion: 'snad.mission/1', missionId: 'snad-attribution-transition-grammar-v1', sourceCommit: options.sourceCommit,
    repository: { requested: 'https://github.com/akadaan310/snad', local: 'files/', remoteStatus: 'GitHub creation blocked: integration HTTP 403; bundled source is authoritative for this package' },
    integrityMeaning: 'SHA-256 detects accidental or adversarial content changes against this manifest; it is not a signature or proof of authenticity.',
    objectives: [
      { id: 'reconstruct', status: 'evidence-recorded', evidence: ['docs/reconstruction.md', 'data/legacy-selection.json', 'data/original-detectors.json'] },
      { id: 'corpus', status: 'exhaustively-addressable', evidence: ['data/quran.provenance.json', 'evidence/corpus-status.json'] },
      { id: 'sdk', status: 'implemented-testable', evidence: ['packages/snad-core/src/index.ts', 'tests/core.test.ts'] },
      { id: 'research', status: 'computational-results-only', evidence: ['evidence/experiments.json', 'docs/research-register.md'] },
      { id: 'lab', status: 'automated-browser-journeys-verified', evidence: ['web/main.ts', 'tests/browser.spec.ts', 'artifacts/browser-results.json'] },
      { id: 'continuation', status: 'content-hashed-offline', evidence: ['scripts/mission.ts', 'docs/handoff.md'] }
    ],
    objectiveEdges: [
      { from: 'reconstruct', to: 'sdk', relation: 'informs' }, { from: 'corpus', to: 'research', relation: 'supplies' },
      { from: 'sdk', to: 'lab', relation: 'powers' }, { from: 'research', to: 'continuation', relation: 'preserves' }
    ],
    events: [
      { id: 'source-audit', kind: 'evidence', evidence: 'evidence/isnaad-source.json' },
      { id: 'contract-discovery', kind: 'evidence', evidence: 'evidence/service-discovery.json' },
      { id: 'whole-corpus-pass', kind: 'test', evidence: 'evidence/benchmark.json' }
    ],
    blockers: [
      { id: 'github-create', description: 'Authenticated integration cannot create akadaan310/snad: GraphQL createRepository and REST POST /user/repos rejected; REST HTTP 403.' },
      { id: 'human-validation', description: 'Independent human usability, linguistic adjudication and audio verification require real participants; automated agents cannot substitute.' },
      { id: 'durable-purl-ownership', description: 'Unverified guest PURL sessions expire. Published anonymous read/replay does not grant write or delegated agent authority; inspect docs/integrations.md.' }
    ],
    nextPermittedOperation: { command: 'node --experimental-strip-types scripts/mission.ts verify --package .. && npm ci && npm test && npm run build', cwd: 'files/', effects: 'First verifies the pristine package using Node built-ins, then installs pinned public development dependencies, runs local tests and writes ignored build outputs; no original repository or service writes.', authorization: 'Local reproduction authorized by the supplied SNAD mission.' },
    continuation: [
      'Before installing dependencies, from files/ run: node --experimental-strip-types scripts/mission.ts verify --package .. (the final two dots name the package directory). Verification deliberately rejects unlisted files, including later generated node_modules/build outputs.',
      'Read docs/handoff.md, evidence/benchmark.json, docs/evidence-report.md and docs/integrations.md.',
      'Use the exact bundled sourceCommit as a snapshot identifier; later release metadata commits do not rewrite it.',
      'Never mutate akadaan310/isnaad, FALAK, or the previous mission resource_95a5662789076892fe698316.',
      'For a new remote publication obtain scoped supported credentials; do not infer write authority from public GET access.'
    ], artifacts
  };
  const manifest = { ...body, contentHash: hash(canonical(body)) };
  await mkdir(options.destination, { recursive: true });
  await noSymlinks(join(options.destination, 'manifest.json'));
  await writeFile(join(options.destination, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  return manifest;
}

export async function verifyPackage(destination: string): Promise<{ valid: boolean; errors: string[]; checked: number; contentHash?: string }> {
  const errors: string[] = [];
  let checked = 0;
  try {
    const manifest = JSON.parse(await readFile(await regularFile(destination, 'manifest.json'), 'utf8')) as MissionManifest;
    const { contentHash, ...body } = manifest;
    if (manifest.schemaVersion !== 'snad.mission/1' || !Array.isArray(manifest.artifacts)) throw new Error('Unsupported manifest schema');
    if (hash(canonical(body)) !== contentHash) errors.push('Manifest content hash mismatch');
    const seen = new Set<string>();
    for (const artifact of manifest.artifacts) {
      if (seen.has(artifact.path)) { errors.push(`Duplicate path: ${artifact.path}`); continue; }
      seen.add(artifact.path);
      try {
        const data = await readFile(await regularFile(join(destination, 'files'), artifact.path));
        if (data.byteLength !== artifact.bytes || hash(data) !== artifact.sha256) errors.push(`Artifact mismatch: ${artifact.path}`);
        checked++;
      } catch (error) { errors.push(`Artifact ${artifact.path}: ${(error as Error).message}`); }
    }
    for (const path of await listedFiles(join(destination, 'files'))) {
      if (!seen.has(path)) errors.push(`Unlisted artifact: ${path}`);
    }
    return { valid: errors.length === 0, errors, checked, contentHash };
  } catch (error) { return { valid: false, errors: [(error as Error).message], checked }; }
}

async function main(): Promise<void> {
  const operation = process.argv[2];
  const packageIndex = process.argv.indexOf('--package');
  const destination = resolve(packageIndex >= 0 ? process.argv[packageIndex + 1] : 'mission/package');
  if (operation === 'verify') {
    const result = await verifyPackage(destination);
    console.log(JSON.stringify(result, null, 2));
    if (!result.valid) process.exitCode = 1;
    return;
  }
  if (operation !== 'pack') throw new Error('Usage: tsx scripts/mission.ts pack|verify [--package directory]');
  const root = process.cwd();
  execFileSync('git', ['diff', '--quiet', 'HEAD', '--'], { cwd: root });
  const sourceCommit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim();
  const paths = execFileSync('git', ['ls-files', '-z'], { cwd: root, encoding: 'utf8' }).split('\0').filter(path => path && !path.startsWith('mission/') && !path.startsWith('web/public/'));
  const manifest = await buildPackage({ root, destination, paths, sourceCommit });
  await mkdir(join(root, 'mission'), { recursive: true });
  await writeFile(join(root, 'mission', 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  console.log(JSON.stringify({ destination: relative(root, destination), sourceCommit, artifacts: manifest.artifacts.length, contentHash: manifest.contentHash }));
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) main().catch(error => { console.error((error as Error).message); process.exitCode = 1; });
