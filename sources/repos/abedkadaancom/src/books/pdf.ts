// Real downloadable PDFs, generated in the browser with pdf-lib 1.17.1 and
// @pdf-lib/fontkit. Fonts: DejaVu Serif / Sans / Sans Mono (Bitstream Vera
// licence, redistribution permitted), embedded and subset. Text is wrapped with
// real font metrics; characters missing from one font fall back to the next.

import { PDFDocument, rgb, type PDFFont, type PDFPage, type RGB } from 'pdf-lib';
import fontkit from '@pdf-lib/fontkit';
import type { Block, Book } from './compose';
import { ROMAN } from './compose';
import type { Ink, Plate } from './plates';

export interface FontBytes {
  serif: Uint8Array | ArrayBuffer;
  serifBold: Uint8Array | ArrayBuffer;
  sans: Uint8Array | ArrayBuffer;
  mono: Uint8Array | ArrayBuffer;
}

export const FONT_URLS = {
  serif: '/fonts/pdf/DejaVuSerif.ttf',
  serifBold: '/fonts/pdf/DejaVuSerif-Bold.ttf',
  sans: '/fonts/pdf/DejaVuSans.ttf',
  mono: '/fonts/pdf/DejaVuSansMono.ttf',
};

export async function fetchFonts(): Promise<FontBytes> {
  const get = async (u: string) => new Uint8Array(await (await fetch(u)).arrayBuffer());
  const [serif, serifBold, sans, mono] = await Promise.all([get(FONT_URLS.serif), get(FONT_URLS.serifBold), get(FONT_URLS.sans), get(FONT_URLS.mono)]);
  return { serif, serifBold, sans, mono };
}

const W = 420; // A5 in points
const H = 595;
const M = 46;
const OBSIDIAN = rgb(0.039, 0.039, 0.039);
const GOLD = rgb(0.84, 0.675, 0.384);
const GOLD_DEEP = rgb(0.6, 0.45, 0.2);
const INK = rgb(0.1, 0.1, 0.1);
const MUTED = rgb(0.42, 0.4, 0.38);
const CRIMSON = rgb(0.553, 0.137, 0.173);
const IVORY = rgb(0.957, 0.922, 0.863);
const INKS: Record<Ink, RGB> = { gold: GOLD_DEEP, ink: INK, crimson: CRIMSON, faint: rgb(0.65, 0.63, 0.6) };

interface Fonts {
  serif: PDFFont;
  bold: PDFFont;
  sans: PDFFont;
  mono: PDFFont;
  sets: Map<PDFFont, Set<number>>;
}

class Writer {
  page!: PDFPage;
  y = 0;
  pageNo = 0;
  constructor(
    readonly doc: PDFDocument,
    readonly f: Fonts,
    readonly running: string,
  ) {}

  newPage() {
    this.page = this.doc.addPage([W, H]);
    this.pageNo++;
    this.y = H - M;
    if (this.pageNo > 1) {
      this.text(this.running, M, H - 28, 7, this.f.sans, MUTED);
      this.text(String(this.pageNo), W - M - 10, 26, 8, this.f.sans, MUTED);
    }
  }

  /** Split a string into runs, each drawable in one font (serif → sans → mono fallback). */
  runs(s: string, primary: PDFFont): { t: string; font: PDFFont }[] {
    const order = [primary, this.f.sans, this.f.mono, this.f.serif];
    const out: { t: string; font: PDFFont }[] = [];
    for (const raw of s) {
      const ch = SUBSTITUTE[raw] ?? raw;
      const cp = ch.codePointAt(0)!;
      const font = order.find((fo) => this.f.sets.get(fo)!.has(cp)) ?? null;
      const glyph = font ? ch : '?';
      const use = font ?? primary;
      const last = out[out.length - 1];
      if (last && last.font === use) last.t += glyph;
      else out.push({ t: glyph, font: use });
    }
    return out;
  }

  width(s: string, size: number, font: PDFFont): number {
    return this.runs(s, font).reduce((w, r) => w + r.font.widthOfTextAtSize(r.t, size), 0);
  }

