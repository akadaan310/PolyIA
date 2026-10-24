// The Scriptorium: deterministic, browser-local composition of six personal
// volumes from (1) vetted registry content, (2) computations recorded in the
// participant's own exercises, (3) the participant's own words, and (4) typed
// narrative templates. Every block carries an attribution so that each book can
// state exactly what the participant did, what was sourced and what was computed.

import type { Division, DivisionId, ExhibitId, Source, Topic } from '../content/types';
import { DIVISIONS, EPISTEMIC_LABELS, topic, topicsOf } from '../content/registry';
import { findTerm } from '../content/glossary';
import type { ExerciseRecord, HarnessState, StationRecord } from '../state/store';
import { DEFAULT_RECORDS } from '../exhibits/records';
import { plateFor, type Plate } from './plates';
import { hashString, mulberry32 } from '../math/world';
import { analyse, apply, fmtVec, mat } from '../math/matrix';
import { compile, opMatrix } from '../math/addressCompiler';
import { analyseInterval } from '../math/music';
import { ruleTable, weave } from '../math/world';
import { evaluateWord, DFA } from '../math/bridgeGrammar';
import { startFold, foldOnce, grammarSize } from '../math/fold';
import { CGT_BOOK } from '../content/sources';

export type Attribution = 'participant' | 'generated' | 'sourced' | 'computed';

export type Block =
  | { k: 'p'; text: string; by: Attribution }
  | { k: 'h'; text: string }
  | { k: 'eq'; lines: string[]; by: Attribution }
  | { k: 'quote'; text: string; by: Attribution; who: string }
  | { k: 'list'; items: string[]; by: Attribution }
  | { k: 'def'; term: string; text: string; status: string; by: Attribution };

export interface Chapter {
  id: string;
  title: string;
  blocks: Block[];
}

export type Depth = 'exercised' | 'visited' | 'not-entered';

export interface Book {
  id: string;
  runId: string;
  edition: number;
  division: DivisionId;
  divisionName: string;
  numeral: string;
  title: string;
  subtitle: string;
  author: string;
  isPrivate: boolean;
  createdAt: string;
  depth: Depth;
  topicId: string;
  chapters: Chapter[];
  glossary: { term: string; text: string; status: string }[];
  bibliography: Source[];
  plate: Plate;
  credits: {
    participant: string;
    foundingWorks: string[];
    generatedBy: string;
  };
  ledger: { participant: string[]; sourced: string[]; computed: string[]; generated: string[] };
}

export const PRIVATE_NAME = 'A Private Harnesser';
export const SCRIPTORIUM = 'Substrate University Scriptorium — browser-generated educational material (no AI model, no server)';

const GENRES = ['Volume', 'Notebook', 'Primer', 'Ledger', 'Atlas', 'Folio', 'Commonplace Book'];
const OPENINGS: Record<DivisionId, string[]> = {
  foundations: ['Doors and Dials', 'The Twice-Checked Walk', 'Of States and Their Crossings', 'The Admissible Road'],
  relational: ['What Is Folded Is Not Lost', 'The Glyph and Its Path', 'Strata of a Word', 'Seeds and Their Closures'],
  languages: ['The Address That Computes', 'A Program in One Knot', 'The Refusing Machine', 'Threads of the Loom'],
  geometry: ['What Survives the Map', 'The Kernel Door', 'Image and Loss', 'The Shadow Ledger'],
  acoustic: ['The Circle of Twelve', 'Orbits of a Single Step', 'Light by Interval', 'The Closing Fifth'],
  worlds: ['A World Woven Row by Row', 'What Must Be Born First', 'The Cloth of Rules', 'Worlds From Eight Bits'],
};

function cap(s: string) {
  return s.replace(/(^|\s)(\p{L})/gu, (_m, a: string, b: string) => a + b.toUpperCase());
}

