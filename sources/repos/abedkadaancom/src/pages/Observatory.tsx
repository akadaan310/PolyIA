import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { feature } from 'topojson-client';
import type { Topology, GeometryCollection } from 'topojson-specification';
import landTopo from '../data/land-110m.json';
import { computeSky, localSiderealHours, moonPhaseDeg, nearestStar, skyCondition, STAR_COUNT, STAR_SOURCE, sunAltitude, validateObserver, zenith, type SkyObject } from '../math/sky';
import { FIXTURES, fetchStreets, geocode, normalizeShape, round3, SAMPLE_PLACES, type PathCandidate } from '../world/geo';
import { bestCorrespondence, compare, wordString, type Normalization } from '../math/paths';
import { DEFAULT_OBSERVER, updateWorld, useStore } from '../state/store';
import { ImageSculptureExhibit } from '../exhibits/ImageSculpture';
import { Crumbs, usePageTitle } from '../ui/bits';
import type { PathJob } from '../workers/paths.worker';

// ---------------------------------------------------------------- globe
type Ring = [number, number][];
let landRings: Ring[] | null = null;
function rings(): Ring[] {
  if (landRings) return landRings;
  const topo = landTopo as unknown as Topology<{ land: GeometryCollection }>;
  const fc = feature(topo, topo.objects.land) as unknown as { features: { geometry: { type: string; coordinates: number[][][] | number[][][][] } }[] };
  const out: Ring[] = [];
  for (const f of fc.features) {
    const g = f.geometry;
    if (g.type === 'Polygon') for (const r of g.coordinates as number[][][]) out.push(r as Ring);
    else for (const p of g.coordinates as number[][][][]) for (const r of p) out.push(r as Ring);
  }
  landRings = out;
  return out;
}

function ortho(lon: number, lat: number, lon0: number, lat0: number): [number, number, boolean] {
  const r = Math.PI / 180;
  const [l, p, l0, p0] = [lon * r, lat * r, lon0 * r, lat0 * r];
  const cosc = Math.sin(p0) * Math.sin(p) + Math.cos(p0) * Math.cos(p) * Math.cos(l - l0);
  const x = Math.cos(p) * Math.sin(l - l0);
  const y = Math.cos(p0) * Math.sin(p) - Math.sin(p0) * Math.cos(p) * Math.cos(l - l0);
  return [x, y, cosc >= 0];
}

