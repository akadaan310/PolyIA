/** The university crest: an original equilateral arch over a root-glyph (a tree whose roots are a fold). */
export function Crest({ size = 34 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden="true">
      <defs>
        <linearGradient id="cg" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stopColor="#F1D79C" />
          <stop offset="1" stopColor="#B98D45" />
        </linearGradient>
      </defs>
      <path d="M12 60 V30 A20 20 0 0 1 32 4 A20 20 0 0 1 52 30 V60" fill="none" stroke="url(#cg)" strokeWidth="3" />
      <path d="M20 60 V34 A12 12 0 0 1 32 16 A12 12 0 0 1 44 34 V60" fill="none" stroke="#D6AC62" strokeWidth="1.2" opacity="0.7" />
      <path d="M32 22 V42 M32 42 L24 52 M32 42 L40 52 M24 52 L20 58 M24 52 L28 58 M40 52 L36 58 M40 52 L44 58" stroke="#F1D79C" strokeWidth="1.8" fill="none" strokeLinecap="round" />
      <circle cx="32" cy="22" r="2.6" fill="#8D232C" stroke="#F1D79C" strokeWidth="0.8" />
    </svg>
  );
}

/** Static first composition: the campus silhouette, drawn before any JavaScript-heavy 3D loads. */
export function CampusSilhouette() {
  return (
    <svg viewBox="0 0 1400 520" aria-hidden="true" preserveAspectRatio="xMidYMax meet">
      <defs>
        <linearGradient id="sil" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stopColor="#15120f" />
          <stop offset="1" stopColor="#060606" />
        </linearGradient>
      </defs>
      {Array.from({ length: 60 }, (_, i) => (
        <circle key={i} cx={(i * 211) % 1400} cy={(i * 97) % 260} r={i % 7 === 0 ? 1.6 : 0.8} fill="#f4ebdc" opacity={0.25 + ((i * 13) % 10) / 20} />
      ))}
      <path fill="url(#sil)" d="M0 520 V420 H180 V360 H210 V300 L232 250 L254 300 V360 H330 V400 H470 V210 L520 120 L570 210 V400 H600 V330 A100 100 0 0 1 800 330 V400 H830 V210 L880 120 L930 210 V400 H1070 V360 H1146 V300 L1168 250 L1190 300 V360 H1220 V420 H1400 V520 Z" />
      <path d="M640 400 V340 A60 60 0 0 1 760 340 V400" fill="none" stroke="#D6AC62" strokeWidth="2" opacity="0.8" />
      <text x="700" y="300" textAnchor="middle" fill="#D6AC62" fontFamily="Cinzel, serif" fontSize="22" letterSpacing="6">SUBSTRATE UNIVERSITY</text>
      {[490, 545, 850, 905].map((x) => (
        <rect key={x} x={x} y={260} width={8} height={40} fill="#e7b866" opacity="0.7" />
      ))}
    </svg>
  );
}