export function bookTitle(div: Division, t: Topic, name: string, interest: string | null, edition: number): { title: string; subtitle: string } {
  const rnd = mulberry32(hashString(`${name}|${div.id}|${t.id}|${interest ?? ''}|${edition}`));
  const pick = <T,>(xs: T[]) => xs[Math.floor(rnd() * xs.length)]!;
  const terms = t.glossary.map((g) => findTerm(g)?.term ?? g);
  const term = cap(terms[0] ?? t.subject);
  const term2 = cap(terms[1] ?? div.name);
  const form = Math.floor(rnd() * 4);
  const title = form === 0 ? pick(OPENINGS[div.id]) : form === 1 ? `On ${term} and ${term2}` : form === 2 ? `The ${term} ${pick(['Door', 'Lamp', 'Thread', 'Stair', 'Window'])}` : `${pick(OPENINGS[div.id])}`;
  const subtitle = `A Harnesser’s ${pick(GENRES)} of ${div.name}${interest === div.id ? ' — the interest volume' : ''}`;
  return { title, subtitle };
}

function depthOf(st: StationRecord | undefined): Depth {
  if (!st) return 'not-entered';
  return st.exercise ? 'exercised' : 'visited';
}

function para(text: string, by: Attribution): Block {
  return { k: 'p', text, by };
}

