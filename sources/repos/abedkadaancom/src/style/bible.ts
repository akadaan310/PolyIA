// The cinematographic style bible, in code. Every colour, type mood, camera
// move and quality tier used by the campus is declared here, so the world and
// the pages share one visual grammar.

export const COLOR = {
  obsidian: '#0A0A0A',
  charcoal: '#1A1A1A',
  stone: '#24221f',
  gold: '#D6AC62',
  goldGlow: '#F1D79C',
  ivory: '#F4EBDC',
  crimson: '#8D232C',
  fog: '#0b0b0d',
} as const;

/** Three typography moods (see global.css for the CSS side). */
export const TYPE = {
  engraved: { family: 'Cinzel', weight: 600, tracking: '0.18em', use: 'Carved signage on stone, lintels, door names.' },
  luminous: { family: 'Cormorant Garamond', weight: 500, tracking: '0.02em', use: 'Glowing gold inscriptions and titles.' },
  practical: { family: 'Inter', weight: 400, tracking: '0', use: 'Reading, controls, captions.' },
  mathematical: { family: 'JetBrains Mono', weight: 400, tracking: '0', use: 'Equations, computed values, addresses.' },
} as const;

/** World-space sign fonts (WOFF, loaded by troika-three-text). */
export const SIGN_FONTS = {
  engraved: '/fonts/3d/cinzel-600.woff',
  luminous: '/fonts/3d/cormorant-500.woff',
  mono: '/fonts/3d/jbmono-400.woff',
};

/** Material rules: black stone is rough and slightly specular; gold is metallic and warm. */
export const MATERIAL = {
  blackStone: { color: '#3d3935', roughness: 0.78, metalness: 0.05 },
  polishedStone: { color: '#24211e', roughness: 0.3, metalness: 0.2 },
  wetFloor: { color: '#0c0c0c', roughness: 0.18, metalness: 0.4 },
  gold: { color: '#D6AC62', roughness: 0.32, metalness: 1, emissive: '#3a2a10' },
  goldGlow: { color: '#F1D79C', emissive: '#F1D79C', emissiveIntensity: 1.6 },
  crimsonGlass: { color: '#8D232C', emissive: '#5a1219', emissiveIntensity: 0.8, roughness: 0.2 },
  ivory: { color: '#F4EBDC', roughness: 0.6 },
} as const;

export interface Tier {
  id: 'low' | 'medium' | 'high';
  dpr: [number, number];
  reflections: boolean;
  environment: boolean;
  stars: number; // magnitude limit
  residents: number;
  shadows: boolean;
  antialias: boolean;
}

/** Mobile performance tiers. 'low' targets entry Android phones (e.g. Galaxy A16 class). */
export const TIERS: Record<Tier['id'], Tier> = {
  low: { id: 'low', dpr: [1, 1], reflections: false, environment: false, stars: 4.0, residents: 6, shadows: false, antialias: false },
  medium: { id: 'medium', dpr: [1, 1.5], reflections: false, environment: true, stars: 4.6, residents: 10, shadows: false, antialias: true },
  high: { id: 'high', dpr: [1, 2], reflections: true, environment: true, stars: 5.0, residents: 14, shadows: false, antialias: true },
};

export function detectTier(): Tier['id'] {
  if (typeof navigator === 'undefined') return 'medium';
  const mem = (navigator as Navigator & { deviceMemory?: number }).deviceMemory ?? 4;
  const cores = navigator.hardwareConcurrency ?? 4;
  const small = typeof window !== 'undefined' && Math.min(window.innerWidth, window.innerHeight) < 600;
  const coarse = typeof matchMedia === 'function' && matchMedia('(pointer: coarse)').matches;
  if ((small && coarse) || mem <= 3 || cores <= 4) return 'low';
  if (mem >= 8 && cores >= 8 && !coarse) return 'high';
  return 'medium';
}

/** Camera choreography: the approach is a single dolly with a slight crane, eased. */
export const CHOREOGRAPHY = {
  approachSeconds: 6.5,
  maxUnskippableSeconds: 0, // controls are available from the first frame
  ease: (t: number) => 1 - Math.pow(1 - t, 3),
  travelDamping: 2.4, // exponential damping rate for location-to-location moves
};

/** Scene lighting rules. */
export const LIGHTING = {
  ambient: 0.55,
  moon: { color: '#b9c4d6', intensity: 1.9 },
  key: { color: '#f1c27a', intensity: 0.9 },
  lanterns: { color: '#F1D79C', intensity: 14, distance: 22 },
  fogDensity: 0.0105,
};
