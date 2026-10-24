// Geography for the Observatory: openly labelled offline samples, explicit
// geocoding through OpenStreetMap Nominatim, and street paths from Overpass.
// Remote calls happen only after an explicit visitor action. Coordinates are
// rounded to 3 decimals (~100 m) before they are stored; addresses are never stored.

import { signature, project, type PathSignature, type Pt } from '../math/paths';

export interface Place {
  lat: number;
  lon: number;
  label: string;
  provenance: string;
}

export const SAMPLE_PLACES: Place[] = [
  { lat: 51.477, lon: -0.001, label: 'Royal Observatory Greenwich', provenance: 'Offline sample: approximate public-landmark coordinates entered by hand.' },
  { lat: 19.821, lon: -155.468, label: 'Maunakea summit', provenance: 'Offline sample: approximate public-landmark coordinates entered by hand.' },
  { lat: -23.023, lon: -67.755, label: 'Chajnantor plateau, Atacama', provenance: 'Offline sample: approximate public-landmark coordinates entered by hand.' },
  { lat: -33.86, lon: 151.205, label: 'Sydney Observatory', provenance: 'Offline sample: approximate public-landmark coordinates entered by hand.' },
  { lat: 48.836, lon: 2.336, label: 'Paris Observatory', provenance: 'Offline sample: approximate public-landmark coordinates entered by hand.' },
  { lat: 64.146, lon: -21.942, label: 'Reykjavík', provenance: 'Offline sample: approximate city-centre coordinates entered by hand.' },
];

export const round3 = (x: number) => Math.round(x * 1000) / 1000;

export interface GeocodeResult {
  lat: number;
  lon: number;
  displayName: string;
  precision: string;
  provider: string;
}

function precisionOf(rank: number | undefined, type: string | undefined): string {
  if (rank === undefined) return type ? `feature type “${type}”` : 'unknown';
  if (rank >= 29) return `building or address point (OSM place_rank ${rank})`;
  if (rank >= 26) return `street (OSM place_rank ${rank})`;
  if (rank >= 17) return `neighbourhood or locality (OSM place_rank ${rank})`;
  if (rank >= 13) return `town or city (OSM place_rank ${rank})`;
  if (rank >= 5) return `region (OSM place_rank ${rank})`;
  return `country or larger (OSM place_rank ${rank})`;
}

/** One explicit request to Nominatim (usage policy: ≤ 1 request/second, no autocomplete). */
export async function geocode(query: string): Promise<GeocodeResult | null> {
  const url = `https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=${encodeURIComponent(query.slice(0, 200))}`;
  const res = await fetch(url, { headers: { Accept: 'application/json' }, referrerPolicy: 'strict-origin-when-cross-origin' });
  if (!res.ok) throw new Error(`Nominatim answered ${res.status}`);
  const data = (await res.json()) as { lat: string; lon: string; display_name: string; place_rank?: number; type?: string }[];
  const r = data[0];
  if (!r) return null;
  return { lat: Number(r.lat), lon: Number(r.lon), displayName: r.display_name, precision: precisionOf(r.place_rank, r.type), provider: 'OpenStreetMap Nominatim (data © OpenStreetMap contributors, ODbL 1.0)' };
}

export interface PathCandidate {
  id: string;
  name: string;
  source: 'synthetic' | 'osm';
  points: Pt[]; // metres in a local plane
  sig: PathSignature;
  note: string;
}

function fixture(id: string, name: string, pts: Pt[], note: string): PathCandidate {
  return { id, name, source: 'synthetic', points: pts, sig: signature(pts), note };
}

