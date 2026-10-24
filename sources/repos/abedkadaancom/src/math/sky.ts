// Observer-dependent celestial positions.
//
// Stars: Hipparcos J2000/ICRS positions (d3-celestial data, BSD-3-Clause),
// rotated to the observer's horizon with astronomy-engine 2.1.19
// (Don Cross, MIT; Rotation_EQJ_HOR includes precession and nutation).
// Proper motion over ~26 years is not applied (error < 0.1° for these stars).
// Planets, Sun and Moon: astronomy-engine topocentric apparent positions.
// Altitudes include standard atmospheric refraction ("normal").

import * as Astronomy from 'astronomy-engine';
import starData from '../data/stars.json';

export interface ObserverInput {
  lat: number;
  lon: number;
  date: Date;
}

export interface SkyObject {
  id: string;
  name: string | null;
  kind: 'star' | 'planet' | 'sun' | 'moon';
  alt: number;
  az: number;
  mag: number;
  bv: number;
  raDeg: number;
  decDeg: number;
}

type StarRow = [number, number, number, number, number];
const STARS = (starData as unknown as { stars: StarRow[] }).stars;
const NAMES = (starData as unknown as { names: Record<string, string> }).names;
export const STAR_SOURCE = (starData as unknown as { source: string }).source;
export const STAR_COUNT = STARS.length;

const PLANETS: [Astronomy.Body, string, number][] = [
  [Astronomy.Body.Sun, 'Sun', -26.7],
  [Astronomy.Body.Moon, 'Moon', -12],
  [Astronomy.Body.Mercury, 'Mercury', 0],
  [Astronomy.Body.Venus, 'Venus', -4],
  [Astronomy.Body.Mars, 'Mars', 0.5],
  [Astronomy.Body.Jupiter, 'Jupiter', -2.2],
  [Astronomy.Body.Saturn, 'Saturn', 0.7],
];

export function validateObserver(o: ObserverInput): string | null {
  if (!Number.isFinite(o.lat) || o.lat < -90 || o.lat > 90) return 'Latitude must be between −90° and 90°.';
  if (!Number.isFinite(o.lon) || o.lon < -180 || o.lon > 180) return 'Longitude must be between −180° and 180°.';
  if (!(o.date instanceof Date) || Number.isNaN(o.date.getTime())) return 'The time is not a valid date.';
  return null;
}

export function computeSky(o: ObserverInput, magLimit = 5): SkyObject[] {
  const obs = new Astronomy.Observer(o.lat, o.lon, 0);
  const time = Astronomy.MakeTime(o.date);
  const rot = Astronomy.Rotation_EQJ_HOR(time, obs);
  const out: SkyObject[] = [];
  for (const [hip, ra, dec, mag, bv] of STARS) {
    if (mag > magLimit) continue;
    const v = Astronomy.VectorFromSphere(new Astronomy.Spherical(dec, ra, 1), time);
    const h = Astronomy.HorizonFromVector(Astronomy.RotateVector(rot, v), 'normal');
    out.push({ id: `HIP ${hip}`, name: NAMES[String(hip)] ?? null, kind: 'star', alt: h.lat, az: h.lon, mag, bv, raDeg: ra, decDeg: dec });
  }
  for (const [body, name, mag] of PLANETS) {
    const eq = Astronomy.Equator(body, time, obs, true, true);
    const hor = Astronomy.Horizon(time, obs, eq.ra, eq.dec, 'normal');
    out.push({
      id: name,
      name,
      kind: body === Astronomy.Body.Sun ? 'sun' : body === Astronomy.Body.Moon ? 'moon' : 'planet',
      alt: hor.altitude,
      az: hor.azimuth,
      mag,
      bv: 0.6,
      raDeg: eq.ra * 15,
      decDeg: eq.dec,
    });
  }
  return out;
}

export function sunAltitude(o: ObserverInput): number {
  const obs = new Astronomy.Observer(o.lat, o.lon, 0);
  const eq = Astronomy.Equator(Astronomy.Body.Sun, o.date, obs, true, true);
  return Astronomy.Horizon(o.date, obs, eq.ra, eq.dec, 'normal').altitude;
}

export function skyCondition(sunAlt: number): 'day' | 'civil twilight' | 'nautical twilight' | 'astronomical twilight' | 'night' {
  if (sunAlt > -0.833) return 'day';
  if (sunAlt > -6) return 'civil twilight';
  if (sunAlt > -12) return 'nautical twilight';
  if (sunAlt > -18) return 'astronomical twilight';
  return 'night';
}

export function moonPhaseDeg(date: Date): number {
  return Astronomy.MoonPhase(date);
}

/** Local apparent sidereal time in hours: GAST + λ/15. */
export function localSiderealHours(o: ObserverInput): number {
  const gast = Astronomy.SiderealTime(o.date);
  return (((gast + o.lon / 15) % 24) + 24) % 24;
}

/**
 * The zenith map Z: (φ, λ, t) ↦ (α, δ) = (LAST(λ, t), φ).
 * The point of the sky straight overhead has declination equal to the
 * observer's (geodetic, ≈ astronomical) latitude and right ascension equal to
 * the local sidereal time. Declared loss: Z forgets the observer's height,
 * terrain and weather; it is many-to-one across time (each sky point is the
 * zenith of a whole circle of longitudes over a sidereal day) and the
 * coordinates are of date, so the same place maps to a slowly drifting point
 * over years because of precession.
 */
export function zenith(o: ObserverInput): { raHours: number; raDeg: number; decDeg: number } {
  const lst = localSiderealHours(o);
  return { raHours: lst, raDeg: lst * 15, decDeg: o.lat };
}

/** Great-circle angular distance in degrees between two (ra, dec) points. */
export function angularDistance(ra1: number, dec1: number, ra2: number, dec2: number): number {
  const r = Math.PI / 180;
  const c = Math.sin(dec1 * r) * Math.sin(dec2 * r) + Math.cos(dec1 * r) * Math.cos(dec2 * r) * Math.cos((ra1 - ra2) * r);
  return Math.acos(Math.min(1, Math.max(-1, c))) / r;
}

/** Brightest catalogue star nearest to a sky point (J2000 catalogue frame; the zenith is of date — difference < 0.4°). */
export function nearestStar(raDeg: number, decDeg: number, magLimit = 3.5): { id: string; name: string | null; sep: number; mag: number } {
  let best = { id: '', name: null as string | null, sep: 999, mag: 99 };
  for (const [hip, ra, dec, mag] of STARS) {
    if (mag > magLimit) continue;
    const s = angularDistance(raDeg, decDeg, ra, dec);
    if (s < best.sep) best = { id: `HIP ${hip}`, name: NAMES[String(hip)] ?? null, sep: s, mag };
  }
  return best;
}

/** Colour of a star from its B−V index (approximate blackbody tint, for rendering only). */
export function bvToRgb(bv: number): [number, number, number] {
  const t = Math.max(-0.4, Math.min(2, bv));
  if (t < 0) return [0.7, 0.8, 1];
  if (t < 0.4) return [0.9, 0.93, 1];
  if (t < 0.8) return [1, 0.96, 0.85];
  if (t < 1.4) return [1, 0.82, 0.6];
  return [1, 0.68, 0.45];
}
