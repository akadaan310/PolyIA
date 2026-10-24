import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('complete corpus lookup preserves even a short verse and rejects invalid loci', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Trace the structure.' })).toBeVisible();
  await expect(page.getByTestId('addressable-count')).toHaveText('6,236');
  await page.getByLabel('Ayah locus').fill('20:1');
  await page.getByRole('button', { name: 'Open passage' }).click();
  await expect(page.getByTestId('source-locus')).toHaveText('20:1');
  await expect(page.getByTestId('source-text')).toContainText('طه');
  await page.getByLabel('Ayah locus').fill('115:1');
  await page.getByRole('button', { name: 'Open passage' }).click();
  await expect(page.getByRole('alert')).toContainText('No ayah');
  await expect(page.getByTestId('source-locus')).toHaveText('20:1');
});

test('source tokens connect to evidence and required examples are all addressable', async ({ page }) => {
  await page.goto('/');
  for (const locus of ['11:36', '50:2', '28:4–5', '11:29']) {
    await page.getByRole('button', { name: new RegExp(`Explore ${locus}`) }).click();
    await expect(page.getByTestId('source-locus')).toHaveText(locus);
    await expect(page.getByTestId('path-description')).toBeVisible();
  }
  await page.getByTestId('source-text').getByRole('button').nth(2).click();
  await expect(page.getByTestId('span-detail')).toContainText(/source span/i);
  await expect(page.getByTestId('span-detail')).toContainText('UNIT 03');
  await expect(page.getByTestId('uncertainty-panel')).toContainText('speaker');
});

test('nested dialogue retains timestamps through perturbation and portable export', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Your own dialogue' }).click();
  await page.getByLabel('Dialogue turns (JSON)').fill(JSON.stringify([
    { speaker: 'Mira', text: 'I said, “He replied, ‘Stay.’”', timestamp: { start: 1.25, end: 4.5, original: '00:01.250', uncertainty: 0.1, unit: 'seconds' } },
    { speaker: 'Noor', text: 'We will wait.', timestamp: { start: 4.7, original: '00:04.700', unit: 'seconds' } },
  ]));
  await page.getByRole('button', { name: 'Analyze dialogue' }).click();
  await expect(page.getByTestId('analysis-label')).toContainText('Your dialogue');
  await expect(page.getByTestId('frame-count')).not.toHaveText('0');
  await page.getByLabel('Perturbation').selectOption('mask-speakers');
  await page.getByRole('button', { name: 'Run comparison' }).click();
  await expect(page.getByTestId('comparison-result')).toContainText('Mask speakers');
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export JSON' }).click();
  const artifact = await download;
  expect(artifact.suggestedFilename()).toMatch(/snad.*\.json$/);
  const stream = await artifact.createReadStream();
  const chunks: Buffer[] = [];
  for await (const chunk of stream!) chunks.push(Buffer.from(chunk));
  const data = JSON.parse(Buffer.concat(chunks).toString());
  expect(data.analysis.input.units[0].timestamp.original).toBe('00:01.250');
  expect(data.analysis.frames.length).toBeGreaterThan(1);
  expect(data.comparison.perturbation.kind).toBe('mask-speakers');
});

test('desk and dialogue are accessible with no serious or critical axe findings', async ({ page }) => {
  await page.goto('/');
  let results = await new AxeBuilder({ page }).analyze();
  expect(results.violations.filter(v => ['serious', 'critical'].includes(v.impact ?? ''))).toEqual([]);
  await page.getByRole('button', { name: 'Your own dialogue' }).click();
  results = await new AxeBuilder({ page }).analyze();
  expect(results.violations.filter(v => ['serious', 'critical'].includes(v.impact ?? ''))).toEqual([]);
});

test('mobile view keeps the source and controls within the viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await expect(page.getByTestId('source-text')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
});

test('switching to dialogue immediately exports matching source provenance', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Your own dialogue' }).click();
  await expect(page.getByTestId('analysis-label')).toContainText('Your dialogue');
  const pending = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export JSON' }).click();
  const artifact = await pending;
  const stream = await artifact.createReadStream();
  const chunks: Buffer[] = [];
  for await (const chunk of stream!) chunks.push(Buffer.from(chunk));
  const data = JSON.parse(Buffer.concat(chunks).toString());
  expect(data.analysis.input.source.kind).toBe('user-supplied');
  expect(data.analysis.input.units[0].text).toContain('I said');
  expect(data.sourceProvenance.source).toBe('user-supplied');
});
