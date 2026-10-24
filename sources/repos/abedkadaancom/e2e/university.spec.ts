import { test, expect, type Page, type ConsoleMessage } from '@playwright/test';
import { mkdirSync, readFileSync } from 'node:fs';

const SHOTS = 'docs/screenshots';
mkdirSync(SHOTS, { recursive: true });

/** Collect console errors and page errors; GL driver performance notes are warnings, not errors. */
function watch(page: Page) {
  const errors: string[] = [];
  page.on('console', (m: ConsoleMessage) => {
    if (m.type() === 'error') errors.push(`${m.text()} @ ${m.location().url}`);
  });
  page.on('pageerror', (e) => errors.push(`pageerror: ${e.message}`));
  return errors;
}

async function shot(page: Page, name: string) {
  await page.screenshot({ path: `${SHOTS}/${test.info().project.name}-${name}.png` });
}

/** The CGT book is proxied from its own deployment in production; tests stub it so they stay offline. */
async function stubBook(page: Page) {
  await page.route('**/cgt/**', (r) => r.fulfill({ status: 200, contentType: 'text/html', body: '<!doctype html><title>CGT (test stub)</title><p>stub</p>' }));
}

async function settle(page: Page, ms = 3500) {
  await page.waitForTimeout(ms);
}

async function skipIntro(page: Page) {
  const skip = page.getByRole('button', { name: 'Skip intro' });
  if (await skip.isVisible().catch(() => false)) await skip.click();
}

test('first impression: approach, controls immediately, welcome', async ({ page }) => {
  const errors = watch(page);
  const t0 = Date.now();
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Skip intro' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Enter the Gate' })).toBeVisible();
  expect(Date.now() - t0).toBeLessThan(8000);
  await expect(page.getByText(/what is one plus one/)).toBeVisible();
  await expect(page.locator('[data-testid="campus-canvas"]')).toBeAttached({ timeout: 30_000 });
  await settle(page, 2500);
  await shot(page, '01-approach');
  await settle(page, 5000);
  await shot(page, '02-approach-arrived');
  await skipIntro(page);
  await expect(page.getByRole('heading', { name: 'Substrate University — Haq Roots' })).toBeVisible();
  await expect(page.getByRole('link', { name: /The Door of Transitions/ })).toBeVisible();
  expect(errors).toEqual([]);
});

test('the arithmetic gate opens the first door by demonstration', async ({ page }) => {
  const errors = watch(page);
  await page.goto('/gate');
  await expect(page.getByRole('heading', { name: 'The Arithmetic of Possibility' })).toBeVisible();
  await page.getByLabel(/F₂ — The two-element field/).check();
  await page.getByLabel('In F₂, 1 + 1 =').fill('1');
  await expect(page.getByText(/In F₂ your answer is the element 1, but 1 \+ 1 = 0/)).toBeVisible();
  await page.getByLabel('In F₂, 1 + 1 =').fill('2');
  await expect(page.getByText(/“2” is not an element of F₂ as written; read modulo 2, it is 0/)).toBeVisible();
  await page.getByLabel('In F₂, 1 + 1 =').fill('0');
  await expect(page.getByText('Yes: in F₂, 1 + 1 = 0.')).toBeVisible();
  await page.getByRole('button', { name: 'Next: zero, one and division' }).click();
  await expect(page.getByText('0 / 1 in F₂')).toBeVisible();
  await expect(page.getByText(/no solution \(image failure\)/)).toBeVisible();
  await expect(page.getByText(/no unique solution \(kernel failure\)/)).toBeVisible();
  await expect(page.getByText(/not definitions of field division/)).toBeVisible();
  await shot(page, '03-gate-division');
  await page.getByRole('button', { name: 'Next: transform something' }).click();
  await page.getByRole('button', { name: 'Collapse to a line' }).click();
  await page.getByRole('button', { name: 'Apply the transformation' }).click();
  await page.getByLabel('everything').check();
  await expect(page.getByText(/Not quite: what survives is a line/)).toBeVisible();
  await page.getByLabel('a line').check();
  await expect(page.getByText(/Exactly\. rank A = 1, dim ker A = 1/)).toBeVisible();
  await page.getByRole('button', { name: /open the first door/ }).click();
  await expect(page).toHaveURL(/\/divisions\/foundations$/);
  const st = await page.evaluate(() => JSON.parse(localStorage.getItem('substrate-university.v1')!).world);
  expect(st.gate.doorOpened).toBe(true);
  expect(st.sculpture).toEqual([[1, 2], [2, 4]]);
  await settle(page);
  await shot(page, '04-first-door-realm');
  expect(errors).toEqual([]);
});

const DIVS = ['foundations', 'relational', 'languages', 'geometry', 'acoustic', 'worlds'];

