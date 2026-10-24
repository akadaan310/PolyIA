import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { PDFDocument } from 'pdf-lib';
import { composeBooks, bookPlainText, PRIVATE_NAME } from '../src/books/compose';
import { bookToPdf } from '../src/books/pdf';
import { defaultHarness, type HarnessState } from '../src/state/store';
import { bridgeRecord, foldRecord, imageRecord, loomRecord, addressRecord } from '../src/exhibits/records';
import { INITIAL_BRIDGES } from '../src/math/bridgeGrammar';

const at = '2026-10-21T10:00:00.000Z';
function journey(name: string | null): HarnessState {
  const h = defaultHarness();
  return {
    ...h,
    runId: 'run-test-1',
    startedAt: at,
    displayName: name,
    interest: 'geometry',
    stations: {
      foundations: { division: 'foundations', topicId: 'operational-grammar', enteredAt: at, exercise: { ...bridgeRecord('FRPGA', INITIAL_BRIDGES), at }, reflection: 'A walk can be allowed by the rules and still impossible on the ground.', completedAt: at },
      relational: { division: 'relational', topicId: 'plicastratum', enteredAt: at, exercise: { ...foldRecord('NENENESS', 4), at }, reflection: 'Folding moved the path into the rules.', completedAt: at },
      languages: { division: 'languages', topicId: 'matrix-loom', enteredAt: at, exercise: { ...addressRecord('loom://plate/START/SCALE:2/SHEAR:1/COMMIT'), at }, reflection: '', completedAt: at },
      geometry: { division: 'geometry', topicId: 'image-kernel', enteredAt: at, exercise: { ...imageRecord([[1, 0, 0], [0, 1, 0], [0, 0, 0]], [1, 2, 0]), at }, reflection: 'The floor keeps two dimensions; height is the kernel.', completedAt: at },
      acoustic: { division: 'acoustic', topicId: 'interval-geometry', enteredAt: at, exercise: null, reflection: '', completedAt: at },
      worlds: { division: 'worlds', topicId: 'borne', enteredAt: at, exercise: { ...loomRecord(30, 'road'), at }, reflection: 'Remove the road and the night route goes dark.', completedAt: at },
    },
    contribution: { kind: 'example', term: 'kernel', text: 'A shadow is a projection whose kernel is the light direction.', at },
    completedAt: at,
  };
}

describe('Scriptorium', () => {
  const books = composeBooks({ harness: journey('Ada Example'), now: at });

  it('produces six distinct books, one per division, credited to the chosen name', () => {
    expect(books).toHaveLength(6);
    expect(new Set(books.map((b) => b.division)).size).toBe(6);
    expect(new Set(books.map((b) => b.id)).size).toBe(6);
    expect(new Set(books.map((b) => b.title + b.subtitle)).size).toBe(6);
    for (const b of books) expect(b.author).toBe('Ada Example');
    const texts = books.map(bookPlainText);
    expect(new Set(texts).size).toBe(6);
    for (const t of texts) expect(t.length).toBeGreaterThan(3000);
  });

  it('is deterministic and regenerable', () => {
    const again = composeBooks({ harness: journey('Ada Example'), now: at });
    expect(again.map((b) => b.title)).toEqual(books.map((b) => b.title));
    const ed2 = composeBooks({ harness: { ...journey('Ada Example'), edition: 2 }, now: at });
    expect(ed2.map((b) => b.id)).not.toEqual(books.map((b) => b.id));
  });

  it('quotes the participant verbatim and states encounter depth honestly', () => {
    const f = books.find((b) => b.division === 'foundations')!;
    expect(bookPlainText(f)).toContain('A walk can be allowed by the rules and still impossible on the ground.');
    const a = books.find((b) => b.division === 'acoustic')!;
    expect(a.depth).toBe('visited');
    expect(bookPlainText(a)).toMatch(/computed by the Scriptorium on standard inputs/);
    expect(bookPlainText(a)).toMatch(/encounter, not mastery/);
    const g = books.find((b) => b.division === 'geometry')!;
    expect(bookPlainText(g)).toContain('A shadow is a projection whose kernel is the light direction.');
    expect(bookPlainText(g)).toMatch(/A·k = \(0, 0, 0\) = 0 ✓/);
  });

  it('carries a transparency chapter, glossary, bibliography and plate', () => {
    for (const b of books) {
      expect(b.chapters.map((c) => c.id)).toContain('transparency');
      expect(b.ledger.participant.length).toBeGreaterThan(0);
      expect(b.ledger.generated.join(' ')).toMatch(/No AI model/);
      expect(b.glossary.length).toBeGreaterThan(1);
      expect(b.bibliography.length).toBeGreaterThan(0);
      expect(b.plate.prims.length).toBeGreaterThan(3);
      expect(b.chapters.find((c) => c.id === 'derivation')!.blocks.some((x) => x.k === 'eq')).toBe(true);
    }
  });

  it('honours anonymity', () => {
    const anon = composeBooks({ harness: journey(null), now: at });
    for (const b of anon) {
      expect(b.author).toBe(PRIVATE_NAME);
      expect(b.isPrivate).toBe(true);
    }
  });

  it('exports real PDFs with embedded fonts and metadata', async () => {
    const fonts = {
      serif: readFileSync('public/fonts/pdf/DejaVuSerif.ttf'),
      serifBold: readFileSync('public/fonts/pdf/DejaVuSerif-Bold.ttf'),
      sans: readFileSync('public/fonts/pdf/DejaVuSans.ttf'),
      mono: readFileSync('public/fonts/pdf/DejaVuSansMono.ttf'),
    };
    for (const b of books.slice(0, 6)) {
      const bytes = await bookToPdf(b, fonts);
      expect(new TextDecoder().decode(bytes.slice(0, 5))).toBe('%PDF-');
      const doc = await PDFDocument.load(bytes);
      expect(doc.getPageCount()).toBeGreaterThanOrEqual(10);
      expect(doc.getAuthor()).toBe('Ada Example');
      expect(doc.getTitle()).toContain(b.title);
      expect(doc.getSubject()).toContain(b.id);
    }
  }, 60_000);
});