function Globe({ lat, lon, second }: { lat: number; lon: number; second?: { lat: number; lon: number } | null }) {
  const [view, setView] = useState({ lon, lat });
  useEffect(() => setView({ lon, lat }), [lon, lat]);
  const drag = useRef<{ x: number; y: number; lon: number; lat: number } | null>(null);
  const R = 140;
  const C = 150;
  const paths = useMemo(() => {
    const ds: string[] = [];
    for (const ring of rings()) {
      let d = '';
      let pen = false;
      for (const [lo, la] of ring) {
        const [x, y, vis] = ortho(lo, la, view.lon, view.lat);
        if (vis) {
          d += `${pen ? 'L' : 'M'}${(C + x * R).toFixed(1)} ${(C - y * R).toFixed(1)}`;
          pen = true;
        } else pen = false;
      }
      if (d) ds.push(d);
    }
    return ds;
  }, [view]);
  const grat = useMemo(() => {
    const ds: string[] = [];
    for (let lo = -180; lo < 180; lo += 30) {
      let d = '';
      let pen = false;
      for (let la = -90; la <= 90; la += 5) {
        const [x, y, v] = ortho(lo, la, view.lon, view.lat);
        if (v) { d += `${pen ? 'L' : 'M'}${C + x * R} ${C - y * R}`; pen = true; } else pen = false;
      }
      ds.push(d);
    }
    for (let la = -60; la <= 60; la += 30) {
      let d = '';
      let pen = false;
      for (let lo = -180; lo <= 180; lo += 5) {
        const [x, y, v] = ortho(lo, la, view.lon, view.lat);
        if (v) { d += `${pen ? 'L' : 'M'}${C + x * R} ${C - y * R}`; pen = true; } else pen = false;
      }
      ds.push(d);
    }
    return ds;
  }, [view]);
  const mark = (p: { lat: number; lon: number }, color: string, key: string) => {
    const [x, y, v] = ortho(p.lon, p.lat, view.lon, view.lat);
    return v ? <circle key={key} cx={C + x * R} cy={C - y * R} r={5} fill={color} stroke="#0a0a0a" /> : null;
  };
  return (
    <figure className="figure">
      <svg
        viewBox="0 0 300 300"
        role="img"
        aria-label={`Globe centred near latitude ${view.lat.toFixed(1)}, longitude ${view.lon.toFixed(1)}`}
        style={{ touchAction: 'none', cursor: 'grab' }}
        onPointerDown={(e) => { drag.current = { x: e.clientX, y: e.clientY, ...view }; (e.target as Element).setPointerCapture?.(e.pointerId); }}
        onPointerMove={(e) => { if (!drag.current) return; const d = drag.current; setView({ lon: ((d.lon - (e.clientX - d.x) * 0.5 + 540) % 360) - 180, lat: Math.max(-85, Math.min(85, d.lat + (e.clientY - d.y) * 0.5)) }); }}
        onPointerUp={() => (drag.current = null)}
      >
        <circle cx={C} cy={C} r={R} fill="#0c1218" stroke="#d6ac62" strokeWidth={0.8} />
        {grat.map((d, i) => <path key={`g${i}`} d={d} fill="none" stroke="#2a3540" strokeWidth={0.5} />)}
        {paths.map((d, i) => <path key={i} d={d} fill="none" stroke="#b9a27a" strokeWidth={0.8} />)}
        {mark({ lat, lon }, '#f1d79c', 'a')}
        {second ? mark(second, '#c0394a', 'b') : null}
      </svg>
      <figcaption>Orthographic globe (drag to turn). Land: Natural Earth 1:110m (public domain) via world-atlas 2.0.2. Gold: the observer; crimson: the linked place.</figcaption>
    </figure>
  );
}

// ---------------------------------------------------------------- sky chart
function SkyChart({ objects, condition, zen, campus }: { objects: SkyObject[]; condition: string; zen: { raDeg: number; decDeg: number }; campus: [SkyObject, SkyObject][] }) {
  const R = 145;
  const C = 150;
  const P = (alt: number, az: number): [number, number] => {
    const r = R * Math.tan(((90 - alt) * Math.PI) / 360); // stereographic, horizon at r = R·tan 45° = R
    const a = (az * Math.PI) / 180;
    return [C - r * Math.sin(a), C - r * Math.cos(a)];
  };
  const day = condition === 'day';
  const visible = objects.filter((o) => o.alt > 0);
  return (
    <figure className="figure">
      <svg viewBox="0 0 300 300" role="img" aria-label={`All-sky chart: ${visible.filter((o) => o.kind === 'star').length} catalogue stars above the horizon; condition ${condition}`}>
        <circle cx={C} cy={C} r={R} fill={day ? '#1d3550' : condition === 'night' ? '#05060a' : '#101828'} stroke="#d6ac62" />
        {[30, 60].map((alt) => <circle key={alt} cx={C} cy={C} r={R * Math.tan(((90 - alt) * Math.PI) / 360)} fill="none" stroke="#28303c" strokeWidth={0.5} />)}
        {(['N', 'E', 'S', 'W'] as const).map((d, i) => {
          const [x, y] = P(-6, i * 90);
          return <text key={d} x={x} y={y + 4} textAnchor="middle" fontSize="11" fill="#d6ac62">{d}</text>;
        })}
        {visible.filter((o) => o.kind === 'star').map((s) => {
          const [x, y] = P(s.alt, s.az);
          return <circle key={s.id} cx={x} cy={y} r={Math.max(0.5, 3.2 - 0.55 * s.mag)} fill="#f4ebdc" opacity={day ? 0.25 : 0.95} />;
        })}
        {campus.map(([a, b], i) => {
          const [x1, y1] = P(a.alt, a.az);
          const [x2, y2] = P(b.alt, b.az);
          return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#c0394a" strokeDasharray="3 3" strokeWidth={1} />;
        })}
        {visible.filter((o) => o.kind !== 'star').map((o) => {
          const [x, y] = P(o.alt, o.az);
          return (
            <g key={o.id}>
              <circle cx={x} cy={y} r={o.kind === 'sun' ? 7 : o.kind === 'moon' ? 6 : 3} fill={o.kind === 'sun' ? '#ffd76a' : o.kind === 'moon' ? '#e9e4d8' : '#f1d79c'} />
              <text x={x + 6} y={y - 5} fontSize="9" fill="#f1d79c">{o.name}</text>
            </g>
          );
        })}
        {visible.filter((o) => o.kind === 'star' && o.name && o.mag < 1.6).map((s) => {
          const [x, y] = P(s.alt, s.az);
          return <text key={`n${s.id}`} x={x + 4} y={y + 3} fontSize="8" fill="#b6ab9a">{s.name}</text>;
        })}
        <circle cx={C} cy={C} r={2} fill="#d6ac62" />
        <text x={C + 4} y={C - 4} fontSize="8" fill="#d6ac62">zenith δ {zen.decDeg.toFixed(1)}°</text>
      </svg>
      <figcaption>
        Stereographic all-sky chart, north up, east left (as seen looking up). White: {STAR_COUNT} Hipparcos stars (mag ≤ 5) at computed positions. Gold: Sun, Moon and planets (astronomy-engine). <span style={{ color: '#f0b3bb' }}>Crimson dashes: an authored campus constellation, fiction drawn on real positions.</span>
      </figcaption>
    </figure>
  );
}