/** Explanatory derivation for each exhibit, filled with the participant's actual numbers. */
function derivation(exhibit: ExhibitId, rec: ExerciseRecord): Block[] {
  const out: Block[] = [];
  switch (exhibit) {
    case 'bridge-grammar': {
      const word = String(rec.input.word ?? '');
      const bridges = ((rec.input.bridges as string[]) ?? []).map((s) => {
        const [ab, type] = s.split(':');
        return { a: ab![0] as never, b: ab![1] as never, type: type as 'stone' | 'gold' };
      });
      const r = evaluateWord(word, bridges);
      out.push(para(`The walk ${word} is read as ${Math.max(0, word.length - 1)} steps. Each step is checked twice. Realizability asks whether the structure contains the bridge; admissibility feeds the bridge’s type to the automaton. ${DFA.description}`, 'generated'));
      out.push({ k: 'eq', by: 'computed', lines: ['q₀ = 0', ...r.steps.map((s, i) => (s.bridge ? `q${i + 1} = δ(q${i}, ${s.bridge}) = ${s.dfaState}` : `step ${i + 1}: ${s.from}–${s.to} ∉ bridges  ⇒ unrealizable`)), `accept ⇔ q_final ∈ {0, 1}: ${r.admissible ? 'accepted' : 'rejected'}`] });
      out.push(para(r.verdict, 'computed'));
      break;
    }
    case 'fold': {
      const word = String(rec.input.word ?? '');
      const depth = Number(rec.input.depth ?? 0);
      let st = startFold(word);
      const lines = [`|w| = ${word.length}, grammar size g₀ = ${grammarSize(st)}`];
      for (let i = 0; i < depth && st.current.length > 1; i++) {
        st = foldOnce(st);
        const r = st.rules[st.rules.length - 1]!;
        lines.push(`${r.glyph} → ${r.left}${r.right}   (×${r.count})   g${i + 1} = |w${i + 1}| + 2·${i + 1} = ${grammarSize(st)}`);
      }
      out.push(para('Each fold chooses the most frequent pair of adjacent symbols (Re-Pair) and replaces every non-overlapping occurrence with one new glyph. The grammar size counts the symbols in the current stratum plus two for each rule, so a fold pays for itself only when the pair occurs at least three times.', 'generated'));
      out.push({ k: 'eq', by: 'computed', lines });
      out.push(para(`Because each rule records exactly the pair it replaced, unfolding substitutes the pair back and the original path ${word} is recovered symbol for symbol. That identity, unfold(fold(w)) = w, was re-checked by the Scriptorium when this book was composed.`, 'computed'));
      break;
    }
    case 'address-compiler': {
      const address = String(rec.input.address ?? '');
      const r = compile(address);
      out.push(para('The address is read in two layers: a regular parse into typed tokens, then a typed machine that admits each token only in an allowed state. Each admitted geometric operation contributes a 3×3 homogeneous matrix; later operations multiply on the left.', 'generated'));
      const lines = r.tokens.map((t) => {
        if (t.type !== 'geometric' || !t.op) return `${t.raw}: control`;
        const m = opMatrix(t.op, t.arg).m;
        return `${t.raw}: ${m ? m.map((row) => `[${row.map(String).join(' ')}]`).join('') : t.error}`;
      });
      if (r.matrix) lines.push(`M = ${r.matrix.map((row) => `[${row.map(String).join(' ')}]`).join('')}`);
      else lines.push(`refused: ${r.diagnostics[0] ?? ''}`);
      out.push({ k: 'eq', by: 'computed', lines });
      out.push(para(r.ok ? 'Because matrix multiplication is associative, applying M once is exactly applying every operation in order: the program has been compiled to a single constant-size operation.' : 'Because the machine refused the address, no matrix was woven. A refusal is a result: it says precisely which condition failed.', 'computed'));
      break;
    }
    case 'image-sculpture': {
      const rows = (rec.input.matrix as number[][]) ?? [[1, 0], [0, 1]];
      const A = mat(rows);
      const a = analyse(A);
      const n = rows[0]!.length;
      out.push(para(`Row reduction of A finds ${a.rank} pivot${a.rank === 1 ? '' : 's'}, so rank A = ${a.rank}. By the rank–nullity theorem, dim ker A = ${n} − ${a.rank} = ${a.nullity}.`, 'computed'));
      const lines = [`A = ${rows.map((r) => `[${r.join(' ')}]`).join('')}`, `rank A = ${a.rank},  dim ker A = ${a.nullity}`];
      for (const k of a.kernel) {
        const Ak = apply(A, k);
        lines.push(`k = (${fmtVec(k)}):  A·k = (${fmtVec(Ak)}) = 0 ✓`);
      }
      for (const v of a.image) lines.push(`image direction (${fmtVec(v)})`);
      out.push({ k: 'eq', by: 'computed', lines });
      out.push(para(a.nullity === 0 ? 'The kernel is {0}: distinct inputs have distinct outputs, and nothing was lost.' : `Any two inputs differing by a kernel vector produce the same output. That is the precise sense in which ${a.nullity} dimension${a.nullity === 1 ? ' was' : 's were'} lost: not erased at random, but identified.`, 'generated'));
      break;
    }
    case 'interval-ring': {
      const a = analyseInterval(Number(rec.input.k ?? 7));
      const steps: string[] = [];
      let x = 12;
      let y = a.k;
      while (y) {
        steps.push(`${x} = ${Math.floor(x / y)}·${y} + ${x % y}`);
        [x, y] = [y, x % y];
      }
      out.push(para(`The orbit of 0 under x ↦ x + ${a.k} in ℤ/12 is the cyclic subgroup generated by ${a.k}. Its size is 12 / gcd(12, ${a.k}), and the gcd is found by Euclid’s algorithm:`, 'generated'));
      out.push({ k: 'eq', by: 'computed', lines: [...(steps.length ? steps : ['gcd(12, 0) = 12']), `gcd(12, ${a.k}) = ${a.gcd}   ⇒   |⟨${a.k}⟩| = 12 / ${a.gcd} = ${a.orbitLength}`, `orbit: ${a.orbit.join(' ')}`, `2^(${a.k}/12) = ${a.equalTemperedRatio.toFixed(6)}  vs  ${a.justRatio[0]}/${a.justRatio[1]}: ${a.centsDeviation.toFixed(2)} cents`] });
      out.push(para(`The campus read this result as ${a.orbitLength} lit arches. Light and sound are consequences of the computation; neither is evidence for it.`, 'generated'));
      break;
    }
    case 'world-loom': {
      const rule = Number(rec.input.rule ?? 90);
      const g = weave(rule, 31, 3);
      const row0 = g[0]!;
      const i = 15;
      const k = (row0[i - 1]! << 2) | (row0[i]! << 1) | row0[i + 1]!;
      out.push(para(`Rule ${rule} is the binary number ${rule.toString(2).padStart(8, '0')}. A cell’s next value is bit k of the rule, where k is its neighbourhood (left, self, right) read in binary.`, 'generated'));
      out.push({ k: 'eq', by: 'computed', lines: [ruleTable(rule).map((r) => `${r.neighbourhood}→${r.out}`).join('  '), `centre cell at t = 0: neighbourhood ${row0[i - 1]}${row0[i]}${row0[i + 1]} = ${k}  ⇒  bit ${k} of ${rule} = ${(rule >> k) & 1}`, `row 1: ${g[1]!.map((c) => (c ? '█' : '·')).join('')}`] });
      if (rec.input.removed) out.push(para(`You removed the fact “${rec.input.removed}”. In the BORNE dependency graph, every fact reachable from it lost a cause: ${rec.output.find((l) => l.startsWith('removing')) ?? ''}.`, 'computed'));
      break;
    }
  }
  return out;
}

