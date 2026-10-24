import type { Plate } from '../books/plates';

const INK: Record<string, string> = { gold: '#d6ac62', ink: '#f4ebdc', crimson: '#c0394a', faint: '#5e574d' };

export function PlateSvg({ plate, title, light = false }: { plate: Plate; title?: string; light?: boolean }) {
  const ink = light ? { ...INK, ink: '#1a1a1a', faint: '#9a9288', gold: '#9a7233' } : INK;
  const S = 300;
  return (
    <svg viewBox={`0 0 ${S} ${S}`} role="img" aria-label={title ?? plate.title}>
      <rect x="0" y="0" width={S} height={S} fill={light ? '#f6f1e7' : '#0d0c0b'} />
      {plate.prims.map((p, i) => {
        switch (p.t) {
          case 'line':
            return <line key={i} x1={p.x1 * S} y1={p.y1 * S} x2={p.x2 * S} y2={p.y2 * S} stroke={ink[p.ink]} strokeWidth={p.w ?? 1} strokeLinecap="round" />;
          case 'circle':
            return <circle key={i} cx={p.cx * S} cy={p.cy * S} r={p.r * S} stroke={ink[p.ink]} fill={p.fill ? ink[p.ink] : 'none'} strokeWidth={1} />;
          case 'rect':
            return <rect key={i} x={p.x * S} y={p.y * S} width={p.w * S} height={p.h * S} stroke={p.fill ? 'none' : ink[p.ink]} fill={p.fill ? ink[p.ink] : 'none'} />;
          case 'poly':
            return <polygon key={i} points={p.pts.map(([x, y]) => `${x * S},${y * S}`).join(' ')} stroke={ink[p.ink]} fill={p.fill ? ink[p.ink] : 'none'} fillOpacity={p.fill ? 0.25 : 0} strokeWidth={1.4} />;
          case 'text':
            return (
              <text key={i} x={p.x * S} y={p.y * S} fill={ink[p.ink]} fontSize={p.size ?? 10} textAnchor={p.anchor ?? 'start'} fontFamily="JetBrains Mono, DejaVu Sans Mono, monospace">
                {p.text}
              </text>
            );
        }
      })}
    </svg>
  );
}
