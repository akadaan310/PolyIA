// Campus locations: one table drives navigation, direct routes and camera anchors.

import type { DivisionId } from '../content/types';
import { DIVISIONS } from '../content/registry';

export type Vec3 = [number, number, number];

export interface Location {
  id: string;
  path: string;
  label: string;
  short: string;
  camera: Vec3;
  target: Vec3;
}

export const ATRIUM_RADIUS = 15;
export const REALM_RADIUS = 27;

/** Doors sit on the atrium circle, spanning 30°…330° from the +z axis, leaving the front open to the Gate. */
export function doorAngle(index: number): number {
  return Math.PI / 6 + (index * (5 * Math.PI)) / 3 / 5;
}

export function onCircle(index: number, r: number, y = 0): Vec3 {
  const a = doorAngle(index);
  return [r * Math.sin(a), y, r * Math.cos(a)];
}

/** Wings stand on the five gap directions between the realms (the sixth gap is the Gate). */
export const WING_RADIUS = 46;
export const WING_ANGLES = { library: (4 * Math.PI) / 3, observatory: (2 * Math.PI) / 3, 'harness-masters': Math.PI, scriptorium: (5 * Math.PI) / 3, 'common-room': Math.PI / 3 } as const;
export function wingPos(id: keyof typeof WING_ANGLES, r = WING_RADIUS, y = 0): Vec3 {
  const a = WING_ANGLES[id];
  return [r * Math.sin(a), y, r * Math.cos(a)];
}

export const BASE_LOCATIONS: Location[] = [
  { id: 'approach', path: '/', label: 'The Approach', short: 'Approach', camera: [0, 10, 66], target: [0, 9, 4] },
  { id: 'gate', path: '/gate', label: 'The Gate · Hall of First Principles', short: 'Gate', camera: [7, 6, 55], target: [0, 9, 30] },
  { id: 'atrium', path: '/atrium', label: 'The Atrium of Six Divisions', short: 'Atrium', camera: [0, 25, 27], target: [0, 1, -4] },
  { id: 'library', path: '/library', label: 'The Library of Forms', short: 'Library', camera: wingPos('library', 28, 7), target: wingPos('library', WING_RADIUS, 6) },
  { id: 'observatory', path: '/observatory', label: 'The Observatory', short: 'Observatory', camera: wingPos('observatory', 17, 9), target: wingPos('observatory', WING_RADIUS, 11) },
  { id: 'sky', path: '/observatory/sky', label: 'The Observatory · looking up', short: 'Sky', camera: wingPos('observatory', 36, 2.2), target: wingPos('observatory', 60, 45) },
  { id: 'harness-masters', path: '/harness-masters', label: 'The Hall of Harness Masters', short: 'Harness Masters', camera: wingPos('harness-masters', 27, 7), target: wingPos('harness-masters', WING_RADIUS, 7) },
  { id: 'scriptorium', path: '/scriptorium', label: 'The Scriptorium', short: 'Scriptorium', camera: wingPos('scriptorium', 28, 6), target: wingPos('scriptorium', WING_RADIUS, 5) },
  { id: 'common-room', path: '/common-room', label: 'The Founder Office · Common Room', short: 'Common Room', camera: wingPos('common-room', 28, 6), target: wingPos('common-room', WING_RADIUS, 5) },
  { id: 'harness', path: '/harness', label: 'The One-Day Harness', short: 'Harness', camera: [0, 30, 44], target: [0, 0, -6] },
  { id: 'glossary', path: '/glossary', label: 'The Glossary Field', short: 'Glossary', camera: [0, 44, 8], target: [0, 0, -4] },
  { id: 'about', path: '/about', label: 'About the University', short: 'About', camera: [0, 12, 60], target: [0, 9, 10] },
];

export const DIVISION_LOCATIONS: Location[] = DIVISIONS.map((d, i) => {
  // through the open door: stand just beyond the threshold, facing the realm's exhibit
  const cam = onCircle(i, ATRIUM_RADIUS + 4.6, 3.8);
  const tgt = onCircle(i, REALM_RADIUS + 1.5, 3.4);
  return { id: `division:${d.id}`, path: `/divisions/${d.id}`, label: `${d.door} — ${d.name}`, short: d.name.split(' ')[0]!, camera: cam, target: tgt };
});

export const LOCATIONS: Location[] = [...BASE_LOCATIONS, ...DIVISION_LOCATIONS];

export function locationForPath(pathname: string): Location {
  const m = /^\/divisions\/([a-z]+)/.exec(pathname);
  if (m) return DIVISION_LOCATIONS.find((l) => l.id === `division:${m[1]}`) ?? BASE_LOCATIONS[2]!;
  if (pathname === '/observatory/sky') return BASE_LOCATIONS.find((l) => l.id === 'sky')!;
  if (pathname.startsWith('/library')) return BASE_LOCATIONS.find((l) => l.id === 'library')!;
  if (pathname.startsWith('/scriptorium')) return BASE_LOCATIONS.find((l) => l.id === 'scriptorium')!;
  if (pathname.startsWith('/harness-masters')) return BASE_LOCATIONS.find((l) => l.id === 'harness-masters')!;
  if (pathname.startsWith('/harness')) {
    const d = /^\/harness\/([a-z]+)/.exec(pathname);
    if (d) return DIVISION_LOCATIONS.find((l) => l.id === `division:${d[1]}`) ?? BASE_LOCATIONS.find((l) => l.id === 'harness')!;
    return BASE_LOCATIONS.find((l) => l.id === 'harness')!;
  }
  if (pathname.startsWith('/glossary')) return BASE_LOCATIONS.find((l) => l.id === 'glossary')!;
  return BASE_LOCATIONS.find((l) => l.path === pathname) ?? BASE_LOCATIONS[0]!;
}

export function divisionIndex(id: DivisionId): number {
  return DIVISIONS.findIndex((d) => d.id === id);
}

/** Primary navigation order (keyboard [ and ] cycle through it). */
export const NAV_ORDER = ['/', '/gate', '/atrium', ...DIVISIONS.map((d) => `/divisions/${d.id}`), '/library', '/observatory', '/harness-masters', '/harness', '/scriptorium', '/common-room', '/glossary'];
