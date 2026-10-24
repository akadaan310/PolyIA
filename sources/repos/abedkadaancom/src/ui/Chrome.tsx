import { useEffect, useRef, useState } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { Crest } from './Crest';
import { DIVISIONS } from '../content/registry';
import { resetAll, updateSettings, useStore, getState, setState } from '../state/store';
import { soundOff, soundOn, speak } from '../audio/engine';
import { RESIDENTS, residentLine, FICTION_NOTE } from '../world/residents';
import { openResident, useActiveResident } from './residentBus';

export function TopBar({ onMenu, onSettings }: { onMenu: () => void; onSettings: () => void }) {
  return (
    <header className="topbar">
      <button className="iconbtn" onClick={onMenu} aria-label="Open campus map" aria-haspopup="dialog">
        ☰ <span className="sr-only">Campus map</span>
      </button>
      <Link to="/" className="brand" aria-label="Substrate University — Haq Roots, home">
        <Crest />
        <span className="brand-text">
          <span className="brand-name">SUBSTRATE UNIVERSITY</span>
          <span className="brand-sub">Haq Roots</span>
        </span>
      </Link>
      <span className="spacer" />
      <Link to="/harness" className="btn no-print harness-link" style={{ textDecoration: 'none' }}>
        One-Day Harness
      </Link>
      <button className="iconbtn" onClick={onSettings} aria-label="Settings: motion, sound, contrast, quality" aria-haspopup="dialog">
        ⚙
      </button>
    </header>
  );
}

const GROUPS: { title: string; links: [string, string][] }[] = [
  { title: 'Arrive', links: [['/', 'The Approach'], ['/gate', 'The Gate · Hall of First Principles'], ['/atrium', 'The Atrium of Six Divisions']] },
  { title: 'The six divisions', links: DIVISIONS.map((d) => [`/divisions/${d.id}`, `${d.numeral}. ${d.name}`]) },
  { title: 'Halls', links: [['/library', 'The Library of Forms'], ['/observatory', 'The Observatory'], ['/harness-masters', 'The Hall of Harness Masters'], ['/scriptorium', 'The Scriptorium'], ['/common-room', 'Founder Office · Common Room']] },
  { title: 'Make and read', links: [['/harness', 'The One-Day Harness'], ['/glossary', 'The Glossary Field'], ['/library/computational-grammar-theory', 'Computational Grammar Theory (book)'], ['/about', 'About, credits and disclosures']] },
];