test('all six realms open with real content and a computing exhibit', async ({ page }) => {
  const errors = watch(page);
  for (const id of DIVS) {
    await page.goto(`/divisions/${id}`);
    await expect(page.getByRole('heading', { name: /Signature exhibit/ })).toBeVisible();
    await expect(page.locator('ol.path li')).toHaveCount(await page.locator('ol.path li').count());
    expect(await page.locator('ol.path li').count()).toBeGreaterThanOrEqual(8);
    await expect(page.locator('.math-block').first()).toBeVisible();
    await settle(page, 2500);
    await shot(page, `05-realm-${id}`);
  }
  await page.goto('/divisions/relational/plicastratum');
  await expect(page.getByText('House construction').first()).toBeVisible();
  await expect(page.getByText(/unfold check: unfold\(fold\(w\)\) = w ✓/)).toBeVisible();
  expect(errors).toEqual([]);
});

test('bridges change only where the typed predicate passes', async ({ page }) => {
  await page.goto('/divisions/foundations');
  await page.getByLabel('from').selectOption('F');
  await page.getByLabel('to').selectOption('F');
  await expect(page.getByRole('button', { name: 'Refused by the predicate' })).toBeDisabled();
  await page.getByLabel('from').selectOption('P');
  await page.getByLabel('to').selectOption('A');
  await page.getByRole('button', { name: 'Apply (predicate passes)' }).click();
  await page.getByLabel('Walk (door letters)').fill('RPA');
  await expect(page.getByText(/Realizable but not admissible/)).toBeVisible();
  const bridges = await page.evaluate(() => JSON.parse(localStorage.getItem('substrate-university.v1')!).world.bridges.length);
  expect(bridges).toBe(7);
});

test('observatory: offline fallback, real sky day and night, path correspondence, portal', async ({ page }) => {
  const errors = watch(page);
  await page.route('https://nominatim.openstreetmap.org/**', (r) => r.abort());
  await page.goto('/observatory');
  await expect(page.getByRole('heading', { name: 'The Observatory' })).toBeVisible();
  await page.getByLabel('Place or address').fill('Greenwich Park, London');
  await page.getByRole('button', { name: /Find \(one request to Nominatim\)/ }).click();
  await expect(page.getByText(/geocoder is unavailable; the offline samples and coordinates still work/)).toBeVisible();
  await page.getByRole('button', { name: 'Maunakea summit' }).click();
  await expect(page.locator('strong', { hasText: 'Maunakea summit (offline sample)' })).toBeVisible();
  await page.getByLabel(/^Moment/).fill('2026-06-21T10:00');
  const cond = page.locator('p[aria-live="polite"] strong').first();
  const c1 = await cond.innerText();
  await page.getByRole('button', { name: '+12 hours' }).click();
  const c2 = await cond.innerText();
  expect([c1, c2].sort()).toEqual(['day', 'night']);
  await expect(page.getByRole('img', { name: /All-sky chart/ })).toBeVisible();
  await page.getByLabel('Source path').selectOption('fx-zigzag');
  const row = page.locator('tr', { hasText: 'Fixture B' });
  await expect(row).toContainText('exact');
  await expect(row).toContainText('100%');
  await row.click();
  await page.getByLabel('braid').check();
  await page.getByRole('button', { name: /Open a fictional portal \(braid\)/ }).click();
  const portal = await page.evaluate(() => JSON.parse(localStorage.getItem('substrate-university.v1')!).world.portal);
  expect(portal.similarity).toBe(1);
  await page.mouse.wheel(0, 0);
  await shot(page, '06-observatory');
  await page.goto('/observatory/sky');
  await settle(page, 4000);
  await shot(page, '07-observatory-sky');
  // The only tolerated error is the browser's log line for the geocoder outage this test simulates.
  expect(errors.filter((e) => !e.includes('nominatim.openstreetmap.org'))).toEqual([]);
});

test('one complete harness journey produces six books and a real PDF', async ({ page }) => {
  test.setTimeout(420_000);
  const errors = watch(page);
  await page.goto('/harness');
  await page.getByLabel('Display name (as it will appear on your books)').fill('Test Harnesser');
  await page.getByLabel('Your intellectual interest (the harness begins there)').selectOption('geometry');
  await page.getByRole('button', { name: 'Enter the harness' }).click();
  await page.getByRole('link', { name: 'IV. Geometry, Physics, and Representation' }).click();
  for (let i = 0; i < 6; i++) {
    await expect(page.getByRole('heading', { name: /^Reading/ })).toBeVisible();
    if (i !== 4) await page.locator('section').getByRole('button', { name: /record/i }).first().click();
    await page.locator('#refl').fill(`Reflection ${i + 1}: the kernel is what the map forgets.`);
    await page.getByRole('button', { name: /Complete this station/ }).click();
  }
  await expect(page.getByRole('heading', { name: 'Your One-Day Harness' })).toBeVisible();
  await page.getByLabel('Your contribution').fill('A shadow is a projection whose kernel is the direction of the light.');
  await page.getByRole('button', { name: 'Complete the harness and go to the Scriptorium' }).click();
  await expect(page.getByRole('heading', { name: 'Your six volumes' })).toBeVisible();
  await expect(page.locator('.card .t')).toHaveCount(6);
  const titles = await page.locator('.card .t').allInnerTexts();
  expect(new Set(titles).size).toBe(6);
  await settle(page, 2000);
  await shot(page, '08-scriptorium');
  await page.getByRole('link', { name: 'Read' }).first().click();
  await expect(page.locator('.reader .cover')).toContainText('Test Harnesser');
  await expect(page.getByText(/What You Did, What Was Sourced, What Was Computed/)).toBeVisible();
  await shot(page, '09-book-reader');
  const [dl] = await Promise.all([page.waitForEvent('download'), page.getByRole('button', { name: 'Download PDF' }).click()]);
  const path = await dl.path();
  const bytes = readFileSync(path!);
  expect(bytes.subarray(0, 5).toString()).toBe('%PDF-');
  expect(bytes.length).toBeGreaterThan(30_000);
  expect(dl.suggestedFilename()).toMatch(/\.pdf$/);
  expect(errors).toEqual([]);
});