// ---------------------------------------------------------------- path overlay
function PathOverlay({ a, b, normalization, mode }: { a: PathCandidate; b: PathCandidate; normalization: Normalization; mode: 'overlay' | 'braid' | 'visit' }) {
  const na = normalizeShape(a.points);
  const nb = normalizeShape(b.points, normalization.startsWith('reverse'), normalization === 'mirror');
  const toD = (p: [number, number][], dy = 0) => p.map(([x, y], i) => `${i ? 'L' : 'M'}${20 + x * 260} ${150 - (y + dy) * 260}`).join(' ');
  return (
    <figure className="figure">
      <svg viewBox="0 0 300 300" role="img" aria-label="Overlay of two normalized paths">
        <style>{`.braid{stroke-dasharray:10 10;animation:dash 2s linear infinite}@keyframes dash{to{stroke-dashoffset:-40}}`}</style>
        <path d={toD(na, mode === 'braid' ? 0.01 : 0)} fill="none" stroke="#f1d79c" strokeWidth={2.4} className={mode === 'braid' ? 'braid' : ''} />
        <path d={toD(nb, mode === 'braid' ? -0.01 : 0)} fill="none" stroke="#c0394a" strokeWidth={1.6} className={mode === 'braid' ? 'braid' : ''} style={mode === 'braid' ? { animationDirection: 'reverse' } : undefined} />
      </svg>
      <figcaption>Gold: {a.name}. Crimson: {b.name} after normalization “{normalization}”. Both are translated to start at the origin, rotated so the first segment points right, and scaled to unit length. {mode === 'braid' ? 'Braid is an authored visual: the two paths are interleaved, not physically joined.' : ''}</figcaption>
    </figure>
  );
}

function usePathWorker() {
  const ref = useRef<Worker | null>(null);
  useEffect(() => {
    try {
      ref.current = new Worker(new URL('../workers/paths.worker.ts', import.meta.url), { type: 'module' });
    } catch {
      ref.current = null;
    }
    return () => ref.current?.terminate();
  }, []);
  return (job: PathJob): Promise<(ReturnType<typeof compare> & { id: string })[]> =>
    new Promise((resolve) => {
      const w = ref.current;
      const local = () => resolve(job.candidates.map((c) => ({ id: c.id, ...(job.normalization === 'best' ? bestCorrespondence(job.source, c.sig) : compare(job.source, c.sig, job.normalization)) })).sort((x, y) => y.similarity - x.similarity));
      if (!w) return local();
      w.onmessage = (e) => resolve(e.data);
      w.onerror = () => local();
      w.postMessage(job);
    });
}

// ---------------------------------------------------------------- page
function toLocalInput(d: Date) {
  const p = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
}

