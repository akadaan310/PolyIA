/* Optional development checks: Node built-ins only, against the real Python API. */
import test, { before, after } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createInterface } from 'node:readline';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

let Client;
try { ({ CommandClient: Client } = await import('./client.mjs')); } catch (error) {
  if (error.code !== 'ERR_MODULE_NOT_FOUND') throw error;
}

let server, base, serverFailure = '';
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const token = 'development-test-operator-token';
const readToken = 'development-test-read-token';
before(async () => {
  if (!Client) return;
  const source = `
import json, tempfile
from pathlib import Path
from polyia.store import Ledger
from polyia.server import make_server
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    workspace = root / 'workspace'
    workspace.mkdir()
    (workspace / 'evidence.txt').write_text('An actual captured artifact.\\n')
    with Ledger(root / 'state' / 'ledger.sqlite3', workspace, [{'id':'R-1','title':'Client contract','verifier':'artifact-integrity'}]) as ledger:
        with make_server(ledger, token='${token}', read_token='${readToken}', request_burst=400) as server:
            print(json.dumps({'port':server.server_port}), flush=True)
            server.serve_forever()
`;
  server = spawn(process.env.PYTHON || 'python', ['-u', '-c', source], { cwd: root });
  server.stderr.on('data', chunk => { serverFailure += chunk.toString(); });
  base = await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('Test server did not start: ' + serverFailure)), 5000);
    const lines = createInterface({ input: server.stdout });
    lines.once('line', line => { clearTimeout(timeout); lines.close(); resolve('http://127.0.0.1:' + JSON.parse(line).port); });
    server.once('exit', code => { clearTimeout(timeout); reject(new Error('Test server exited ' + code + ': ' + serverFailure)); });
  });
});
after(() => { if (server) server.kill('SIGTERM'); });

function client(fetchImpl) {
  assert.ok(Client, 'The browser command client is not implemented yet');
  return new Client(fetchImpl || ((url, options) => fetch(base + url, options)));
}

test('a connection reads real state and a read token cannot issue a command', async () => {
  const reader = client();
  await reader.connect(readToken);
  assert.equal(reader.scope, 'read');
  assert.equal(reader.state.commission_status, 'NOT_COMMISSIONED');
  const before = reader.state.revision;
  await assert.rejects(reader.command('checkpoint.create', { note: 'forbidden' }), { code: 'FORBIDDEN' });
  await reader.refresh();
  assert.equal(reader.state.revision, before);
  reader.disconnect();
  assert.equal(reader.state, null);
  await assert.rejects(reader.read('/v1/state'), { code: 'DISCONNECTED' });
});

test('lost command response keeps the exact command available for idempotent retry', async () => {
  let loseResponse = true;
  const requests = [];
  const operator = client(async (url, options) => {
    const response = await fetch(base + url, options);
    if (options.method === 'POST') {
      requests.push(JSON.parse(options.body));
      if (loseResponse) { loseResponse = false; throw new TypeError('Simulated response loss after commit'); }
    }
    return response;
  });
  await operator.connect(token);
  const before = operator.state.revision;
  await assert.rejects(operator.command('checkpoint.create', { note: 'exactly once' }), { code: 'CONNECTION_ERROR' });
  assert.equal(operator.hasPending, true);
  await assert.rejects(operator.command('checkpoint.create', { note: 'not duplicated' }), { code: 'PENDING_COMMAND' });
  const receipt = await operator.retry();
  assert.equal(receipt.revision, before + 1);
  assert.deepEqual(requests[0], requests[1]);
  assert.equal(operator.hasPending, false);
  await operator.refresh();
  assert.equal(operator.state.revision, before + 1);
  const lookup = await operator.read('/v1/commands/' + encodeURIComponent(receipt.command_id));
  assert.deepEqual(lookup, receipt);
});

test('a revision conflict is visible and does not silently replay with a new revision', async () => {
  const first = client(), second = client();
  await first.connect(token);
  await second.connect(token);
  await first.command('checkpoint.create', { note: 'concurrent operator' });
  await assert.rejects(second.command('checkpoint.create', { note: 'stale view' }), { code: 'REVISION_CONFLICT', status: 409 });
  assert.equal(second.hasPending, false);
  await second.refresh();
  assert.equal(second.state.revision, first.state.revision + 1);
});

test('guidance with malicious markup remains exact data throughout command lifecycle', async () => {
  const operator = client();
  await operator.connect(token);
  const text = '<img src=x onerror=alert(1)> & preserve this exact text';
  const submitted = await operator.command('guidance.submit', { target: 'R-1', text,
    action: { kind: 'set_priority', target: 'R-1', priority: 9 } });
  await operator.refresh();
  const id = submitted.result.guidance_id;
  await operator.command('guidance.ack', { guidance_id: id, disposition: 'ACKNOWLEDGED', reason: 'Explicitly reviewed' });
  await operator.refresh();
  await operator.command('guidance.apply', { guidance_id: id });
  await operator.refresh();
  assert.equal(operator.state.guidance[id].text, text);
  assert.equal(operator.state.guidance[id].status, 'APPLIED');
  assert.equal(operator.state.requirements['R-1'].priority, 9);
});

