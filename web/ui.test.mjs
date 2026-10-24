/* DOM wiring checks, not a browser rendering/accessibility certification.
 * This small test-only DOM exercises the actual application and real HTTP API.
 */
import test, { before, after } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { createInterface } from 'node:readline';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

class Element {
  constructor(tag, document) {
    this.tagName = tag.toLowerCase(); this.document = document; this.children = []; this.attributes = {};
    this.listeners = new Map(); this._text = ''; this._value = ''; this.disabled = false; this.hidden = false;
  }
  set textContent(value) { this._text = String(value); this.children = []; }
  get textContent() { return this._text + this.children.map(child => child.textContent).join(''); }
  set innerHTML(_) { throw new Error('The application must not insert dynamic HTML'); }
  set value(value) { this._value = String(value); }
  get value() {
    if (this.tagName !== 'select') return this._value;
    const options = this.children.filter(child => child.tagName === 'option');
    return options.some(option => option.value === this._value) ? this._value : (options[0]?.value || '');
  }
  setAttribute(name, value) { this.attributes[name] = String(value); if (name === 'id') this.document.ids.set(String(value), this); }
  removeAttribute(name) { delete this.attributes[name]; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this._text = ''; this.children = children; }
  addEventListener(type, handler) { if (!this.listeners.has(type)) this.listeners.set(type, []); this.listeners.get(type).push(handler); }
  fire(type) { for (const handler of this.listeners.get(type) || []) handler({ preventDefault() {}, target: this }); }
  focus() { this.document.activeElement = this; }
  matches(selector) {
    const match = selector.match(/^([a-z-]+)?(?:\[([a-z-]+)(?:="([^"]*)")?\])?$/);
    if (!match) throw new Error('Test DOM selector unsupported: ' + selector);
    const [, tag, attr, value] = match;
    return (!tag || this.tagName === tag) && (!attr || Object.hasOwn(this.attributes, attr)
      && (value === undefined || this.attributes[attr] === value));
  }
  querySelectorAll(selector) {
    const selectors = selector.split(',').map(value => value.trim());
    const result = [];
    for (const child of this.children) {
      if (selectors.some(value => child.matches(value))) result.push(child);
      result.push(...child.querySelectorAll(selector));
    }
    return result;
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}

class TestDocument extends Element {
  constructor(html) {
    super('document', null); this.document = this; this.ids = new Map(); this.hidden = false;
    const stack = [this];
    const voids = new Set(['meta', 'link', 'input', 'br', 'hr']);
    for (const match of html.matchAll(/<!--[^]*?-->|<\/?([a-z][a-z0-9-]*)\b([^>]*?)>|([^<]+)/gi)) {
      const [, tag, attributes, text] = match;
      if (text) { stack.at(-1)._text += text; continue; }
      if (!tag) continue;
      if (match[0].startsWith('</')) { if (stack.length > 1) stack.pop(); continue; }
      const element = this.createElement(tag);
      for (const attr of attributes.matchAll(/([a-z][a-z0-9-]*)(?:="([^"]*)")?/gi)) {
        element.setAttribute(attr[1], attr[2] || '');
      }
      element.disabled = Object.hasOwn(element.attributes, 'disabled');
      element.hidden = Object.hasOwn(element.attributes, 'hidden');
      element._value = element.attributes.value || '';
      stack.at(-1).append(element);
      if (!voids.has(tag.toLowerCase())) stack.push(element);
    }
    for (const textarea of this.querySelectorAll('textarea')) textarea.value = textarea.textContent;
    for (const option of this.querySelectorAll('option')) if (!Object.hasOwn(option.attributes, 'value')) option.value = option.textContent;
  }
  createElement(tag) { return new Element(tag, this); }
  getElementById(id) { const element = this.ids.get(id); if (!element) throw new Error('Actual HTML has no element #' + id); return element; }
}

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const operatorToken = 'ui-development-operator-token', readerToken = 'ui-development-read-token';
let server, base, doc, interval, gate = null, release = null, serviceFailure = '';
const nativeFetch = globalThis.fetch, nativeInterval = globalThis.setInterval;
const windowEvents = new Map();
const $ = id => doc.getElementById(id);

async function until(predicate, message) {
  const started = Date.now();
  while (!predicate()) {
    if (Date.now() - started > 3000) throw new Error(message + ' | visible error: ' + $('error-message').textContent);
    await new Promise(resolve => setTimeout(resolve, 5));
  }
}

async function connect(token = operatorToken) {
  $('token').value = token;
  $('connect-form').fire('submit');
  await Promise.resolve();
  await until(() => !$('connect-button').disabled && $('connection-label').textContent.startsWith('Connected'), 'UI did not connect');
}

async function state() {
  return (await nativeFetch(base + '/v1/state', { headers: { Authorization: 'Bearer ' + operatorToken } })).json();
}

async function submit(id) {
  const before = (await state()).revision;
  $(id).fire('submit');
  await until(() => Number($('revision').textContent) > before, 'UI command did not refresh committed revision');
  await until(() => !$('checkpoint-form').querySelector('button[type="submit"]').disabled, 'UI did not finish the command');
}

before(async () => {
  const source = `
import json, tempfile
from pathlib import Path
from polyia.store import Ledger
from polyia.server import make_server
with tempfile.TemporaryDirectory() as directory:
    root=Path(directory); workspace=root/'workspace'; workspace.mkdir()
    (workspace/'evidence.txt').write_text('Actual UI captured evidence.\\n')
    with Ledger(root/'state'/'ledger.sqlite3', workspace, [{'id':'R-1','title':'UI contract','verifier':'artifact-integrity'}]) as ledger:
        # This suite rapidly exercises form wiring. Admission limits have their
        # own actual-socket tests; reserve enough burst for these independent flows.
        with make_server(ledger, token='${operatorToken}', read_token='${readerToken}', request_burst=400) as server:
            print(json.dumps({'port':server.server_port}), flush=True)
            server.serve_forever()
`;
  server = spawn(process.env.PYTHON || 'python', ['-u', '-c', source], { cwd: root });
  server.stderr.on('data', chunk => { serviceFailure += chunk.toString(); });
  base = await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('UI test server failed: ' + serviceFailure)), 5000);
    const lines = createInterface({ input: server.stdout });
    lines.once('line', line => { clearTimeout(timeout); lines.close(); resolve('http://127.0.0.1:' + JSON.parse(line).port); });
    server.once('exit', code => { clearTimeout(timeout); reject(new Error('UI test server exited ' + code + ': ' + serviceFailure)); });
  });
  doc = new TestDocument(readFileSync(path.join(root, 'web/index.html'), 'utf8'));
  globalThis.document = doc;
  globalThis.window = { addEventListener(type, callback) { windowEvents.set(type, callback); } };
  globalThis.setInterval = callback => { interval = callback; return 0; };
  globalThis.fetch = async (url, options) => {
    const response = await nativeFetch(base + url, options);
    if (gate && options.method === 'POST') {
      gate = null;
      await new Promise(resolve => { release = resolve; });
    }
    return response;
  };
  await import('./app.js');
});

