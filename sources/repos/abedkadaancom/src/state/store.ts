// One small observable store for the whole campus, persisted to localStorage.
// Every write is wrapped: private windows and blocked storage simply run
// without persistence. Nothing here leaves the browser unless the visitor
// explicitly opts into the optional cloud facility (see src/lib/cloud.ts).

import { useSyncExternalStore } from 'react';
import type { DivisionId, ExhibitId } from '../content/types';
import { INITIAL_BRIDGES, type Bridge } from '../math/bridgeGrammar';
import type { SystemId } from '../math/numberSystems';

export type Quality = 'auto' | 'low' | 'medium' | 'high';

export interface Settings {
  reducedMotion: boolean;
  sound: boolean;
  voice: boolean;
  highContrast: boolean;
  quality: Quality;
  /** Hide the 3D campus and read pages as plain documents. */
  textOnly: boolean;
}

/** A recorded result of an exhibit, as plain data: what the visitor chose and what was computed. */
export interface ExerciseRecord {
  exhibit: ExhibitId;
  at: string;
  input: Record<string, string | number | boolean | number[] | number[][] | string[]>;
  output: string[];
  /** A one-line statement of what was computed, for books. */
  headline: string;
}

export interface GateState {
  stage: 0 | 1 | 2 | 3;
  system: SystemId | null;
  sumAnswer: string | null;
  divisionsSeen: string[];
  matrix: number[][] | null;
  survivesAnswer: string | null;
  doorOpened: boolean;
}

export interface WorldState {
  gate: GateState;
  bridges: Bridge[];
  foldWord: string;
  foldDepth: number;
  interval: number;
  loomRule: number;
  /** The accepted matrix shown as the image-space sculpture at the Gate (2×2 or 3×3). */
  sculpture: number[][] | null;
  /** Inscription offset, moved by accepted matrix operations. */
  inscriptionShift: number;
  compiledAddress: string | null;
  portal: { a: string; b: string; similarity: number; normalization: string; mode: 'visit' | 'overlay' | 'braid' } | null;
  visited: string[];
  exercises: Partial<Record<ExhibitId, ExerciseRecord>>;
  /** The observer used by the Observatory and the campus sky. Coordinates are rounded to 3 decimals (~100 m). */
  observer: Observer;
  /** The moment shown by the campus sky (null = now). */
  skyTime: string | null;
}

export interface Observer {
  lat: number;
  lon: number;
  label: string;
  provenance: string;
}

export const DEFAULT_OBSERVER: Observer = {
  lat: 51.477,
  lon: -0.001,
  label: 'Royal Observatory Greenwich (offline sample)',
  provenance: 'Offline sample location: approximate public-landmark coordinates entered by hand; no geocoder used.',
};

export interface StationRecord {
  division: DivisionId;
  topicId: string;
  enteredAt: string;
  exercise: ExerciseRecord | null;
  reflection: string;
  completedAt: string | null;
}

export interface Contribution {
  kind: 'glossary-sense' | 'example' | 'question';
  term: string;
  text: string;
  at: string;
}

export interface HarnessState {
  runId: string | null;
  startedAt: string | null;
  /** null means the participant chose to remain private. */
  displayName: string | null;
  storage: 'local' | 'cloud';
  interest: DivisionId | null;
  stations: Partial<Record<DivisionId, StationRecord>>;
  contribution: Contribution | null;
  completedAt: string | null;
  edition: number;
}

export interface ResidentMemory {
  met: number;
  lastLine: string | null;
}

export interface Store {
  version: 1;
  introSeen: boolean;
  lastRoute: string | null;
  settings: Settings;
  world: WorldState;
  harness: HarnessState;
  residents: Record<string, ResidentMemory>;
  notes: { text: string; at: string }[];
}

const KEY = 'substrate-university.v1';

export function defaultSettings(): Settings {
  const prefersReduced = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
  return { reducedMotion: prefersReduced, sound: false, voice: false, highContrast: false, quality: 'auto', textOnly: false };
}

export function defaultWorld(): WorldState {
  return {
    gate: { stage: 0, system: null, sumAnswer: null, divisionsSeen: [], matrix: null, survivesAnswer: null, doorOpened: false },
    bridges: INITIAL_BRIDGES,
    foldWord: 'NENENESSWNENENE',
    foldDepth: 0,
    interval: 7,
    loomRule: 90,
    sculpture: null,
    inscriptionShift: 0,
    compiledAddress: null,
    portal: null,
    visited: [],
    exercises: {},
    observer: DEFAULT_OBSERVER,
    skyTime: null,
  };
}

export function defaultHarness(): HarnessState {
  return { runId: null, startedAt: null, displayName: null, storage: 'local', interest: null, stations: {}, contribution: null, completedAt: null, edition: 1 };
}

function initial(): Store {
  return { version: 1, introSeen: false, lastRoute: null, settings: defaultSettings(), world: defaultWorld(), harness: defaultHarness(), residents: {}, notes: [] };
}

function load(): Store {
  const base = initial();
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return base;
    const parsed = JSON.parse(raw) as Partial<Store>;
    if (parsed.version !== 1) return base;
    return {
      ...base,
      ...parsed,
      settings: { ...base.settings, ...parsed.settings },
      world: { ...base.world, ...parsed.world, gate: { ...base.world.gate, ...parsed.world?.gate }, skyTime: null },
      harness: { ...base.harness, ...parsed.harness },
    };
  } catch {
    return base;
  }
}

let state: Store = typeof window === 'undefined' ? initial() : load();
const listeners = new Set<() => void>();

function persist() {
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    /* storage unavailable: run without persistence */
  }
}

export function getState(): Store {
  return state;
}

export function setState(update: (s: Store) => Store): void {
  state = update(state);
  persist();
  listeners.forEach((l) => l());
}

export function subscribe(l: () => void): () => void {
  listeners.add(l);
  return () => listeners.delete(l);
}

export function useStore<T>(selector: (s: Store) => T): T {
  return useSyncExternalStore(subscribe, () => selector(state), () => selector(state));
}

// Convenience updaters ------------------------------------------------------

export function updateSettings(patch: Partial<Settings>): void {
  setState((s) => ({ ...s, settings: { ...s.settings, ...patch } }));
}

export function updateWorld(patch: Partial<WorldState> | ((w: WorldState) => Partial<WorldState>)): void {
  setState((s) => ({ ...s, world: { ...s.world, ...(typeof patch === 'function' ? patch(s.world) : patch) } }));
}

export function updateGate(patch: Partial<GateState>): void {
  setState((s) => ({ ...s, world: { ...s.world, gate: { ...s.world.gate, ...patch } } }));
}

export function recordExercise(rec: Omit<ExerciseRecord, 'at'>): ExerciseRecord {
  const full: ExerciseRecord = { ...rec, at: new Date().toISOString() };
  setState((s) => ({ ...s, world: { ...s.world, exercises: { ...s.world.exercises, [rec.exhibit]: full } } }));
  return full;
}

export function updateHarness(patch: Partial<HarnessState> | ((h: HarnessState) => Partial<HarnessState>)): void {
  setState((s) => ({ ...s, harness: { ...s.harness, ...(typeof patch === 'function' ? patch(s.harness) : patch) } }));
}

export function markVisited(location: string): void {
  if (state.world.visited.includes(location)) return;
  updateWorld((w) => ({ visited: [...w.visited, location] }));
}

export function resetAll(): void {
  state = initial();
  persist();
  listeners.forEach((l) => l());
}

/** For tests: replace the state wholesale. */
export function __setStateForTests(s: Store): void {
  state = s;
}
