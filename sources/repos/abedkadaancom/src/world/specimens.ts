// Specimen volumes: deterministic previews generated from pairs of real
// registry topics. Every one is labelled "Specimen Volume / Preview" and is
// never presented as a participant's book or a real publication.

import { DIVISIONS, TOPICS } from '../content/registry';
import type { Topic } from '../content/types';
import { hashString, mulberry32 } from '../math/world';

export const SPECIMEN_LABEL = 'Specimen Volume / Preview';

export interface Specimen {
  id: string;
  title: string;
  a: Topic;
  b: Topic;
  color: string;
  height: number;
  width: number;
  shelf: number;
  slot: number;
}

const FORMS = ['On {A} and {B}', '{A}, Read Through {B}', 'A Primer of {A} for Students of {B}', 'Where {A} Meets {B}', 'The {A} Ledger, With Notes on {B}'];

let cache: Specimen[] | null = null;

export function specimens(): Specimen[] {
  if (cache) return cache;
  const out: Specimen[] = [];
  const rnd = mulberry32(20261021);
  for (let i = 0; i < TOPICS.length; i++) {
    for (let j = 0; j < TOPICS.length; j++) {
      if (i === j) continue;
      const a = TOPICS[i]!;
      const b = TOPICS[j]!;
      // keep pairs that share a glossary term or a prerequisite: genuine connections
      const linked = a.glossary.some((g) => b.glossary.includes(g)) || a.prerequisites.includes(b.id);
      if (!linked) continue;
      const h = hashString(`${a.id}×${b.id}`);
      if (h % 2 !== 0) continue;
      const div = DIVISIONS.find((d) => d.id === a.division)!;
      const form = FORMS[h % FORMS.length]!;
      out.push({
        id: `${a.id}--${b.id}`,
        title: form.replace('{A}', a.subject).replace('{B}', b.subject),
        a,
        b,
        color: div.accent,
        height: 0.75 + rnd() * 0.45,
        width: 0.12 + rnd() * 0.1,
        shelf: 0,
        slot: 0,
      });
    }
  }
  out.forEach((s, i) => {
    s.shelf = Math.floor(i / 48);
    s.slot = i % 48;
  });
  cache = out;
  return out;
}

export function specimen(id: string): Specimen | undefined {
  return specimens().find((s) => s.id === id);
}