after(() => {
  if (release) release();
  globalThis.fetch = nativeFetch; globalThis.setInterval = nativeInterval;
  delete globalThis.document; delete globalThis.window;
  server?.kill('SIGTERM');
});

test('actual UI connection shows state and enables only permitted controls', async () => {
  assert.equal($('revision').textContent, '—');
  await connect(readerToken);
  assert.equal($('token').value, '');
  assert.equal($('scope-display').textContent, 'Read access only');
  assert.equal($('verify-ledger').disabled, false);
  assert.equal($('checkpoint-form').querySelector('button[type="submit"]').disabled, true);
  $('disconnect-button').fire('click');
  assert.equal($('revision').textContent, '—');
  await connect();
  assert.equal($('checkpoint-form').querySelector('button[type="submit"]').disabled, false);
});

test('actual guidance form preserves markup as text and applies its explicit action', async () => {
  $('guidance-target').value = 'R-1'; $('guidance-action').value = 'set_priority';
  $('guidance-priority').value = '8';
  const text = '<img src=x onerror=alert(1)> literal instruction';
  $('guidance-text').value = text;
  await submit('guidance-form');
  assert.ok($('guidance-preview').textContent.includes(text));
  assert.equal($('guidance-preview').querySelector('img'), null);
  assert.equal($('apply-guidance').disabled, true);
  $('guidance-reason').value = 'Reviewed in real UI handler';
  await submit('ack-form');
  assert.equal($('apply-guidance').disabled, false);
  const before = (await state()).revision;
  $('apply-guidance').fire('click');
  await until(() => Number($('revision').textContent) > before, 'UI did not apply guidance');
  assert.equal((await state()).requirements['R-1'].priority, 8);
  assert.ok($('guidance-preview').textContent.includes('APPLIED'));
});

test('switching session during a pending response does not leave controls locked', async () => {
  await connect();
  gate = true; release = null;
  $('checkpoint-note').value = 'Delayed response'; $('checkpoint-form').fire('submit');
  await until(() => release !== null, 'Delayed POST did not reach the server');
  await connect();
  release(); release = null;
  await new Promise(resolve => setTimeout(resolve, 20));
  assert.equal($('checkpoint-form').querySelector('button[type="submit"]').disabled, false);
});

test('pagehide clears the visible session before a page can return from history cache', async () => {
  await connect();
  windowEvents.get('pagehide')();
  assert.equal($('connection-label').textContent, 'Disconnected');
  assert.equal($('revision').textContent, '—');
  assert.equal($('checkpoint-form').querySelector('button[type="submit"]').disabled, true);
});