  text(s: string, x: number, y: number, size: number, font: PDFFont, color: RGB) {
    let cx = x;
    for (const r of this.runs(s, font)) {
      this.page.drawText(r.t, { x: cx, y, size, font: r.font, color });
      cx += r.font.widthOfTextAtSize(r.t, size);
    }
  }

  wrap(s: string, size: number, font: PDFFont, maxW: number): string[] {
    const lines: string[] = [];
    for (const paragraph of s.split('\n')) {
      let line = '';
      for (const word of paragraph.split(/\s+/).filter(Boolean)) {
        const trial = line ? `${line} ${word}` : word;
        if (this.width(trial, size, font) <= maxW) line = trial;
        else {
          if (line) lines.push(line);
          // break very long tokens
          let w = word;
          while (this.width(w, size, font) > maxW && w.length > 1) {
            let cut = w.length - 1;
            while (cut > 1 && this.width(w.slice(0, cut), size, font) > maxW) cut--;
            lines.push(w.slice(0, cut));
            w = w.slice(cut);
          }
          line = w;
        }
      }
      lines.push(line);
    }
    return lines;
  }

  ensure(h: number) {
    if (this.y - h < M + 10) this.newPage();
  }

  para(s: string, opts: { size?: number; font?: PDFFont; color?: RGB; indent?: number; leading?: number; after?: number } = {}) {
    const size = opts.size ?? 9.5;
    const font = opts.font ?? this.f.serif;
    const lead = opts.leading ?? size * 1.42;
    const indent = opts.indent ?? 0;
    for (const line of this.wrap(s, size, font, W - 2 * M - indent)) {
      this.ensure(lead);
      this.y -= lead;
      this.text(line, M + indent, this.y, size, font, opts.color ?? INK);
    }
    this.y -= opts.after ?? 5;
  }
}

function drawPlate(w: Writer, plate: Plate) {
  const box = W - 2 * M;
  w.ensure(box + 40);
  w.y -= 14;
  w.text(plate.title, M, w.y, 10, w.f.bold, INK);
  w.y -= 8;
  const top = w.y;
  const X = (x: number) => M + x * box;
  const Y = (y: number) => top - y * box;
  w.page.drawRectangle({ x: M, y: top - box, width: box, height: box, color: IVORY, borderColor: GOLD_DEEP, borderWidth: 0.6 });
  for (const p of plate.prims) {
    const c = INKS[p.ink];
    if (p.t === 'line') w.page.drawLine({ start: { x: X(p.x1), y: Y(p.y1) }, end: { x: X(p.x2), y: Y(p.y2) }, thickness: (p.w ?? 1) * 0.8, color: c });
    else if (p.t === 'circle') w.page.drawCircle({ x: X(p.cx), y: Y(p.cy), size: p.r * box, borderColor: c, borderWidth: 0.7, ...(p.fill ? { color: c } : {}) });
    else if (p.t === 'rect') w.page.drawRectangle({ x: X(p.x), y: Y(p.y + p.h), width: p.w * box, height: p.h * box, ...(p.fill ? { color: c } : { borderColor: c, borderWidth: 0.6 }) });
    else if (p.t === 'poly' && p.pts.length > 1) {
      const d = p.pts.map(([x, y], i) => `${i ? 'L' : 'M'}${(x * box).toFixed(2)} ${(y * box).toFixed(2)}`).join(' ') + (p.closed ? ' Z' : '');
      w.page.drawSvgPath(d, { x: M, y: top, borderColor: c, borderWidth: 0.9, ...(p.fill ? { color: c, opacity: 0.25, borderOpacity: 1 } : {}) });
    } else if (p.t === 'text') {
      const size = (p.size ?? 9) * 0.8;
      const tw = w.width(p.text, size, w.f.sans);
      const x = p.anchor === 'middle' ? X(p.x) - tw / 2 : p.anchor === 'end' ? X(p.x) - tw : X(p.x);
      w.text(p.text, x, Y(p.y), size, w.f.sans, c);
    }
  }
  w.y = top - box - 6;
}

