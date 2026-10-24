// Offline integrity checking for the observed cgit-export/1 format.
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const canonical = value => value === null || typeof value !== 'object'
  ? JSON.stringify(value)
  : Array.isArray(value)
    ? `[${value.map(canonical).join(',')}]`
    : `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
const digest = value => createHash('sha256').update(canonical(value)).digest('hex');
const assert = (condition, reason) => { if (!condition) throw Error(reason); };
function verifyObject(value) {
  const { hash, ...unsigned } = value;
  assert(/^[a-f0-9]{64}$/.test(hash) && digest(unsigned) === hash, 'Object digest mismatch');
}
export function verifyCgitExport(snapshot) {
  const { format, repository, commits, blobs, contentHash } = snapshot;
  assert(format === 'cgit-export/1' && repository?.gitWireProtocol === false, 'Unsupported CGIT snapshot');
  assert(Array.isArray(commits) && Array.isArray(blobs), 'Missing object collections');
  assert(digest({ format, repository, commits, blobs }) === contentHash, 'Snapshot digest mismatch');
  commits.forEach(verifyObject); blobs.forEach(verifyObject);
  const commitIndex = new Map(commits.map(value => [value.hash, value]));
  const blobIndex = new Map(blobs.map(value => [value.hash, value]));
  assert(commitIndex.size === commits.length && blobIndex.size === blobs.length, 'Duplicate objects');
  for (const commit of commits) {
    assert(Array.isArray(commit.parents) && commit.parents.every(parent => commitIndex.has(parent)), 'Missing commit parent');
    for (const [path, entry] of Object.entries(commit.tree)) {
      assert(!path.startsWith('/') && !/[\\\x00-\x1f%]/.test(path) && path.split('/').every(part => part && part !== '.' && part !== '..'), 'Unsafe artifact path');
      assert(blobIndex.has(entry.hash) && blobIndex.get(entry.hash).type === entry.type, 'Missing or mismatched blob');
    }
  }
  const active = new Set(), visited = new Set();
  function visit(hash) {
    assert(!active.has(hash), 'Commit parent cycle');
    if (visited.has(hash)) return;
    active.add(hash); commitIndex.get(hash).parents.forEach(visit); active.delete(hash); visited.add(hash);
  }
  commits.forEach(value => visit(value.hash));
  for (const head of Object.values(repository.branches)) assert(head === null || commitIndex.has(head), 'Missing branch head');
  for (const release of Object.values(repository.releases)) assert(commitIndex.has(release.commit), 'Missing release commit');
  return { valid: true, format, repositoryId: repository.id, commits: commits.length, blobs: blobs.length, contentHash, assurance: 'Internal content integrity only; no external authenticity, scientific validity or ownership transfer.' };
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  if (!process.argv[2]) throw Error('Usage: node scripts/integrations/verify-cgit-export.mjs <snapshot.json>');
  console.log(JSON.stringify(verifyCgitExport(JSON.parse(await readFile(process.argv[2], 'utf8'))), null, 2));
}