export function Observatory() {
  usePageTitle('The Observatory');
  const navigate = useNavigate();
  const observer = useStore((s) => s.world.observer);
  const [latIn, setLatIn] = useState(String(observer.lat));
  const [lonIn, setLonIn] = useState(String(observer.lon));
  const [when, setWhen] = useState(() => toLocalInput(new Date()));
  const [query, setQuery] = useState('');
  const [geo, setGeo] = useState<{ status: 'idle' | 'busy' | 'error' | 'none' | 'ok'; msg?: string; display?: string; precision?: string; provider?: string }>({ status: 'idle' });
  const [linked, setLinked] = useState(SAMPLE_PLACES[1]!);
  const date = useMemo(() => new Date(when), [when]);
  useEffect(() => {
    if (!Number.isNaN(date.getTime())) updateWorld({ skyTime: date.toISOString() });
  }, [date]);
  const o = { lat: observer.lat, lon: observer.lon, date };
  const invalid = validateObserver(o);
  const sky = useMemo(() => (invalid ? [] : computeSky(o, 5)), [observer.lat, observer.lon, when]); // eslint-disable-line react-hooks/exhaustive-deps
  const sunAlt = invalid ? 0 : sunAltitude(o);
  const condition = skyCondition(sunAlt);
  const zen = invalid ? { raHours: 0, raDeg: 0, decDeg: 0 } : zenith(o);
  const zenStar = nearestStar(zen.raDeg, zen.decDeg);
  const zenB = zenith({ lat: linked.lat, lon: linked.lon, date });
  // authored campus constellation: the five brightest stars above 20°, joined in order of azimuth (fiction)
  const campusLines = useMemo(() => {
    const top = sky.filter((s) => s.kind === 'star' && s.alt > 20).sort((a, b) => a.mag - b.mag).slice(0, 5).sort((a, b) => a.az - b.az);
    return top.slice(1).map((s, i) => [top[i]!, s] as [SkyObject, SkyObject]);
  }, [sky]);
  const planets = sky.filter((x) => x.kind !== 'star');

  const setObserver = (lat: number, lon: number, label: string, provenance: string) => {
    updateWorld({ observer: { lat: round3(lat), lon: round3(lon), label, provenance } });
    setLatIn(String(round3(lat)));
    setLonIn(String(round3(lon)));
  };

  // path correspondence
  const [candidates, setCandidates] = useState<PathCandidate[]>(FIXTURES);
  const [streetsStatus, setStreetsStatus] = useState<string | null>(null);
  const [srcId, setSrcId] = useState(FIXTURES[0]!.id);
  const [norm, setNorm] = useState<Normalization | 'best'>('best');
  const [results, setResults] = useState<(ReturnType<typeof compare> & { id: string })[]>([]);
  const [chosen, setChosen] = useState<string | null>(null);
  const [mode, setMode] = useState<'visit' | 'overlay' | 'braid'>('overlay');
  const runJob = usePathWorker();
  const src = candidates.find((c) => c.id === srcId) ?? candidates[0]!;
  useEffect(() => {
    let live = true;
    runJob({ source: src.sig, candidates: candidates.filter((c) => c.id !== src.id).map((c) => ({ id: c.id, sig: c.sig })), normalization: norm }).then((r) => {
      if (!live) return;
      setResults(r);
      setChosen(r[0]?.id ?? null);
    });
    return () => {
      live = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [srcId, norm, candidates]);
  const best = results.find((r) => r.id === chosen);
  const other = candidates.find((c) => c.id === chosen);

  return (
    <article>
      <Crumbs items={[['Campus', '/'], ['Observatory']]} />
      <h1>The Observatory</h1>
      <p>An address is a gateway to computational geography. Choose a place, see the real sky above it at any moment, and compare the shapes of paths. Every number here is computed in your browser; remote services are contacted only when you press a button that says so.</p>

      <h2>I. The observer</h2>
      <p className="small">
        Current: <strong>{observer.label}</strong> — {observer.lat.toFixed(3)}°, {observer.lon.toFixed(3)}°. <span className="muted">{observer.provenance}</span>
      </p>
      <fieldset>
        <legend>Offline sample locations (openly labelled examples)</legend>
        <div className="btn-row">
          {SAMPLE_PLACES.map((p) => (
            <button key={p.label} className="btn small" onClick={() => setObserver(p.lat, p.lon, `${p.label} (offline sample)`, p.provenance)}>
              {p.label}
            </button>
          ))}
        </div>
      </fieldset>
      <fieldset>
        <legend>Known coordinates (no third-party service)</legend>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: 8, alignItems: 'end' }}>
          <div>
            <label htmlFor="lat">Latitude °</label>
            <input id="lat" type="number" step="0.001" value={latIn} onChange={(e) => setLatIn(e.target.value)} />
          </div>
          <div>
            <label htmlFor="lon">Longitude °</label>
            <input id="lon" type="number" step="0.001" value={lonIn} onChange={(e) => setLonIn(e.target.value)} />
          </div>
          <button className="btn" onClick={() => { const la = Number(latIn); const lo = Number(lonIn); if (!validateObserver({ lat: la, lon: lo, date: new Date() })) setObserver(la, lo, 'Coordinates you entered', 'Entered directly; no geocoder used. Rounded to 3 decimals.'); }}>
            Use
          </button>
        </div>
      </fieldset>
      <fieldset>
        <legend>Find a place or address (sends your text to OpenStreetMap Nominatim)</legend>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            if (!query.trim()) return;
            setGeo({ status: 'busy' });
            try {
              const r = await geocode(query.trim());
              if (!r) setGeo({ status: 'none', msg: 'No match. Try a town or landmark, or enter coordinates.' });
              else {
                setObserver(r.lat, r.lon, 'Geocoded location', `${r.provider}; precision: ${r.precision}; rounded to 3 decimals (~100 m). The address text is not stored.`);
                setGeo({ status: 'ok', display: r.displayName, precision: r.precision, provider: r.provider });
              }
            } catch (err) {
              setGeo({ status: 'error', msg: `${(err as Error).message}. The geocoder is unavailable; the offline samples and coordinates still work.` });
            }
          }}
        >
          <label htmlFor="q">Place or address</label>
          <input id="q" type="text" value={query} onChange={(e) => setQuery(e.target.value)} autoComplete="off" />
          <div className="btn-row">
            <button className="btn primary" type="submit" disabled={geo.status === 'busy'}>
              {geo.status === 'busy' ? 'Asking Nominatim…' : 'Find (one request to Nominatim)'}
            </button>
          </div>
        </form>
        {geo.status === 'ok' ? <p className="small">Match: {geo.display} · precision: {geo.precision} · provider: {geo.provider}. Only rounded coordinates are kept.</p> : null}
        {geo.msg ? <p className="small" role="status">{geo.msg}</p> : null}
      </fieldset>
      <Globe lat={observer.lat} lon={observer.lon} second={linked} />

      <h2>II. The sky above the observer</h2>
      <label htmlFor="when">Moment (your browser’s time zone: {Intl.DateTimeFormat().resolvedOptions().timeZone})</label>
      <input id="when" type="datetime-local" value={when} onChange={(e) => setWhen(e.target.value)} />
      <div className="btn-row">
        <button className="btn small" onClick={() => setWhen(toLocalInput(new Date()))}>Now</button>
        <button className="btn small" onClick={() => { const d = new Date(date); d.setHours(d.getHours() + 12); setWhen(toLocalInput(d)); }}>+12 hours</button>
        <Link className="btn small" to="/observatory/sky" style={{ textDecoration: 'none' }}>Look up from the campus (3D)</Link>
      </div>
      {invalid ? (
        <p className="notice">{invalid}</p>
      ) : (
        <>
          <p className="small" aria-live="polite">
            UTC {date.toISOString().slice(0, 16).replace('T', ' ')} · Sun altitude {sunAlt.toFixed(1)}° → <strong>{condition}</strong> · local apparent sidereal time {localSiderealHours(o).toFixed(3)} h · Moon phase angle {moonPhaseDeg(date).toFixed(0)}° · frame: horizontal (altitude/azimuth), refraction “normal”.
          </p>
          <SkyChart objects={sky} condition={condition} zen={zen} campus={campusLines} />
          {condition === 'day' ? <p className="small muted">Daylight: stars are not visible to the eye now, but their positions are still computed and drawn faintly.</p> : null}
          <table className="data">
            <thead>
              <tr><th>body</th><th>altitude</th><th>azimuth</th></tr>
            </thead>
            <tbody>
              {planets.map((p) => (
                <tr key={p.id}><td>{p.name}</td><td>{p.alt.toFixed(1)}°{p.alt < 0 ? ' (below horizon)' : ''}</td><td>{p.az.toFixed(1)}°</td></tr>
              ))}
            </tbody>
          </table>
          <p className="small muted">Sources: {STAR_SOURCE}. Planetary positions: astronomy-engine 2.1.19 (Don Cross, MIT licence), topocentric, aberration and nutation included. The observer’s own civil time zone is not computed (no time-zone database is bundled); times are shown in UTC and in your browser’s zone. Repeatable: the same place and moment give the same chart.</p>
        </>
      )}

      <h2>III. Ground to sky: the zenith map</h2>
      <div className="def">
        <b>Definition.</b> Z(φ, λ, t) = (α, δ) = (LAST(λ, t), φ): the point straight overhead has declination equal to the latitude and right ascension equal to the local apparent sidereal time.
        <div className="math-block">{`Z(${observer.lat.toFixed(3)}°, ${observer.lon.toFixed(3)}°, t) = (α ${zen.raHours.toFixed(3)} h, δ ${zen.decDeg.toFixed(3)}°)\nnearest star brighter than mag 3.5: ${zenStar.name ?? zenStar.id} (mag ${zenStar.mag}) at ${zenStar.sep.toFixed(2)}°`}</div>
        <b>Declared loss.</b> Z forgets height, terrain and weather; at a fixed latitude it is many-to-one over a sidereal day; it uses coordinates of date, so the same place drifts slowly across the catalogue over years (precession).
      </div>
      <fieldset>
        <legend>A linked place</legend>
        <select aria-label="Linked place" value={linked.label} onChange={(e) => setLinked(SAMPLE_PLACES.find((p) => p.label === e.target.value)!)}>
          {SAMPLE_PLACES.map((p) => <option key={p.label}>{p.label}</option>)}
        </select>
        <p className="small">
          Zenith of {linked.label} (offline sample): α {zenB.raHours.toFixed(3)} h, δ {zenB.decDeg.toFixed(3)}°. Angular separation of the two zeniths:{' '}
          {(Math.acos(Math.min(1, Math.max(-1, Math.sin((zen.decDeg * Math.PI) / 180) * Math.sin((zenB.decDeg * Math.PI) / 180) + Math.cos((zen.decDeg * Math.PI) / 180) * Math.cos((zenB.decDeg * Math.PI) / 180) * Math.cos(((zen.raDeg - zenB.raDeg) * Math.PI) / 180)))) * 180 / Math.PI).toFixed(2)}° — equal, up to the difference between geodetic and geocentric latitude (under 0.2°), to the great-circle angle between the two places on Earth, because at a fixed instant Z is a rigid rotation of the sphere.
        </p>
      </fieldset>

      <h2>IV. Geometry of linked places</h2>
      <p className="small">A path becomes a typed word: each turn is quantized to L (&gt;60° left), l, S (within ±20°), r, R. Signatures are compared by normalized Levenshtein distance after a normalization. Similar shapes are a mathematical correspondence. They do not imply a tunnel, a cause or any physical connection.</p>
      <div className="btn-row">
        <button
          className="btn"
          onClick={async () => {
            setStreetsStatus('Asking the Overpass API for streets within 350 m…');
            try {
              const s = await fetchStreets(observer.lat, observer.lon);
              setCandidates([...FIXTURES, ...s]);
              setStreetsStatus(s.length ? `${s.length} OpenStreetMap ways loaded near the observer (data © OpenStreetMap contributors, ODbL 1.0). Coverage reflects OSM data, which varies by place.` : 'No street ways were returned for this location; OSM coverage may be sparse here.');
            } catch (e) {
              setStreetsStatus(`${(e as Error).message}. Overpass is unavailable; the synthetic fixtures remain.`);
            }
          }}
        >
          Load real streets near the observer (one Overpass request)
        </button>
      </div>
      {streetsStatus ? <p className="small" role="status">{streetsStatus}</p> : <p className="small muted">Until you load streets, only clearly disclosed synthetic fixtures are used.</p>}
      <label htmlFor="src">Source path</label>
      <select id="src" value={srcId} onChange={(e) => setSrcId(e.target.value)}>
        {candidates.map((c) => <option key={c.id} value={c.id}>{c.source === 'synthetic' ? '[synthetic] ' : '[OSM] '}{c.name}</option>)}
      </select>
      <p className="small">
        signature: <code>{wordString(src.sig.word)}</code> · length {src.sig.totalLength.toFixed(0)} m · total turning {src.sig.totalTurnDeg.toFixed(0)}°{src.sig.junctionDegrees.length ? ` · junction degrees ${src.sig.junctionDegrees.join(',')}` : ''} · <span className="muted">{src.note}</span>
      </p>
      <label htmlFor="norm">Normalization</label>
      <select id="norm" value={norm} onChange={(e) => setNorm(e.target.value as Normalization | 'best')}>
        <option value="best">best of all four (none, reverse, mirror, reverse+mirror)</option>
        <option value="none">none</option>
        <option value="reverse">reverse (walk it backwards)</option>
        <option value="mirror">mirror</option>
        <option value="reverse+mirror">reverse + mirror</option>
      </select>
      <table className="data" style={{ marginTop: 8 }}>
        <thead>
          <tr><th>candidate</th><th>word</th><th>normalization</th><th>similarity</th><th>status</th></tr>
        </thead>
        <tbody>
          {results.slice(0, 10).map((r) => {
            const c = candidates.find((x) => x.id === r.id)!;
            return (
              <tr key={r.id} onClick={() => setChosen(r.id)} style={{ cursor: 'pointer', background: chosen === r.id ? 'rgba(214,172,98,0.1)' : undefined }}>
                <td>{c.source === 'synthetic' ? '[synthetic] ' : '[OSM] '}{c.name}</td>
                <td><code>{wordString(c.sig.word)}</code></td>
                <td>{r.normalization}</td>
                <td>{(r.similarity * 100).toFixed(0)}% (d = {r.distance})</td>
                <td>{r.status}{c.source === 'osm' ? ' · unverified on the ground' : ''}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      {best && other ? (
        <>
          <div className="btn-row" role="radiogroup" aria-label="Experience mode">
            {(['overlay', 'braid', 'visit'] as const).map((m) => (
              <label key={m} className="choice">
                <input type="radio" name="mode" checked={mode === m} onChange={() => setMode(m)} /> {m}
              </label>
            ))}
          </div>
          <PathOverlay a={src} b={other} normalization={best.normalization} mode={mode} />
          <div className="btn-row">
            <button
              className="btn primary"
              disabled={best.status === 'weak'}
              onClick={() => {
                updateWorld({ portal: { a: src.name, b: other.name, similarity: best.similarity, normalization: best.normalization, mode } });
                if (mode === 'visit') navigate('/atrium');
              }}
            >
              {best.status === 'weak' ? 'Correspondence too weak for a portal' : `Open a fictional portal (${mode})`}
            </button>
          </div>
          <p className="small muted">The portal is campus mythology: it appears in the courtyard, labelled as fiction, to visualize this computed correspondence.</p>
        </>
      ) : null}

      <h2>V. Imagistratum: the sky chart is an image</h2>
      <p>The chart above is the <em>image</em> of the celestial sphere under a projection, as a photograph is the image of a scene under a camera. In linear algebra the image is the reachable output set of a map, so the same questions apply: what is its rank, what is lost, and which inputs collide? The exhibit below computes them for any 3×3 matrix.</p>
      <details>
        <summary>Open the image, rank and projection-loss exhibit</summary>
        <ImageSculptureExhibit />
      </details>
      <p className="small muted">Reset the observer to the default sample: <button className="btn small" onClick={() => setObserver(DEFAULT_OBSERVER.lat, DEFAULT_OBSERVER.lon, DEFAULT_OBSERVER.label, DEFAULT_OBSERVER.provenance)}>Greenwich</button></p>
    </article>
  );
}
