#!/usr/bin/env node
// Development-only Chromium verification. Playwright is never a runtime dependency.
// PLAYWRIGHT_MODULE_PATH selects an externally installed playwright module.
// Optional --origin HTTPS uses POLYIA_READ_TOKEN for observational live checks.
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { randomBytes } from 'node:crypto';
import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const originIndex = process.argv.indexOf('--origin');
const live = originIndex !== -1;
let origin = live ? process.argv[originIndex + 1] : null;
if (live) assert.match(origin || '', /^https:\/\/[^/]+$/);
const output = resolve(process.env.POLYIA_BROWSER_OUTPUT || '/tmp/polyia-browser-evidence');
await mkdir(output, { recursive: true });
const temp = await mkdtemp(join(tmpdir(), 'polyia-browser-fixture-'));
const reader = live ? process.env.POLYIA_READ_TOKEN : randomBytes(32).toString('hex');
const operator = randomBytes(32).toString('hex');
assert(reader, 'read credential must be provided for a live check');
let child, browser;
const checks = [], errors = [], requests = [];
const check = (name, condition) => { assert(condition, name); checks.push({ name, pass: true }); };
const report = { scope: live ? 'observational public HTTPS Chromium client from the target VM' : 'isolated local HTTP Chromium client and actual SQLite fixture', checks };
try {
  if (!live) {
    const script = `import json,os,pathlib,sys
from polyia.store import Ledger
from polyia.server import make_server
p=pathlib.Path(sys.argv[1]);w=p/'workspace';w.mkdir()
book=pathlib.Path('books/book-of-forms/BOOK.md').read_bytes()
(w/'BOOK.md').write_bytes(book)
(w/'hostile.txt').write_text('<script>window.__polyia_injected=1</script>\\n'+('A'*65535)+'é')
defs=json.loads(pathlib.Path('registry/constitution.json').read_text())['requirements']
l=Ledger(p/'state'/'ledger.sqlite3',w,defs)
l.command({'command_id':'browser-book','expected_revision':0,'kind':'requirement.produce','payload':{'requirement_id':'PIA-189','artifacts':['BOOK.md','hostile.txt']}})
s=make_server(l,token=os.environ['BROWSER_OPERATOR'],read_token=os.environ['BROWSER_READER'])
print('http://127.0.0.1:'+str(s.server_port),flush=True)
try:s.serve_forever(poll_interval=.01)
finally:s.server_close();l.close()
`;
    child = spawn(process.env.PYTHON || '/opt/polyia/runtime/bin/python3', ['-B', '-c', script, temp], {
      cwd: root, env: { ...process.env, BROWSER_OPERATOR: operator, BROWSER_READER: reader }, stdio: ['ignore', 'pipe', 'pipe'],
    });
    let diagnostics = '';
    child.stderr.on('data', data => { diagnostics += data.toString(); });
    origin = await new Promise((ok, fail) => {
      const timer = setTimeout(() => fail(new Error('fixture start timed out')), 15000);
      child.stdout.once('data', data => { clearTimeout(timer); ok(data.toString().trim()); });
      child.once('exit', code => { clearTimeout(timer); fail(new Error('fixture exited ' + code + ': ' + diagnostics.slice(-500))); });
    });
  }
  browser = await chromium.launch({ headless: true, chromiumSandbox: true });
  report.browser = browser.version(); report.origin = origin;
  const context = await browser.newContext({ viewport: { width: 1440, height: 1050 }, reducedMotion: 'reduce' });
  const page = await context.newPage();
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => requests.push(request.url()));
  await page.goto(origin, { waitUntil: 'networkidle' });
  await page.locator('#token').fill(reader);
  await page.locator('#connect-button').click();
  await page.waitForFunction(() => document.querySelector('#scope-display').textContent.includes('Read access only'));
  check('observer connected in real browser', await page.locator('#run-experiment').isDisabled());
  check('credential removed from input after connection', await page.locator('#token').inputValue() === '');
  await page.locator('#requirement-select').selectOption('PIA-189');
  await page.locator('#captured-artifacts button').first().click();
  await page.waitForFunction(() => document.querySelector('#artifact-status').textContent.includes('captured object'));
  check('captured book is actually inspectable', (await page.locator('#artifact-output').textContent()).includes('Book of Forms'));
  check('mission remains uncommissioned', /not.commissioned/i.test(await page.locator('#mission-status').textContent()));
  await page.locator('#overview').scrollIntoViewIfNeeded();
  await page.screenshot({ path: join(output, 'desktop.png') });
  await page.locator('#artifact-panel').scrollIntoViewIfNeeded();
  await page.screenshot({ path: join(output, 'captured-book.png') });
  if (!live) {
    await page.getByRole('button', { name: 'Inspect captured bytes of hostile.txt', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('#artifact-output').textContent.includes('<script>'));
    check('hostile captured HTML remains inert', await page.evaluate(() => window.__polyia_injected === undefined));
    check('large captured content is explicitly partial', (await page.locator('#artifact-status').textContent()).includes('Partial'));
    await page.locator('#artifact-next').click();
    await page.waitForFunction(() => document.querySelector('#artifact-status').textContent.includes('bytes [65536,'));
    check('next chunk uses real captured continuation', (await page.locator('#artifact-output').textContent()).endsWith('é'));
    await page.locator('#disconnect-button').click();
    check('disconnect clears captured bytes', await page.locator('#artifact-output').textContent() === '');
    await page.locator('#token').fill(operator);
    await page.locator('#connect-button').click();
    await page.waitForFunction(() => document.querySelector('#scope-display').textContent.includes('Operator'));
    await page.locator('#rasm-example').click();
    await page.locator('#run-experiment').click();
    await page.waitForFunction(() => document.querySelector('#runs-list').textContent.includes('rasm'));
    const state = await page.evaluate(async token => (await fetch('/v1/state', { headers: { Authorization: 'Bearer ' + token } })).json(), reader);
    check('rasm browser submission records actual fifteen-candidate result', state.runs.at(-1).report.result.inverse.candidate_total === 15);
    await page.locator('#intake-text').fill('Teach polynomial division\nUnrecognized <img src=x onerror=alert(1)>');
    await page.locator('#run-intake').click();
    await page.waitForFunction(() => document.querySelector('#intake-result').textContent.includes('Unrecognized'));
    check('unsupported source remains visible', (await page.locator('#intake-result').textContent()).includes('Unrecognized'));
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => scrollTo({ top: 0, behavior: 'instant' }));
  check('mobile page has no horizontal document overflow', await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.screenshot({ path: join(output, 'mobile.png') });
  await page.locator('#disconnect-button').click();
  check('session storage and local storage remain empty', await page.evaluate(() => localStorage.length === 0 && sessionStorage.length === 0));
  check('no credential in request URLs', requests.every(url => !url.includes(reader) && !url.includes(operator)));
  check('no browser script error', errors.length === 0);
  report.ok = true;
  report.limitations = ['One Chromium build on one VM; no cross-browser or accessibility certification.', 'Screenshots show observed rendering, not all possible UI states.'];
} catch (error) {
  report.ok = false; report.error = error.message.replaceAll(reader, '[redacted]').replaceAll(operator, '[redacted]');
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  if (child && child.exitCode === null) { child.kill('SIGTERM'); await new Promise(ok => child.once('exit', ok)); }
  await rm(temp, { recursive: true, force: true });
  await writeFile(join(output, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ ok: report.ok, checks: checks.length, output, error: report.error }));
}
