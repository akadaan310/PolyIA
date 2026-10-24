// Builds src/data/stars.json from the d3-celestial data package (BSD-3-Clause,
// Olaf Frohn; positions from the Hipparcos catalogue, J2000 / ICRS).
// Usage: node tools/build-stars.mjs <path-to-d3-celestial>/data
// Output: [[hip, raDeg, decDeg, mag, bv], ...] for mag <= 5.0, plus proper names.
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const dir = process.argv[2];
if (!dir) throw new Error('pass the d3-celestial data directory');
const stars = JSON.parse(readFileSync(join(dir, 'stars.6.json'), 'utf8'));
const names = JSON.parse(readFileSync(join(dir, 'starnames.json'), 'utf8'));
const out = [];
const named = {};
for (const f of stars.features) {
  const mag = Number(f.properties.mag);
  if (!(mag <= 5.0)) continue;
  let [lon, lat] = f.geometry.coordinates;
  const ra = (lon + 360) % 360; // d3-celestial stores RA as longitude in [-180, 180]
  out.push([f.id, +ra.toFixed(4), +lat.toFixed(4), mag, +(Number(f.properties.bv) || 0).toFixed(2)]);
  const n = names[f.id];
  if (n && n.name) named[f.id] = n.name;
}
out.sort((a, b) => a[3] - b[3]);
writeFileSync('src/data/stars.json', JSON.stringify({
  source: 'd3-celestial 0.7.35 data (BSD-3-Clause, (c) 2015 Olaf Frohn); Hipparcos positions, J2000/ICRS, mag <= 5.0',
  fields: ['hip', 'raDeg', 'decDeg', 'mag', 'bv'],
  stars: out,
  names: named,
}));
console.log(out.length, 'stars,', Object.keys(named).length, 'named');
