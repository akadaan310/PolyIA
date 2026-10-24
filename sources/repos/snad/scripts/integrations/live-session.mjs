// Explicit remote publication utility. Credentials exist only in this process.
// Start with NODE_USE_ENV_PROXY=1 node scripts/integrations/live-session.mjs,
// then send one JSON command per line. Never redirect identity responses.
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { createInterface } from 'node:readline';

const root = resolve(import.meta.dirname, '../..');
const evidence = resolve(root, 'evidence/purl-live');
const origin = 'https://purls-production.up.railway.app';
const cgitOrigin = 'https://cgit-hub-production.up.railway.app';
const sdkDigest = '7e195c72e3db43f52bc1af07a4ec77b491dd2f30d942a3a88fdaa769254893d0';
const hash = value => createHash('sha256').update(value).digest('hex');
const records = [];
const secretKeys = new Set(['csrf_token', 'token', 'credential', 'credentialId', 'authorization', 'cookie', 'set-cookie']);
function safe(value) {
  if (Array.isArray(value)) return value.map(safe);
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).filter(([key]) => !secretKeys.has(key.toLowerCase()) && !secretKeys.has(key)).map(([key, item]) => [key, safe(item)]));
  return value;
}
async function save(name, value) {
  await mkdir(evidence, { recursive: true });
  await writeFile(resolve(evidence, `${name}.json`), `${JSON.stringify(safe(value), null, 2)}\n`);
}
async function transport(url, options) {
  const response = await fetch(url, { ...options, signal: AbortSignal.timeout(30000) });
  const bytes = await response.clone().arrayBuffer();
  records.push({ at: new Date().toISOString(), method: options?.method ?? 'GET', url: String(url), status: response.status, responseBytes: bytes.byteLength, responseSha256: hash(Buffer.from(bytes)) });
  await save('http-operations', records);
  return response;
}
const sdkResponse = await transport(`${origin}/sdk/launch.js`);
if (!sdkResponse.ok) throw Error(`SDK unavailable: ${sdkResponse.status}`);
const sdk = await sdkResponse.text();
if (hash(sdk) !== sdkDigest) throw Error('SDK digest changed: inspect the new contract before using it');
const { PurlLaunchClient } = await import(`data:text/javascript;base64,${Buffer.from(sdk).toString('base64')}`);
const client = new PurlLaunchClient(origin, { fetch: transport });
let resourceId = null, currentState = null, identity = null, cgit = null, repository = null;