test('library: founding book reader, specimens labelled, no invented counts', async ({ page }) => {
  await stubBook(page);
  const errors = watch(page);
  await page.goto('/library');
  await expect(page.getByText(/No participant books are listed, and no counts are shown/)).toBeVisible();
  await settle(page);
  await shot(page, '10-library');
  await page.getByRole('link', { name: /Computational Grammar Theory/ }).first().click();
  await expect(page).toHaveURL(/computational-grammar-theory$/);
  await expect(page.getByText('Arrays: Addresses You Can Compute')).toBeVisible();
  await expect(page.locator('iframe[title*="Computational Grammar Theory"]')).toBeAttached();
  await page.goto('/library');
  await page.locator('a.card', { hasText: 'Specimen Volume / Preview' }).first().click();
  await expect(page.getByText(/This volume was generated by the Library/)).toBeVisible();
  expect(errors).toEqual([]);
});

test('every route loads its scene directly, without the intro', async ({ page }) => {
  await stubBook(page);
  const errors = watch(page);
  const paths = ['/atrium', '/library', '/observatory', '/harness-masters', '/harness', '/scriptorium', '/common-room', '/glossary', '/glossary/image', '/about', '/divisions/geometry/imagistratum', '/library/computational-grammar-theory'];
  for (const p of paths) {
    await page.goto(p);
    await expect(page.getByRole('button', { name: 'Skip intro' })).toHaveCount(0);
    await expect(page.locator('main#content h1')).toBeVisible();
    await expect(page.getByText('No such place on campus')).toHaveCount(0);
  }
  await page.goto('/glossary/image');
  await expect(page.getByText('Everyday usage')).toBeVisible();
  await expect(page.getByText(/rank P = 3/)).toBeVisible();
  await settle(page);
  await shot(page, '11-glossary-image');
  await page.goto('/harness-masters');
  await expect(page.getByText(/This produces a request, not a confirmed booking/)).toBeVisible();
  await shot(page, '12-harness-masters');
  await page.goto('/no/such/place');
  await expect(page.getByText('No such place on campus')).toBeVisible();
  expect(errors).toEqual([]);
});

test('keyboard navigation and accessible controls', async ({ page }, info) => {
  test.skip(info.project.name === 'android', 'hardware keyboard test runs on desktop');
  await page.goto('/gate');
  await page.keyboard.press('Escape');
  await page.locator('body').click({ position: { x: 5, y: 500 } });
  await page.keyboard.press(']');
  await expect(page).toHaveURL(/\/atrium$/);
  await page.keyboard.press('4');
  await expect(page).toHaveURL(/\/divisions\/geometry$/);
  await page.keyboard.press('m');
  await expect(page.getByRole('dialog', { name: 'Campus map' })).toBeVisible();
  await page.keyboard.press('Escape');
  await page.keyboard.press('Tab');
  const focused = await page.evaluate(() => document.activeElement?.textContent ?? '');
  expect(focused.length).toBeGreaterThan(0);
});

test('works without WebGL and in text-only mode', async ({ browser }) => {
  const ctx = await browser.newContext();
  await ctx.addInitScript(() => {
    const orig = HTMLCanvasElement.prototype.getContext;
    // @ts-expect-error test override
    HTMLCanvasElement.prototype.getContext = function (type: string, ...rest: unknown[]) {
      if (type === 'webgl' || type === 'webgl2' || type === 'experimental-webgl') return null;
      // @ts-expect-error passthrough
      return orig.call(this, type, ...rest);
    };
  });
  const page = await ctx.newPage();
  const errors = watch(page);
  await page.goto('/divisions/acoustic');
  await expect(page.locator('body.no-webgl')).toBeAttached();
  await expect(page.locator('[data-testid="campus-canvas"]')).toHaveCount(0);
  await page.getByLabel(/Interval k/).fill('4');
  await expect(page.getByText(/\|⟨4⟩\| = 3/)).toBeVisible();
  await shot(page, '13-no-webgl-fallback');
  expect(errors).toEqual([]);
  await ctx.close();
});