test('actual experiment form records science and polling reads external transitions', async () => {
  await connect();
  $('experiment-name').value = 'acceptance'; $('experiment-parameters').value = '{}';
  await submit('experiment-form');
  assert.ok($('runs-list').textContent.includes('PASS'));
  const current = await state();
  const response = await nativeFetch(base + '/v1/commands', { method: 'POST',
    headers: { Authorization: 'Bearer ' + operatorToken, 'Content-Type': 'application/json' },
    body: JSON.stringify({ command_id: 'external-ui-poll', expected_revision: current.revision,
      kind: 'checkpoint.create', payload: { note: 'External process wrote this' } }) });
  assert.equal(response.status, 200);
  interval();
  await until(() => Number($('revision').textContent) === current.revision + 1, 'Polling did not read the external revision');
  assert.ok($('latest-checkpoint').textContent.includes('External process wrote this'));
});

test('actual artifact controls produce verify accept and expose checkpoint integrity receipts', async () => {
  await connect();
  $('requirement-select').value = 'R-1'; $('artifact-paths').value = 'evidence.txt';
  $('production-note').value = 'Captured through the actual UI';
  await submit('produce-form');
  assert.equal($('accept-requirement').disabled, true);
  assert.equal($('verify-requirement').disabled, false);
  let revision = (await state()).revision;
  $('verify-requirement').fire('click');
  await until(() => Number($('revision').textContent) > revision && !$('accept-requirement').disabled, 'Verifier did not enable acceptance');
  revision = (await state()).revision;
  $('accept-requirement').fire('click');
  await until(() => Number($('revision').textContent) > revision, 'Acceptance did not refresh state');
  assert.equal($('accepted-count').textContent, '1');
  assert.equal($('mission-status').textContent, 'Not commissioned');
  await until(() => !$('checkpoint-form').querySelector('button[type="submit"]').disabled, 'Command did not settle');
  $('checkpoint-note').value = 'UI workflow snapshot'; await submit('checkpoint-form');
  $('load-checkpoint').fire('click');
  await until(() => $('checkpoint-output').textContent.includes('ACCEPTED'), 'Checkpoint read not displayed');
  $('verify-ledger').fire('click');
  await until(() => $('verification-status').textContent.startsWith('Verification passed'), 'Ledger verification not displayed');
  $('receipt-form').fire('submit');
  await until(() => $('receipt-output').textContent.includes('checkpoint_id'), 'Command receipt not displayed');
  $('load-refusals').fire('click');
  await until(() => $('refusals-output').textContent.includes('refusals'), 'Refusals not displayed');
});

test('malformed scientific parameters show a visible refusal without a mutation', async () => {
  await connect();
  const revision = (await state()).revision;
  $('experiment-parameters').value = '[]'; $('experiment-form').fire('submit');
  await until(() => !$('error-banner').hidden, 'Input error was not visible');
  assert.equal($('error-title').textContent, 'INVALID_PARAMETERS');
  assert.equal((await state()).revision, revision);
});

test('intake submits real text, computes supported spans and displays unknown markup as text', async () => {
  await connect();
  const original = 'Teach polynomial division\n<img src=x onerror=alert(1)> unknown request';
  $('intake-text').value = original; $('intake-format').value = 'text';
  $('intake-style').value = 'tutorial';
  await submit('intake-form');
  const run = (await state()).runs.at(-1);
  assert.equal(run.name, 'intake');
  assert.equal(run.parameters.text, original);
  assert.equal(run.report.status, 'INCONCLUSIVE');
  assert.deepEqual(run.report.result.interpretations[0].computation.result.quotient, ['-1', '1', '1']);
  assert.ok($('intake-result').textContent.includes('UNSUPPORTED_INTENT'));
  assert.ok($('intake-result').textContent.includes('<img src=x onerror=alert(1)>'));
  assert.equal($('intake-result').querySelector('img'), null);
  assert.ok($('intake-result').textContent.includes('b(x) != 0'));
  $('disconnect-button').fire('click');
  assert.ok(!$('intake-result').textContent.includes(original));
  await connect(readerToken);
  assert.equal($('run-intake').disabled, true);
  assert.ok($('intake-result').textContent.includes('UNSUPPORTED_INTENT'));
});

test('native intake executes typed output and oversized input refuses before a command', async () => {
  await connect();
  $('intake-format').value = 'polyia';
  $('intake-text').value = '(commission (profile "polyia.native/0.1") (emit answer (add 2 3)))';
  await submit('intake-form');
  const run = (await state()).runs.at(-1);
  assert.equal(run.report.result.interpretations[0].computation.outputs.answer.value, '5');
  const revision = (await state()).revision;
  $('intake-text').value = 'é'.repeat(8193); $('intake-form').fire('submit');
  await until(() => !$('error-banner').hidden, 'Intake byte limit refusal not displayed');
  assert.equal($('error-title').textContent, 'INTAKE_LIMIT');
  assert.equal((await state()).revision, revision);
});