/** Clearly disclosed synthetic fixtures. They are not real streets. */
export const FIXTURES: PathCandidate[] = [
  fixture('fx-zigzag', 'Fixture A · zig-zag lane', [[0, 0], [60, 0], [100, 40], [160, 40], [200, 0], [260, 0]], 'Synthetic fixture: drawn by hand to demonstrate signatures.'),
  fixture('fx-zigzag-rev', 'Fixture B · the same lane, walked backwards and rotated', [[0, 0], [0, 60], [-40, 100], [-40, 160], [0, 200], [0, 260]].reverse() as Pt[], 'Synthetic fixture: Fixture A rotated by 90° and traversed in reverse.'),
  fixture('fx-mirror', 'Fixture C · zig-zag mirrored', [[0, 0], [60, 0], [100, -40], [160, -40], [200, 0], [260, 0]], 'Synthetic fixture: Fixture A reflected across its axis.'),
  fixture('fx-crescent', 'Fixture D · crescent', [[0, 0], [50, 10], [95, 35], [125, 75], [140, 120], [140, 170]], 'Synthetic fixture: a curve of gentle left turns.'),
  fixture('fx-block', 'Fixture E · around a block', [[0, 0], [100, 0], [100, 80], [0, 80], [0, 10]], 'Synthetic fixture: three right-angle left turns.'),
  fixture('fx-switchback', 'Fixture F · switchback', [[0, 0], [80, 0], [80, 20], [0, 20], [0, 40], [80, 40]], 'Synthetic fixture: alternating sharp turns.'),
];

interface OverpassWay {
  id: number;
  nodes?: number[];
  geometry?: { lat: number; lon: number }[];
  tags?: Record<string, string>;
}

/** Street ways within 350 m, from the public Overpass API (one explicit request). */
export async function fetchStreets(lat: number, lon: number): Promise<PathCandidate[]> {
  const q = `[out:json][timeout:20];way(around:350,${lat},${lon})[highway~"^(primary|secondary|tertiary|residential|unclassified|living_street|pedestrian|service)$"];out body geom 60;`;
  const res = await fetch('https://overpass-api.de/api/interpreter', { method: 'POST', body: new URLSearchParams({ data: q }) });
  if (!res.ok) throw new Error(`Overpass answered ${res.status}`);
  const data = (await res.json()) as { elements: OverpassWay[] };
  const ways = data.elements.filter((w) => (w.geometry?.length ?? 0) >= 3);
  const nodeCount = new Map<number, number>();
  for (const w of ways) for (const n of new Set(w.nodes ?? [])) nodeCount.set(n, (nodeCount.get(n) ?? 0) + 1);
  return ways.map((w) => {
    const pts = project(w.geometry!.map((g) => [g.lon, g.lat] as Pt), lat);
    const degrees = (w.nodes ?? []).slice(1, -1).map((n) => nodeCount.get(n) ?? 1);
    const o = pts[0]!;
    const local = pts.map(([x, y]) => [x - o[0], y - o[1]] as Pt);
    return {
      id: `osm-${w.id}`,
      name: w.tags?.name ?? `unnamed ${w.tags?.highway ?? 'way'} ${w.id}`,
      source: 'osm',
      points: local,
      sig: signature(local, degrees),
      note: `OpenStreetMap way ${w.id} (${w.tags?.highway ?? 'highway'}); data © OpenStreetMap contributors, ODbL 1.0.`,
    };
  });
}

/** Normalize a polyline for overlay: start at the origin, first segment along +x, total length 1. */
export function normalizeShape(pts: Pt[], reverse = false, mirror = false): Pt[] {
  let p = reverse ? [...pts].reverse() : [...pts];
  if (p.length < 2) return p;
  const [x0, y0] = p[0]!;
  p = p.map(([x, y]) => [x - x0, y - y0] as Pt);
  const [dx, dy] = p[1]!;
  const a = -Math.atan2(dy, dx);
  p = p.map(([x, y]) => [x * Math.cos(a) - y * Math.sin(a), x * Math.sin(a) + y * Math.cos(a)] as Pt);
  if (mirror) p = p.map(([x, y]) => [x, -y] as Pt);
  let L = 0;
  for (let i = 1; i < p.length; i++) L += Math.hypot(p[i]![0] - p[i - 1]![0], p[i]![1] - p[i - 1]![1]);
  return p.map(([x, y]) => [x / (L || 1), y / (L || 1)] as Pt);
}