/** Characters absent from every embedded font, written with their nearest covered equivalent. */
const SUBSTITUTE: Record<string, string> = { '𝔄': 'A', '𝒞': 'C', '⟲': '↺' };

const BY_LABEL: Record<string, string> = { participant: 'BY YOU', computed: 'COMPUTED', sourced: 'SOURCED', generated: 'GENERATED' };

function block(w: Writer, b: Block) {
  switch (b.k) {
    case 'p':
      w.para(b.text);
      break;
    case 'h':
      w.ensure(22);
      w.y -= 16;
      w.text(b.text.toUpperCase(), M, w.y, 8, w.f.sans, GOLD_DEEP);
      w.y -= 4;
      break;
    case 'eq': {
      w.y -= 2;
      for (const line of b.lines) w.para(line, { font: w.f.mono, size: 7.6, leading: 11, indent: 10, after: 0, color: rgb(0.15, 0.13, 0.1) });
      w.ensure(10);
      w.y -= 3;
      w.text(BY_LABEL[b.by]!, M + 10, w.y - 6, 6, w.f.sans, MUTED);
      w.y -= 14;
      break;
    }
    case 'quote':
      w.para(`“${b.text}”`, { indent: 14, size: 10, color: rgb(0.2, 0.12, 0.08), after: 1 });
      w.para(`— ${b.who}`, { indent: 14, size: 8, font: w.f.sans, color: MUTED });
      break;
    case 'list':
      for (const it of b.items) w.para(`•  ${it}`, { indent: 8, size: 9, after: 2 });
      w.y -= 3;
      break;
    case 'def':
      w.para(`${b.term}`, { font: w.f.bold, size: 9.5, after: 0 });
      w.para(b.status, { font: w.f.sans, size: 6.5, color: GOLD_DEEP, after: 1 });
      w.para(b.text, { indent: 8 });
      break;
  }
}