test('artifact capture verification acceptance and checkpoint use registered operations', async () => {
  const operator = client();
  await operator.connect(token);
  await operator.command('requirement.produce', { requirement_id: 'R-1', artifacts: ['evidence.txt'], note: 'Real client evidence' });
  await operator.refresh();
  const verification = await operator.command('requirement.verify', { requirement_id: 'R-1' });
  assert.equal(verification.result.verification.evidence_class, 'ARTIFACT_INTEGRITY');
  await operator.refresh();
  await operator.command('requirement.accept', { requirement_id: 'R-1' });
  await operator.refresh();
  assert.equal(operator.state.requirements['R-1'].status, 'ACCEPTED');
  assert.equal(operator.state.commission_status, 'NOT_COMMISSIONED');
  assert.equal((await operator.read('/v1/verify')).ok, true);
  assert.ok((await operator.read('/v1/checkpoints/latest')).state);
  assert.ok((await operator.read('/v1/events?after=0&limit=100')).events.length > 0);
});

test('disconnect during a delayed response cannot restore an old session', async () => {
  let release;
  const operator = client(async (url, options) => {
    const response = await fetch(base + url, options);
    await new Promise(resolve => { release = resolve; });
    return response;
  });
  const connecting = operator.connect(token);
  while (!release) await new Promise(resolve => setTimeout(resolve, 5));
  operator.disconnect();
  release();
  await assert.rejects(connecting, { code: 'SESSION_CHANGED' });
  assert.equal(operator.state, null);
  assert.equal(operator.scope, null);
});

test('an incomplete 200 receipt is not reported as command success and can be recovered', async () => {
  let replaceResponse = true;
  const operator = client(async (url, options) => {
    const response = await fetch(base + url, options);
    if (replaceResponse && options.method === 'POST') {
      replaceResponse = false;
      return new Response(JSON.stringify({ ok: true }), { status: 200, headers: { 'Content-Type': 'application/json' } });
    }
    return response;
  });
  await operator.connect(token);
  const revision = operator.state.revision;
  await assert.rejects(operator.command('checkpoint.create', { note: 'Must have a full receipt' }), { code: 'INVALID_RESPONSE' });
  assert.equal(operator.hasPending, true);
  const receipt = await operator.retry();
  assert.equal(receipt.revision, revision + 1);
  assert.equal(operator.hasPending, false);
});

test('admission refusal during recovery retains a command whose original response was lost', async () => {
  const requests = [];
  const operator = client(async (url, options) => {
    if (options.method === 'POST') {
      requests.push(JSON.parse(options.body));
      if (requests.length === 2) return new Response(JSON.stringify({ ok: false,
        error: { code: 'RATE_LIMITED', message: 'Admission refused before command lookup' } }),
        { status: 429, headers: { 'Content-Type': 'application/json' } });
    }
    const response = await fetch(base + url, options);
    if (options.method === 'POST' && requests.length === 1) throw new TypeError('Lost after actual commit');
    return response;
  });
  await operator.connect(token);
  const before = operator.state.revision;
  await assert.rejects(operator.command('checkpoint.create', { note: 'Retain unresolved receipt through admission limit' }), { code: 'CONNECTION_ERROR' });
  await assert.rejects(operator.retry(), { code: 'RATE_LIMITED' });
  assert.equal(operator.hasPending, true);
  const receipt = await operator.retry();
  assert.equal(receipt.revision, before + 1);
  assert.deepEqual(requests[0], requests[1]);
  assert.deepEqual(requests[0], requests[2]);
  await operator.refresh();
  assert.equal(operator.state.revision, before + 1);
});

test('pre-ledger and unreadable error responses cannot erase a previously unresolved receipt', async () => {
  for (const [status, code] of [[401, 'UNAUTHORIZED'], [403, 'FORBIDDEN'], [408, 'REQUEST_TIMEOUT'], [400, null]]) {
    const requests = [];
    const operator = client(async (url, options) => {
      if (options.method === 'POST') {
        requests.push(JSON.parse(options.body));
        if (requests.length === 2) return new Response(code ? JSON.stringify({ ok: false,
          error: { code, message: 'Before ledger lookup' } }) : '<html>proxy failure</html>', { status });
      }
      const response = await fetch(base + url, options);
      if (options.method === 'POST' && requests.length === 1) throw new TypeError('Lost after commit');
      return response;
    });
    await operator.connect(token);
    const before = operator.state.revision;
    await assert.rejects(operator.command('checkpoint.create', { note: 'Recovery through ' + status }), { code: 'CONNECTION_ERROR' });
    await assert.rejects(operator.retry(), { code: code || 'INVALID_RESPONSE' });
    assert.equal(operator.hasPending, true, 'Pending receipt lost on ' + status);
    const receipt = await operator.retry();
    assert.equal(receipt.revision, before + 1);
    assert.deepEqual(requests[0], requests[2]);
  }
});