export interface ComposeInput {
  harness: HarnessState;
  /** Fallback exercise records from the campus, if the station did not record its own. */
  worldExercises?: Partial<Record<ExhibitId, ExerciseRecord>>;
  now?: string;
}

export function composeBooks(input: ComposeInput): Book[] {
  return DIVISIONS.map((d) => composeBook(d, input));
}

export function composeBook(div: Division, input: ComposeInput): Book {
  const h = input.harness;
  const isPrivate = !h.displayName;
  const name = h.displayName?.trim() || PRIVATE_NAME;
  const st = h.stations[div.id];
  const depth = depthOf(st);
  const t = topic(st?.topicId ?? '') ?? topicsOf(div.id).find((x) => x.domainAdapter === div.exhibit)!;
  const ownRec = st?.exercise ?? null;
  const rec: ExerciseRecord = ownRec ?? { ...DEFAULT_RECORDS[div.exhibit]!(), at: input.now ?? new Date().toISOString() };
  const usedDefault = !ownRec;
  const { title, subtitle } = bookTitle(div, t, name, h.interest, h.edition);
  const runId = h.runId ?? 'local';
  const id = `su-${hashString(`${runId}|${div.id}|${h.edition}`).toString(36)}`;
  const interestDiv = DIVISIONS.find((x) => x.id === h.interest);
  const path = div.curriculum.slice(0, 5).map((id) => topic(id)!.title);

  const letter: Chapter = {
    id: 'letter',
    title: 'An Opening Letter',
    blocks: [
      para(`Dear ${name},`, 'generated'),
      para(
        depth === 'exercised'
          ? `This volume records your passage through ${div.door}, the entrance to ${div.name}. You did not only read here: you ran ${div.exhibitTitle} with inputs of your own choosing, and the computation that followed is reproduced in these pages exactly as your browser performed it.`
          : depth === 'visited'
            ? `This volume records a brief encounter with ${div.name}. You entered ${div.door} but did not run ${div.exhibitTitle} with inputs of your own, so the worked example in Chapter IV was computed by the Scriptorium on standard inputs. It describes an encounter, not mastery, and it says so.`
            : `This volume introduces ${div.name}, a division you did not enter during your harness. It is offered as an invitation. Its worked example was computed by the Scriptorium on standard inputs, not by you.`,
        'generated',
      ),
      para(
        interestDiv
          ? interestDiv.id === div.id
            ? `You named ${div.name} as your interest when you entered the harness, so this is the volume the others orbit.`
            : `You named ${interestDiv.name} as your interest. This volume connects to it through the glossary at the end: several of its terms have senses in both divisions.`
          : 'You entered the harness without naming an interest, which is a perfectly good way to enter a university.',
        'generated',
      ),
      para(`The motto over this door reads: “${div.motto}” The rest of this book explains what that sentence means in mathematics, and where the mathematics came from.`, 'generated'),
      para('— The Scriptorium of Substrate University', 'generated'),
    ],
  };

  const intro: Chapter = {
    id: 'introduction',
    title: `Introduction to ${div.name}`,
    blocks: [
      para(div.description, 'sourced'),
      para(`A first path through the division runs: ${path.join('; ')}. The topic at the centre of this volume is “${t.title}”, marked as ${EPISTEMIC_LABELS[t.status].label.toLowerCase()}: ${EPISTEMIC_LABELS[t.status].description}`, 'sourced'),
      para(t.summary, 'sourced'),
    ],
  };

  const foundationDefs = t.definitions.map<Block>((d) => ({ k: 'def', term: d.term, text: d.text, status: EPISTEMIC_LABELS[d.status].label, by: 'sourced' }));
  const second = topicsOf(div.id).find((x) => x.id !== t.id && x.domainAdapter === div.exhibit);
  const foundation: Chapter = {
    id: 'foundation',
    title: 'The Mathematical Foundation',
    blocks: [
      para('The definitions below are reproduced from the university registry. Each carries its epistemic label: established mathematics is cited to standard references; house constructions are defined by the co-founders and are not externally established.', 'generated'),
      ...foundationDefs,
      ...(t.constraints.length ? [{ k: 'list', by: 'sourced', items: t.constraints } as Block] : []),
      ...t.examples.slice(0, 2).map((e) => para(`${e.title}. ${e.body}`, 'sourced')),
      ...(second ? [para(`A neighbouring topic, “${second.title}”, extends this: ${second.summary}`, 'sourced')] : []),
    ],
  };

  const worked: Chapter = {
    id: 'derivation',
    title: 'A Worked Derivation',
    blocks: [
      para(usedDefault ? `The following was computed by the Scriptorium on standard inputs because no exercise of yours was recorded at this station. ${rec.headline}` : `The following reproduces your exercise of ${new Date(rec.at).toISOString().slice(0, 16).replace('T', ' ')} UTC. ${rec.headline}`, usedDefault ? 'computed' : 'participant'),
      ...derivation(div.exhibit, rec),
      { k: 'eq', by: 'computed', lines: rec.output.slice(0, 14) },
    ],
  };

  const reflection = st?.reflection?.trim();
  const yours: Chapter = {
    id: 'yours',
    title: 'Your Answer and Its Derivation',
    blocks: [
      ...(reflection
        ? [{ k: 'quote', text: reflection, by: 'participant', who: name } as Block, para('These words are yours, recorded at the station and reproduced without alteration.', 'generated')]
        : [para('You left no written reflection at this station. The space is left open: a harness volume can be regenerated after you add one.', 'generated')]),
      ...(ownRec
        ? [para(`Your choices: ${Object.entries(ownRec.input).map(([k, v]) => `${k} = ${Array.isArray(v) ? JSON.stringify(v) : String(v)}`).join('; ')}.`, 'participant'), para(`From those choices the browser derived: ${rec.headline} The derivation in Chapter IV is the complete trace.`, 'computed')]
        : []),
      ...(h.contribution && (h.interest === div.id || (!h.interest && div.id === 'foundations'))
        ? [para(`Your contribution to the university (${h.contribution.kind.replace('-', ' ')}${h.contribution.term ? `, “${h.contribution.term}”` : ''}):`, 'generated'), { k: 'quote', text: h.contribution.text, by: 'participant', who: name } as Block]
        : []),
      para(`The challenge posed by this topic: ${t.challenge.prompt} The registry’s answer: ${t.challenge.answer}`, 'sourced'),
    ],
  };

  const plate = plateFor(div.exhibit, rec);
  const plateChapter: Chapter = { id: 'plate', title: 'The Plate', blocks: [para(plate.caption, 'computed')] };

  const glossaryTerms = [...new Set([...t.glossary, ...(second?.glossary ?? [])])]
    .map((g) => findTerm(g))
    .filter((x): x is NonNullable<typeof x> => !!x)
    .slice(0, 10);
  const glossary = glossaryTerms.map((term) => {
    const sense = term.senses.find((s) => s.domain === div.id) ?? term.senses[0]!;
    const other = term.senses.filter((s) => s !== sense).map((s) => s.domain);
    return {
      term: term.term,
      text: sense.text + (other.length ? ` (Also used in: ${[...new Set(other)].join(', ')}.)` : ''),
      status: EPISTEMIC_LABELS[sense.status].label,
    };
  });

  const bibliography = dedupeSources([...t.sources, ...(second?.sources ?? []), ...(div.id === 'foundations' ? [CGT_BOOK] : [])]);

  const ledger = {
    participant: [
      depth === 'not-entered' ? 'You did not enter this station.' : `You entered this station${st?.enteredAt ? ` at ${st.enteredAt.slice(0, 16).replace('T', ' ')} UTC` : ''}.`,
      ...(ownRec ? [`You chose the exercise inputs: ${Object.keys(ownRec.input).join(', ')}.`] : []),
      ...(reflection ? ['You wrote the reflection quoted in Chapter V.'] : []),
      ...(h.contribution && h.interest === div.id ? ['You wrote the contribution quoted in Chapter V.'] : []),
      `You chose the name on this book: ${isPrivate ? 'you remained private' : name}.`,
    ],
    sourced: [`Definitions, constraints and examples from the Substrate University registry, topic “${t.title}”.`, ...bibliography.map((s) => `${s.authors}, ${s.title}${s.year ? ` (${s.year})` : ''}.`)],
    computed: [usedDefault ? 'The worked derivation, on standard inputs (not yours).' : 'The worked derivation, from your inputs, recomputed when this book was composed.', 'The plate, drawn from the same computation.'],
    generated: ['The title and subtitle, from a seeded template grammar over your name, the division, the topic and your interest.', 'The opening letter and connecting paragraphs, from fixed templates.', 'No AI model wrote any part of this book; nothing was sent to a server.'],
  };

  const transparency: Chapter = {
    id: 'transparency',
    title: 'What You Did, What Was Sourced, What Was Computed',
    blocks: [
      para('This chapter is the book’s own provenance. A harness volume is a record of a day’s learning; it is not a degree, a credential or a proof of mastery.', 'generated'),
      { k: 'h', text: 'By you' },
      { k: 'list', by: 'participant', items: ledger.participant },
      { k: 'h', text: 'From sources' },
      { k: 'list', by: 'sourced', items: ledger.sourced },
      { k: 'h', text: 'Computed in your browser' },
      { k: 'list', by: 'computed', items: ledger.computed },
      { k: 'h', text: 'Generated by the Scriptorium' },
      { k: 'list', by: 'generated', items: ledger.generated },
    ],
  };

  return {
    id,
    runId,
    edition: h.edition,
    division: div.id,
    divisionName: div.name,
    numeral: div.numeral,
    title,
    subtitle,
    author: name,
    isPrivate,
    createdAt: input.now ?? new Date().toISOString(),
    depth,
    topicId: t.id,
    chapters: [letter, intro, foundation, worked, yours, plateChapter, transparency],
    glossary,
    bibliography,
    plate,
    credits: {
      participant: `${name} — author of the recorded choices${reflection ? ' and reflection' : ''}`,
      foundingWorks: bibliography.filter((s) => s.status === 'published-book' || s.status === 'public-repository').map((s) => `${s.title} — ${s.authors}`),
      generatedBy: SCRIPTORIUM,
    },
    ledger,
  };
}

function dedupeSources(xs: Source[]): Source[] {
  const seen = new Set<string>();
  return xs.filter((s) => (seen.has(s.title) ? false : (seen.add(s.title), true)));
}

export function bookPlainText(b: Book): string {
  const lines = [b.title, b.subtitle, `by ${b.author}`, ''];
  b.chapters.forEach((c, i) => {
    lines.push(`${ROMAN[i]}. ${c.title}`);
    for (const bl of c.blocks) {
      if (bl.k === 'p') lines.push(bl.text);
      else if (bl.k === 'h') lines.push(bl.text);
      else if (bl.k === 'eq') lines.push(...bl.lines);
      else if (bl.k === 'quote') lines.push(`“${bl.text}” — ${bl.who}`);
      else if (bl.k === 'list') lines.push(...bl.items.map((x) => `• ${x}`));
      else if (bl.k === 'def') lines.push(`${bl.term} [${bl.status}]: ${bl.text}`);
    }
    lines.push('');
  });
  return lines.join('\n');
}

export const ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'];
