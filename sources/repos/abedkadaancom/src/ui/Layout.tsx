import { Component, lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { NavDrawer, ResidentDialog, SettingsDialog, TopBar, useRouteAnnouncement } from './Chrome';
import { CampusSilhouette } from './Crest';
import { getState, markVisited, setState, useStore } from '../state/store';
import { locationForPath, NAV_ORDER, LOCATIONS } from '../world/locations';
import { DIVISIONS } from '../content/registry';
import { welcomeLine } from '../world/residents';
import { travel, speak } from '../audio/engine';

const CampusCanvas = lazy(() => import('../scene/CampusCanvas'));

class SceneBoundary extends Component<{ children: ReactNode; onError: () => void }, { failed: boolean }> {
  override state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  override componentDidCatch() {
    this.props.onError();
  }
  override render() {
    return this.state.failed ? null : this.props.children;
  }
}

function hasWebGL(): boolean {
  try {
    const c = document.createElement('canvas');
    return !!(c.getContext('webgl2') || c.getContext('webgl'));
  } catch {
    return false;
  }
}

export function Layout() {
  const loc = useLocation();
  const navigate = useNavigate();
  const settings = useStore((s) => s.settings);
  const lastRoute = useStore((s) => s.lastRoute);
  const [menu, setMenu] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [webgl] = useState(() => hasWebGL());
  const [sceneFailed, setSceneFailed] = useState(false);
  const [contextLost, setContextLost] = useState(false);
  const [canvasKey, setCanvasKey] = useState(0);
  const [mount3d, setMount3d] = useState(false);
  const [introPlaying, setIntroPlaying] = useState(() => loc.pathname === '/' && !getState().introSeen);
  const [sheet, setSheet] = useState<'peek' | 'half' | 'full'>('half');
  const scrollRef = useRef<HTMLDivElement>(null);
  const announcement = useRouteAnnouncement();
  const location = useMemo(() => locationForPath(loc.pathname), [loc.pathname]);
  const show3d = webgl && !settings.textOnly && !sceneFailed;
  const resumeTarget = lastRoute && lastRoute !== '/' ? LOCATIONS.find((l) => lastRoute.startsWith(l.path) && l.path !== '/') : null;

  useEffect(() => {
    document.body.classList.toggle('text-only', settings.textOnly);
    document.body.classList.toggle('no-webgl', !webgl || sceneFailed);
    document.documentElement.dataset.contrast = settings.highContrast ? 'high' : 'normal';
  }, [settings.textOnly, settings.highContrast, webgl, sceneFailed]);

  // Mount the 3D campus right after first paint: the static composition shows immediately.
  useEffect(() => {
    if (!show3d) return;
    const id = requestAnimationFrame(() => setMount3d(true));
    return () => cancelAnimationFrame(id);
  }, [show3d]);

  // Route side effects: visited set, last route, sound, scroll.
  useEffect(() => {
    markVisited(location.id);
    if (loc.pathname !== '/') setState((s) => ({ ...s, lastRoute: loc.pathname }));
    travel(location.id === 'scriptorium' || location.id === 'library');
    scrollRef.current?.scrollTo({ top: 0 });
  }, [loc.pathname, location.id]);

  const finishIntro = useCallback(() => {
    setIntroPlaying(false);
    if (!getState().introSeen) setState((s) => ({ ...s, introSeen: true }));
  }, []);
  const skipIntro = () => {
    window.dispatchEvent(new Event('su:skip-intro'));
    finishIntro();
  };

  // Keyboard navigation (ignored while typing).
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement;
      if (t.closest('input, textarea, select, [contenteditable]') || e.metaKey || e.ctrlKey || e.altKey) return;
      const i = NAV_ORDER.indexOf(loc.pathname);
      if (e.key === ']' || e.key === '[') {
        const next = NAV_ORDER[(Math.max(0, i) + (e.key === ']' ? 1 : NAV_ORDER.length - 1)) % NAV_ORDER.length]!;
        navigate(next);
      } else if (/^[1-6]$/.test(e.key)) navigate(`/divisions/${DIVISIONS[Number(e.key) - 1]!.id}`);
      else if (e.key === 'g' || e.key === 'G') navigate('/gate');
      else if (e.key === 'a' || e.key === 'A') navigate('/atrium');
      else if (e.key === 'm' || e.key === 'M') setMenu(true);
      else if (e.key === 'Escape') {
        if (introPlaying) skipIntro();
        setMenu(false);
        setSettingsOpen(false);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loc.pathname, introPlaying]);

  const welcome = welcomeLine(getState());
  useEffect(() => {
    if (introPlaying && settings.voice) speak(welcome);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <a href="#content" className="sr-only">
        Skip to content
      </a>
      {show3d ? (
        <div className="stage">
          {!mount3d || contextLost ? (
            <div className="backdrop">
              <CampusSilhouette />
            </div>
          ) : null}
          {mount3d && !contextLost ? (
            <SceneBoundary onError={() => setSceneFailed(true)}>
              <Suspense fallback={<div className="backdrop"><CampusSilhouette /></div>}>
                <CampusCanvas key={canvasKey} location={location} intro={introPlaying} onIntroDone={finishIntro} onContextLost={() => setContextLost(true)} panelOpen={!(introPlaying && loc.pathname === '/')} />
              </Suspense>
            </SceneBoundary>
          ) : null}
        </div>
      ) : (
        <div className="backdrop" aria-hidden="true">
          <CampusSilhouette />
        </div>
      )}
      <div className="vignette" />
      <TopBar onMenu={() => setMenu(true)} onSettings={() => setSettingsOpen(true)} />

      {contextLost ? (
        <div className="toast" role="status">
          The 3D view paused because the graphics context was lost.{' '}
          <button className="btn" onClick={() => { setContextLost(false); setCanvasKey((k) => k + 1); }}>
            Restore 3D
          </button>
        </div>
      ) : null}

      {introPlaying && loc.pathname === '/' ? (
        <div className="intro" role="region" aria-label="Arrival">
          <h1 className="intro-title">SUBSTRATE UNIVERSITY</h1>
          <p className="intro-sub">Haq Roots · a university of the mathematics of possible worlds</p>
          <p className="intro-hm">
            <span className="engraved small" style={{ color: 'var(--gold)' }}>Harness Master · </span>
            {welcome}
          </p>
          <div className="btn-row">
            <button className="btn primary" onClick={() => { skipIntro(); navigate('/gate'); }}>
              Enter the Gate
            </button>
            <button className="btn" onClick={skipIntro}>
              Skip intro
            </button>
            {resumeTarget ? (
              <button className="btn" onClick={() => { skipIntro(); navigate(lastRoute!); }}>
                Resume at {resumeTarget.short}
              </button>
            ) : null}
          </div>
          <p className="keys">Drag or swipe to look around · <kbd>Esc</kbd> skips · reduced motion and sound are in ⚙</p>
        </div>
      ) : (
        <main className="panel" id="content" data-sheet={sheet} aria-label="Page">
          <button className="panel-handle" onClick={() => setSheet(sheet === 'peek' ? 'half' : sheet === 'half' ? 'full' : 'peek')} aria-label={`Resize panel (currently ${sheet})`}>
            <span />
          </button>
          <div className="panel-tools no-print">
            {show3d ? (
              <button className="btn" onClick={() => setSheet(sheet === 'peek' ? 'half' : 'peek')}>
                {sheet === 'peek' ? 'Show page' : 'View campus'}
              </button>
            ) : null}
            <Link className="btn" to="/atrium" style={{ textDecoration: 'none' }}>
              Atrium
            </Link>
          </div>
          <div className="panel-scroll" ref={scrollRef}>
            <Outlet />
          </div>
        </main>
      )}
      <NavDrawer open={menu} onClose={() => setMenu(false)} />
      <SettingsDialog open={settingsOpen} onClose={() => setSettingsOpen(false)} />
      <ResidentDialog />
      <div className="sr-only" aria-live="polite">
        {announcement}
      </div>
    </>
  );
}
