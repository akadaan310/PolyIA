import { chromium } from '@playwright/test';
const out = process.argv[2];
const base = 'http://localhost:4173';
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();
const errors = [];
page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errors.push(`${m.type()}: ${m.text()}`); });
page.on('request', (r) => { if (!r.url().startsWith(base) && !r.url().startsWith('data:') && !r.url().startsWith('blob:')) errors.push('EXTERNAL ' + r.url()); });
page.on('pageerror', (e) => errors.push(`pageerror: ${e.message}`));
await page.goto(base + '/', { waitUntil: 'load' });
await page.waitForTimeout(2500);
await page.screenshot({ path: `${out}/01-approach-early.png` });
await page.waitForTimeout(6000);
await page.screenshot({ path: `${out}/02-approach-end.png` });
for (const [i, p] of ['/gate', '/atrium', '/divisions/geometry', '/library', '/observatory'].entries()) {
  await page.goto(base + p, { waitUntil: 'load' });
  await page.waitForTimeout(5000);
  await page.screenshot({ path: `${out}/1${i}-${p.replace(/\//g, '_')}.png` });
}
console.log(errors.slice(0, 40).join('\n'));
await browser.close();