export async function bookToPdf(book: Book, fontBytes: FontBytes, origin = 'https://abedkadaan.com'): Promise<Uint8Array> {
  const doc = await PDFDocument.create();
  doc.registerFontkit(fontkit);
  const [serif, bold, sans, mono] = await Promise.all([
    doc.embedFont(fontBytes.serif, { subset: true }),
    doc.embedFont(fontBytes.serifBold, { subset: true }),
    doc.embedFont(fontBytes.sans, { subset: true }),
    doc.embedFont(fontBytes.mono, { subset: true }),
  ]);
  const sets = new Map<PDFFont, Set<number>>([serif, bold, sans, mono].map((f) => [f, new Set(f.getCharacterSet())]));
  const f: Fonts = { serif, bold, sans, mono, sets };

  doc.setTitle(`${book.title} — ${book.subtitle}`);
  doc.setAuthor(book.author);
  doc.setSubject(`Substrate University — Haq Roots · ${book.divisionName} · One-Day Harness volume · id ${book.id} · edition ${book.edition}`);
  doc.setKeywords(['Substrate University', 'Haq Roots', book.divisionName, book.id, `depth:${book.depth}`]);
  doc.setCreator(book.credits.generatedBy);
  doc.setProducer('pdf-lib 1.17.1 in the visitor’s browser');
  doc.setCreationDate(new Date(book.createdAt));

  const w = new Writer(doc, f, `${book.title} · ${book.author}`);

  // Cover
  w.newPage();
  w.page.drawRectangle({ x: 0, y: 0, width: W, height: H, color: OBSIDIAN });
  w.page.drawRectangle({ x: 22, y: 22, width: W - 44, height: H - 44, borderColor: GOLD, borderWidth: 0.8 });
  w.page.drawRectangle({ x: 28, y: 28, width: W - 56, height: H - 56, borderColor: GOLD_DEEP, borderWidth: 0.4 });
  const center = (s: string, y: number, size: number, font: PDFFont, color: RGB) => w.text(s, (W - w.width(s, size, font)) / 2, y, size, font, color);
  center('SUBSTRATE UNIVERSITY', H - 90, 10, sans, GOLD);
  center('HAQ ROOTS', H - 104, 7, sans, GOLD_DEEP);
  center(`DIVISION ${book.numeral}`, H - 170, 8, sans, GOLD_DEEP);
  let y = H - 210;
  for (const line of w.wrap(book.title, 22, bold, W - 110)) {
    center(line, y, 22, bold, IVORY);
    y -= 28;
  }
  for (const line of w.wrap(book.subtitle, 10, serif, W - 120)) {
    center(line, y - 4, 10, serif, GOLD);
    y -= 15;
  }
  center(book.author, 150, 13, serif, IVORY);
  center(`edition ${book.edition} · ${book.createdAt.slice(0, 10)} · ${book.id}`, 110, 7, mono, GOLD_DEEP);
  center('A One-Day Harness volume. Not a degree or credential.', 92, 7, sans, rgb(0.6, 0.55, 0.48));

  // Credits page
  w.newPage();
  w.y -= 20;
  w.para('Credits', { font: bold, size: 13, after: 8 });
  w.para(book.credits.participant);
  if (book.credits.foundingWorks.length) {
    w.para('Founding works cited (credited to their actual authors):', { font: sans, size: 8.5, color: MUTED, after: 2 });
    for (const fw of book.credits.foundingWorks) w.para(`•  ${fw}`, { indent: 8, size: 9 });
  }
  w.para(`Generated educational material: ${book.credits.generatedBy}.`, { size: 9 });
  w.para('Substrate University — Haq Roots is a free public university of ideas and experiences founded by Abed Kadaan and 7u (an AI collaborator). It is not an accredited degree-granting institution.', { size: 8.5, color: MUTED });
  w.y -= 10;
  w.para('Contents', { font: bold, size: 11, after: 4 });
  book.chapters.forEach((c, i) => w.para(`${ROMAN[i]}.  ${c.title}`, { size: 9.5, after: 1 }));
  w.para(`${ROMAN[book.chapters.length]}.  Glossary`, { size: 9.5, after: 1 });
  w.para(`${ROMAN[book.chapters.length + 1]}.  Bibliography and Links`, { size: 9.5, after: 1 });

  // Chapters
  book.chapters.forEach((c, i) => {
    w.newPage();
    w.y -= 18;
    w.text(`CHAPTER ${ROMAN[i]}`, M, w.y, 7.5, sans, GOLD_DEEP);
    w.y -= 6;
    w.para(c.title, { font: bold, size: 15, leading: 19, after: 10 });
    for (const b of c.blocks) block(w, b);
    if (c.id === 'plate') drawPlate(w, book.plate);
  });

  // Glossary
  w.newPage();
  w.y -= 18;
  w.text(`CHAPTER ${ROMAN[book.chapters.length]}`, M, w.y, 7.5, sans, GOLD_DEEP);
  w.y -= 6;
  w.para('Glossary', { font: bold, size: 15, leading: 19, after: 10 });
  for (const g of book.glossary) block(w, { k: 'def', term: g.term, text: g.text, status: g.status, by: 'sourced' });

  // Bibliography
  w.newPage();
  w.y -= 18;
  w.text(`CHAPTER ${ROMAN[book.chapters.length + 1]}`, M, w.y, 7.5, sans, GOLD_DEEP);
  w.y -= 6;
  w.para('Bibliography and Links', { font: bold, size: 15, leading: 19, after: 10 });
  for (const s of book.bibliography) {
    const url = s.url ? (s.url.startsWith('/') ? `${origin}${s.url}` : s.url) : '';
    w.para(`${s.authors}${s.year ? ` (${s.year})` : ''}. ${s.title}.${s.locator ? ` ${s.locator}.` : ''}${url ? ` ${url}` : ''} [${s.status}]`, { size: 8.8, after: 4 });
  }
  return doc.save();
}