async function inspect() {
  if (!resourceId) throw Error('No owned mission has been created in this process');
  return (await client.inspect(resourceId)).resource;
}
async function transition(name, payload = {}) {
  const before = await inspect();
  const result = await client.operation(resourceId, name, before.version, payload, `snad-${resourceId}-${name}-${before.version}`);
  const after = await inspect();
  if (after.version < result.resource.version) throw Error(`Read-back failed for ${name}`);
  await save(`latest-${name}`, result);
  return result;
}
async function run() {
  await transition('compile');
  const built = await transition('build');
  if (built.build.status !== 'passed') throw Error('Native declared tests failed');
  const queued = await transition('run', { input: currentState, seed: 20261018 });
  const path = `/api/resources/${resourceId}/executions/${queued.execution.id}`;
  let result;
  for (let attempt = 0; attempt < 60; attempt++) {
    result = await client.request(path);
    if (['succeeded', 'failed', 'cancelled'].includes(result.execution.status)) break;
    await new Promise(done => setTimeout(done, 1000));
  }
  await save('latest-execution', result);
  if (result.execution.status !== 'succeeded') throw Error(`Execution status: ${result.execution.status}`);
  if (result.execution.artifact_id) await save('latest-artifact', await client.request(`/api/resources/${resourceId}/artifacts/${result.execution.artifact_id}`));
  return result.execution;
}
async function publish(summary, next, refs = []) {
  await transition('checkpoint', { summary, next, evidence: refs });
  await save('owned-continuity', await client.request(`/api/resources/${resourceId}/continuity`));
  await transition('publish', { visibility: 'public' });
  const manifestResponse = await transport(`${origin}/api/resources/${resourceId}/manifest`);
  const manifest = await manifestResponse.json();
  if (!manifestResponse.ok || manifest.authority.owner || manifest.authority.principal_id) throw Error('Anonymous manifest verification failed');
  await save('anonymous-manifest', manifest);
  const replayResponse = await transport(`${origin}/api/resources/${resourceId}/replay`);
  const replay = await replayResponse.json();
  await save('anonymous-replay', replay);
  if (!replayResponse.ok || !replay.valid) throw Error('Anonymous replay verification failed');
  const result = { resourceId, url: `${origin}/p/${resourceId}`, version: manifest.program.version, principal: safe(identity), nativeProgram: 'Typed JSON identity/replay only; SNAD algorithms run in the standalone SDK', replayValid: replay.valid, credentialPersistence: 'process memory only', continuation: 'Read anonymously. A newly authenticated principal must fork. Guest ownership expires after 1800 seconds.' };
  await save('mission', result);
  return result;
}
async function initialize(command) {
  if (resourceId) throw Error('This session already owns a mission');
  const preview = await client.preview();
  identity = preview.identity;
  const me = await client.me();
  if (!me.identity.scopes.includes('resources:write')) throw Error('Preview lacks resources:write');
  await save('identity-readiness', me);
  currentState = JSON.parse(await readFile(resolve(root, command.stateFile), 'utf8'));
  const schema = JSON.parse(await readFile(resolve(root, 'schemas/live-mission-state.schema.json'), 'utf8'));
  const fixture = { schema: 'snad.mission-state/1', mission: { id: 'fixture', status: 'INCOMPLETE' }, graph: { nodes: [], edges: [] }, events: [], artifacts: [], blockers: [], checkpoint: {}, next: [] };
  const created = await client.createResource({ title: 'SNAD · Computational Attribution & Transition Grammar', kind: 'mission', language: 'purl', visibility: 'private', source: 'input json', state: currentState, input_schema: schema, output_schema: schema, tests: [{ input: fixture, expected: fixture }] }, 'snad-independent-mission-2026-10-18-v1');
  resourceId = created.resource.id;
  const owned = await client.request(`/api/resources/${resourceId}/manifest`);
  if (!owned.authority.owner) throw Error('Created mission ownership read-back failed');
  await save('created-private-mission', created);
  const execution = await run();
  return publish('Initial independent SNAD mission checkpoint. Typed state identity program compiled, passed its declared deterministic test and executed through the bounded worker. This verifies transport/replay only. Scientific implementation and full acceptance remain incomplete; code repository creation is blocked by GitHub integration permissions.', currentState.next, [{ execution_id: execution.id }, { service_discovery: 'evidence/service-discovery.json' }]);
}
async function update(command) {
  currentState = JSON.parse(await readFile(resolve(root, command.stateFile), 'utf8'));
  await transition('source', { state: currentState });
  const execution = await run();
  return publish(command.summary ?? 'SNAD evidence checkpoint; inspect recorded limitations and unfinished work.', currentState.next, [...(command.evidence ?? []), { execution_id: execution.id }]);
}
async function cgitCommit(command) {
  if (!cgit) {
    cgit = new PurlLaunchClient(cgitOrigin, { fetch: transport });
    await cgit.preview();
    const me = await cgit.me();
    if (!me.identity.scopes.includes('cgit:write')) throw Error('CGIT preview lacks cgit:write');
    await save('cgit-identity-readiness', me);
  }
  if (!repository) {
    const created = await cgit.request('/api/cgit/repos/create', { method: 'POST', body: { name: 'SNAD mission artifacts' } });
    repository = created.repository;
    const check = await cgit.request(`/api/cgit/repos/${repository.id}`);
    if (check.repository.id !== repository.id) throw Error('CGIT repository read-back failed');
    await save('cgit-created-repository', check);
  }
  const before = await cgit.request(`/api/cgit/repos/${repository.id}`);
  const artifacts = [];
  if (command.sourceCommit !== undefined && !/^[a-f0-9]{40}$/.test(command.sourceCommit)) throw Error('sourceCommit must be an exact Git commit');
  for (const file of command.files) {
    const content = await readFile(resolve(root, file), 'utf8');
    artifacts.push({ path: file, type: file.endsWith('.json') ? 'research' : 'code', content, provenance: { source: 'SNAD independent mission', path: file, fileSha256: hash(content), sourceCommit: command.sourceCommit ?? null, limitations: 'Authorship attributed to an unverified preview principal; sourceCommit is an author assertion.' } });
  }
  const result = await cgit.request(`/api/cgit/repos/${repository.id}/commit`, { method: 'POST', body: { branch: 'main', expectedHead: before.head?.hash ?? null, message: command.message ?? 'SNAD attributable mission artifacts', artifacts } });
  const after = await cgit.request(`/api/cgit/repos/${repository.id}`);
  if (after.head.hash !== result.commit.hash) throw Error('CGIT commit read-back failed');
  await save('cgit-latest-commit', result);
  const snapshot = await cgit.request(`/api/cgit/repos/${repository.id}/export`);
  await save('cgit-export', snapshot);
  return { repositoryId: repository.id, commit: result.commit.hash, artifacts: artifacts.length, readableBy: 'Authenticated owner only; no public repository publication endpoint observed', export: 'evidence/purl-live/cgit-export.json' };
}
console.log(JSON.stringify({ ready: true, operations: ['initialize', 'update', 'inspect', 'cgitCommit', 'quit'], credentialPersistence: 'process memory only' }));
for await (const line of createInterface({ input: process.stdin })) {
  try {
    const command = JSON.parse(line);
    if (command.op === 'quit') break;
    const result = command.op === 'initialize' ? await initialize(command) : command.op === 'update' ? await update(command) : command.op === 'inspect' ? await inspect() : command.op === 'cgitCommit' ? await cgitCommit(command) : (() => { throw Error('Unknown operation'); })();
    console.log(JSON.stringify({ ok: true, op: command.op, result: safe(result) }));
  } catch (error) { console.log(JSON.stringify({ ok: false, code: error.code ?? error.name, status: error.status, message: error.message })); }
}