export function NavDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (open) ref.current?.querySelector<HTMLElement>('a')?.focus();
  }, [open]);
  if (!open) return null;
  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} />
      <div className="drawer" role="dialog" aria-modal="true" aria-label="Campus map" ref={ref} onKeyDown={(e) => e.key === 'Escape' && onClose()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span className="engraved small">Campus map</span>
          <button className="iconbtn" onClick={onClose} aria-label="Close campus map">
            ✕
          </button>
        </div>
        <nav aria-label="Campus locations">
          {GROUPS.map((g) => (
            <div key={g.title}>
              <div className="grp">{g.title}</div>
              {g.links.map(([to, label]) => (
                <NavLink key={to} to={to} end onClick={onClose}>
                  {label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
        <p className="keys" style={{ marginTop: '1rem' }}>
          Keys: <kbd>[</kbd> <kbd>]</kbd> previous / next place · <kbd>1</kbd>–<kbd>6</kbd> divisions · <kbd>G</kbd> Gate · <kbd>A</kbd> Atrium · <kbd>M</kbd> map · drag or swipe to look around.
        </p>
      </div>
    </>
  );
}

export function SettingsDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const s = useStore((x) => x.settings);
  const [confirmReset, setConfirmReset] = useState(false);
  if (!open) return null;
  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} />
      <div className="dialog" role="dialog" aria-modal="true" aria-label="Settings" onKeyDown={(e) => e.key === 'Escape' && onClose()}>
        <h2 style={{ marginTop: 0 }}>Settings</h2>
        <label className="choice">
          <input type="checkbox" checked={s.reducedMotion} onChange={(e) => updateSettings({ reducedMotion: e.target.checked })} autoFocus /> Reduced motion (camera cuts instead of flights; no rotating rings)
        </label>
        <label className="choice">
          <input
            type="checkbox"
            checked={s.sound}
            onChange={(e) => {
              updateSettings({ sound: e.target.checked });
              if (e.target.checked) soundOn();
              else soundOff();
            }}
          />{' '}
          Sound: procedural ambience, footsteps, page turns (synthesized live; off by default)
        </label>
        <label className="choice">
          <input type="checkbox" checked={s.voice} onChange={(e) => updateSettings({ voice: e.target.checked })} /> Read Harness Master lines aloud (browser speech synthesis; text stays primary)
        </label>
        <label className="choice">
          <input type="checkbox" checked={s.highContrast} onChange={(e) => updateSettings({ highContrast: e.target.checked })} /> High contrast
        </label>
        <label className="choice">
          <input type="checkbox" checked={s.textOnly} onChange={(e) => updateSettings({ textOnly: e.target.checked })} /> Text-only: hide the 3D campus and read pages as documents
        </label>
        <label htmlFor="quality">3D quality</label>
        <select id="quality" value={s.quality} onChange={(e) => updateSettings({ quality: e.target.value as typeof s.quality })}>
          <option value="auto">Automatic (detects phone or desktop)</option>
          <option value="low">Low: phones, 1× pixels, no reflections</option>
          <option value="medium">Medium: environment light, 1.5× pixels</option>
          <option value="high">High: wet-floor reflections, 2× pixels</option>
        </select>
        <h2>Your data</h2>
        <p className="small">Progress, drafts and books are stored only in this browser (localStorage) unless you opt into cloud sync in the Harness. Geocoding is sent to OpenStreetMap Nominatim only when you press “Find” in the Observatory.</p>
        {confirmReset ? (
          <div className="btn-row">
            <button className="btn crimson" onClick={() => { resetAll(); setConfirmReset(false); onClose(); }}>
              Yes, erase everything on this device
            </button>
            <button className="btn" onClick={() => setConfirmReset(false)}>
              Cancel
            </button>
          </div>
        ) : (
          <button className="btn" onClick={() => setConfirmReset(true)}>
            Erase my local progress…
          </button>
        )}
        <div className="btn-row" style={{ justifyContent: 'flex-end' }}>
          <button className="btn primary" onClick={onClose}>
            Done
          </button>
        </div>
      </div>
    </>
  );
}

export function ResidentDialog() {
  const id = useActiveResident();
  const state = useStore((s) => s);
  const r = RESIDENTS.find((x) => x.id === id);
  const [line, setLine] = useState<string | null>(null);
  useEffect(() => {
    if (!r) return;
    const mem = getState().residents[r.id] ?? { met: 0, lastLine: null };
    const out = residentLine(getState(), r, mem.met);
    setLine(out.line);
    setState((s) => ({ ...s, residents: { ...s.residents, [r.id]: { met: mem.met + 1, lastLine: out.line } } }));
    if (getState().settings.voice) speak(`${r.name}: ${out.line}`);
  }, [r]);
  if (!r) return null;
  return (
    <aside className="resident" role="dialog" aria-label={`${r.name}, ${r.role}`}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
        <div>
          <div className="engraved small" style={{ color: r.color }}>
            {r.role}
          </div>
          <div className="luminous" style={{ fontSize: '1.25rem' }}>
            {r.name}
          </div>
        </div>
        <button className="iconbtn" onClick={() => openResident(null)} aria-label="Close dialogue">
          ✕
        </button>
      </div>
      <p style={{ margin: '0.5rem 0' }}>“{line}”</p>
      <p className="small muted">{FICTION_NOTE} It remembers only this browser: met {state.residents[r.id]?.met ?? 0} time(s).</p>
      <div className="btn-row">
        <Link className="btn" to={r.home} onClick={() => openResident(null)} style={{ textDecoration: 'none' }}>
          Go where {r.name.split(' ').slice(-1)[0]} points
        </Link>
        <button
          className="btn"
          onClick={() => {
            const mem = getState().residents[r.id] ?? { met: 0, lastLine: null };
            const out = residentLine(getState(), r, mem.met);
            setLine(out.line);
            setState((s) => ({ ...s, residents: { ...s.residents, [r.id]: { met: mem.met + 1, lastLine: out.line } } }));
            if (getState().settings.voice) speak(out.line);
          }}
        >
          Ask more
        </button>
      </div>
    </aside>
  );
}

export function useRouteAnnouncement(): string {
  const loc = useLocation();
  const [msg, setMsg] = useState('');
  useEffect(() => {
    const t = setTimeout(() => setMsg(document.title), 50);
    return () => clearTimeout(t);
  }, [loc.pathname]);
  return msg;
}
