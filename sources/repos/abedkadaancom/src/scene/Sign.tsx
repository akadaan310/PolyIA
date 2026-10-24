import { Text } from '@react-three/drei';
import type { ComponentProps } from 'react';
import { configureTextBuilder } from 'troika-three-text';
import { SIGN_FONTS } from '../style/bible';

// troika fetches fallback fonts from a public CDN when a glyph is missing. Every
// sign's glyphs are covered by the bundled fonts (tools/check-glyphs.mjs), and the
// fallback is pointed at this site so no third-party request can ever be made.
configureTextBuilder({ unicodeFontsURL: '/fonts/unicode-fallback-disabled' });

const FONT = {
  engraved: SIGN_FONTS.engraved,
  luminous: SIGN_FONTS.luminous,
  // Mathematical inscriptions need ℤ, ∀, ⊕, subscripts: DejaVu Sans Mono covers them.
  math: '/fonts/pdf/DejaVuSansMono.ttf',
} as const;

type Props = Omit<ComponentProps<typeof Text>, 'font' | 'children'> & { text: string; mood?: keyof typeof FONT };

/** World-space signage with real glyphs (troika SDF text). */
export function Sign({ text, mood = 'engraved', fontSize = 0.6, color, ...rest }: Props) {
  const c = color ?? (mood === 'engraved' ? '#D6AC62' : '#F1D79C');
  return (
    <Text
      font={FONT[mood]}
      fontSize={fontSize}
      color={c}
      anchorX="center"
      anchorY="middle"
      letterSpacing={mood === 'engraved' ? 0.14 : 0.01}
      outlineWidth={mood === 'engraved' ? 0.004 : 0}
      outlineColor="#000000"
      material-toneMapped={false}
      {...rest}
    >
      {text}
    </Text>
  );
}
